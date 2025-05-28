#!/usr/bin/env python3

import pandas as pd
import requests
import json

def test_data_endpoints():
    """Test the data endpoints to see what data is available"""
    base_url = "http://localhost:8000"
    
    print("Testing data endpoints...")
    
    # Test vehicles endpoint
    try:
        print("\n--- Testing /vehicles endpoint ---")
        response = requests.get(f"{base_url}/vehicles", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Number of vehicles: {len(data)}")
            if data:
                print(f"Sample vehicle: {json.dumps(data[0], indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing vehicles endpoint: {e}")
    
    # Test CSV file directly
    try:
        print("\n--- Testing vehicles.csv file directly ---")
        df = pd.read_csv("exports/vehicles.csv")
        print(f"CSV file shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample data:\n{df.head()}")
        
        # Test specific questions manually
        print(f"\n--- Manual Data Analysis ---")
        print(f"Total vehicles: {len(df)}")
        if 'price' in df.columns:
            max_price_vehicle = df.loc[df['price'].idxmax()]
            print(f"Most expensive vehicle: {max_price_vehicle['make']} {max_price_vehicle['model']} - ${max_price_vehicle['price']}")
        
        if 'make' in df.columns:
            toyota_vehicles = df[df['make'].str.lower() == 'toyota']
            if 'price' in df.columns:
                toyota_under_25k = toyota_vehicles[toyota_vehicles['price'] < 25000]
                print(f"Toyota vehicles under $25,000: {len(toyota_under_25k)}")
            else:
                print(f"Toyota vehicles: {len(toyota_vehicles)}")
    except Exception as e:
        print(f"Error testing CSV file: {e}")

if __name__ == "__main__":
    test_data_endpoints() 