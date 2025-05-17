#!/usr/bin/env python

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.automotive_routes import router as automotive_router
from src.routes.file_routes import router as file_router
from src.routes.file_download_routes import router as download_router

# Create a FastAPI app
app = FastAPI(title="Automotive and File API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the automotive router
app.include_router(automotive_router)

# Include the file router
app.include_router(file_router)

# Include the file download router
app.include_router(download_router)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "message": "API is healthy and running"}

# Root endpoint
@app.get("/")
async def index():
    return {
        "title": "Data Analytics API",
        "message": "Explore our API for automotive inventory and market analysis.",
        "endpoints": [
            "/api/vehicles",
            "/api/vehicles/{vehicle_id}",
            "/api/market-data",
            "/api/market-data/{vehicle_id}",
            "/api/opportunities",
            "/api/statistics",
            "/api/files/upload",
            "/exports/{file_name}"
        ]
    }

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Check if data files exist
    vehicles_file = os.path.join(data_dir, "vehicles.json")
    market_data_file = os.path.join(data_dir, "market_data.json")
    
    if not os.path.exists(vehicles_file) or not os.path.exists(market_data_file):
        print("Data files not found. Running data generator script...")
        try:
            from scripts.generate_automotive_data import main as generate_data
            generate_data()
            print("Data generated successfully!")
        except Exception as e:
            print(f"Error generating data: {e}")
            print("Please run the script manually: python scripts/generate_automotive_data.py")
    
    # Create exports directory if it doesn't exist
    exports_dir = os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(exports_dir, exist_ok=True)
    
    # Generate export files if they don't exist
    export_files = [
        os.path.join(exports_dir, "vehicles.csv"),
        os.path.join(exports_dir, "market_data.csv"),
        os.path.join(exports_dir, "automotive_analysis.csv")
    ]
    
    if not all(os.path.exists(f) for f in export_files):
        print("Export files not found. Running export script...")
        try:
            from scripts.export_data_for_download import main as export_data
            export_data()
            print("Data exported successfully!")
        except Exception as e:
            print(f"Error exporting data: {e}")
            print("Please run the script manually: python scripts/export_data_for_download.py")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Start the server
    print("Starting API server...")
    uvicorn.run(app, host="0.0.0.0", port=8002) 