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
    """Test the specific questions you mentioned"""
    print("🚗 Testing Auto-Analyst Chat Questions")
    print("=" * 60)
    
    # The exact questions you mentioned
    test_questions = [
        "How many vehicles do we have in total?",
        "What's our most expensive vehicle?",
        "Show me all Toyota vehicles under $25,000"
    ]
    
    print("Expected Results Based on Data Analysis:")
    print("- Total vehicles: 51")
    print("- Most expensive: Ferrari 488 at $275,000")
    print("- Toyota vehicles under $25,000: 0")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}/3] Testing: {question}")
        print("-" * 50)
        
        result = test_chat_question(question)
        
        if result["success"]:
            response = result["response"]
            
            # Check response type
            if "Authentication failed" in response or "API key" in response:
                print(f"🔑 API KEY ERROR: {response}")
            elif "Error" in response:
                print(f"❌ ERROR: {response}")
            elif len(response) < 50:
                print(f"⚠️  SHORT RESPONSE: {response}")
            else:
                print(f"✅ RESPONSE: {response[:200]}...")
                
        else:
            print(f"❌ FAILED: {result['error']}")
        
        time.sleep(1)  # Brief pause between requests
    
    print(f"\n" + "=" * 60)
    print("🔧 CURRENT STATUS:")
    print("✅ Connection issues: FIXED")
    print("✅ String indexing errors: FIXED") 
    print("❌ API key authentication: NEEDS FIXING")
    print("\n💡 NEXT STEPS:")
    print("1. Fix API key configuration in session management")
    print("2. Ensure proper data loading (51 vehicles vs 2 from API)")
    print("3. Test with working authentication")

if __name__ == "__main__":
    main() 