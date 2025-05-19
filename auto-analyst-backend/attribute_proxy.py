#!/usr/bin/env python3
# attribute_proxy.py - Proxy for attribute filtering functionality

import json
import logging
import os
import sys
import time
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("attribute-proxy")

# Configuration
MAIN_APP_URL = os.getenv("MAIN_APP_URL", "http://localhost:8000")
ATTRIBUTE_SERVER_URL = os.getenv("ATTRIBUTE_SERVER_URL", "http://localhost:8002")
PROXY_PORT = int(os.getenv("PROXY_PORT", "8080"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = Flask(__name__)
# Enable CORS with more explicit configuration
CORS(app, 
     origins=[FRONTEND_URL, "*"],  # Allow frontend and any origin during development
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"]
)

def check_server_health(url):
    """Check if a server is running by making a health check request"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def forward_request(target_url, path="", method=None, headers=None, data=None, params=None, timeout=30):
    """Forward a request to the specified URL and return the response"""
    if headers is None:
        headers = {}
    
    # Remove problematic headers that might cause issues
    for header in ['Host', 'Content-Length']:
        if header in headers:
            del headers[header]
    
    # Add some headers that will help with CORS
    headers['Origin'] = FRONTEND_URL
    
    url = f"{target_url}/{path}" if path else target_url
    method = method or request.method
    
    try:
        logger.info(f"Forwarding {method} request to {url}")
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            timeout=timeout,
            allow_redirects=True
        )
        
        # Copy the response headers to our response
        response_headers = dict(response.headers)
        # Add CORS headers
        response_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Expose-Headers': 'Content-Type, Authorization'
        })
        
        return Response(
            response=response.content,
            status=response.status_code,
            headers=response_headers,
            content_type=response.headers.get('Content-Type', 'application/json')
        )
    except requests.RequestException as e:
        logger.error(f"Error forwarding request to {url}: {str(e)}")
        # Check if the attribute server is available as fallback
        attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
        main_app_health = check_server_health(MAIN_APP_URL)
        
        # Try to provide a helpful response if servers are unavailable
        if not attribute_server_health and not main_app_health:
            return jsonify({
                "error": "Both main app and attribute servers are unavailable",
                "message": "Please check that the servers are running and try again",
                "success": False
            }), 503
        elif target_url == MAIN_APP_URL and not main_app_health:
            return jsonify({
                "error": "The main application server is unavailable",
                "message": "Unable to process LLM-based requests at this time",
                "success": False
            }), 503
        else:
            return jsonify({
                "error": str(e),
                "message": "Error processing your request",
                "success": False
            }), 503

def handle_options_request():
    """Handle OPTIONS request with proper CORS headers"""
    response = jsonify({'message': 'CORS preflight handled'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Max-Age', '86400')  # 24 hours
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    main_app_health = check_server_health(MAIN_APP_URL)
    
    return jsonify({
        "status": "healthy",
        "attribute_server": "up" if attribute_server_health else "down",
        "main_app": "up" if main_app_health else "down"
    })

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_proxy():
    """Proxy for chat requests - check if it's an attribute query first"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    try:
        # First check if this is an attribute query
        if request.is_json:
            data = request.get_json()
            if data and 'query' in data:
                # Try to identify if this is an attribute query
                try:
                    # Check if attribute server is available
                    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
                    if attribute_server_health:
                        # Check with the attribute server
                        logger.info(f"Checking if chat is an attribute query: {data['query']}")
                        attr_response = requests.post(
                            f"{ATTRIBUTE_SERVER_URL}/api/chat-attribute",
                            json=data,
                            timeout=5
                        )
                        
                        # If this is a valid attribute query, return the response
                        if attr_response.status_code == 200:
                            attr_data = attr_response.json()
                            if attr_data.get("is_attribute_query", False) and not attr_data.get("pass_through", False):
                                logger.info(f"Handling as attribute query: {data['query']}")
                                # Add CORS headers to the response
                                response = jsonify(attr_data)
                                response.headers.add('Access-Control-Allow-Origin', '*')
                                response.headers.add('Access-Control-Allow-Credentials', 'true')
                                return response
                except requests.RequestException as e:
                    logger.warning(f"Error checking attribute query (trying main app): {str(e)}")
        
        # If not an attribute query or check failed, check if main app is available
        main_app_health = check_server_health(MAIN_APP_URL)
        if main_app_health:
            # Forward to main app with a longer timeout for LLM processing
            logger.info("Forwarding chat request to main app")
            return forward_request(
                MAIN_APP_URL,
                path="chat",
                data=request.get_data(),
                headers=dict(request.headers),
                params=request.args,
                timeout=120  # Longer timeout for LLM processing
            )
        else:
            # If main app is not available, check if attribute server can handle it as fallback
            attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
            if attribute_server_health:
                # Use a simple fallback message for attributes only
                return jsonify({
                    "agent_name": "attribute_agent",
                    "query": data.get('query', 'unknown'),
                    "response": "I can only answer simple attribute questions about vehicles right now. The main analysis service is currently unavailable. Try asking about counts of vehicles by color, make, model, or year.",
                    "success": True
                })
            else:
                # Both servers are down
                return jsonify({
                    "error": "Both main app and attribute servers are unavailable",
                    "message": "Unable to process requests at this time",
                    "success": False
                }), 503
    except Exception as e:
        logger.error(f"Error in chat_proxy: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/attribute-query', methods=['POST', 'OPTIONS'])
def attribute_query_proxy():
    """Proxy for attribute-query endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_server_health:
        return forward_request(
            ATTRIBUTE_SERVER_URL,
            path="api/attribute-query",
            data=request.get_data(),
            headers=dict(request.headers),
            params=request.args
        )
    else:
        return jsonify({
            "error": "Attribute server is unavailable",
            "message": "Unable to process attribute queries at this time",
            "success": False
        }), 503

@app.route('/api/direct-count', methods=['POST', 'OPTIONS'])
def direct_count_proxy():
    """Proxy for direct-count endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_server_health:
        return forward_request(
            ATTRIBUTE_SERVER_URL,
            path="api/direct-count",
            data=request.get_data(),
            headers=dict(request.headers),
            params=request.args
        )
    else:
        return jsonify({
            "error": "Attribute server is unavailable",
            "message": "Unable to process count queries at this time",
            "success": False
        }), 503

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_all(path):
    """Catch-all proxy route that first tries the attribute server for known endpoints, then falls back to main app"""
    
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # First check if the attribute server has this endpoint
    attribute_server_endpoints = [
        'model', 'model-settings', 'settings/model', 'agents', 'api/model-settings', 'api/session-info'
    ]
    
    # Check if the path starts with any of these endpoints
    is_attribute_endpoint = any(path.startswith(endpoint) for endpoint in attribute_server_endpoints)
    
    logger.info(f"Processing request for {path} - attribute endpoint: {is_attribute_endpoint}")
    
    if is_attribute_endpoint:
        # Check if attribute server is available
        attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
        if attribute_server_health:
            # Try the attribute server first
            try:
                response = forward_request(
                    ATTRIBUTE_SERVER_URL,
                    path=path,
                    data=request.get_data(),
                    headers=dict(request.headers),
                    params=request.args
                )
                return response
            except Exception as e:
                logger.warning(f"Error from attribute server for {path}, falling back to main app: {str(e)}")
    
    # If not an attribute endpoint or attribute server failed/unavailable, try the main app
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:
        logger.info(f"Forwarding request to main app: {path}")
        return forward_request(
            MAIN_APP_URL,
            path=path,
            data=request.get_data(),
            headers=dict(request.headers),
            params=request.args
        )
    else:
        # Main app is unavailable - for attribute endpoints, check if attribute server is available as fallback
        if is_attribute_endpoint:
            attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
            if attribute_server_health:
                return forward_request(
                    ATTRIBUTE_SERVER_URL,
                    path=path,
                    data=request.get_data(),
                    headers=dict(request.headers),
                    params=request.args
                )
            
        # Both servers unavailable or not an attribute endpoint and main app is down
        return jsonify({
            "error": "Server unavailable",
            "message": f"The endpoint /{path} is not available at this time",
            "success": False
        }), 503

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    logger.info(f"Starting Attribute Proxy on port {PROXY_PORT}...")
    logger.info(f"Main App URL: {MAIN_APP_URL}")
    logger.info(f"Attribute Server URL: {ATTRIBUTE_SERVER_URL}")
    logger.info("Available endpoints:")
    logger.info("  - /health - Health check")
    logger.info("  - /chat - Chat proxy (tries attribute server first)")
    logger.info("  - /api/attribute-query - Attribute query proxy")
    logger.info("  - /api/direct-count - Direct count proxy")
    logger.info("  - /* - Proxy for all other endpoints")
    
    # Final health check
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    main_app_health = check_server_health(MAIN_APP_URL)
    
    if attribute_server_health and main_app_health:
        logger.info("✅ Both attribute server and main app are available")
    elif attribute_server_health:
        logger.warning("⚠️ Attribute server is available, but main app is not responding")
        logger.warning("LLM-based features will not be available")
    elif main_app_health:
        logger.warning("⚠️ Main app is available, but attribute server is not responding")
        logger.warning("Attribute filtering features will be limited")
    else:
        logger.error("❌ Neither attribute server nor main app is responding")
        logger.error("Most features will be unavailable")
    
    app.run(host='0.0.0.0', port=PROXY_PORT, debug=True) 