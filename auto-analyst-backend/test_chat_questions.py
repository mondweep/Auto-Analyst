#!/usr/bin/env python3

import requests
import json
import time

def test_chat_question(question, endpoint="chat"):
    """Test a specific chat question"""
    base_url = "http://localhost:8000"
    
    headers = {
        "Content-Type": "application/json",
        "X-Session-ID": "test-session-123"
    }
    
    data = {"query": question}
    
    print(f"\n{'='*60}")
    print(f"TESTING: {question}")
    print(f"{'='*60}")
    
    try:
        if endpoint == "chat":
            response = requests.post(f"{base_url}/chat", 
                                   json=data, headers=headers, timeout=30)
        else:
            response = requests.post(f"{base_url}/chat/{endpoint}", 
                                   json=data, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if 'text/event-stream' in response.headers.get('content-type', ''):
                # Handle streaming response
                print("STREAMING RESPONSE:")
                for line in response.text.split('\n'):
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            agent = chunk.get('agent', 'Unknown')
                            content = chunk.get('content', '')
                            status = chunk.get('status', 'unknown')
                            print(f"[{agent}] ({status}): {content[:200]}...")
                        except:
                            print(f"Raw line: {line}")
            else:
                # Handle regular JSON response
                try:
                    result = response.json()
                    print("JSON RESPONSE:")
                    print(json.dumps(result, indent=2))
                except:
                    print("TEXT RESPONSE:")
                    print(response.text[:500] + "...")
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

def main():
    print("Testing specific chat questions that are failing...")
    
    # Test the problematic questions
    questions = [
        "How many vehicles do we have in total?",
        "What's our most expensive vehicle?", 
        "Show me all Toyota vehicles under $25,000"
    ]
    
    # Test with general chat endpoint
    for question in questions:
        test_chat_question(question, "chat")
        time.sleep(1)
    
    # Test with specific agent
    print(f"\n{'='*60}")
    print("TESTING WITH DATA VIZ AGENT SPECIFICALLY")
    print(f"{'='*60}")
    
    for question in questions:
        test_chat_question(question, "data_viz_agent")
        time.sleep(1)

if __name__ == "__main__":
    main() 