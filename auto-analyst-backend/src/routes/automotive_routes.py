import json
import os
import csv
import pandas as pd
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query

# Create router
router = APIRouter(
    prefix="/api",
    tags=["automotive"],
    responses={404: {"description": "Not found"}},
)

# Path to the data files (try frontend demo files first, then fallback to data dir)
frontend_demo_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                              "Auto-Analyst/auto-analyst-frontend/public/demo-files")
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

# First try frontend demo files
vehicles_file_csv = os.path.join(frontend_demo_dir, "vehicles.csv")
market_data_file_csv = os.path.join(frontend_demo_dir, "market_data.csv")

# If not found, fallback to json files in data dir
vehicles_file_json = os.path.join(data_dir, "vehicles.json")
market_data_file_json = os.path.join(data_dir, "market_data.json")

# Load data from CSV files if available, otherwise use JSON
def load_data():
    vehicles = []
    market_data = []
    
    # Try to load from CSV first (frontend demo files)
    if os.path.exists(vehicles_file_csv):
        try:
            vehicles_df = pd.read_csv(vehicles_file_csv)
            vehicles = vehicles_df.to_dict(orient="records")
            print(f"Loaded {len(vehicles)} vehicles from CSV file")
        except Exception as e:
            print(f"Error loading vehicles CSV: {str(e)}")
    
    if os.path.exists(market_data_file_csv):
        try:
            market_df = pd.read_csv(market_data_file_csv)
            market_data = market_df.to_dict(orient="records")
            print(f"Loaded {len(market_data)} market data entries from CSV file")
        except Exception as e:
            print(f"Error loading market data CSV: {str(e)}")
    
    # If CSV loading failed or files don't exist, try JSON
    if not vehicles and os.path.exists(vehicles_file_json):
        try:
            with open(vehicles_file_json, "r") as f:
                vehicles = json.load(f)
                print(f"Loaded {len(vehicles)} vehicles from JSON file")
        except Exception as e:
            print(f"Error loading vehicles JSON: {str(e)}")
    
    if not market_data and os.path.exists(market_data_file_json):
        try:
            with open(market_data_file_json, "r") as f:
                market_data = json.load(f)
                print(f"Loaded {len(market_data)} market data entries from JSON file")
        except Exception as e:
            print(f"Error loading market data JSON: {str(e)}")
    
    # Convert numeric fields that might be stored as strings in CSV
    for vehicle in vehicles:
        for field in ["id", "year", "price", "mileage", "days_in_inventory"]:
            if field in vehicle and isinstance(vehicle[field], str) and vehicle[field].strip():
                try:
                    vehicle[field] = int(float(vehicle[field]))
                except ValueError:
                    pass
        if "is_sold" in vehicle and isinstance(vehicle["is_sold"], str):
            vehicle["is_sold"] = vehicle["is_sold"].lower() in ["true", "1", "yes"]
    
    for item in market_data:
        for field in ["id", "vehicle_id", "year", "your_price", "market_price", "days_in_inventory"]:
            if field in item and isinstance(item[field], str) and item[field].strip():
                try:
                    item[field] = int(float(item[field]))
                except ValueError:
                    pass
        for field in ["price_difference", "price_difference_percent", "avg_days_to_sell"]:
            if field in item and isinstance(item[field], str) and item[field].strip():
                try:
                    item[field] = float(item[field])
                except ValueError:
                    pass
        if "is_opportunity" in item and isinstance(item["is_opportunity"], str):
            item["is_opportunity"] = item["is_opportunity"].lower() in ["true", "1", "yes"]
    
    return vehicles, market_data

# Routes
@router.get("/vehicles")
async def get_vehicles(
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    condition: Optional[str] = None,
    sold: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get vehicle inventory with optional filters
    """
    vehicles, _ = load_data()
    
    # Apply filters
    filtered_vehicles = vehicles
    
    if make:
        filtered_vehicles = [v for v in filtered_vehicles if v["make"].lower() == make.lower()]
    
    if model:
        filtered_vehicles = [v for v in filtered_vehicles if v["model"].lower() == model.lower()]
    
    if year:
        filtered_vehicles = [v for v in filtered_vehicles if v["year"] == year]
    
    if min_price is not None:
        filtered_vehicles = [v for v in filtered_vehicles if v["price"] >= min_price]
    
    if max_price is not None:
        filtered_vehicles = [v for v in filtered_vehicles if v["price"] <= max_price]
    
    if condition:
        filtered_vehicles = [v for v in filtered_vehicles if v["condition"].lower() == condition.lower()]
    
    if sold is not None:
        filtered_vehicles = [v for v in filtered_vehicles if v["is_sold"] == sold]
    
    # Apply pagination
    total_count = len(filtered_vehicles)
    paginated_vehicles = filtered_vehicles[offset:offset + limit]
    
    return {
        "total": total_count,
        "vehicles": paginated_vehicles
    }

@router.get("/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: int):
    """
    Get a specific vehicle by ID
    """
    vehicles, _ = load_data()
    
    for vehicle in vehicles:
        if vehicle["id"] == vehicle_id:
            return vehicle
    
    raise HTTPException(status_code=404, detail=f"Vehicle with ID {vehicle_id} not found")

@router.get("/market-data")
async def get_market_data(
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    is_opportunity: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get market data with optional filters
    """
    _, market_data = load_data()
    
    # Apply filters
    filtered_data = market_data
    
    if make:
        filtered_data = [d for d in filtered_data if d.get("make", "").lower() == make.lower()]
    
    if model:
        filtered_data = [d for d in filtered_data if d.get("model", "").lower() == model.lower()]
    
    if year:
        filtered_data = [d for d in filtered_data if d.get("year") == year]
    
    if is_opportunity is not None:
        # Check both possible field options
        filtered_data = []
        for d in market_data:
            # Direct field match
            if "is_opportunity" in d and d["is_opportunity"] == is_opportunity:
                filtered_data.append(d)
            # Calculate from percent difference if is_opportunity is True
            elif is_opportunity is True:
                if "percent_difference" in d:
                    try:
                        if float(d["percent_difference"]) >= 5.0:
                            filtered_data.append(d)
                    except (ValueError, TypeError):
                        pass
                elif "price_difference_percent" in d:
                    try:
                        if float(d["price_difference_percent"]) >= 5.0:
                            filtered_data.append(d)
                    except (ValueError, TypeError):
                        pass
            # Calculate from percent difference if is_opportunity is False
            elif is_opportunity is False:
                if "percent_difference" in d:
                    try:
                        if float(d["percent_difference"]) < 5.0:
                            filtered_data.append(d)
                    except (ValueError, TypeError):
                        filtered_data.append(d)  # If we can't parse, treat as not an opportunity
                elif "price_difference_percent" in d:
                    try:
                        if float(d["price_difference_percent"]) < 5.0:
                            filtered_data.append(d)
                    except (ValueError, TypeError):
                        filtered_data.append(d)  # If we can't parse, treat as not an opportunity
    
    # Apply pagination
    total_count = len(filtered_data)
    paginated_data = filtered_data[offset:offset + limit]
    
    return {
        "total": total_count,
        "market_data": paginated_data
    }

@router.get("/market-data/{vehicle_id}")
async def get_market_data_for_vehicle(vehicle_id: int):
    """
    Get market data for a specific vehicle
    """
    _, market_data = load_data()
    
    for data in market_data:
        if data["vehicle_id"] == vehicle_id:
            return data
    
    raise HTTPException(status_code=404, detail=f"Market data for vehicle ID {vehicle_id} not found")

@router.get("/opportunities")
async def get_opportunities(
    min_percent_difference: float = 5.0,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get undervalued vehicle opportunities
    """
    vehicles, market_data = load_data()
    
    # Create a lookup dictionary for vehicles by ID
    vehicle_lookup = {vehicle["id"]: vehicle for vehicle in vehicles}
    
    # Find opportunities
    opportunities = []
    for data in market_data:
        # Check the field name that contains price difference percentage
        price_diff_field = None
        if "percent_difference" in data:
            price_diff_field = "percent_difference"
        elif "price_difference_percent" in data:
            price_diff_field = "price_difference_percent"
        
        # Skip if we can't find a price difference field
        if not price_diff_field:
            continue
            
        try:
            price_diff_value = float(data[price_diff_field])
            if price_diff_value >= min_percent_difference:
                # Find the vehicle_id field
                vehicle_id_field = None
                if "vehicle_id" in data:
                    vehicle_id_field = "vehicle_id"
                elif "id" in data:
                    vehicle_id_field = "id"
                
                if not vehicle_id_field:
                    continue
                    
                vehicle_id = data[vehicle_id_field]
                
                # Check if the vehicle exists in our lookup
                if vehicle_id in vehicle_lookup:
                    # Combine vehicle and market data
                    opportunity = {
                        **vehicle_lookup[vehicle_id],
                        "market_data": data
                    }
                    opportunities.append(opportunity)
        except (ValueError, TypeError):
            # Skip entries where we can't parse the price difference as a float
            continue
    
    # Apply pagination
    total_count = len(opportunities)
    paginated_opportunities = opportunities[offset:offset + limit]
    
    return {
        "total": total_count,
        "opportunities": paginated_opportunities
    }

@router.get("/statistics")
async def get_statistics():
    """
    Get statistical overview of the inventory
    """
    vehicles, market_data = load_data()
    
    # Basic stats
    total_vehicles = len(vehicles)
    available_vehicles = sum(1 for v in vehicles if not v.get("is_sold", False))
    sold_vehicles = sum(1 for v in vehicles if v.get("is_sold", False))
    
    # Count by make
    make_counts = {}
    for vehicle in vehicles:
        make = vehicle.get("make", "Unknown")
        if make not in make_counts:
            make_counts[make] = 0
        make_counts[make] += 1
    
    # Count by condition
    condition_counts = {}
    for vehicle in vehicles:
        condition = vehicle.get("condition", "Unknown")
        if condition not in condition_counts:
            condition_counts[condition] = 0
        condition_counts[condition] += 1
    
    # Average price by make
    prices_by_make = {}
    for vehicle in vehicles:
        make = vehicle.get("make", "Unknown")
        if make not in prices_by_make:
            prices_by_make[make] = []
        
        # Skip if price is not a number
        try:
            price = float(vehicle.get("price", 0))
            prices_by_make[make].append(price)
        except (ValueError, TypeError):
            pass
    
    avg_prices_by_make = {
        make: sum(prices) / len(prices) if prices else 0
        for make, prices in prices_by_make.items()
    }
    
    # Count opportunities (vehicles with price_difference_percent >= 5.0)
    opportunities_count = 0
    for data in market_data:
        # Check for both field possibilities
        if "is_opportunity" in data:
            try:
                if data["is_opportunity"]:
                    opportunities_count += 1
            except (ValueError, TypeError):
                pass
        elif "price_difference_percent" in data:
            try:
                if float(data["price_difference_percent"]) >= 5.0:
                    opportunities_count += 1
            except (ValueError, TypeError):
                pass
        elif "percent_difference" in data:
            try:
                if float(data["percent_difference"]) >= 5.0:
                    opportunities_count += 1
            except (ValueError, TypeError):
                pass
    
    return {
        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "sold_vehicles": sold_vehicles,
        "make_distribution": make_counts,
        "condition_distribution": condition_counts,
        "avg_prices_by_make": avg_prices_by_make,
        "opportunities_count": opportunities_count
    } 