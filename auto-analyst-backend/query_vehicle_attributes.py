#!/usr/bin/env python3
"""
Simple CSV-based vehicle attribute query tool.
Doesn't require pandas or NumPy, avoiding compatibility issues.
"""
import os
import sys
import csv
import re
from pathlib import Path
import argparse

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

def detect_attribute_query(query):
    """
    Detect if a query is asking about a specific attribute
    
    Args:
        query (str): The user query
        
    Returns:
        tuple: (is_attribute_query, attribute_name, attribute_value)
    """
    # Common patterns for attribute queries
    patterns = [
        # Colors
        r"how many (\w+) (vehicles|cars)",  # "how many green vehicles"
        r"count (?:of|the) (\w+) (vehicles|cars)",  # "count of green vehicles"
        
        # Makes
        r"how many (toyota|honda|ford|bmw|mercedes|audi|tesla|hyundai|kia|nissan|chevrolet) (vehicles|cars)",
        r"count of (toyota|honda|ford|bmw|mercedes|audi|tesla|hyundai|kia|nissan|chevrolet)",
        
        # Years
        r"how many vehicles (?:from|in|made in) (\d{4})",  # "how many vehicles from 2022"
        r"vehicles from (\d{4})",  # "vehicles from 2022"
        
        # Conditions
        r"how many (excellent|good|fair|poor) condition",
        
        # General attribute queries
        r"how many (vehicles|cars) with (\w+) (?:is|=) (\w+)",  # "how many vehicles with color is green"
        r"number of (vehicles|cars) that are (\w+)",  # "number of vehicles that are green"
        r"(vehicles|cars) that are (\w+)",  # "vehicles that are green"
    ]
    
    query = query.lower()
    
    # Check for color queries
    colors = ["green", "red", "blue", "black", "white", "silver", "gray", "yellow", "orange", "purple", "pink", "brown"]
    for color in colors:
        if f"how many {color} vehicles" in query or f"count of {color}" in query:
            return True, "color", color
    
    # Check for make queries
    makes = ["toyota", "honda", "ford", "bmw", "mercedes", "audi", "tesla", "hyundai", "kia", "nissan", "chevrolet"]
    for make in makes:
        if f"how many {make}" in query or f"count of {make}" in query:
            return True, "make", make
            
    # Check for year queries
    year_match = re.search(r"from (\d{4})|in (\d{4})|made in (\d{4})", query)
    if year_match:
        year = next(g for g in year_match.groups() if g)
        return True, "year", year
        
    # Check for condition queries
    conditions = ["excellent", "good", "fair", "poor"]
    for condition in conditions:
        if f"{condition} condition" in query:
            return True, "condition", condition
            
    # Check for general attribute queries
    attr_match = re.search(r"with (\w+) (?:is|=) (\w+)", query)
    if attr_match:
        return True, attr_match.group(1), attr_match.group(2)
    
    return False, None, None

def filter_csv_by_attribute(dataset_path, attribute_name, attribute_value):
    """
    Filter CSV file by attribute value
    
    Args:
        dataset_path (str): Path to the CSV file
        attribute_name (str): Name of the column to filter on
        attribute_value (str): Value to match
        
    Returns:
        list: Filtered rows
    """
    try:
        # Read CSV file
        with open(dataset_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Check if attribute exists
            header = reader.fieldnames
            if attribute_name not in header:
                print(f"❌ Attribute '{attribute_name}' not found in dataset")
                print(f"Available attributes: {', '.join(header)}")
                return None
            
            # Filter rows by attribute
            matched_rows = []
            for row in reader:
                if row[attribute_name].lower() == attribute_value.lower():
                    matched_rows.append(row)
                    
            return matched_rows, header
    except Exception as e:
        print(f"❌ Error reading dataset: {str(e)}")
        return None, None
        
def count_attribute_values(dataset_path, attribute_name, attribute_value):
    """
    Count vehicles with specific attribute value
    
    Args:
        dataset_path (str): Path to the CSV file
        attribute_name (str): Name of the column to count
        attribute_value (str): Value to match
        
    Returns:
        dict: Count information
    """
    try:
        # Filter rows
        matched_rows, header = filter_csv_by_attribute(dataset_path, attribute_name, attribute_value)
        
        if matched_rows is None:
            return
            
        # Count matching rows
        count = len(matched_rows)
        
        # Count total rows
        with open(dataset_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            total_rows = sum(1 for row in reader) - 1  # Subtract header
            
        # Calculate percentage
        percentage = (count / total_rows) * 100
        
        print(f"\n=== Results for {attribute_name}='{attribute_value}' ===")
        print(f"Count: {count} vehicles ({percentage:.1f}% of total)")
        
        # Distribution of values
        distribution = {}
        with open(dataset_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                value = row[attribute_name]
                if value in distribution:
                    distribution[value] += 1
                else:
                    distribution[value] = 1
        
        # Sort by count (descending)
        sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nDistribution of {attribute_name} values:")
        print("-" * 40)
        for value, count in sorted_dist[:10]:  # Top 10
            percentage = (count / total_rows) * 100
            print(f"{value}: {count} ({percentage:.1f}%)")
            
        # Sample of matching vehicles
        if count > 0:
            print("\nSample of matching vehicles:")
            print("-" * 40)
            for i, row in enumerate(matched_rows[:5]):  # Show up to 5
                print(f"{i+1}. {row.get('make', '')} {row.get('model', '')} ({row.get('year', '')}), " +
                      f"Color: {row.get('color', '')}, Price: ${row.get('price', '')}")
        
    except Exception as e:
        print(f"❌ Error counting attribute values: {str(e)}")

def interactive_mode():
    """Run in interactive mode"""
    dataset_path = find_dataset()
    if not dataset_path:
        print("Exiting due to missing dataset.")
        return
        
    print("\n==== Vehicle Attribute Query Tool ====")
    print("This tool helps you query the vehicle dataset without requiring pandas or NumPy")
    
    while True:
        print("\nOptions:")
        print("1. Ask a question (e.g., 'How many green vehicles do we have?')")
        print("2. Direct attribute query")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == '1':
            query = input("\nEnter your question: ")
            is_attribute_query, attribute_name, attribute_value = detect_attribute_query(query)
            
            if is_attribute_query:
                print(f"✅ Detected query for {attribute_name}='{attribute_value}'")
                count_attribute_values(dataset_path, attribute_name, attribute_value)
            else:
                print("❌ Could not detect attribute in your question")
                print("Try phrases like 'How many green vehicles?' or 'Count of Toyota vehicles'")
                
        elif choice == '2':
            attribute_name = input("\nEnter attribute name (e.g., color, make, year): ")
            attribute_value = input(f"Enter {attribute_name} value: ")
            count_attribute_values(dataset_path, attribute_name, attribute_value)
            
        elif choice == '3':
            print("\nExiting. Thanks for using the Vehicle Attribute Query Tool!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")

def main():
    parser = argparse.ArgumentParser(description="Query vehicle attributes without pandas/NumPy dependencies")
    parser.add_argument("--query", help="Natural language query (e.g., 'How many green vehicles?')")
    parser.add_argument("--attribute", help="Specific attribute to query (e.g., 'color')")
    parser.add_argument("--value", help="Value to match (e.g., 'green')")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Find dataset path
    dataset_path = find_dataset()
    if not dataset_path:
        print("Exiting due to missing dataset.")
        return
    
    # Interactive mode
    if args.interactive or (not args.query and not args.attribute):
        interactive_mode()
        return
    
    # Process query
    if args.query:
        is_attribute_query, attribute_name, attribute_value = detect_attribute_query(args.query)
        
        if is_attribute_query:
            print(f"✅ Detected query for {attribute_name}='{attribute_value}'")
            count_attribute_values(dataset_path, attribute_name, attribute_value)
        else:
            print("❌ Could not detect attribute in your query")
            print("Try phrases like 'How many green vehicles?' or 'Count of Toyota vehicles'")
    
    # Direct attribute query
    elif args.attribute and args.value:
        count_attribute_values(dataset_path, args.attribute, args.value)
    
    # Missing parameters
    elif args.attribute and not args.value:
        print("❌ Missing value parameter. Use --value to specify the attribute value")
    
if __name__ == "__main__":
    main() 