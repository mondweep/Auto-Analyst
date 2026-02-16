#!/usr/bin/env python3

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app
from dotenv import load_dotenv

load_dotenv()

def debug_session_state():
    """Debug the session state creation process"""
    
    # Test creating a session state directly
    print("--- Direct session state test ---")
    session_id = "debug-session-direct"
    session_state = app.state.get_session_state(session_id)
    
    print(f"Session ID: {session_id}")
    print(f"Model config: {session_state['model_config']}")
    print(f"Has current_df: {session_state['current_df'] is not None}")
    print(f"Has retrievers: {session_state['retrievers'] is not None}")
    
    # Test the session LM
    from app import get_session_lm
    session_lm = get_session_lm(session_state)
    print(f"Session LM type: {type(session_lm)}")
    print(f"Session LM model: {getattr(session_lm, 'model', 'UNKNOWN')}")
    
    # Test calling the model settings API to see what it returns
    print("\n--- Model settings API test ---")
    base_url = "http://localhost:8000"
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": "debug-session-api"
    }
    
    try:
        response = requests.get(f"{base_url}/api/model-settings", headers=headers, timeout=10)
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            settings = response.json()
            print(f"API Settings: {json.dumps(settings, indent=2)}")
        else:
            print(f"API Error: {response.text}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    debug_session_state() 