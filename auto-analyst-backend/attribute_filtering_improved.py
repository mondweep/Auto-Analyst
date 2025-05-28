#!/usr/bin/env python3
"""
Improved attribute filtering functionality designed to pass TDD tests
"""
import os
import csv
import re
from typing import Tuple, List, Dict, Optional, Union

def detect_attribute_query(query: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detect if a query is asking about a specific attribute
    
    Args:
        query (str): The user query
        
    Returns:
        tuple: (is_attribute_query, attribute_name, attribute_value)
    """
    if not query or not isinstance(query, str):
        return False, None, None
    
    query_lower = query.lower().strip()
    
    # Color detection patterns
    colors = ["green", "red", "blue", "black", "white", "silver", "gray", "grey", 
              "yellow", "orange", "purple", "pink", "brown", "beige", "gold"]
    
    color_patterns = [
        r"how many (\w+) (?:vehicles|cars)",
        r"count (?:of|the) (\w+) (?:vehicles|cars)",
        r"(?:vehicles|cars) that are (\w+)",
        r"(\w+) (?:vehicles|cars)"
    ]
    
    # Check colors first
    for pattern in color_patterns:
        match = re.search(pattern, query_lower)
        if match:
            potential_color = match.group(1)
            if potential_color in colors:
                return True, "color", potential_color
    
    # Make detection patterns
    makes = ["toyota", "honda", "ford", "bmw", "mercedes", "audi", "tesla", 
             "hyundai", "kia", "nissan", "chevrolet", "lexus", "acura", "infiniti"]
    
    make_patterns = [
        r"how many (\w+) (?:vehicles|cars)",
        r"count (?:of|the) (\w+)(?: vehicles| cars|$)",
        r"(\w+) (?:vehicles|cars)",
        r"(\w+)$"  # Just the make name
    ]
    
    for pattern in make_patterns:
        match = re.search(pattern, query_lower)
        if match:
            potential_make = match.group(1)
            if potential_make in makes:
                return True, "make", potential_make
    
    # Year detection
    year_patterns = [
        r"(?:from|in|made in|year) (\d{4})",
        r"vehicles (?:from|in) (\d{4})",
        r"(\d{4}) (?:vehicles|cars)"
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, query_lower)
        if match:
            year = match.group(1)
            return True, "year", year
    
    # Condition detection
    conditions = ["excellent", "good", "fair", "poor"]
    condition_patterns = [
        r"(\w+) condition",
        r"condition (?:is )?(\w+)"
    ]
    
    for pattern in condition_patterns:
        match = re.search(pattern, query_lower)
        if match:
            potential_condition = match.group(1)
            if potential_condition in conditions:
                return True, "condition", potential_condition
    
    # General attribute pattern: "vehicles with attribute is value"
    general_match = re.search(r"with (\w+) (?:is|=) (\w+)", query_lower)
    if general_match:
        return True, general_match.group(1), general_match.group(2)
    
    return False, None, None

def filter_csv_by_attribute(dataset_path: str, attribute_name: str, 
                          attribute_value: str) -> Tuple[Optional[List[Dict]], Optional[List[str]]]:
    """
    Filter CSV file by attribute value
    
    Args:
        dataset_path (str): Path to the CSV file
        attribute_name (str): Name of the column to filter on
        attribute_value (str): Value to match
        
    Returns:
        tuple: (filtered_rows, header) or (None, None) if error
    """
    try:
        if not os.path.exists(dataset_path):
            return None, None
            
        with open(dataset_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            header = reader.fieldnames
            
            if not header or attribute_name not in header:
                print(f"❌ Attribute '{attribute_name}' not found in dataset")
                if header:
                    print(f"Available attributes: {', '.join(header)}")
                return None, None
            
            matched_rows = []
            for row in reader:
                if attribute_name in row and row[attribute_name]:
                    if row[attribute_name].lower() == attribute_value.lower():
                        matched_rows.append(row)
                        
            return matched_rows, header
            
    except Exception as e:
        print(f"❌ Error reading dataset: {str(e)}")
        return None, None

def count_attribute_values(dataset_path: str, attribute_name: str, 
                         attribute_value: str) -> Optional[Dict]:
    """
    Count vehicles with specific attribute value
    
    Args:
        dataset_path (str): Path to the CSV file
        attribute_name (str): Name of the column to count
        attribute_value (str): Value to match
        
    Returns:
        dict: Count information or None if error
    """
    try:
        matched_rows, header = filter_csv_by_attribute(dataset_path, attribute_name, attribute_value)
        
        if matched_rows is None:
            return None
            
        count = len(matched_rows)
        
        # Count total rows
        with open(dataset_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            total_rows = sum(1 for row in reader) - 1  # Subtract header
            
        percentage = (count / total_rows * 100) if total_rows > 0 else 0
        
        result = {
            'count': count,
            'total': total_rows,
            'percentage': percentage,
            'attribute': attribute_name,
            'value': attribute_value,
            'matched_rows': matched_rows
        }
        
        print(f"\n=== Results for {attribute_name}='{attribute_value}' ===")
        print(f"Count: {count} vehicles ({percentage:.1f}% of total)")
        
        return result
        
    except Exception as e:
        print(f"❌ Error counting attribute values: {str(e)}")
        return None

def find_dataset() -> Optional[str]:
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