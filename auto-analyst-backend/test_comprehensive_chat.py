#!/usr/bin/env python3

import requests
import json
import time

def test_chat_question(question, agent="data_viz_agent"):
    """Test a specific chat question"""
    base_url = "http://localhost:8000"
    
    headers = {
        "Content-Type": "application/json", 
        "X-Session-ID": f"test-session-{int(time.time())}"
    }
    
    data = {"query": question}
    
    try:
        response = requests.post(f"{base_url}/chat/{agent}", 
                               json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "agent": result.get("agent_name", agent),
                "query": result.get("query", question),
                "response": result.get("response", "No response"),
                "error": None
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Test comprehensive chat functionality"""
    print("🚗 Testing Auto-Analyst Chat Functionality")
    print("=" * 60)
    
    # Test questions based on known data (51 vehicles, most expensive Ferrari at $275,000)
    test_questions = [
        # Basic vehicle counts
        ("How many vehicles do we have in total?", "Should be 51"),
        ("What's our most expensive vehicle?", "Should be Ferrari 488 at $275,000"),
        ("Show me all Toyota vehicles under $25,000", "Should be 0 vehicles"),
        
        # Vehicle analysis
        ("What's the average vehicle price?", "Should calculate average"),
        ("Which vehicle makes do we have the most of?", "Should analyze distribution"),
        ("What's the price range of vehicles?", "Should show min/max"),
        
        # Data visualization requests
        ("Create a bar chart showing vehicles by make", "Should generate viz code"),
        ("Show me a histogram of vehicle prices", "Should create histogram"),
        ("Generate a pie chart of vehicle colors", "Should create pie chart"),
        
        # Statistical analysis
        ("Calculate basic statistics for vehicle prices", "Should show stats"),
        ("What's the correlation between price and mileage?", "Should analyze correlation"),
        
        # Simple questions that should work
        ("Hello", "Should respond"),
        ("Describe the dataset", "Should describe vehicles"),
    ]
    
    success_count = 0
    total_tests = len(test_questions)
    
    for i, (question, expected) in enumerate(test_questions, 1):
        print(f"\n[{i:2d}/{total_tests}] {question}")
        print(f"Expected: {expected}")
        print("-" * 50)
        
        result = test_chat_question(question)
        
        if result["success"]:
            success_count += 1
            response = result["response"]
            
            # Check if it's an error response
            if "string indices must be integers" in response:
                print(f"❌ AGENT ERROR: {response}")
            elif "No dataset" in response or "No data" in response:
                print(f"⚠️  NO DATA: {response}")
            elif len(response) < 50:
                print(f"⚠️  SHORT RESPONSE: {response}")
            else:
                print(f"✅ SUCCESS: {response[:100]}...")
                
        else:
            print(f"❌ FAILED: {result['error']}")
        
        time.sleep(0.5)  # Brief pause between requests
    
    print(f"\n" + "=" * 60)
    print(f"📊 RESULTS: {success_count}/{total_tests} tests succeeded")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
    elif success_count >= total_tests * 0.7:
        print("✅ Most tests passed - good progress!")
    elif success_count >= total_tests * 0.3:
        print("⚠️  Some tests passed - needs improvement")
    else:
        print("❌ Many tests failed - significant issues remain")

if __name__ == "__main__":
    main() 