#!/usr/bin/env python
import os
import csv
import shutil
import random

# Define paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BACKEND_DIR, "exports")
FRONTEND_PUBLIC_DIR = os.path.join(BACKEND_DIR, "..", "auto-analyst-frontend", "public", "demo-files")

# Create directories if they don't exist
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(FRONTEND_PUBLIC_DIR, exist_ok=True)
os.makedirs(os.path.join(FRONTEND_PUBLIC_DIR, "exports"), exist_ok=True)

def create_sample_csv_files():
    """Create sample CSV files if they don't exist"""
    
    # Define the sample files to create if they don't exist
    sample_files = {
        "vehicles.csv": {
            "headers": ["id", "make", "model", "year", "color", "price", "mileage", "condition", "fuel_type", "list_date", "days_in_inventory", "vin", "is_sold"],
            "row_count": 50,
            "makes": ["Toyota", "Honda", "Ford", "BMW", "Audi", "Chevrolet", "Mercedes", "Hyundai", "Kia", "Nissan", "Tesla"],
            "models": {
                "Toyota": ["Camry", "Corolla", "RAV4", "Tacoma", "Highlander"],
                "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
                "Ford": ["F-150", "Edge", "Explorer", "Escape", "Mustang"],
                "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series"],
                "Audi": ["A4", "A6", "Q5", "Q7", "A8"],
                "Chevrolet": ["Silverado", "Equinox", "Tahoe", "Malibu", "Traverse"],
                "Mercedes": ["C-Class", "E-Class", "GLE", "S-Class", "GLC"],
                "Hyundai": ["Elantra", "Sonata", "Santa Fe", "Tucson", "Palisade"],
                "Kia": ["Sorento", "Sportage", "Telluride", "Soul", "Optima"],
                "Nissan": ["Altima", "Rogue", "Pathfinder", "Murano", "Sentra"],
                "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck"]
            },
            "colors": ["Red", "Blue", "Black", "White", "Silver", "Gray", "Green", "Orange", "Brown"],
            "conditions": ["Excellent", "Good", "Fair", "Poor"],
            "fuel_types": ["Gasoline", "Diesel", "Hybrid", "Electric"],
            "year_range": [2015, 2023],
            "price_range": [5000, 60000],
            "mileage_range": [1000, 100000]
        },
        "market_data.csv": {
            "headers": ["id", "make", "model", "year", "avg_market_price", "inventory_count", "days_to_sell", "demand_index"],
            "row_count": 30
        },
        "automotive_analysis.csv": {
            "headers": ["id", "vehicle_id", "price_delta", "price_position", "profit_potential", "recommendation"],
            "row_count": 40
        }
    }
    
    # Create each sample file if it doesn't exist
    for filename, config in sample_files.items():
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"Creating sample file: {filepath}")
            
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(config["headers"])
                
                # Generate sample data based on the file type
                if filename == "vehicles.csv":
                    # Generate more complex vehicle data
                    for i in range(1, config["row_count"] + 1):
                        make = random.choice(config["makes"])
                        model = random.choice(config["models"][make])
                        year = random.randint(config["year_range"][0], config["year_range"][1])
                        color = random.choice(config["colors"])
                        price = random.randint(config["price_range"][0], config["price_range"][1])
                        mileage = random.randint(config["mileage_range"][0], config["mileage_range"][1])
                        condition = random.choice(config["conditions"])
                        fuel_type = random.choice(config["fuel_types"])
                        
                        # Generate a realistic date
                        month = random.randint(1, 5)
                        day = random.randint(1, 28)
                        list_date = f"2025-{month:02d}-{day:02d}"
                        
                        # Calculate days in inventory (current date is May 17, 2025)
                        days_in_inventory = (5 - month) * 30 + (17 - day)
                        if days_in_inventory < 0:
                            days_in_inventory += 365  # Previous year
                        
                        vin = f"VIN{i}ABC{random.randint(10000, 99999)}"
                        is_sold = "True" if random.random() < 0.2 else "False"  # 20% sold
                        
                        writer.writerow([
                            i, make, model, year, color, price, mileage, condition, 
                            fuel_type, list_date, days_in_inventory, vin, is_sold
                        ])
                
                elif filename == "market_data.csv":
                    # Generate market data
                    makes_models = []
                    vehicle_config = sample_files["vehicles.csv"]
                    
                    # Generate unique make/model combinations
                    for _ in range(config["row_count"]):
                        make = random.choice(vehicle_config["makes"])
                        model = random.choice(vehicle_config["models"][make])
                        year = random.randint(vehicle_config["year_range"][0], vehicle_config["year_range"][1])
                        
                        combo = (make, model, year)
                        if combo not in makes_models:
                            makes_models.append(combo)
                    
                    # Fill with more if needed
                    while len(makes_models) < config["row_count"]:
                        make = random.choice(vehicle_config["makes"])
                        model = random.choice(vehicle_config["models"][make])
                        year = random.randint(vehicle_config["year_range"][0], vehicle_config["year_range"][1])
                        
                        combo = (make, model, year)
                        if combo not in makes_models:
                            makes_models.append(combo)
                    
                    # Write the data
                    for i, (make, model, year) in enumerate(makes_models[:config["row_count"]], 1):
                        avg_price = random.randint(vehicle_config["price_range"][0], vehicle_config["price_range"][1])
                        inventory = random.randint(1, 20)
                        days_to_sell = random.randint(10, 90)
                        demand_index = round(random.uniform(1.0, 10.0), 1)
                        
                        writer.writerow([i, make, model, year, avg_price, inventory, days_to_sell, demand_index])
                
                elif filename == "automotive_analysis.csv":
                    # Generate analysis data
                    for i in range(1, config["row_count"] + 1):
                        vehicle_id = random.randint(1, sample_files["vehicles.csv"]["row_count"])
                        price_delta = random.randint(-5000, 5000)
                        
                        # Determine price position
                        if price_delta < -1000:
                            price_position = "Below Market"
                        elif price_delta > 1000:
                            price_position = "Above Market"
                        else:
                            price_position = "At Market"
                        
                        # Calculate profit potential
                        if price_delta < 0:
                            profit_potential = abs(price_delta)
                        else:
                            profit_potential = 0
                        
                        # Generate recommendation
                        if price_delta < -2000:
                            recommendation = "Increase Price"
                        elif price_delta > 2000:
                            recommendation = "Reduce Price"
                        else:
                            recommendation = "Maintain Price"
                        
                        writer.writerow([i, vehicle_id, price_delta, price_position, profit_potential, recommendation])
                
                else:
                    # Generic data for any other files
                    for i in range(1, config["row_count"] + 1):
                        row = [i] + [f"Sample{j}" for j in range(1, len(config["headers"]))]
                        writer.writerow(row)
            
            print(f"✅ Created sample file: {filename}")
        else:
            print(f"✅ Sample file already exists: {filename}")


def copy_files_to_frontend():
    """Copy files from the exports directory to the frontend public directory"""
    source_dir = EXPORTS_DIR
    target_dir = os.path.join(FRONTEND_PUBLIC_DIR, "exports")
    
    # Get list of CSV files in exports directory
    csv_files = [f for f in os.listdir(source_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ No CSV files found in exports directory.")
        return
    
    # Copy each file
    for filename in csv_files:
        source_path = os.path.join(source_dir, filename)
        target_path = os.path.join(target_dir, filename)
        
        try:
            shutil.copy2(source_path, target_path)
            print(f"✅ Copied {filename} to frontend public directory")
        except Exception as e:
            print(f"❌ Failed to copy {filename}: {str(e)}")

def main():
    print("Auto-Analyst: Copy Files to Public")
    print("=================================")
    
    # Create sample CSV files if they don't exist
    print("\nCreating sample CSV files...")
    create_sample_csv_files()
    
    # Copy files to frontend public directory
    print("\nCopying files to frontend public directory...")
    copy_files_to_frontend()
    
    print("\nDone!")


if __name__ == "__main__":
    main() 