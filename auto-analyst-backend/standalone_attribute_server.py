#!/usr/bin/env python3
# standalone_attribute_server.py - Zero-dependency attribute filtering server

import csv
import json
import logging
import os
import re
import sys
from typing import Dict, List, Any, Tuple, Optional
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("attribute-server")

# Configuration
FRONTEND_DEMO_DIR = os.getenv("FRONTEND_DEMO_DIR", 
                             os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                         "Auto-Analyst/auto-analyst-frontend/public/demo-files"))
EXPORTS_DIR = os.getenv("EXPORTS_DIR", "exports")
# Prefer frontend demo files, fallback to exports dir
DEFAULT_VEHICLES_FILE = os.path.join(FRONTEND_DEMO_DIR, "vehicles.csv")
if not os.path.exists(DEFAULT_VEHICLES_FILE):
    DEFAULT_VEHICLES_FILE = os.path.join(EXPORTS_DIR, "vehicles.csv")
    logger.info(f"Frontend demo vehicles file not found, using {DEFAULT_VEHICLES_FILE} instead")
else:
    logger.info(f"Using frontend demo vehicles file: {DEFAULT_VEHICLES_FILE}")

PORT = int(os.getenv("ATTRIBUTE_SERVER_PORT", "8002"))

# Initialize Flask app
app = Flask(__name__)

# Cached vehicles data
vehicles_data = []

# Get model configuration from environment variables
model_provider = os.getenv("MODEL_PROVIDER", "gemini")
model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
temperature = float(os.getenv("TEMPERATURE", "0.7"))
max_tokens = int(os.getenv("MAX_TOKENS", "1000"))

# Map provider to a friendly name
provider_names = {
    "openai": "OpenAI",
    "groq": "Groq",
    "anthropic": "Anthropic",
    "gemini": "Google"
}

provider_display = provider_names.get(model_provider, model_provider.capitalize())

# Model settings from environment variables
model_settings = {
    "default": {
        "id": "default",
        "name": "Default Model",
        "description": f"Default model settings from environment (.env)",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "model": model_name
    }
}

# Models data from environment variables
models = [
    {
        "id": model_name,
        "name": model_name.replace("-", " ").title(),
        "provider": provider_display,
        "description": f"{provider_display}'s {model_name.replace('-', ' ').title()} large language model"
    }
]

# Mock agents data
agents = [
    {
        "id": "data_viz_agent",
        "name": "Data Visualization Agent",
        "description": "Agent for handling attribute queries and data visualization",
        "capabilities": ["attribute_filtering", "data_viz"]
    }
]

# Mock session info
session_info = {
    "user": {
        "id": "demo-user",
        "name": "Demo User",
        "email": "demo@example.com",
        "role": "user"
    },
    "session": {
        "id": "demo-session",
        "created_at": "2025-05-19T12:00:00Z",
        "expires_at": "2025-05-20T12:00:00Z"
    },
    "demo_mode": True
}

def load_csv_data(file_path: str) -> List[Dict[str, Any]]:
    """Load CSV data without using pandas to avoid NumPy compatibility issues"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        return []

def detect_attribute_query(query: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Detect if a query is about counting vehicles with a specific attribute"""
    # Common patterns for attribute queries
    patterns = [
        r"how many (.*?) (vehicles|cars) (do we have|are there)",
        r"(count|show|find|get) (all|the) (.*?) (vehicles|cars)",
        r"number of (.*?) (vehicles|cars)",
        r"(vehicles|cars) that are (.*?)",
        r"(vehicles|cars) with (.*?)$"
    ]
    
    query = query.lower().strip()
    
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            attribute_value = None
            attribute_name = None
            
            # Extract potential attribute information
            if 'color' in query:
                attribute_name = 'color'
                colors = ["black", "white", "red", "blue", "green", "silver", "gray", "yellow", "brown", "orange"]
                for color in colors:
                    if color in query:
                        attribute_value = color
                        break
            
            elif 'make' in query or 'brand' in query:
                attribute_name = 'make'
                brands = ["toyota", "honda", "ford", "chevrolet", "bmw", "audi", "mercedes", "tesla", "volkswagen"]
                for brand in brands:
                    if brand in query:
                        attribute_value = brand
                        break
            
            elif 'year' in query:
                attribute_name = 'year'
                # Extract years like 2020, 2021, 2022, etc.
                year_match = re.search(r'(20\d{2})', query)
                if year_match:
                    attribute_value = year_match.group(1)
            
            elif 'fuel' in query or 'electric' in query or 'gas' in query:
                attribute_name = 'fuel_type'
                if 'electric' in query:
                    attribute_value = 'electric'
                elif 'gas' in query or 'gasoline' in query:
                    attribute_value = 'gasoline'
                elif 'hybrid' in query:
                    attribute_value = 'hybrid'
                elif 'diesel' in query:
                    attribute_value = 'diesel'
            
            return True, attribute_name, attribute_value
    
    return False, None, None

def filter_vehicles_by_attribute(vehicles: List[Dict[str, Any]], 
                                attribute_name: str, 
                                attribute_value: str) -> List[Dict[str, Any]]:
    """Filter vehicles by a specific attribute without using pandas"""
    if not attribute_name or not attribute_value:
        return vehicles
    
    # Handle case-insensitive and partial matching
    attribute_value = attribute_value.lower().strip()
    
    filtered_vehicles = []
    for vehicle in vehicles:
        # Skip if attribute doesn't exist in this vehicle
        if attribute_name not in vehicle:
            continue
            
        # Get the vehicle's attribute value and handle None/empty values
        vehicle_attr_value = vehicle[attribute_name]
        if vehicle_attr_value is None or vehicle_attr_value == "":
            continue
            
        # Compare as strings with case-insensitivity
        vehicle_attr_value = str(vehicle_attr_value).lower().strip()
        
        # Match if the attribute value contains or equals the search value
        if attribute_value in vehicle_attr_value or vehicle_attr_value in attribute_value:
            filtered_vehicles.append(vehicle)
    
    return filtered_vehicles

def format_attribute_count_response(count: int, total: int, attribute_name: str, attribute_value: str) -> Dict[str, Any]:
    """Format the response for attribute counting"""
    percentage = (count / total * 100) if total > 0 else 0
    
    return {
        "count": count,
        "total": total,
        "percentage": round(percentage, 1),
        "attribute_name": attribute_name,
        "attribute_value": attribute_value,
        "message": f"Found {count} vehicles ({percentage:.1f}%) with {attribute_name} '{attribute_value}' out of {total} total vehicles."
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Attribute filtering server is running",
        "loaded_vehicles": len(vehicles_data)
    })

@app.route('/api/attribute-query', methods=['POST'])
def attribute_query():
    """Detect and process attribute-specific queries about vehicles"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' in request body",
                "success": False
            }), 400
            
        query = data['query'].lower()
        
        # Detect if this is an attribute query
        is_attribute_query, attribute_name, attribute_value = detect_attribute_query(query)
        
        if not is_attribute_query:
            return jsonify({
                "is_attribute_query": False,
                "message": "This query doesn't appear to be about counting vehicles by attributes.",
                "success": True
            })
            
        if not attribute_name or not attribute_value:
            return jsonify({
                "is_attribute_query": True,
                "detected": True,
                "attribute_detected": False,
                "message": "This seems to be an attribute query, but couldn't determine the specific attribute or value.",
                "success": True
            })
            
        # Filter vehicles by attribute
        filtered_vehicles = filter_vehicles_by_attribute(vehicles_data, attribute_name, attribute_value)
        count = len(filtered_vehicles)
        total = len(vehicles_data)
        
        # Format the response
        return jsonify({
            "is_attribute_query": True,
            "detected": True,
            "attribute_detected": True,
            "success": True,
            **format_attribute_count_response(count, total, attribute_name, attribute_value)
        })
        
    except Exception as e:
        logger.error(f"Error in attribute_query: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/direct-count', methods=['POST'])
def direct_count():
    """Directly count vehicles by attribute name and value"""
    try:
        data = request.json
        if not data or 'attribute_name' not in data or 'attribute_value' not in data:
            return jsonify({
                "error": "Missing 'attribute_name' or 'attribute_value' in request body",
                "success": False
            }), 400
            
        attribute_name = data['attribute_name']
        attribute_value = data['attribute_value']
        
        # Filter vehicles by attribute
        filtered_vehicles = filter_vehicles_by_attribute(vehicles_data, attribute_name, attribute_value)
        count = len(filtered_vehicles)
        total = len(vehicles_data)
        
        # Format the response
        return jsonify({
            "success": True,
            **format_attribute_count_response(count, total, attribute_name, attribute_value)
        })
        
    except Exception as e:
        logger.error(f"Error in direct_count: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/chat-attribute', methods=['POST'])
def chat_attribute():
    """Endpoint for chat messages that might be attribute queries"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' in request body",
                "success": False
            }), 400
            
        query = data['query'].lower()
        
        # Detect if this is an attribute query
        is_attribute_query, attribute_name, attribute_value = detect_attribute_query(query)
        
        if not is_attribute_query or not attribute_name or not attribute_value:
            # Not a valid attribute query, pass through to main app
            return jsonify({
                "is_attribute_query": False,
                "message": "Not a valid attribute query",
                "success": True,
                "pass_through": True
            })
            
        # Filter vehicles by attribute
        filtered_vehicles = filter_vehicles_by_attribute(vehicles_data, attribute_name, attribute_value)
        count = len(filtered_vehicles)
        total = len(vehicles_data)
        
        # Format the response for chat interface
        result = format_attribute_count_response(count, total, attribute_name, attribute_value)
        formatted_message = f"**Vehicle Count Analysis**\n\n{result['message']}\n\n"
        
        # For more complex queries, add extra context
        if attribute_name == "color" and count > 0:
            formatted_message += f"**Note:** Out of all vehicles, {result['percentage']}% are {attribute_value}.\n"
        elif attribute_name == "make" and count > 0:
            formatted_message += f"**Note:** {attribute_value.title()} represents {result['percentage']}% of our inventory.\n"
        
        # Return a response that mimics the chat endpoint format
        return jsonify({
            "agent_name": "data_viz_agent",  # Use the visualization agent name
            "query": query,
            "response": formatted_message,
            "is_attribute_query": True,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error in chat_attribute: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/model-settings', methods=['GET'])
def get_model_settings():
    """Return mock model settings to prevent frontend errors"""
    return jsonify({
        "success": True,
        "settings": model_settings
    })

@app.route('/api/model-settings', methods=['GET'])
def get_api_model_settings():
    """Alternative endpoint for model settings"""
    return jsonify({
        "success": True,
        "settings": model_settings
    })

@app.route('/model-settings/<model_id>', methods=['GET'])
def get_model_setting(model_id):
    """Return specific model setting by ID"""
    if model_id in model_settings:
        return jsonify({
            "success": True,
            "setting": model_settings[model_id]
        })
    return jsonify({
        "success": False,
        "error": f"Model setting '{model_id}' not found"
    }), 404

@app.route('/model', methods=['GET'])
def get_models():
    """Return mock model data to prevent frontend errors"""
    return jsonify({
        "success": True,
        "models": models
    })

@app.route('/settings/model', methods=['GET'])
def get_settings_model():
    """Alternative endpoint for model settings"""
    return jsonify({
        "success": True,
        "settings": model_settings,
        "models": models
    })

@app.route('/model/<model_id>', methods=['GET'])
def get_model(model_id):
    """Return specific model by ID"""
    for model in models:
        if model["id"] == model_id:
            return jsonify({
                "success": True,
                "model": model
            })
    return jsonify({
        "success": False,
        "error": f"Model '{model_id}' not found"
    }), 404

@app.route('/agents', methods=['GET'])
def get_agents():
    """Return mock agents data"""
    return jsonify({
        "success": True,
        "agents": agents
    })

@app.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Return specific agent by ID"""
    for agent in agents:
        if agent["id"] == agent_id:
            return jsonify({
                "success": True,
                "agent": agent
            })
    return jsonify({
        "success": False,
        "error": f"Agent '{agent_id}' not found"
    }), 404

@app.route('/api/session-info', methods=['GET'])
def get_session_info():
    """Return mock session info"""
    return jsonify({
        "success": True,
        **session_info
    })

if __name__ == '__main__':
    # Load the vehicles data at startup
    logger.info(f"Loading dataset from: {DEFAULT_VEHICLES_FILE}")
    vehicles_data = load_csv_data(DEFAULT_VEHICLES_FILE)
    if vehicles_data:
        logger.info(f"✅ Loaded dataset with {len(vehicles_data)} vehicles")
    else:
        logger.error(f"❌ Failed to load vehicles dataset from {DEFAULT_VEHICLES_FILE}")
    
    # Start the Flask server
    logger.info(f"Starting Attribute Server on port {PORT}...")
    logger.info("Available endpoints:")
    logger.info("  - /health - Health check")
    logger.info("  - /api/attribute-query - Detect and process attribute queries")
    logger.info("  - /api/direct-count - Direct counting by attribute name and value")
    logger.info("  - /api/chat-attribute - Chat integration for attribute queries")
    logger.info("  - /model - Get available models")
    logger.info("  - /model/<model_id> - Get specific model")
    logger.info("  - /model-settings - Get model settings")
    logger.info("  - /api/model-settings - Alternative model settings endpoint")
    logger.info("  - /settings/model - Alternative model settings endpoint")
    logger.info("  - /model-settings/<model_id> - Get specific model setting")
    logger.info("  - /agents - Get available agents")
    logger.info("  - /agents/<agent_id> - Get specific agent")
    logger.info("  - /api/session-info - Get session info")
    app.run(host='0.0.0.0', port=PORT, debug=True) 