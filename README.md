# Auto-Analyst

A data analysis and visualization platform with a focus on automotive data.

## Current Status

The application is currently functioning with the following servers:
- Frontend server (Next.js) on port 3000
- File server (Python) on port 8001
- Automotive server (Python) on port 8003

Several issues have been identified and fixed:
1. TypeScript error in the PlotlyMessage interface - fixed by correcting the "as const" syntax
2. Visualization rendering issues in the PlotlyChart component - enhanced with better error handling and loading states
3. File upload issues - fixed by properly implementing the UPLOAD_API_URL and improving error handling
4. CSV parsing in file_server.py - enhanced with better data type detection and quote handling

## Architecture

The Auto-Analyst consists of three main components:

1. **Frontend (Next.js)**: 
   - A modern React application built with Next.js
   - Uses TypeScript for type safety
   - Implements Plotly.js for data visualization
   - Located in `auto-analyst-frontend/`

2. **File Server (Python)**:
   - A simple HTTP server for file uploads and processing
   - Handles CSV parsing and data extraction
   - Serves demo files for development
   - Located in `auto-analyst-backend/file_server.py`

3. **Automotive API (Python)**:
   - Provides automotive data-specific endpoints
   - Includes vehicles, market data, opportunities, and statistics
   - Located in `auto-analyst-backend/automotive_server.py`

## Running the Application

To run the application locally:

1. Start the file server:
   ```bash
   cd auto-analyst-backend
   python file_server.py
   ```

2. Start the automotive server:
   ```bash
   cd auto-analyst-backend
   python automotive_server.py
   ```

3. Start the frontend:
   ```bash
   cd auto-analyst-frontend
   npm run dev
   ```

## Features

- Interactive data visualization with Plotly
- CSV file upload and processing
- Automotive data analysis
- Chat interface for data queries
- Demo mode with fallback responses

## Recent Improvements

1. Enhanced error handling in the PlotlyChart component
2. Improved CSV parsing with quoted value support
3. Better handling of file uploads with proper error messages
4. Fixed TypeScript issues in the frontend
5. Improved column type detection in CSV files
6. Added detailed data visualizations for automotive data

## Demo Mode

The application includes a demo mode that provides fallback responses and visualizations when backend services are unavailable. This ensures the application remains functional for demonstration purposes even without a running backend.

## 🚗 Auto-Analyst Automotive Pricing Intelligence Demo

A powerful AI-driven analytics platform designed to help automotive dealers optimize inventory pricing and identify market opportunities.

## 📋 Overview

This demo showcases how advanced AI and data analytics can transform automotive dealership operations by providing:

- Real-time market pricing intelligence
- Inventory optimization recommendations
- Profit opportunity identification
- Data-driven insights through interactive dashboards

## 🛠️ Architecture

The application consists of three main components:

1. **Frontend** (Next.js/React)
   - Interactive automotive dashboards
   - File upload/download capabilities
   - Responsive UI for all devices

2. **Automotive API** (Python HTTP Server)
   - Provides vehicle data, market analysis, and pricing recommendations
   - Runs on port 8003

3. **File Server** (Python HTTP Server)
   - Serves downloadable data files (CSV exports)
   - Runs on port 8001

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
# Navigate to the backend directory
cd auto-analyst-backend

# Install Python dependencies
pip install -r requirements.txt

# Start all services with the convenience script
./start_services.sh
```

This will start:
- File server on port 8001
- Automotive API on port 8003

### Frontend Setup

```bash
# In a separate terminal, navigate to the frontend directory
cd auto-analyst-frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be accessible at http://localhost:3000

## 📊 Available Endpoints

### Automotive API (Port 8003)

- `/api/vehicles` - Vehicle inventory data
- `/api/market-data` - Market pricing analysis
- `/api/opportunities` - Profit opportunities
- `/api/statistics` - Inventory and performance metrics
- `/health` - API health check

### File Server (Port 8001)

- `/exports/vehicles.csv` - Vehicle inventory export
- `/exports/market_data.csv` - Market data export
- `/exports/automotive_analysis.csv` - Combined analysis export
- `/health` - Server health check

## 🧪 Testing

The system includes comprehensive tests to ensure all functionality works as expected:

```bash
# Run backend unit tests for automotive features
cd auto-analyst-backend
python test_automotive.py

# Run backend end-to-end tests
python test_e2e.py

# Run frontend test to verify connectivity
cd ../auto-analyst-frontend
node test-frontend.js
```

## 🔍 Key Features

### 1. Vehicle Inventory Management

View complete inventory with detailed information about each vehicle including:
- Make, model, year, condition
- Current pricing
- Days in inventory
- Full specifications

### 2. Market Analysis

Compare your inventory against market prices:
- Price differentials
- Market positioning
- Competitive analysis

### 3. Profit Opportunities

Identify vehicles that are:
- Underpriced compared to market
- Likely to appreciate
- Opportunities for acquisition

### 4. Performance Metrics

Track key performance indicators:
- Inventory aging
- Price distribution
- Make/model popularity

## 📑 Documentation

For more detailed documentation, see:
- [Implementation Guide](./docs/implementation-guide.md)
- [Data Schema](./docs/data-schema.md)
- [API Documentation](./docs/api-docs.md)

## 🔧 Troubleshooting

### Common Issues

- **404 Errors**: Ensure both the file server and automotive server are running
- **CORS Issues**: Check that both servers are configured with the correct CORS headers
- **Download Failures**: Verify the exports directory contains the CSV files

To restart all services:
```bash
cd auto-analyst-backend
./start_services.sh
```

## 🤝 Contributing

Contributions are welcome! Please follow the existing code style and add tests for new features.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 