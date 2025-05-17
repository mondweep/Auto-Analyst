#!/usr/bin/env python
# Generate synthetic automotive data for the BI tool

import json
import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Define constants
MAKES = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Tesla", "Hyundai", "Kia", "Chevrolet"]
MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
    "Ford": ["F-150", "Escape", "Explorer", "Mustang", "Edge"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series"],
    "Mercedes": ["C-Class", "E-Class", "GLC", "GLE", "S-Class"],
    "Audi": ["A4", "A6", "Q5", "Q7", "A8"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck"],
    "Hyundai": ["Elantra", "Tucson", "Santa Fe", "Kona", "Palisade"],
    "Kia": ["Forte", "Sportage", "Sorento", "Telluride", "Soul"],
    "Chevrolet": ["Silverado", "Equinox", "Tahoe", "Malibu", "Traverse"]
}
COLORS = ["Red", "Blue", "Black", "White", "Silver", "Gray", "Green", "Yellow", "Orange", "Brown"]
CONDITIONS = ["Excellent", "Good", "Fair", "Poor"]
FUEL_TYPES = ["Gasoline", "Diesel", "Hybrid", "Electric"]

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(output_dir, exist_ok=True)

def generate_vehicle_data(num_vehicles=200):
    """Generate synthetic vehicle inventory data"""
    vehicles = []
    
    for i in range(num_vehicles):
        make = random.choice(MAKES)
        model = random.choice(MODELS[make])
        year = random.randint(2010, 2024)
        
        # Adjust price based on age, make and condition
        base_price = random.randint(5000, 60000)
        age_factor = (2024 - year) * 0.05
        
        # Luxury brands have higher prices
        if make in ["BMW", "Mercedes", "Audi", "Tesla"]:
            base_price *= 1.5
            
        condition = random.choice(CONDITIONS)
        condition_factor = {
            "Excellent": 1.1,
            "Good": 1.0,
            "Fair": 0.85,
            "Poor": 0.7
        }[condition]
        
        # Calculate final price with some randomness
        price = int(base_price * (1 - age_factor) * condition_factor * random.uniform(0.9, 1.1))
        
        # Generate mileage based on age and condition
        avg_yearly_miles = random.randint(8000, 15000)
        age_years = 2024 - year
        base_mileage = avg_yearly_miles * age_years
        mileage_factor = {
            "Excellent": 0.8,
            "Good": 1.0,
            "Fair": 1.2,
            "Poor": 1.5
        }[condition]
        mileage = int(base_mileage * mileage_factor * random.uniform(0.9, 1.1))
        
        # Random date in the last 90 days for when vehicle was added to inventory
        days_in_inventory = random.randint(1, 90)
        list_date = (datetime.now() - timedelta(days=days_in_inventory)).strftime("%Y-%m-%d")
        
        vehicles.append({
            "id": i + 1,
            "make": make,
            "model": model,
            "year": year,
            "color": random.choice(COLORS),
            "price": price,
            "mileage": mileage,
            "condition": condition,
            "fuel_type": random.choice(FUEL_TYPES),
            "list_date": list_date,
            "days_in_inventory": days_in_inventory,
            "vin": f"VIN{random.randint(100000, 999999)}",
            "is_sold": random.random() < 0.2,  # 20% chance the vehicle is sold
        })
    
    return vehicles

def generate_market_data(vehicles):
    """Generate market data based on the vehicles"""
    market_data = []
    
    for vehicle in vehicles:
        # Create 3-5 market comparables for each make/model/year
        if not vehicle["is_sold"]:  # Only generate market data for unsold vehicles
            make = vehicle["make"]
            model = vehicle["model"]
            year = vehicle["year"]
            
            # Find vehicles with the same make, model and year (+/- 1 year)
            similar_vehicles = [v for v in vehicles if 
                               v["make"] == make and 
                               v["model"] == model and 
                               abs(v["year"] - year) <= 1]
            
            # Calculate market statistics
            prices = [v["price"] for v in similar_vehicles]
            avg_price = sum(prices) / len(prices) if prices else vehicle["price"]
            
            # Add some market fluctuation
            market_fluctuation = random.uniform(0.85, 1.15)
            market_price = int(avg_price * market_fluctuation)
            
            # Calculate if the vehicle is undervalued
            price_difference = market_price - vehicle["price"]
            percent_difference = price_difference / market_price * 100 if market_price > 0 else 0
            is_opportunity = percent_difference > 10  # More than 10% undervalued
            
            market_data.append({
                "vehicle_id": vehicle["id"],
                "make": make,
                "model": model,
                "year": year,
                "avg_market_price": market_price,
                "price_difference": price_difference,
                "percent_difference": round(percent_difference, 2),
                "is_opportunity": is_opportunity,
                "sample_size": len(similar_vehicles),
                "avg_days_to_sell": random.randint(20, 60),
                "market_demand": random.choice(["High", "Medium", "Low"]),
            })
    
    return market_data

def main():
    # Generate vehicle data
    vehicles = generate_vehicle_data(200)
    
    # Generate market data
    market_data = generate_market_data(vehicles)
    
    # Save to files
    with open(os.path.join(output_dir, "vehicles.json"), "w") as f:
        json.dump(vehicles, f, indent=2)
    
    with open(os.path.join(output_dir, "market_data.json"), "w") as f:
        json.dump(market_data, f, indent=2)
    
    # Also save as CSV
    vehicles_df = pd.DataFrame(vehicles)
    vehicles_df.to_csv(os.path.join(output_dir, "vehicles.csv"), index=False)
    
    market_df = pd.DataFrame(market_data)
    market_df.to_csv(os.path.join(output_dir, "market_data.csv"), index=False)
    
    print(f"Generated {len(vehicles)} vehicles and {len(market_data)} market data records.")
    print(f"Files saved to {output_dir}")

if __name__ == "__main__":
    main() 