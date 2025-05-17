#!/usr/bin/env python3
"""
Synthetic Automotive Data Generator

This script generates realistic synthetic data for the automotive pricing POV demo.
It creates multiple JSON files containing vehicle inventory, market data,
historical sales, price recommendations, and market opportunities.
"""

import json
import random
import uuid
import os
import datetime
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common data for realistic values
MAKES_MODELS = {
    "Audi": ["A3", "A4", "A6", "Q5", "Q7", "e-tron"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "i4", "i7"],
    "Ford": ["Focus", "Fiesta", "Mustang", "Explorer", "F-150", "Ranger"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "HR-V"],
    "Toyota": ["Corolla", "Camry", "RAV4", "Highlander", "Prius"],
    "Volkswagen": ["Golf", "Passat", "Tiguan", "ID.4", "Atlas"],
    "Mercedes-Benz": ["A-Class", "C-Class", "E-Class", "GLC", "GLE"],
    "Nissan": ["Juke", "Qashqai", "Micra", "Leaf", "X-Trail"],
    "Hyundai": ["i10", "i30", "Tucson", "Kona", "Ioniq"],
    "Kia": ["Picanto", "Rio", "Sportage", "Niro", "EV6"]
}

BODY_TYPES = ["Sedan", "SUV", "Hatchback", "Coupe", "Convertible", "Pickup", "Estate", "MPV"]
FUEL_TYPES = ["Petrol", "Diesel", "Hybrid", "Electric", "Plug-in Hybrid"]
TRANSMISSIONS = ["Automatic", "Manual", "Semi-automatic", "CVT"]
COLORS = ["Black", "White", "Silver", "Grey", "Blue", "Red", "Green", "Brown", "Yellow", "Orange"]
CONDITIONS = ["Excellent", "Good", "Fair", "Poor"]
FEATURES = ["Leather Seats", "Navigation", "Sunroof", "Bluetooth", "Backup Camera", 
            "Heated Seats", "Cruise Control", "Parking Sensors", "Lane Assist", 
            "Blind Spot Monitor", "Apple CarPlay", "Android Auto", "Keyless Entry"]
LOCATIONS = ["North Showroom", "South Showroom", "West Lot", "East Lot", "Main Building"]
STATUSES = ["In Stock", "Sold", "On Hold", "In Transit", "Pending", "Servicing"]
CUSTOMER_TYPES = ["Retail", "Wholesale", "Trade-In"]
FINANCING_TYPES = ["Cash", "Finance", "Lease", "PCP", "HP"]
SALESPEOPLE = ["John Smith", "Sarah Johnson", "David Williams", "Emma Brown", "Michael Jones"]
OPPORTUNITY_TYPES = ["Undervalued", "High Demand", "Seasonal", "Quick Sale", "Rare Find"]
OPPORTUNITY_SOURCES = ["Auction", "Private Sale", "Trade", "Competitor", "Fleet", "Lease Return"]
COMPETITIVE_POSITIONS = ["Underpriced", "Competitive", "Overpriced"]
REGIONS = ["London", "South East", "South West", "Midlands", "North West", "North East", "Scotland", "Wales"]

def generate_random_date(start_date, end_date):
    """Generate a random date between start_date and end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_vin():
    """Generate a random VIN number"""
    chars = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
    return ''.join(random.choice(chars) for _ in range(17))

def generate_vehicle_inventory(count: int = 100) -> List[Dict[str, Any]]:
    """Generate vehicle inventory data"""
    vehicles = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for _ in range(count):
        make = random.choice(list(MAKES_MODELS.keys()))
        model = random.choice(MAKES_MODELS[make])
        year = random.randint(2015, 2023)
        
        acquisition_date = generate_random_date(start_date, end_date)
        days_on_lot = (end_date - acquisition_date).days
        
        # Base price depends on make, model, year and mileage
        base_value = random.randint(5000, 50000)
        mileage = random.randint(500, 120000)
        mileage_factor = 1 - (mileage / 200000)  # Higher mileage reduces price
        year_factor = 1 - ((2023 - year) * 0.05)  # Older vehicles are worth less
        
        # Calculate prices
        acquisition_price = round(base_value * mileage_factor * year_factor, 2)
        markup = random.uniform(1.08, 1.25)  # 8-25% markup
        current_price = round(acquisition_price * markup, 2)
        
        # Generate features
        num_features = random.randint(2, 8)
        selected_features = random.sample(FEATURES, num_features)
        
        vehicle = {
            "vehicle_id": str(uuid.uuid4()),
            "make": make,
            "model": model,
            "year": year,
            "trim": random.choice(["Base", "Sport", "Luxury", "Premium", "SE", "GT", "Limited"]),
            "body_type": random.choice(BODY_TYPES),
            "fuel_type": random.choice(FUEL_TYPES),
            "transmission": random.choice(TRANSMISSIONS),
            "engine_size": round(random.uniform(1.0, 5.0), 1),
            "mileage": mileage,
            "color_exterior": random.choice(COLORS),
            "color_interior": random.choice(COLORS),
            "condition": random.choice(CONDITIONS),
            "features": selected_features,
            "acquisition_date": acquisition_date.strftime('%Y-%m-%d'),
            "acquisition_price": acquisition_price,
            "current_price": current_price,
            "recommended_price": round(current_price * random.uniform(0.95, 1.1), 2),
            "days_on_lot": days_on_lot,
            "images": [f"https://example.com/vehicles/{uuid.uuid4()}.jpg" for _ in range(random.randint(3, 8))],
            "vin": generate_vin(),
            "status": "In Stock" if random.random() < 0.7 else random.choice(STATUSES),
            "location": random.choice(LOCATIONS)
        }
        
        vehicles.append(vehicle)
    
    return vehicles

def generate_market_data(vehicles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate market data based on vehicle inventory"""
    market_data = []
    now = datetime.now()
    
    # Get unique vehicle types from inventory
    vehicle_types = set()
    for vehicle in vehicles:
        vehicle_type = f"{vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle['trim']}"
        vehicle_types.add(vehicle_type)
    
    # Add some additional vehicle types not in inventory (for opportunities)
    extra_types = []
    for _ in range(20):
        make = random.choice(list(MAKES_MODELS.keys()))
        model = random.choice(MAKES_MODELS[make])
        year = random.randint(2015, 2023)
        trim = random.choice(["Base", "Sport", "Luxury", "Premium", "SE", "GT", "Limited"])
        vehicle_type = f"{year} {make} {model} {trim}"
        extra_types.append(vehicle_type)
    
    vehicle_types.update(extra_types)
    
    for vehicle_type in vehicle_types:
        # Parse the vehicle type to get components
        parts = vehicle_type.split(" ")
        year = int(parts[0])
        make = parts[1]
        
        # Base price depends on make and year
        base_price = random.randint(8000, 60000)
        
        # Apply adjustments based on year and make
        year_factor = 1 - ((2023 - year) * 0.05)
        make_factor = 1.0
        if make in ["Audi", "BMW", "Mercedes-Benz"]:
            make_factor = 1.3  # Luxury brands
        
        avg_price = round(base_price * year_factor * make_factor, 2)
        
        # Generate market variance
        price_variance = random.uniform(0.07, 0.15)  # 7-15% variance in market
        lowest_price = round(avg_price * (1 - price_variance), 2)
        highest_price = round(avg_price * (1 + price_variance), 2)
        
        # Generate price trend
        trend_percentage = random.uniform(-0.05, 0.08)  # -5% to +8% trend
        
        # Generate seasonal adjustment
        month = now.month
        seasonal_adjustment = 1.0
        if month in [12, 1, 2]:  # Winter
            seasonal_adjustment = random.uniform(0.92, 0.98)  # Lower winter demand
        elif month in [6, 7, 8]:  # Summer
            seasonal_adjustment = random.uniform(1.02, 1.08)  # Higher summer demand
            
        for region in random.sample(REGIONS, random.randint(3, 8)):
            # Slight regional price variations
            regional_factor = random.uniform(0.95, 1.05)
            
            market_entry = {
                "market_id": str(uuid.uuid4()),
                "vehicle_type": vehicle_type,
                "average_market_price": round(avg_price * regional_factor, 2),
                "lowest_market_price": round(lowest_price * regional_factor, 2),
                "highest_market_price": round(highest_price * regional_factor, 2),
                "price_trend_30d": round(trend_percentage * 100, 2),  # Convert to percentage
                "average_days_to_sell": random.randint(15, 90),
                "demand_index": round(random.uniform(10, 95), 1),
                "competitor_count": random.randint(2, 15),
                "region": region,
                "timestamp": now.strftime('%Y-%m-%d %H:%M:%S'),
                "seasonal_adjustment": round(seasonal_adjustment, 2)
            }
            
            market_data.append(market_entry)
    
    return market_data

def save_data(data, filename):
    """Save data to a JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Generated {filename} with {len(data)} records")

def main():
    """Main function to generate all datasets"""
    print("Generating synthetic automotive data...")
    
    # Generate vehicle inventory
    vehicles = generate_vehicle_inventory(100)
    save_data(vehicles, "vehicles.json")
    
    # Generate market data
    market_data = generate_market_data(vehicles)
    save_data(market_data, "market_data.json")
    
    # The rest of the data generation functions will be added in subsequent parts
    
    print("Data generation complete. Files saved to:", OUTPUT_DIR)

if __name__ == "__main__":
    main()