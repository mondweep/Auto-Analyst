#!/usr/bin/env python
import os
import json
import http.server
import socketserver
from urllib.parse import urlparse, unquote
import random
from datetime import datetime, timedelta

PORT = 8003

# Create sample data
def generate_vehicles(count=50):
    makes = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Chevrolet", "Nissan", "Kia", "Hyundai"]
    models = {
        "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
        "Ford": ["F-150", "Escape", "Explorer", "Mustang", "Edge"],
        "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series"],
        "Mercedes": ["C-Class", "E-Class", "GLC", "GLE", "S-Class"],
        "Audi": ["A4", "A6", "Q5", "Q7", "A8"],
        "Chevrolet": ["Silverado", "Equinox", "Tahoe", "Malibu", "Traverse"],
        "Nissan": ["Altima", "Rogue", "Pathfinder", "Murano", "Sentra"],
        "Kia": ["Sorento", "Sportage", "Telluride", "Forte", "Soul"],
        "Hyundai": ["Santa Fe", "Tucson", "Elantra", "Palisade", "Sonata"]
    }
    colors = ["Black", "White", "Silver", "Red", "Blue", "Gray", "Green"]
    conditions = ["Excellent", "Good", "Fair", "Poor"]
    fuel_types = ["Gasoline", "Diesel", "Hybrid", "Electric"]
    
    vehicles = []
    for i in range(1, count + 1):
        make = random.choice(makes)
        model = random.choice(models[make])
        year = random.randint(2015, 2023)
        price = random.randint(15000, 60000)
        mileage = random.randint(1000, 100000)
        
        # List date between 1-120 days ago
        days_ago = random.randint(1, 120)
        list_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        vehicles.append({
            "id": i,
            "make": make,
            "model": model,
            "year": year,
            "color": random.choice(colors),
            "price": price,
            "mileage": mileage,
            "condition": random.choice(conditions),
            "fuel_type": random.choice(fuel_types),
            "list_date": list_date,
            "days_in_inventory": days_ago,
            "vin": f"VIN{i}ABC{random.randint(10000, 99999)}",
            "is_sold": random.random() < 0.2  # 20% chance of being sold
        })
    
    return vehicles

def generate_market_data(vehicles):
    market_data = []
    
    for vehicle in vehicles:
        # Market price is between 90% and 110% of the actual price
        market_price = int(vehicle["price"] * random.uniform(0.9, 1.1))
        
        # Calculate price difference
        price_diff = vehicle["price"] - market_price
        price_diff_percent = (price_diff / market_price) * 100
        
        market_data.append({
            "id": vehicle["id"],
            "make": vehicle["make"],
            "model": vehicle["model"],
            "year": vehicle["year"],
            "your_price": vehicle["price"],
            "market_price": market_price,
            "price_difference": price_diff,
            "price_difference_percent": round(price_diff_percent, 2),
            "days_in_inventory": vehicle["days_in_inventory"]
        })
    
    return market_data

def generate_opportunities(market_data):
    # Filter to vehicles priced at least 3% below market
    opportunities = [item for item in market_data if item["price_difference_percent"] <= -3]
    
    # Sort by largest negative percent difference (best deals first)
    opportunities.sort(key=lambda x: x["price_difference_percent"])
    
    # Add potential profit
    for opp in opportunities:
        opp["potential_profit"] = abs(opp["price_difference"])
    
    return opportunities

def generate_statistics(vehicles):
    # Count by make
    makes = {}
    for v in vehicles:
        make = v["make"]
        if make in makes:
            makes[make] += 1
        else:
            makes[make] = 1
    
    make_stats = [{"name": make, "value": count} for make, count in makes.items()]
    
    # Count by condition
    conditions = {}
    for v in vehicles:
        condition = v["condition"]
        if condition in conditions:
            conditions[condition] += 1
        else:
            conditions[condition] = 1
    
    condition_stats = [{"name": cond, "value": count} for cond, count in conditions.items()]
    
    # Price ranges
    price_ranges = {
        "under_20k": 0,
        "20k_to_30k": 0,
        "30k_to_40k": 0,
        "40k_to_50k": 0,
        "over_50k": 0
    }
    
    for v in vehicles:
        price = v["price"]
        if price < 20000:
            price_ranges["under_20k"] += 1
        elif price < 30000:
            price_ranges["20k_to_30k"] += 1
        elif price < 40000:
            price_ranges["30k_to_40k"] += 1
        elif price < 50000:
            price_ranges["40k_to_50k"] += 1
        else:
            price_ranges["over_50k"] += 1
    
    price_stats = [
        {"name": "Under $20K", "value": price_ranges["under_20k"]},
        {"name": "$20K - $30K", "value": price_ranges["20k_to_30k"]},
        {"name": "$30K - $40K", "value": price_ranges["30k_to_40k"]},
        {"name": "$40K - $50K", "value": price_ranges["40k_to_50k"]},
        {"name": "Over $50K", "value": price_ranges["over_50k"]}
    ]
    
    # Inventory age
    age_ranges = {
        "new_30_days": 0,
        "30_to_60_days": 0,
        "60_to_90_days": 0,
        "over_90_days": 0
    }
    
    for v in vehicles:
        days = v["days_in_inventory"]
        if days <= 30:
            age_ranges["new_30_days"] += 1
        elif days <= 60:
            age_ranges["30_to_60_days"] += 1
        elif days <= 90:
            age_ranges["60_to_90_days"] += 1
        else:
            age_ranges["over_90_days"] += 1
    
    age_stats = [
        {"name": "0-30 Days", "value": age_ranges["new_30_days"]},
        {"name": "31-60 Days", "value": age_ranges["30_to_60_days"]},
        {"name": "61-90 Days", "value": age_ranges["60_to_90_days"]},
        {"name": "90+ Days", "value": age_ranges["over_90_days"]}
    ]
    
    # Calculate summary statistics
    total_vehicles = len(vehicles)
    sold_vehicles = sum(1 for v in vehicles if v["is_sold"])
    available_vehicles = total_vehicles - sold_vehicles
    avg_price = sum(v["price"] for v in vehicles) / total_vehicles if total_vehicles > 0 else 0
    avg_days = sum(v["days_in_inventory"] for v in vehicles) / total_vehicles if total_vehicles > 0 else 0
    
    return {
        "makes": make_stats,
        "conditions": condition_stats,
        "price_ranges": price_stats,
        "inventory_age": age_stats,
        "summary": {
            "total_vehicles": total_vehicles,
            "available_vehicles": available_vehicles,
            "sold_vehicles": sold_vehicles,
            "average_price": int(avg_price),
            "average_days_in_inventory": int(avg_days)
        }
    }

class AutomotiveHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.vehicles = generate_vehicles(50)
        self.market_data = generate_market_data(self.vehicles)
        self.opportunities = generate_opportunities(self.market_data)
        self.statistics = generate_statistics(self.vehicles)
        super().__init__(*args, **kwargs)
    
    def _set_response(self, status_code=200, content_type='application/json'):
        """Set response headers correctly"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)
        
        # Handle API endpoints
        if path == '/api/vehicles':
            self._set_response()
            self.wfile.write(json.dumps({'vehicles': self.vehicles}).encode())
            return
        
        elif path == '/api/market-data':
            self._set_response()
            self.wfile.write(json.dumps({'market_data': self.market_data}).encode())
            return
        
        elif path == '/api/opportunities':
            self._set_response()
            self.wfile.write(json.dumps({'opportunities': self.opportunities}).encode())
            return
        
        elif path == '/api/statistics':
            self._set_response()
            self.wfile.write(json.dumps({'statistics': self.statistics}).encode())
            return
        
        elif path == '/health':
            self._set_response()
            self.wfile.write(json.dumps({
                'status': 'ok', 
                'message': 'Automotive API is running'
            }).encode())
            return
        
        elif path == '/':
            self._set_response()
            endpoints = [
                "/api/vehicles", 
                "/api/market-data", 
                "/api/opportunities", 
                "/api/statistics",
                "/health"
            ]
            self.wfile.write(json.dumps({
                "message": "Automotive API Server",
                "endpoints": endpoints
            }).encode())
            return
        
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
            return
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self._set_response()
        self.wfile.write(b'{}')


if __name__ == "__main__":
    Handler = AutomotiveHandler
    
    print(f"Starting Automotive API server on port {PORT}...")
    print(f"Available endpoints:")
    print(f"  - /api/vehicles")
    print(f"  - /api/market-data")
    print(f"  - /api/opportunities")
    print(f"  - /api/statistics")
    print(f"  - /health")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user")
            httpd.server_close() 