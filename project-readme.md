# 🚗 Automotive Pricing Intelligence POV Demo

A point-of-view (POV) demonstration application built using Auto-Analyst to showcase how AI can power an interactive, proactive, and intelligent front-end for automotive pricing data.

## 📌 Overview
This application demonstrates how an AI-powered analytics platform can enhance the automotive dealer experience by providing:

- **Intelligent Pricing Recommendations** - AI-driven suggestions for optimal vehicle pricing
- **Market Trend Analysis** - Real-time insights into market shifts and opportunities
- **Interactive Data Exploration** - Conversational interface for exploring vehicle data
- **Proactive Alerts** - Notifications about undervalued vehicles and pricing opportunities
- **Comprehensive Dashboards** - Visualizations for tracking inventory performance
- **Efficient Attribute Filtering** - Fast, accurate counting of vehicles by attributes like color, make, and year

## 🏗️ Architecture

This application is built as an AI-powered presentation layer on top of a data core:

- **Frontend**: Next.js application with custom React components for automotive data visualization
- **Backend**: FastAPI providing AI-enhanced analytics capabilities
- **Synthetic Data**: Mock automotive pricing data simulating a real dealer management system
- **AI Integration**: Conversational interface for natural language data exploration
- **Attribute Filtering**: Zero-dependency system for efficient vehicle attribute queries

## 🖥️ System Components

The Auto-Analyst system consists of the following servers working together:

1. **Frontend Server (Next.js)** - Default port: 3000
   - Serves the React-based user interface
   - Handles user authentication and session management
   - Renders data visualizations using Plotly
   - Supports fallback mode for offline operation

2. **Attribute Proxy Server (Flask)** - Default port: 8080
   - Routes requests between frontend and appropriate backend servers
   - Intelligently directs attribute queries to the standalone attribute server
   - Forwards other requests to the main application server
   - Handles CORS and connection issues transparently
   - Provides fallback responses when backends are unavailable

3. **Standalone Attribute Server (Flask)** - Default port: 8002
   - Provides efficient, zero-dependency attribute filtering
   - Handles vehicle counting by color, make, model, year, etc.
   - Serves mock endpoints for model settings and agents
   - Works without NumPy/pandas to avoid compatibility issues
   - Loads demo vehicle data from CSV files

4. **Main Application Server (FastAPI)** - Default port: 8000
   - Provides LLM-powered chat and analysis features
   - Handles complex data processing and visualization
   - Serves the primary API endpoints for vehicles, market data, opportunities, and statistics
   - Note: May have NumPy compatibility issues in some environments

## 🚀 Get Started

To quickly set up the project locally, follow these steps:

### Prerequisites
- Python 3.11+ (Python 3.12 recommended for latest features)
- Node.js 18+ and npm
- Git

### Clone the Repository
```bash
git clone https://github.com/your-org/auto-analyst.git
cd auto-analyst
```

### Backend Setup
```bash
# Navigate to the backend directory
cd Auto-Analyst/auto-analyst-backend

# Create a Python virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the standalone attribute server (for attribute filtering)
python standalone_attribute_server.py
# Keep this running in a terminal

# In a new terminal, start the attribute proxy
python attribute_proxy.py
# Keep this running in a terminal

# (Optional) Start the main application if your environment supports it
# In a new terminal, with venv activated:
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# In a new terminal, navigate to the frontend directory
cd Auto-Analyst/auto-analyst-frontend

# Install dependencies
npm install

# Start the development server
npm run dev -- -p 3000
```

### Access the Application
Open your browser and navigate to: http://localhost:3000

### Configure Environment (Optional)
Create a `.env` file in the backend directory for custom configurations:
```
MODEL_PROVIDER=gemini
MODEL_NAME=gemini-1.5-pro
TEMPERATURE=0.7
MAX_TOKENS=6000
```

## 📊 Demo Data

The application uses synthetic automotive data to demonstrate functionality:

- **Location**: Demo files are located in `Auto-Analyst/auto-analyst-frontend/public/demo-files/`
- **Files**:
  - `vehicles.csv` - Primary inventory data (make, model, year, price, etc.)
  - `market_data.csv` - Market pricing and competitive data
  - `automotive_analysis.csv` - Analysis results and insights

If these files are not found, the system will fall back to:
- Built-in JSON examples in the `auto-analyst-backend/data/` directory
- Dynamically generated mock responses for core functionality

To upload your own data, use the upload feature in the web interface or place CSV files in the demo-files directory.

## 📊 Current Status

As of May 2025, the system has the following status:

- **Frontend**: Operational (http://localhost:3000)
  - Demo mode fully functional with fallback mechanisms
  - Visualization components are working properly
  - UI updated to handle network errors gracefully
  - Chat interface running with fallback responses
  - CORS bypass implemented for compatibility with attribute server

- **Attribute Proxy**: Operational (http://localhost:8080)
  - Successfully routing requests between frontend and backends
  - Handling attribute queries efficiently
  - Providing mock responses when backends are unavailable
  - Resolving CORS issues transparently

- **Standalone Attribute Server**: Operational (http://localhost:8002)
  - Zero-dependency implementation avoids NumPy compatibility issues
  - Successfully serving attribute filtering endpoints
  - Providing mock model/agent endpoints for UI compatibility
  - Handling direct count and attribute queries

- **Main Application Server**: Limited (http://localhost:8000)
  - May face NumPy compatibility issues in environments with NumPy 2.x
  - LLM features available when operational
  - Vehicle data API responding correctly when running
  - Best used through the proxy server to ensure reliable operation

## 🔄 Recent Updates

### Attribute Filtering System (May 2025)
- Implemented zero-dependency attribute filtering to avoid NumPy compatibility issues
- Added direct API endpoints for efficiently counting vehicles by various attributes
- Created proxy server architecture to handle routing between different backends
- Integrated client-side CORS bypass to ensure seamless frontend operation
- Enhanced chat capabilities to detect and accurately answer attribute queries

### Visualization Engine Improvements (May 2025)
- Fixed Plotly chart rendering issues in the chat interface
- Added error boundaries to prevent crashes due to malformed data
- Enhanced the chart component with better responsiveness
- Implemented better fallback visualization patterns

### NumPy Compatibility Workaround
- Created a standalone attribute server that works without NumPy/pandas dependencies
- Implemented a proxy architecture to route requests appropriately
- Added client-side fixes for handling CORS and connection issues
- Enhanced system resilience when the main backend cannot start

### Error Handling & Resilience
- Implemented comprehensive fallback mechanisms throughout the application
- Enhanced network timeout detection and retries
- Added graceful degradation when services are unavailable
- Improved user feedback during error conditions

## 🛠️ Running the Application

The system now supports multiple setup options to handle environments with NumPy compatibility issues:

### Full System Setup (Recommended)

Start all components for complete functionality:

```bash
# 1. Start the standalone attribute server (handles attribute filtering)
cd auto-analyst-backend
python3 standalone_attribute_server.py

# 2. Start the attribute proxy (routes requests between frontend and backends)
cd auto-analyst-backend
python3 attribute_proxy.py

# 3. Start the frontend
cd auto-analyst-frontend
npm run dev -- -p 3000

# 4. (Optional) Start the main application server if your environment supports it
cd auto-analyst-backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Minimal Setup (For environments with NumPy compatibility issues)

If you face NumPy compatibility errors, you can run with this minimal setup:

```bash
# 1. Start the standalone attribute server
cd auto-analyst-backend
python3 standalone_attribute_server.py

# 2. Start the attribute proxy
cd auto-analyst-backend
python3 attribute_proxy.py

# 3. Start the frontend
cd auto-analyst-frontend
npm run dev -- -p 3000
```

### Automated Setup

Use the provided setup script to automate configuration:

```bash
cd auto-analyst-backend
./setup_attribute_filtering.sh
```

## 🔍 Using Attribute Filtering

The system now provides multiple ways to filter and count vehicles by attributes:

### Through the Chat Interface

Simply ask questions like:
- "How many green vehicles do we have?"
- "Count all Toyota cars in the inventory"
- "Show me the number of electric vehicles"
- "What percentage of our inventory is from 2022?"

### Through Direct API Endpoints

For programmatic access, use these endpoints:

- `GET /api/direct-count?attribute=color&value=green`
- `POST /api/attribute-query` with JSON body: `{"query": "how many toyota vehicles?"}`

## 🔧 Troubleshooting

### NumPy Compatibility Issues

If you see errors like:
```
A module that was compiled using NumPy 1.x cannot be run in
NumPy 2.2.2 as it may crash.
```

Use the standalone attribute server and proxy setup described above. This configuration provides attribute filtering functionality without NumPy dependencies.

### Connection Refused Errors

If the frontend shows connection refused errors:
1. Ensure the attribute proxy is running on port 8080
2. Verify the standalone attribute server is running on port 8002
3. Check that frontend API URLs are pointing to port 8080 (the proxy)

### CORS Issues

If you see CORS errors in the browser console:
1. Ensure the frontend is properly loading the CORS bypass script
2. Verify the attribute proxy has appropriate CORS headers enabled
3. Try clearing browser cache and reloading the application

## 📚 Resources

- [Auto-Analyst Documentation](https://github.com/your-org/auto-analyst/docs)
- [Implementation Guide](./docs/implementation-guide.md)
- [Data Schema](./docs/data-schema.md)
- [API Documentation](./docs/api-docs.md)
- [NumPy Compatibility Fix](./auto-analyst-backend/NUMPY_COMPATIBILITY_FIX.md) 