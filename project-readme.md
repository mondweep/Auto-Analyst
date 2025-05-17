# 🚗 Automotive Pricing Intelligence POV Demo

A point-of-view (POV) demonstration application built using Auto-Analyst to showcase how AI can power an interactive, proactive, and intelligent front-end for automotive pricing data.

## 📌 Overview
This application demonstrates how an AI-powered analytics platform can enhance the automotive dealer experience by providing:

- **Intelligent Pricing Recommendations** - AI-driven suggestions for optimal vehicle pricing
- **Market Trend Analysis** - Real-time insights into market shifts and opportunities
- **Interactive Data Exploration** - Conversational interface for exploring vehicle data
- **Proactive Alerts** - Notifications about undervalued vehicles and pricing opportunities
- **Comprehensive Dashboards** - Visualizations for tracking inventory performance

## 🏗️ Architecture

This application is built as an AI-powered presentation layer on top of a data core:

- **Frontend**: Next.js application with custom React components for automotive data visualization
- **Backend**: FastAPI providing AI-enhanced analytics capabilities
- **Synthetic Data**: Mock automotive pricing data simulating a real dealer management system
- **AI Integration**: Conversational interface for natural language data exploration

## 🖥️ System Components

The Auto-Analyst system consists of three servers working together:

1. **Frontend Server (Next.js)** - Default port: 3000
   - Serves the React-based user interface
   - Handles user authentication and session management
   - Renders data visualizations using Plotly
   - Supports fallback mode for offline operation

2. **File Server (Python)** - Default port: 8001
   - Manages CSV file uploads and processing
   - Serves the default dataset and historical data
   - Provides RESTful endpoints for file operations
   - Includes fallback data generation for testing

3. **Automotive Server (Python)** - Default port: 8003
   - Provides automotive-specific data analysis
   - Serves endpoints for vehicles, market data, and opportunities
   - Generates statistics and insights from automotive data
   - Supports the domain-specific analytics features

## 📊 Current Status

As of May 2025, the system has the following status:

- **Frontend**: Operational (http://localhost:3000)
  - Demo mode fully functional with fallback mechanisms
  - Visualization components are working properly
  - UI updated to handle network errors gracefully
  - Chat interface running with fallback responses

- **File Server**: Operational (http://localhost:8001)
  - API endpoints enhanced for reliability
  - Serving default datasets successfully
  - File upload/download functionality working
  - Improved error handling and fallback data

- **Automotive Server**: Operational (http://localhost:8003)
  - Vehicle data API responding correctly
  - Market data endpoints functional
  - Opportunities and statistics APIs available
  - Test data generation working properly

- **Feature Tests**: 
  - All tests passing (100% success rate)
  - Robust fallback mode when services are unavailable
  - Improved timeout and retry handling
  - Comprehensive test coverage for all components

## 🛠️ Key Features

### Buying Radar Dashboard
- List of undervalued vehicles to acquire with profit potential
- Market comparison and automated pricing intelligence
- Filtering by vehicle type, age, condition, and profit margin

### Daily Digest Feed
- Daily summary of pricing changes and market shifts
- Urgent action items for inventory optimization
- Performance metrics for current inventory

### Conversational Search Agent
- Natural language queries like "Which SUVs under £10k are likely to appreciate?"
- AI-powered recommendations for price adjustments
- Market trend analysis through conversational interface

### Competitive Advantage Over Traditional BI
| Feature | Traditional BI (Spark) | This POV Demo |
|---------|------------------------|---------------|
| Static Reports | ✅ | ✅ |
| Real-time Chat with AI | ❌ | ✅ |
| Proactive Daily Insights | ❌ | ✅ |
| Custom ML/AI Recommendations | ❌ | ✅ |
| Extensible React UI | ❌ | ✅ |

## 📊 Synthetic Data Components

This demo uses synthetic data to simulate:

1. **Vehicle Inventory** - Current stock with details on make, model, year, mileage, etc.
2. **Market Pricing Data** - Competitor pricing and market trends
3. **Historical Sales** - Past transaction data for price optimization
4. **Profit Margins** - Estimated profit potential for different vehicles
5. **Market Demand Indicators** - Search frequency, time on lot, seasonal trends

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- OpenAI API key (or other LLM provider)

### Installation
```bash
# Clone this repository
git clone https://github.com/your-org/automotive-pricing-demo.git

# Install frontend dependencies
cd automotive-pricing-demo/auto-analyst-frontend
npm install

# Install backend dependencies
cd ../auto-analyst-backend
pip install -r requirements.txt

# Set up environment variables
cp .env-template .env
# Edit .env with your API keys and configuration
```

### Running the Application

You need to start all three servers for full functionality:

```bash
# Start the file server (in one terminal)
cd auto-analyst-backend
python file_server.py

# Start the automotive server (in another terminal)
cd auto-analyst-backend
python automotive_server.py

# Start the frontend (in a third terminal)
cd auto-analyst-frontend
npm run dev
```

Visit `http://localhost:3000` to access the application.

### Fallback Mechanisms

The system includes robust fallback mechanisms:

- The frontend operates in demo mode when backends are unavailable
- The file server provides default synthetic data when files don't exist
- All components have retry/timeout handling for network issues
- Tests can run in fallback mode to verify component functionality
- Visualization components work offline with local data processing

### Running Tests

```bash
# Test the full system
cd auto-analyst-frontend
node tests/feature-tests.js
```

## 📑 Implementation Plan

1. **Data Modeling** - Design schemas for automotive data
2. **Synthetic Data Generation** - Create realistic mock data
3. **Backend API Enhancement** - Add automotive-specific endpoints
4. **Frontend Dashboard Development** - Build specialized UI for dealers
5. **AI Query Agent Customization** - Train for automotive domain knowledge
6. **Daily Digest Implementation** - Create scheduled insights

## 🔗 Demo Scenarios

### Scenario 1: Market-Based Pricing
Demonstrate how the AI can analyze market data to suggest optimal pricing for new inventory items.

### Scenario 2: Inventory Optimization
Show how the system identifies underperforming vehicles and recommends price adjustments.

### Scenario 3: Opportunity Detection
Highlight how the AI identifies vehicles in the market that are undervalued and represent buying opportunities.

### Scenario 4: Conversational Analytics
Demonstrate natural language queries about inventory performance and market trends.

## 📚 Resources

- [Auto-Analyst Documentation](https://github.com/your-org/auto-analyst/docs)
- [Implementation Guide](./docs/implementation-guide.md)
- [Data Schema](./docs/data-schema.md)
- [API Documentation](./docs/api-docs.md) 