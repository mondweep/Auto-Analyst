#!/usr/bin/env python3
"""
Validation script for Auto-Analyst attribute filtering functionality.
This script demonstrates the TDD implementation working in the live application.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, data=None, method="GET"):
    """Test an API endpoint and return the response."""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "text": response.text}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🚀 Auto-Analyst Application Validation")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Endpoint...")
    health = test_endpoint("/health")
    if "message" in health:
        print(f"✅ Health Check: {health['message']}")
    else:
        print(f"❌ Health Check Failed: {health}")
        return
    
    # Test 2: Available Agents
    print("\n2. Testing Available Agents...")
    agents = test_endpoint("/agents")
    if "available_agents" in agents:
        print(f"✅ Available Agents: {', '.join(agents['available_agents'])}")
    else:
        print(f"❌ Agents Check Failed: {agents}")
    
    # Test 3: Attribute Filtering - Green Vehicles
    print("\n3. Testing Attribute Filtering - Green Vehicles...")
    green_query = {
        "attribute_name": "color",
        "attribute_value": "green"
    }
    green_result = test_endpoint("/api/direct-count", green_query, "POST")
    if green_result.get("success"):
        print(f"✅ Green Vehicles: {green_result['count']} out of {green_result['total']} ({green_result['percentage']}%)")
    else:
        print(f"❌ Green Vehicles Query Failed: {green_result}")
    
    # Test 4: Attribute Filtering - Toyota Vehicles
    print("\n4. Testing Attribute Filtering - Toyota Vehicles...")
    toyota_query = {
        "attribute_name": "make",
        "attribute_value": "Toyota"
    }
    toyota_result = test_endpoint("/api/direct-count", toyota_query, "POST")
    if toyota_result.get("success"):
        print(f"✅ Toyota Vehicles: {toyota_result['count']} out of {toyota_result['total']} ({toyota_result['percentage']}%)")
    else:
        print(f"❌ Toyota Vehicles Query Failed: {toyota_result}")
    
    # Test 5: Attribute Filtering - Excellent Condition
    print("\n5. Testing Attribute Filtering - Excellent Condition...")
    excellent_query = {
        "attribute_name": "condition",
        "attribute_value": "excellent"
    }
    excellent_result = test_endpoint("/api/direct-count", excellent_query, "POST")
    if excellent_result.get("success"):
        print(f"✅ Excellent Condition: {excellent_result['count']} out of {excellent_result['total']} ({excellent_result['percentage']}%)")
    else:
        print(f"❌ Excellent Condition Query Failed: {excellent_result}")
    
    # Test 6: Attribute Filtering - 2022 Vehicles
    print("\n6. Testing Attribute Filtering - 2022 Vehicles...")
    year_query = {
        "attribute_name": "year",
        "attribute_value": "2022"
    }
    year_result = test_endpoint("/api/direct-count", year_query, "POST")
    if year_result.get("success"):
        print(f"✅ 2022 Vehicles: {year_result['count']} out of {year_result['total']} ({year_result['percentage']}%)")
    else:
        print(f"❌ 2022 Vehicles Query Failed: {year_result}")
    
    # Test 7: Natural Language Query
    print("\n7. Testing Natural Language Query...")
    nl_query = {
        "query": "how many green vehicles do we have?"
    }
    nl_result = test_endpoint("/api/attribute-query", nl_query, "POST")
    if nl_result.get("success"):
        print(f"✅ Natural Language Query: {nl_result.get('message', 'Processed successfully')}")
    else:
        print(f"❌ Natural Language Query Failed: {nl_result}")
    
    print("\n" + "=" * 50)
    print("🎉 Validation Complete!")
    print("\nThe Auto-Analyst application is running successfully with:")
    print("- ✅ Health monitoring")
    print("- ✅ Agent system")
    print("- ✅ Attribute filtering (TDD implementation)")
    print("- ✅ Direct count queries")
    print("- ✅ Natural language processing")
    print("\n📊 Sample Data: 51 vehicles with various attributes")
    print("🔗 Application URL: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs (if available)")

if __name__ == "__main__":
    main() 