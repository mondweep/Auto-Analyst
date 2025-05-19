#!/usr/bin/env python3
"""
Test client for the Attribute Query API
"""
import requests
import json
import sys
import argparse

def test_attribute_query(query, api_url='http://localhost:8001'):
    """
    Test the attribute query API
    
    Args:
        query (str): The query to test
        api_url (str): The base URL of the API
        
    Returns:
        dict: The API response
    """
    print(f"Testing query: {query}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{api_url}/api/attribute-query",
            json={"query": query},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response (status {response.status_code}):")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"❌ Error response (status {response.status_code}):")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Exception during API call: {str(e)}")
        return None

def test_direct_count(attribute_name, attribute_value, api_url='http://localhost:8001'):
    """
    Test the direct count API
    
    Args:
        attribute_name (str): The attribute to filter on
        attribute_value (str): The value to match
        api_url (str): The base URL of the API
        
    Returns:
        dict: The API response
    """
    print(f"Testing direct count: {attribute_name}='{attribute_value}'")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{api_url}/api/direct-count",
            json={"attribute_name": attribute_name, "attribute_value": attribute_value},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response (status {response.status_code}):")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"❌ Error response (status {response.status_code}):")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Exception during API call: {str(e)}")
        return None

def test_health(api_url='http://localhost:8001'):
    """Test the health endpoint"""
    print(f"Testing API health at {api_url}/health")
    print("-" * 60)
    
    try:
        response = requests.get(
            f"{api_url}/health",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Health Response (status {response.status_code}):")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Error response (status {response.status_code}):")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception during health check: {str(e)}")
        return False

def run_test_suite(api_url='http://localhost:8001'):
    """Run a suite of tests against the API"""
    if not test_health(api_url):
        print("❌ Health check failed. Is the API running?")
        return False
    
    print("\n=== Testing Attribute Queries ===\n")
    
    test_queries = [
        "How many green vehicles do we have?",
        "Count of Toyota vehicles",
        "How many vehicles are from 2022",
        "Number of vehicles with condition is Excellent",
        "How many vehicles with fuel_type is Electric",
        "What's the total count of all vehicles", # Non-attribute query
    ]
    
    for query in test_queries:
        test_attribute_query(query, api_url)
        print()
    
    print("\n=== Testing Direct Count API ===\n")
    
    test_cases = [
        ("color", "green"),
        ("make", "Toyota"),
        ("year", "2022"),
        ("condition", "Excellent"),
        ("fuel_type", "Electric"),
        ("nonexistent", "value"),  # Should return an error
    ]
    
    for attribute_name, attribute_value in test_cases:
        test_direct_count(attribute_name, attribute_value, api_url)
        print()
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Test the Attribute Query API")
    parser.add_argument("--url", default="http://localhost:8001", help="Base URL of the API")
    parser.add_argument("--query", help="Single query to test")
    parser.add_argument("--attribute", nargs=2, metavar=("ATTRIBUTE", "VALUE"), 
                      help="Test direct count with attribute name and value")
    parser.add_argument("--test-all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Default to test-all if no specific test is specified
    if not (args.query or args.attribute or args.test_all):
        args.test_all = True
    
    if args.test_all:
        run_test_suite(args.url)
    elif args.query:
        test_attribute_query(args.query, args.url)
    elif args.attribute:
        test_direct_count(args.attribute[0], args.attribute[1], args.url)

if __name__ == "__main__":
    main() 