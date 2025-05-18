import requests
import json
import sys
import time

def test_attribute_query():
    """
    Test the system's ability to handle attribute-specific filtering questions
    """
    print("\n===== Testing Attribute-Specific Query =====")
    
    # Test query for color-based filtering
    query = "how many green vehicles do we have?"
    
    # Send the query to the API
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"query": query},
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ API returned error status: {response.status_code}")
            print(response.text)
            return False
        
        # Process the streaming response
        data = response.text
        
        # Log the response for debugging
        print("\nAPI Response:")
        print(data[:1000] + "..." if len(data) > 1000 else data)
        
        # Check for signs of improved attribute filtering in the response
        expected_terms = ["color", "green", "count", "filter"]
        found_terms = [term for term in expected_terms if term.lower() in data.lower()]
        
        if len(found_terms) >= 2:
            print(f"✅ Response contains relevant attribute filtering terms: {found_terms}")
        else:
            print(f"❌ Response doesn't seem to focus on attribute filtering. Found terms: {found_terms}")
            
        # Check if the response provides a specific count or answer
        if any(s in data.lower() for s in ["count", "total", "number of"]):
            print("✅ Response appears to provide a specific count or answer")
        else:
            print("❌ Response doesn't seem to provide a specific count")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during API call: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Starting attribute filtering tests...")
    
    success = test_attribute_query()
    
    print("\n===== Test Summary =====")
    if success:
        print("✅ Tests completed. Check the results above for details.")
    else:
        print("❌ Tests failed or encountered errors.")
    
if __name__ == "__main__":
    main() 