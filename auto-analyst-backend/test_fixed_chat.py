#!/usr/bin/env python3

import requests
import json
import time

def test_with_curl_simulation():
    """Test chat with curl-like behavior"""
    base_url = "http://localhost:8000"
    
    # Test using curl command equivalent
    print("Testing with curl-like request...")
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": "test-session-fixed"
    }
    
    data = {"query": "How many vehicles do we have in total?"}
    
    try:
        # First test the data_viz_agent directly with a simple approach
        print("Testing data_viz_agent directly...")
        response = requests.post(
            f"{base_url}/chat/data_viz_agent",
            json=data,
            headers=headers,
            timeout=20,
            stream=False  # Don't use streaming
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"SUCCESS! Response:")
                print(json.dumps(result, indent=2))
                return True
            except Exception as parse_error:
                print(f"JSON parse error: {parse_error}")
                print(f"Raw response: {response.text}")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
        return False
        
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def test_attribute_middleware():
    """Test the attribute query middleware"""
    base_url = "http://localhost:8000" 
    
    print("\n--- Testing attribute middleware ---")
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": "test-attribute"
    }
    
    # This should be caught by the middleware
    data = {"query": "How many red vehicles do we have?"}
    
    try:
        response = requests.post(
            f"{base_url}/chat/data_viz_agent",
            json=data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Attribute response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Attribute test failed: {e}")
        
    return False

if __name__ == "__main__":
    success1 = test_with_curl_simulation()
    success2 = test_attribute_middleware()
    
    if success1 or success2:
        print("\n✅ At least one test succeeded!")
    else:
        print("\n❌ All tests failed.") 