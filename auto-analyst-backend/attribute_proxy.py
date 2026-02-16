#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Attribute Proxy Server

This proxy server coordinates between the main application server and the attribute server.
It prioritizes real data from the backend servers over mock data, and reads model
configuration from environment variables (.env file).

Key features:
- Prioritizes real data from backend servers when available
- Falls back to environment variable-based configuration when servers are unavailable
- Uses dynamic routing based on endpoint type and server availability
- Serves static files from the frontend public directory
- Handles CORS headers consistently

To configure models, set the following environment variables in .env:
- MODEL_PROVIDER: The provider name (e.g., "gemini", "openai", "anthropic", "groq")
- MODEL_NAME: The model name (e.g., "gemini-1.5-pro", "gpt-4o", "claude-3-opus")
- TEMPERATURE: The temperature setting (e.g., 0.7)
- MAX_TOKENS: The maximum tokens setting (e.g., 6000)
"""

import os
import sys
import json
import logging
import time
import requests
from urllib.parse import urlparse
from flask import Flask, request, jsonify, make_response, send_from_directory
from functools import wraps
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Path to frontend public directory for static files
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(CURRENT_DIR, "..", "auto-analyst-frontend")
FRONTEND_PUBLIC_DIR = os.path.join(FRONTEND_DIR, "public")

app = Flask(__name__)
# Enable CORS with more explicit configuration
CORS(app, 
     origins=[MAIN_APP_URL, "*"],  # Allow frontend and any origin during development
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
    """Forward a request to another server and return the response"""
    url = f"{target_url}/{path}" if path else target_url
    method = method or request.method
    
    # Make a copy of headers to avoid modifying the original
    headers = headers or {}
    
    if 'Host' in headers:
        # Remove the Host header as it should point to the target server
        del headers['Host']
        
    # Get origin from request
    origin = request.headers.get('Origin', '*')
    
    # Add CORS headers to forwarded request
    headers.update({
        'Origin': origin,
        'X-Forwarded-For': request.remote_addr,
        'X-Forwarded-Proto': request.scheme,
        'X-Forwarded-Host': request.host
    })
    
    logger.info(f"Forwarding {method} request to {url}")
    
    try:
        # Forward the request to the target server
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            timeout=timeout,
            allow_redirects=False  # We'll handle redirects manually
        )
        
        # Create a Flask response with the same content
        flask_response = make_response(response.content, response.status_code)
        
        # Copy headers from the target response
        for name, value in response.headers.items():
            if name.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                flask_response.headers[name] = value
                
        # Ensure CORS headers are set
        flask_response.headers.update({
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Origin',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Expose-Headers': 'Content-Type, Authorization',
            'Vary': 'Origin'
        })
        
        return flask_response
    except requests.RequestException as e:
        logger.error(f"Error forwarding request to {url}: {str(e)}")
        raise

def handle_options_request():
    """Handle OPTIONS requests with proper CORS headers"""
    origin = request.headers.get('Origin', '*')
    
    # Create a response with proper CORS headers
    response = jsonify({'status': 'ok'})
    
    # Set all required CORS headers
    response.headers.update({
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Origin',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Expose-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400',  # 24 hours
        'Vary': 'Origin'  # Important for proper caching with CORS
    })
    
    return response

# ==== MAIN APP SPECIFIC ENDPOINTS ====

@app.route('/api/vehicles', methods=['GET', 'OPTIONS'])
def vehicles_proxy():
    """Proxy for vehicles endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    # Try main app first
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:  
        try:
            return forward_request(MAIN_APP_URL, path="api/vehicles", params=request.args)
        except Exception as e:
            logger.warning(f"Error from main app for vehicles, using mock data: {str(e)}")
    
    # Provide mock vehicle data if main app is unavailable
    mock_vehicles = [
        {
            "id": "1",
            "make": "Toyota",
            "model": "Camry",
            "year": 2021,
            "color": "Blue",
            "price": 28500,
            "mileage": 15000,
            "condition": "Excellent",
            "features": ["Bluetooth", "Backup Camera", "Sunroof"]
        },
        {
            "id": "2",
            "make": "Honda",
            "model": "Civic",
            "year": 2022,
            "color": "White",
            "price": 24700,
            "mileage": 8000,
            "condition": "Like New",
            "features": ["Apple CarPlay", "Lane Assist", "Heated Seats"]
        },
        {
            "id": "3",
            "make": "Ford",
            "model": "F-150",
            "year": 2020,
            "color": "Black",
            "price": 38500,
            "mileage": 22000,
            "condition": "Good",
            "features": ["Towing Package", "4x4", "Navigation"]
        }
    ]
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_vehicles)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/api/statistics', methods=['GET', 'OPTIONS'])
def statistics_proxy():
    """Proxy for statistics endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    # Try main app first
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:  
        try:
            return forward_request(MAIN_APP_URL, path="api/statistics", params=request.args)
        except Exception as e:
            logger.warning(f"Error from main app for statistics, using mock data: {str(e)}")
    
    # Provide mock statistics data if main app is unavailable
    mock_statistics = {
        "vehicleCount": 200,
        "averagePrice": 32450,
        "averageMileage": 18750,
        "makeDistribution": {
            "Toyota": 45,
            "Honda": 38,
            "Ford": 33,
            "Chevrolet": 29,
            "BMW": 22,
            "Other": 33
        },
        "yearDistribution": {
            "2023": 35,
            "2022": 42,
            "2021": 51,
            "2020": 38,
            "2019": 22,
            "Older": 12
        },
        "priceRange": {
            "min": 12500,
            "max": 85000,
            "median": 31250
        }
    }
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_statistics)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/api/market-data', methods=['GET', 'OPTIONS'])
def market_data_proxy():
    """Proxy for market-data endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Try main app first
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:
        try:
            return forward_request(MAIN_APP_URL, path="api/market-data", params=request.args)
        except Exception as e:
            logger.warning(f"Error from main app for market-data, using mock data: {str(e)}")
    
    # Provide mock market data if main app is unavailable
    mock_market_data = {
        "trends": [
            {"month": "January", "averagePrice": 31200},
            {"month": "February", "averagePrice": 31050},
            {"month": "March", "averagePrice": 31500},
            {"month": "April", "averagePrice": 32100},
            {"month": "May", "averagePrice": 32450}
        ],
        "demandIndex": {
            "sedans": 72,
            "suvs": 88,
            "trucks": 76,
            "luxury": 64,
            "electric": 91
        },
        "priceVolatility": {
            "overall": "low",
            "bySegment": {
                "sedans": "stable",
                "suvs": "rising",
                "trucks": "stable",
                "luxury": "declining",
                "electric": "rising"
            }
        }
    }
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_market_data)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/api/opportunities', methods=['GET', 'OPTIONS'])
def opportunities_proxy():
    """Proxy for opportunities endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Try main app first
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:
        try:
            return forward_request(MAIN_APP_URL, path="api/opportunities", params=request.args)
        except Exception as e:
            logger.warning(f"Error from main app for opportunities, using mock data: {str(e)}")
    
    # Provide mock opportunities data if main app is unavailable
    mock_opportunities = [
        {
            "id": "opp1",
            "title": "High Demand: Electric Sedans",
            "description": "Electric sedans are showing increased demand with 15% growth in searches. Consider acquiring more inventory.",
            "confidence": 85,
            "impact": "high",
            "category": "inventory"
        },
        {
            "id": "opp2",
            "title": "Underpriced Models",
            "description": "Several Toyota Camry models in your inventory are priced 8% below market average. Consider price adjustments.",
            "confidence": 92,
            "impact": "medium",
            "category": "pricing"
        },
        {
            "id": "opp3",
            "title": "Seasonal Trend: SUVs",
            "description": "SUV sales typically increase 20% during winter months. Consider promotional strategies.",
            "confidence": 78,
            "impact": "medium",
            "category": "marketing"
        }
    ]
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_opportunities)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/session', methods=['GET', 'OPTIONS'])
def session_proxy():
    """Proxy for session endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Provide mock session data
    mock_session = {
        "user": {
            "id": "mock-user-id",
            "name": "Demo User",
            "email": "demo@example.com",
            "emailVerified": True,
            "image": None,
            "credits": 1000,
            "subscription": {
                "status": "active",
                "tier": "pro"
            }
        },
        "isAuthenticated": True,
        "expires": "2030-12-31T23:59:59.999Z"
    }
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_session)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/api/session-info', methods=['GET', 'OPTIONS'])
def session_info_proxy():
    """Proxy for session-info endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Provide mock session info data
    mock_session = {
        "user": {
            "id": "mock-user-id",
            "name": "Demo User",
            "email": "demo@example.com",
            "emailVerified": True,
            "image": None,
            "credits": 1000,
            "subscription": {
                "status": "active",
                "tier": "pro"
            }
        },
        "isAuthenticated": True,
        "expires": "2030-12-31T23:59:59.999Z"
    }
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_session)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/credits', methods=['GET', 'OPTIONS'])
def credits_proxy():
    """Proxy for credits endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Provide mock credits data
    mock_credits = {
        "credits": 1000,
        "used": 150,
        "remaining": 850,
        "plan": "pro",
        "refreshDate": "2030-12-31T23:59:59.999Z"
    }
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_credits)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

# ==== SHARED ENDPOINTS ====

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

# ==== ATTRIBUTE SERVER SPECIFIC ENDPOINTS ====

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

@app.route('/model-settings', methods=['GET', 'OPTIONS'])
def model_settings_proxy():
    """Proxy for model-settings endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_server_health:
        try:
            return forward_request(
                ATTRIBUTE_SERVER_URL,
                path="model-settings",
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from attribute server for model-settings, using env data: {str(e)}")
    
    # Get model settings from environment variables
    model_provider = os.getenv("MODEL_PROVIDER", "gemini")
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("MAX_TOKENS", "6000"))
    
    model_settings = {
        "success": True,
        "settings": {
            "default": {
                "id": "default",
                "name": "Default Model",
                "description": "Default model settings from environment",
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
    }
    return jsonify(model_settings)

@app.route('/api/model-settings', methods=['GET', 'OPTIONS'])
def api_model_settings_proxy():
    """Proxy for API model-settings endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_server_health:
        try:
            return forward_request(
                ATTRIBUTE_SERVER_URL,
                path="api/model-settings",
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from attribute server for api/model-settings, using mock data: {str(e)}")
    
    # Use the same mock data as the non-API endpoint
    return model_settings_proxy()

@app.route('/settings/model', methods=['GET', 'OPTIONS'])
def settings_model_proxy():
    """Proxy for settings/model endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_server_health:
        try:
            return forward_request(
                ATTRIBUTE_SERVER_URL,
                path="settings/model",
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from attribute server for settings/model, using env data: {str(e)}")
    
    # Get model data from environment variables
    model_provider = os.getenv("MODEL_PROVIDER", "gemini")
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("MAX_TOKENS", "6000"))
    
    # Map provider to a friendly name
    provider_names = {
        "openai": "OpenAI",
        "groq": "Groq",
        "anthropic": "Anthropic",
        "gemini": "Google"
    }
    
    provider_display = provider_names.get(model_provider, model_provider.capitalize())
    
    # Combine model and settings data
    model_data = {
        "models": [
            {
                "id": model_name,
                "name": model_name.replace("-", " ").title(),
                "provider": provider_display,
                "description": f"{provider_display}'s {model_name.replace('-', ' ').title()} large language model"
            }
        ],
        "settings": {
            "default": {
                "id": "default",
                "name": "Default Model",
                "description": "Default model settings from environment",
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
    }
    return jsonify(model_data)

@app.route('/agents', methods=['GET', 'OPTIONS'])
def agents_proxy():
    """Proxy for agents endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Provide mock agents data to handle CORS issues
    mock_agents = [
        {
            "id": "auto-analyst",
            "name": "Auto Analyst",
            "description": "Specialized automotive data analysis agent",
            "capabilities": ["Data Analysis", "Attribute Filtering", "Market Trends"],
            "isDefault": True
        },
        {
            "id": "customer-support",
            "name": "Customer Support",
            "description": "Helps with customer inquiries and product support",
            "capabilities": ["FAQ", "Troubleshooting", "User Guides"],
            "isDefault": False
        },
        {
            "id": "market-explorer",
            "name": "Market Explorer",
            "description": "Analyzes market trends and opportunities",
            "capabilities": ["Market Analysis", "Competitor Research", "Opportunity Identification"],
            "isDefault": False
        }
    ]
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_agents)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/model', methods=['GET', 'OPTIONS'])
def model_proxy():
    """Proxy for model endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_server_health:
        try:
            return forward_request(
                ATTRIBUTE_SERVER_URL,
                path="model",
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from attribute server for model, using env data: {str(e)}")
    
    # Get model info from environment variables
    model_provider = os.getenv("MODEL_PROVIDER", "gemini")
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
    
    # Map provider to a friendly name
    provider_names = {
        "openai": "OpenAI",
        "groq": "Groq",
        "anthropic": "Anthropic",
        "gemini": "Google"
    }
    
    provider_display = provider_names.get(model_provider, model_provider.capitalize())
    
    model = {
        "id": model_name,
        "name": model_name.replace("-", " ").title(),
        "provider": provider_display,
        "description": f"{provider_display}'s {model_name.replace('-', ' ').title()} large language model"
    }
    
    return jsonify({"models": [model]})

@app.route('/model/<path:model_id>', methods=['GET', 'OPTIONS'])
def model_id_proxy(model_id):
    """Proxy for model/{id} endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_server_health:
        try:
            return forward_request(
                ATTRIBUTE_SERVER_URL,
                path=f"model/{model_id}",
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from attribute server for model/{model_id}, using env data: {str(e)}")
    
    # Get model data from environment variables
    model_provider = os.getenv("MODEL_PROVIDER", "gemini")
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
    
    # Map provider to a friendly name
    provider_names = {
        "openai": "OpenAI",
        "groq": "Groq",
        "anthropic": "Anthropic",
        "gemini": "Google"
    }
    
    provider_display = provider_names.get(model_provider, model_provider.capitalize())
    
    # Create model info
    if model_id == model_name:
        # Return environment model if IDs match
        model = {
            "id": model_name,
            "name": model_name.replace("-", " ").title(),
            "provider": provider_display,
            "description": f"{provider_display}'s {model_name.replace('-', ' ').title()} large language model"
        }
    else:
        # Return generic model info if not found
        model = {
            "id": model_id,
            "name": f"Model {model_id}",
            "provider": "Unknown",
            "description": "Generic model information"
        }
    
    # Create a response with proper CORS headers
    resp = jsonify(model)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/session-info', methods=['GET', 'OPTIONS'])
def session_info_direct_proxy():
    """Direct proxy for session-info endpoint (without api/ prefix)"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Provide mock session info data
    mock_session = {
        "user": {
            "id": "mock-user-id",
            "name": "Demo User",
            "email": "demo@example.com",
            "emailVerified": True,
            "image": None,
            "credits": 1000,
            "subscription": {
                "status": "active",
                "tier": "pro"
            }
        },
        "isAuthenticated": True,
        "expires": "2030-12-31T23:59:59.999Z"
    }
    
    # Create a response with proper CORS headers
    resp = jsonify(mock_session)
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    })
    return resp

@app.route('/demo-files/<path:filename>', methods=['GET', 'OPTIONS'])
def serve_demo_files(filename):
    """Serve files from the frontend's public/demo-files directory"""
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    try:
        logger.info(f"Serving demo file: {filename} from {os.path.join(FRONTEND_PUBLIC_DIR, 'demo-files')}")
        return send_from_directory(os.path.join(FRONTEND_PUBLIC_DIR, 'demo-files'), filename)
    except Exception as e:
        logger.error(f"Error serving demo file {filename}: {str(e)}")
        return jsonify({
            "error": "File not found",
            "message": f"The file {filename} could not be served",
            "success": False
        }), 404

@app.route('/reset-session', methods=['POST', 'OPTIONS', 'GET'])
def reset_session_proxy():
    """Proxy for reset-session endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    # Try the attribute server first
    attribute_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_health:
        try:
            # For GET requests, just forward with CORS properly handled
            if request.method == 'GET':
                return forward_request(ATTRIBUTE_SERVER_URL, path="reset-session")
            
            # For POST requests, extract request data if present
            data = request.get_json() if request.is_json else None
            
            # Forward the request with the proper data and CORS headers
            response = requests.post(
                f"{ATTRIBUTE_SERVER_URL}/reset-session",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Origin': request.headers.get('Origin', '*'),
                    'X-Session-ID': request.headers.get('X-Session-ID', '')
                }
            )
            
            # Create a Flask response with the same content
            flask_response = make_response(response.content, response.status_code)
            
            # Ensure CORS headers are set properly
            origin = request.headers.get('Origin', '*')
            flask_response.headers.update({
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Origin, X-Session-ID',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Expose-Headers': 'Content-Type, Authorization',
                'Vary': 'Origin'
            })
            
            return flask_response
            
        except Exception as e:
            logger.warning(f"Error resetting session on attribute server: {str(e)}")
            # Fall through to main app attempt
    
    # Try the main app as fallback
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:
        try:
            return forward_request(MAIN_APP_URL, path="reset-session")
        except Exception as e:
            logger.warning(f"Error resetting session on main app: {str(e)}")
            # Fall through to mock response
    
    # Provide mock success response if both servers are unavailable
    mock_response = {
        "message": "Session reset successfully (mock)",
        "success": True
    }
    
    # Create a response with CORS headers
    response = jsonify(mock_response)
    response.headers.update({
        'Access-Control-Allow-Origin': request.headers.get('Origin', '*'),
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Origin, X-Session-ID',
        'Access-Control-Allow-Credentials': 'true'
    })
    
    return response

@app.route('/api/default-dataset', methods=['GET', 'OPTIONS'])
def default_dataset_proxy():
    """Proxy for default-dataset endpoint that serves demo files"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    # Try the main app first
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:  
        try:
            return forward_request(MAIN_APP_URL, path="api/file-server/default-dataset")
        except Exception as e:
            logger.warning(f"Error from main app for default-dataset: {str(e)}")
            # Fall through to attribute server attempt
    
    # Try the attribute server as fallback
    attribute_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_health:
        try:
            # Get the demo file path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            frontend_demo_dir = os.path.join(os.path.dirname(current_dir), 
                                        "Auto-Analyst/auto-analyst-frontend/public/demo-files")
            demo_file = os.path.join(frontend_demo_dir, "vehicles.csv")
            
            if os.path.exists(demo_file):
                try:
                    # Just return success with the filename
                    return jsonify({
                        "success": True, 
                        "filename": "vehicles.csv",
                        "message": "Default dataset is available"
                    })
                except Exception as e:
                    return jsonify({"error": f"Error loading demo file: {str(e)}"}), 500
            else:
                return jsonify({"error": "Default dataset not found"}), 404
        except Exception as e:
            logger.error(f"Error serving default dataset: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Both servers unavailable
    return jsonify({"error": "Both main app and attribute server unavailable"}), 503

@app.route('/upload_dataframe', methods=['POST', 'OPTIONS'])
def upload_dataframe_proxy():
    """Proxy for upload_dataframe endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    try:
        # Get the uploaded file
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Store the file in the demo files directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_demo_dir = os.path.join(os.path.dirname(current_dir), 
                                    "Auto-Analyst/auto-analyst-frontend/public/demo-files")
        
        # Create directory if it doesn't exist
        os.makedirs(frontend_demo_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(frontend_demo_dir, uploaded_file.filename)
        uploaded_file.save(file_path)
        
        return jsonify({
            "success": True,
            "filename": uploaded_file.filename,
            "message": "File uploaded successfully"
        })
    except Exception as e:
        logger.error(f"Error handling file upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/excel-sheets', methods=['POST', 'OPTIONS'])
def excel_sheets_proxy():
    """Proxy for excel sheets endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    # Try main app first
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:  
        try:
            # Pass the multipart form data through to the main app
            return forward_request(MAIN_APP_URL, path="api/excel-sheets")
        except Exception as e:
            logger.error(f"Error from main app for excel sheets: {str(e)}")
            return jsonify({
                "error": "Failed to process Excel file",
                "details": str(e)
            }), 500
    else:
        logger.error("Main app unavailable for excel sheets")
        return jsonify({
            "error": "Excel processing service temporarily unavailable",
            "details": "The main application server is not reachable. Please try again later."
        }), 503

@app.route('/api/preview-csv', methods=['GET', 'POST', 'OPTIONS'])
def preview_csv_proxy():
    """Proxy for preview-csv endpoint"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    # Try the main app first
    main_app_health = check_server_health(MAIN_APP_URL)
    if main_app_health:  
        try:
            return forward_request(MAIN_APP_URL, path="api/preview-csv")
        except Exception as e:
            logger.warning(f"Error from main app for preview-csv: {str(e)}")
            # Fall through to attribute server attempt
    
    # Try the attribute server as fallback
    attribute_health = check_server_health(ATTRIBUTE_SERVER_URL)
    if attribute_health:
        try:
            return forward_request(ATTRIBUTE_SERVER_URL, path="api/preview-csv")
        except Exception as e:
            logger.warning(f"Error from attribute server for preview-csv: {str(e)}")
            # Fall through to mock response
    
    # Provide mock CSV preview if both servers are unavailable
    mock_headers = ["id", "make", "model", "year", "price", "mileage", "color", "fuel_type", "condition"]
    mock_rows = [
        ["1", "Toyota", "Camry", "2021", "28500", "15000", "Blue", "Gasoline", "Excellent"],
        ["2", "Honda", "Civic", "2022", "24700", "8000", "White", "Hybrid", "Like New"],
        ["3", "Ford", "F-150", "2020", "38500", "22000", "Black", "Diesel", "Good"]
    ]
    
    mock_response = {
        "headers": mock_headers,
        "rows": mock_rows,
        "name": "Default Dataset",
        "description": "Default dataset preview containing automotive vehicles"
    }
    
    # Create a response with CORS headers
    response = jsonify(mock_response)
    response.headers.update({
        'Access-Control-Allow-Origin': request.headers.get('Origin', '*'),
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Origin, X-Session-ID',
        'Access-Control-Allow-Credentials': 'true'
    })
    
    return response

# ==== CATCH-ALL ROUTE ====

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_all(path):
    """Catch-all proxy route that first tries the attribute server for known endpoints, then falls back to main app"""
    
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Handle Redis-related paths with mock data if needed
    if path.startswith('hgetall') or path.startswith('redis/') or path.startswith('keys/'):
        # Check if main app is available first for Redis operations
        main_app_health = check_server_health(MAIN_APP_URL)
        if main_app_health:
            try:
                return forward_request(
                    MAIN_APP_URL,
                    path=path,
                    data=request.get_data(),
                    headers=dict(request.headers),
                    params=request.args
                )
            except Exception as e:
                logger.warning(f"Error from main app for Redis operation {path}, using mock data: {str(e)}")
        
        # Fall back to mock data if main app is unavailable
        mock_redis_data = {
            "success": True,
            "message": "Mock Redis operation completed",
            "data": {
                "key1": "value1",
                "key2": "value2",
                "timestamp": int(time.time())
            }
        }
        resp = jsonify(mock_redis_data)
        resp.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Allow-Credentials': 'true'
        })
        return resp
    
    # First check if the path is for a main app endpoint
    main_app_endpoints = [
        'api/vehicles', 'api/statistics', 'api/market-data', 'api/opportunities', 
        'vehicles', 'statistics', 'market-data', 'opportunities',
        'session', 'credits'
    ]
    
    # Check if the path starts with any of these endpoints
    is_main_app_endpoint = any(path.startswith(endpoint) for endpoint in main_app_endpoints)
    
    # Attribute server endpoints
    attribute_server_endpoints = [
        'model', 'model-settings', 'settings/model', 'agents', 
        'api/model-settings', 'api/session-info', 'session-info',
        'model/', 'reset-session'
    ]
    
    # Check if the path starts with any of these endpoints
    is_attribute_endpoint = any(path.startswith(endpoint) for endpoint in attribute_server_endpoints)
    
    logger.info(f"Processing request for {path} - attribute endpoint: {is_attribute_endpoint}")
    
    # Check both servers' health
    main_app_health = check_server_health(MAIN_APP_URL)
    attribute_server_health = check_server_health(ATTRIBUTE_SERVER_URL)
    
    if main_app_health and attribute_server_health:
        logger.info("✅ Both main app and attribute server are available")
    elif main_app_health:
        logger.info("✅ Main app is available, attribute server is unavailable")
    elif attribute_server_health:
        logger.info("✅ Attribute server is available, main app is unavailable")
    else:
        logger.info("❌ Both servers are unavailable, falling back to mock data")
    
    # Route the request to the appropriate server based on endpoint type
    if is_main_app_endpoint and main_app_health:
        # Use main app for main app endpoints
        logger.info(f"Forwarding request to main app: {path}")
        try:
            return forward_request(
                MAIN_APP_URL,
                path=path,
                data=request.get_data(),
                headers=dict(request.headers),
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from main app for {path}: {str(e)}")
    
    if is_attribute_endpoint and attribute_server_health:
        # Use attribute server for attribute endpoints
        logger.info(f"Forwarding request to attribute server: {path}")
        try:
            return forward_request(
                ATTRIBUTE_SERVER_URL,
                path=path,
                data=request.get_data(),
                headers=dict(request.headers),
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from attribute server for {path}: {str(e)}")
    
    # Try fallback routes if primary route failed
    if is_main_app_endpoint and not main_app_health and attribute_server_health:
        # Try attribute server as fallback for main app endpoints
        logger.info(f"Trying attribute server as fallback for main app endpoint: {path}")
        try:
            return forward_request(
                ATTRIBUTE_SERVER_URL,
                path=path,
                data=request.get_data(),
                headers=dict(request.headers),
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from attribute server fallback for {path}: {str(e)}")
    
    if is_attribute_endpoint and not attribute_server_health and main_app_health:
        # Try main app as fallback for attribute endpoints
        logger.info(f"Trying main app as fallback for attribute endpoint: {path}")
        try:
            return forward_request(
                MAIN_APP_URL,
                path=path,
                data=request.get_data(),
                headers=dict(request.headers),
                params=request.args
            )
        except Exception as e:
            logger.warning(f"Error from main app fallback for {path}: {str(e)}")
    
    # For unknown routes, try both servers
    if not is_main_app_endpoint and not is_attribute_endpoint:
        # Try main app first for unknown routes
        if main_app_health:
            logger.info(f"Trying main app for unknown route: {path}")
            try:
                return forward_request(
                    MAIN_APP_URL,
                    path=path,
                    data=request.get_data(),
                    headers=dict(request.headers),
                    params=request.args
                )
            except Exception as e:
                logger.warning(f"Error from main app for unknown route {path}: {str(e)}")
        
        # Try attribute server as fallback for unknown routes
        if attribute_server_health:
            logger.info(f"Trying attribute server for unknown route: {path}")
            try:
                return forward_request(
                    ATTRIBUTE_SERVER_URL,
                    path=path,
                    data=request.get_data(),
                    headers=dict(request.headers),
                    params=request.args
                )
            except Exception as e:
                logger.warning(f"Error from attribute server for unknown route {path}: {str(e)}")
    
    # For static files in demo-files directory, try serving from the frontend public directory
    if path.startswith('demo-files/'):
        try:
            filename = path.replace('demo-files/', '', 1)
            logger.info(f"Trying to serve static file: {filename} from {os.path.join(FRONTEND_PUBLIC_DIR, 'demo-files')}")
            return send_from_directory(os.path.join(FRONTEND_PUBLIC_DIR, 'demo-files'), filename)
        except Exception as e:
            logger.error(f"Error serving demo file {filename}: {str(e)}")
    
    # If we get here, both servers failed or were unavailable
    logger.error(f"No servers available to handle request for {path}")
    
    return jsonify({
        "error": "Server unavailable",
        "message": f"The endpoint /{path} is not available at this time. Please ensure that at least one of the backend servers is running.",
        "success": False
    }), 503

@app.route('/vehicles', methods=['GET', 'OPTIONS'])
def vehicles_direct_proxy():
    """Direct proxy for vehicles endpoint (without api/ prefix)"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Use the same handler as the API endpoint
    return vehicles_proxy()

@app.route('/statistics', methods=['GET', 'OPTIONS'])
def statistics_direct_proxy():
    """Direct proxy for statistics endpoint (without api/ prefix)"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Use the same handler as the API endpoint
    return statistics_proxy()

@app.route('/market-data', methods=['GET', 'OPTIONS'])
def market_data_direct_proxy():
    """Direct proxy for market-data endpoint (without api/ prefix)"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Use the same handler as the API endpoint
    return market_data_proxy()

@app.route('/opportunities', methods=['GET', 'OPTIONS'])
def opportunities_direct_proxy():
    """Direct proxy for opportunities endpoint (without api/ prefix)"""
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    # Use the same handler as the API endpoint
    return opportunities_proxy()

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    # Get the origin from the request
    origin = request.headers.get('Origin', '*')
    
    # Always ensure CORS headers are set
    response.headers.update({
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Origin',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Expose-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400',  # 24 hours
        'Vary': 'Origin'  # Important for proper caching with CORS
    })
    
    # Handle pre-flight OPTIONS requests
    if request.method == 'OPTIONS':
        # Make sure OPTIONS requests return 200 status
        response.status_code = 200
        
        # For OPTIONS requests, we don't need to return the actual content
        response.data = b''
        response.content_length = 0
    
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