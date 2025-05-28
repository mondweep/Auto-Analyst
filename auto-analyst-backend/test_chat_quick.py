#!/usr/bin/env python3

import requests
import json
import time

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Agents endpoint
    try:
        response = requests.get(f"{base_url}/agents", timeout=5)
        print(f"✅ Agents endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Agents endpoint failed: {e}")
        return
    
    # Test 3: Create chat (what frontend does first)
    try:
        session_id = f"test-{int(time.time())}"
        headers = {
            "Content-Type": "application/json",
            "X-Session-ID": session_id
        }
        
        chat_data = {"user_id": None, "is_admin": False}
        response = requests.post(f"{base_url}/chats/", 
                               json=chat_data, 
                               headers=headers, 
                               timeout=10)
        
        if response.status_code == 200:
            chat_id = response.json().get("chat_id")
            print(f"✅ Create chat: {response.status_code}, chat_id: {chat_id}")
            
            # Test 4: Send a simple message
            try:
                message_data = {"query": "Hello, how many vehicles?"}
                response = requests.post(f"{base_url}/api/chat/data_viz_agent",
                                       json=message_data,
                                       headers=headers,
                                       timeout=15)
                
                if response.status_code == 200:
                    print(f"✅ Chat message: {response.status_code}")
                    result = response.json()
                    print(f"   Response preview: {str(result)[:100]}...")
                else:
                    print(f"❌ Chat message failed: {response.status_code}")
                    print(f"   Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Chat message failed: {e}")
                
        else:
            print(f"❌ Create chat failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Create chat failed: {e}")

if __name__ == "__main__":
    test_endpoints() 