#!/usr/bin/env python
# Export automotive data to CSV files for download

import json
import os
import pandas as pd

def main():
    """Export automotive data to CSV files for download"""
    # Define data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
    
    # Create export directory if it doesn't exist
    os.makedirs(export_dir, exist_ok=True)
    
    # Load data from JSON files
    vehicles_file = os.path.join(data_dir, "vehicles.json")
    market_data_file = os.path.join(data_dir, "market_data.json")
    
    if not os.path.exists(vehicles_file) or not os.path.exists(market_data_file):
        print("Data files not found. Run generate_automotive_data.py first.")
        return
    
    # Load data
    with open(vehicles_file, "r") as f:
        vehicles = json.load(f)
    
    with open(market_data_file, "r") as f:
        market_data = json.load(f)
    
    # Convert to DataFrames
    vehicles_df = pd.DataFrame(vehicles)
    market_data_df = pd.DataFrame(market_data)
    
    # Create a combined dataset with vehicle and market data
    # First, create a dictionary to quickly look up market data by vehicle_id
    market_data_dict = {item["vehicle_id"]: item for item in market_data}
    
    # Create a combined dataset
    combined_data = []
    for vehicle in vehicles:
        if not vehicle["is_sold"] and vehicle["id"] in market_data_dict:
            market_info = market_data_dict[vehicle["id"]]
            combined_record = {
                "id": vehicle["id"],
                "make": vehicle["make"],
                "model": vehicle["model"],
                "year": vehicle["year"],
                "color": vehicle["color"],
                "price": vehicle["price"],
                "mileage": vehicle["mileage"],
                "condition": vehicle["condition"],
                "fuel_type": vehicle["fuel_type"],
                "days_in_inventory": vehicle["days_in_inventory"],
                "avg_market_price": market_info["avg_market_price"],
                "price_difference": market_info["price_difference"],
                "percent_difference": market_info["percent_difference"],
                "is_opportunity": market_info["is_opportunity"],
                "market_demand": market_info["market_demand"],
                "avg_days_to_sell": market_info["avg_days_to_sell"]
            }
            combined_data.append(combined_record)
    
    combined_df = pd.DataFrame(combined_data)
    
    # Export to CSV
    vehicles_df.to_csv(os.path.join(export_dir, "vehicles.csv"), index=False)
    market_data_df.to_csv(os.path.join(export_dir, "market_data.csv"), index=False)
    combined_df.to_csv(os.path.join(export_dir, "automotive_analysis.csv"), index=False)
    
    print(f"Exported {len(vehicles)} vehicles to {os.path.join(export_dir, 'vehicles.csv')}")
    print(f"Exported {len(market_data)} market data records to {os.path.join(export_dir, 'market_data.csv')}")
    print(f"Exported {len(combined_data)} combined records to {os.path.join(export_dir, 'automotive_analysis.csv')}")
    print(f"Files are ready for download in the {export_dir} directory")

if __name__ == "__main__":
    main() 