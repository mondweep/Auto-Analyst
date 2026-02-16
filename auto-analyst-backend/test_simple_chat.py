#!/usr/bin/env python3

import requests
import json

def test_simple_question():
    """Test a very simple question"""
    base_url = "http://localhost:8000"
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": "test-session-simple"
    }
    
    # Test the health endpoint first
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test agents list
    print("\nTesting agents endpoint...")
    try:
        response = requests.get(f"{base_url}/agents", timeout=5)
        print(f"Agents: {response.status_code} - {response.text[:200]}...")
    except Exception as e:
        print(f"Agents check failed: {e}")
        return
    
    # Test a very simple question with data_viz_agent
    print("\nTesting simple question with data_viz_agent...")
    data = {"query": "hello"}
    
    try:
        response = requests.post(f"{base_url}/chat/data_viz_agent", 
                               json=data, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content length: {len(response.content)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response JSON: {json.dumps(result, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Chat test failed: {e}")

if __name__ == "__main__":
    test_simple_question() 