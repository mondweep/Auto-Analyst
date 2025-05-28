#!/usr/bin/env python3

import requests
import json
import time

def test_minimal_chat():
    base_url = "http://localhost:8000"
    
    print("Testing minimal chat creation...")
    
    try:
        # Test minimal chat creation
        headers = {
            "Content-Type": "application/json"
        }
        
        # Minimal data - just what's required
        chat_data = {"user_id": None}
        
        print(f"Sending request: {json.dumps(chat_data)}")
        
        # Try with a shorter timeout first
        response = requests.post(f"{base_url}/chats/", 
                               json=chat_data, 
                               headers=headers, 
                               timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat created successfully: {result}")
        else:
            print(f"❌ Chat creation failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_minimal_chat() 