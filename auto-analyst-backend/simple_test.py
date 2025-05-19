import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key with fallback
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment.")
    exit(1)

# Load the vehicles dataset
try:
    # Try to load the dataset from the exports directory
    vehicles_path = "exports/vehicles.csv"
    df = pd.read_csv(vehicles_path)
    print(f"✅ Loaded dataset with {len(df)} vehicles")
    
    # Display the first few rows
    print("\nSample data:")
    print(df.head(3))
    
    # Show available columns
    print("\nAvailable columns:")
    print(df.columns.tolist())
    
    # Check if color column exists
    if 'color' in df.columns:
        # Count green vehicles
        green_vehicles = df[df['color'].str.lower() == 'green']
        print(f"\n✅ Count of green vehicles: {len(green_vehicles)}")
        
        # Show sample of green vehicles
        if not green_vehicles.empty:
            print("\nSample of green vehicles:")
            print(green_vehicles.head(3))
        else:
            print("\nNo green vehicles found in the dataset.")
    else:
        print("\n❌ 'color' column not found in the dataset.")
        
except Exception as e:
    print(f"❌ Error loading dataset: {str(e)}")

# Now let's test the Gemini API directly
def query_gemini(prompt):
    """Execute a query using Gemini"""
    try:
        model = "gemini-1.5-pro"
        
        # API endpoint for Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # Create Gemini API request payload
        data = {
            "contents": [{"parts":[{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 1024
            }
        }
        
        # Send request to Gemini API
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: {response.status_code}, {response.text}"
            
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create a prompt that specifically asks about green vehicles
prompt = """
You are analyzing a vehicle dataset with the following columns:
id, make, model, year, color, price, mileage, condition, fuel_type, days_in_inventory, vin, is_sold

The user has asked: "How many green vehicles do we have?"

Based on my analysis, the answer is [number of green vehicles] green vehicles.
Please provide this exact count along with a brief explanation of what this represents in the dataset.
"""

# Call the API
print("\n===== Testing Gemini API Response =====")
response = query_gemini(prompt)
print(response) 