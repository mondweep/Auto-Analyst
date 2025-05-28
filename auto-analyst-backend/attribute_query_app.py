#!/usr/bin/env python3
"""
Simplified Attribute Query Application for Auto-Analyst
"""
import os
import sys
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the dataset once at startup
def load_dataset():
    """Load the vehicles dataset"""
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
            print(f"Loading dataset from: {path}")
            try:
                df = pd.read_csv(path)
                print(f"✅ Loaded dataset with {len(df)} vehicles")
                return df
            except Exception as e:
                print(f"Error loading dataset: {str(e)}")
    
    print("❌ Could not find vehicles dataset")
    return None

# Global dataset variable
df = load_dataset()

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
        r"how many (\w+) (vehicles|cars) (?:do we have|are there)",  # "how many green vehicles do we have"
        r"count (?:of|the) (\w+) (vehicles|cars)",  # "count of green vehicles"
        r"how many (vehicles|cars) (?:are|with) (\w+) (is|are|=|equal to) (\w+)",  # "how many vehicles with color is green"
        r"number of (vehicles|cars) (?:that are|with) (\w+)",  # "number of vehicles that are green" 
        r"(vehicles|cars) that (?:are|have) (\w+)",  # "vehicles that are green"
        r"how many (vehicles|cars) (?:from|in|made in) (\d{4})",  # "how many vehicles from 2022"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            groups = match.groups()
            if len(groups) == 2:
                if groups[1] in ['vehicles', 'cars']:
                    # Pattern: "how many green vehicles do we have"
                    return True, "color", groups[0]
                elif groups[0] in ['vehicles', 'cars'] and groups[1].isdigit():
                    # Pattern: "how many vehicles from 2022"
                    return True, "year", groups[1]
                else:
                    # Pattern: "number of vehicles that are green"
                    return True, groups[1], groups[0]
            elif len(groups) == 3:
                # Pattern: "vehicles that are green"
                return True, groups[1], groups[2]
            elif len(groups) == 4:
                # Pattern: "how many vehicles with color is green"
                return True, groups[1], groups[3]
    
    return False, None, None

def count_attribute_values(attribute_name, attribute_value):
    """
    Count vehicles with a specific attribute value
    
    Args:
        attribute_name (str): The column name to check
        attribute_value (str): The value to match
        
    Returns:
        dict: Results of the count operation
    """
    if df is None:
        return {"error": "No dataset loaded"}
    
    if attribute_name not in df.columns:
        return {
            "error": f"Attribute '{attribute_name}' not found",
            "available_columns": list(df.columns)
        }
    
    # For string attributes, do case-insensitive matching
    if df[attribute_name].dtype == 'object':
        # Make values strings to handle NaN
        column_values = df[attribute_name].astype(str)
        filtered_df = df[column_values.str.lower() == str(attribute_value).lower()]
    # For numeric attributes
    else:
        try:
            attribute_value = float(attribute_value)
            filtered_df = df[df[attribute_name] == attribute_value]
        except ValueError:
            return {"error": f"Cannot convert '{attribute_value}' to a number for comparison"}
    
    count = len(filtered_df)
    percentage = (count / len(df)) * 100
    
    # Get sample of matching vehicles
    sample = []
    if count > 0:
        sample_df = filtered_df.head(5)
        for _, row in sample_df.iterrows():
            sample.append({col: row[col] for col in ['id', 'make', 'model', 'year', 'color', 'price']})
    
    # Get distribution of all values for this attribute
    distribution = df[attribute_name].value_counts().head(10).to_dict()
    
    return {
        "attribute": attribute_name,
        "value": attribute_value,
        "count": count,
        "percentage": round(percentage, 2),
        "sample": sample,
        "distribution": distribution
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Attribute Query Server is running"}), 200

@app.route('/api/attribute-query', methods=['POST'])
def attribute_query():
    """Handle an attribute query"""
    data = request.json
    query = data.get('query', '')
    
    is_attribute_query, attribute_name, attribute_value = detect_attribute_query(query)
    
    if is_attribute_query:
        result = count_attribute_values(attribute_name, attribute_value)
        return jsonify({
            "query_type": "attribute_query",
            "detected": True,
            "attribute_name": attribute_name,
            "attribute_value": attribute_value,
            "result": result
        })
    else:
        return jsonify({
            "query_type": "unknown",
            "detected": False,
            "message": "This query was not recognized as an attribute-specific query."
        })

@app.route('/api/direct-count', methods=['POST'])
def direct_count():
    """Directly count by attribute and value"""
    data = request.json
    attribute_name = data.get('attribute_name', '')
    attribute_value = data.get('attribute_value', '')
    
    if not attribute_name or not attribute_value:
        return jsonify({"error": "Both attribute_name and attribute_value are required"}), 400
    
    result = count_attribute_values(attribute_name, attribute_value)
    return jsonify(result)

if __name__ == '__main__':
    if df is None:
        print("WARNING: No dataset loaded. The application will run but may not function correctly.")
    
    port = int(os.environ.get('PORT', 8001))
    print(f"Starting Attribute Query Server on port {port}...")
    print("Available endpoints:")
    print("  - /health - Health check")
    print("  - /api/attribute-query - Detect and process attribute queries")
    print("  - /api/direct-count - Direct counting by attribute name and value")
    
    app.run(host='0.0.0.0', port=port, debug=True) 