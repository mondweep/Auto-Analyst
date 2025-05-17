import json
import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

# Create router
router = APIRouter(
    prefix="/api",
    tags=["automotive"],
    responses={404: {"description": "Not found"}},
)

# Path to the data files
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
vehicles_file = os.path.join(data_dir, "vehicles.json")
market_data_file = os.path.join(data_dir, "market_data.json")

# Check if data files exist, if not, give a clear error
if not os.path.exists(vehicles_file) or not os.path.exists(market_data_file):
    raise FileNotFoundError(
        "Automotive data files not found. Please run the script 'scripts/generate_automotive_data.py' first."
    )

# Load data from files
def load_data():
    with open(vehicles_file, "r") as f:
        vehicles = json.load(f)
    
    with open(market_data_file, "r") as f:
        market_data = json.load(f)
    
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
        filtered_data = [d for d in filtered_data if d["make"].lower() == make.lower()]
    
    if model:
        filtered_data = [d for d in filtered_data if d["model"].lower() == model.lower()]
    
    if year:
        filtered_data = [d for d in filtered_data if d["year"] == year]
    
    if is_opportunity is not None:
        filtered_data = [d for d in filtered_data if d["is_opportunity"] == is_opportunity]
    
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
        if data["percent_difference"] >= min_percent_difference:
            vehicle_id = data["vehicle_id"]
            if vehicle_id in vehicle_lookup:
                # Combine vehicle and market data
                opportunity = {
                    **vehicle_lookup[vehicle_id],
                    "market_data": data
                }
                opportunities.append(opportunity)
    
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
    available_vehicles = sum(1 for v in vehicles if not v["is_sold"])
    sold_vehicles = sum(1 for v in vehicles if v["is_sold"])
    
    # Count by make
    make_counts = {}
    for vehicle in vehicles:
        make = vehicle["make"]
        if make not in make_counts:
            make_counts[make] = 0
        make_counts[make] += 1
    
    # Count by condition
    condition_counts = {}
    for vehicle in vehicles:
        condition = vehicle["condition"]
        if condition not in condition_counts:
            condition_counts[condition] = 0
        condition_counts[condition] += 1
    
    # Average price by make
    prices_by_make = {}
    for vehicle in vehicles:
        make = vehicle["make"]
        if make not in prices_by_make:
            prices_by_make[make] = []
        prices_by_make[make].append(vehicle["price"])
    
    avg_prices_by_make = {
        make: sum(prices) / len(prices) 
        for make, prices in prices_by_make.items()
    }
    
    # Count opportunities
    opportunities_count = sum(1 for d in market_data if d["is_opportunity"])
    
    return {
        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "sold_vehicles": sold_vehicles,
        "make_distribution": make_counts,
        "condition_distribution": condition_counts,
        "avg_prices_by_make": avg_prices_by_make,
        "opportunities_count": opportunities_count
    } 