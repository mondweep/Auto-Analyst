#!/usr/bin/env python3
"""
Test script for attribute-specific filtering capabilities in Auto-Analyst
"""
import os
import pandas as pd
import sys
from pathlib import Path

# Import our direct count utility if available
try:
    # Try to import from src/utils first
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from src.utils.direct_count_query import direct_count_attributes, detect_attribute_query
    IMPORTED_FROM = "src.utils.direct_count_query"
except ImportError:
    try:
        # Try importing from root directory
        from direct_count_query import direct_count_attributes, detect_attribute_query
        IMPORTED_FROM = "direct_count_query"
    except ImportError:
        print("❌ Could not import direct_count_query module")
        sys.exit(1)

print(f"✅ Successfully imported direct_count_query from {IMPORTED_FROM}")

def find_dataset():
    """Find the vehicles dataset"""
    possible_paths = [
        "exports/vehicles.csv",
        "data/vehicles.csv",
        "../exports/vehicles.csv",
        "../data/vehicles.csv",
        "Auto-Analyst/auto-analyst-backend/exports/vehicles.csv",
        "Auto-Analyst/auto-analyst-backend/data/vehicles.csv"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found dataset at {path}")
            return path
    
    print("❌ Could not find vehicles dataset")
    return None

def test_direct_attribute_counts():
    """Test direct attribute counting with various attributes"""
    dataset_path = find_dataset()
    if not dataset_path:
        return False
    
    print("\n=== Testing Direct Attribute Counting ===")
    
    # Test with color=green
    print("\n1. Testing color=green:")
    result = direct_count_attributes("color", "green", dataset_path)
    print(result)
    
    # Test with make=Toyota
    print("\n2. Testing make=Toyota:")
    result = direct_count_attributes("make", "Toyota", dataset_path)
    print(result)
    
    # Test with year=2022
    print("\n3. Testing year=2022:")
    result = direct_count_attributes("year", "2022", dataset_path)
    print(result)
    
    # Test with a non-existent attribute
    print("\n4. Testing a non-existent attribute:")
    result = direct_count_attributes("nonexistent", "value", dataset_path)
    print(result)
    
    return True

def test_query_detection():
    """Test the attribute query detection capability"""
    print("\n=== Testing Query Detection ===")
    
    test_queries = [
        "How many green vehicles do we have?",
        "Count of blue cars",
        "How many vehicles with color is red",
        "Number of vehicles that are Toyota",
        "Vehicles that are black",
        "How many vehicles are from 2022",
        "What's the average price of our inventory",  # Non-attribute query
        "Show me the distribution of vehicle prices by make"  # Non-attribute query
    ]
    
    for query in test_queries:
        is_attribute_query, attribute_name, attribute_value = detect_attribute_query(query)
        if is_attribute_query:
            print(f"✅ Detected attribute query: {query}")
            print(f"   Attribute: {attribute_name}, Value: {attribute_value}")
        else:
            print(f"❌ Not detected as attribute query: {query}")
    
    return True

def main():
    """Main test function"""
    print("=" * 80)
    print("Auto-Analyst Attribute Filtering Test".center(80))
    print("=" * 80)
    
    success = test_direct_attribute_counts()
    if success:
        test_query_detection()
    
    print("\nTests completed.")

if __name__ == "__main__":
    main() 