# Auto-Analyst Backend Architecture

The **Auto-Analyst** backend consists of multiple server components working together to provide data analysis, attribute filtering, and AI-powered insights. The system is designed for resilience, with fallback mechanisms to ensure operation even when some components are unavailable.

## System Components

The Auto-Analyst backend is comprised of the following servers:

1. **Attribute Proxy Server (Port 8080)** - Routes requests between frontend and appropriate backend servers
2. **Standalone Attribute Server (Port 8002)** - Provides efficient, zero-dependency attribute filtering
3. **Main Application Server (Port 8000)** - Delivers LLM-powered analysis and complex data processing (optional)

## Server Details

### **1. Attribute Proxy Server**

The Attribute Proxy server intelligently routes requests and provides fallback mechanisms:

- **Core Functionality**
  - Routes attribute queries to the Standalone Attribute Server
  - Forwards other requests to the Main Application Server
  - Handles CORS and connection issues transparently
  - Provides fallback responses when backends are unavailable

- **Primary Endpoints**
  - `/health`: Health check endpoint
  - `/chat`: Chat proxy (tries attribute server first)
  - `/api/attribute-query`: Attribute query proxy
  - `/api/direct-count`: Direct count proxy
  - `/*`: Proxy for all other endpoints

### **2. Standalone Attribute Server**

The Standalone Attribute Server processes attribute queries without heavy dependencies:

- **Core Functionality**
  - Provides zero-dependency attribute filtering
  - Handles vehicle counting by various attributes (color, make, model, year, etc.)
  - Serves mock endpoints for model settings and agents
  - Works without NumPy/pandas to avoid compatibility issues

- **Primary Endpoints**
  - `/health`: Health check endpoint
  - `/api/attribute-query`: Detects and processes attribute queries
  - `/api/direct-count`: Direct counting by attribute name and value
  - `/api/chat-attribute`: Chat integration for attribute queries
  - `/model`: Get available models
  - `/model-settings`: Get model settings
  - `/agents`: Get available agents
  - `/api/session-info`: Get session info

### **3. Main Application Server**

The Main Application Server provides advanced AI capabilities (optional component):

- **Core Functionality**
  - Provides LLM-powered chat and analysis features
  - Handles complex data processing and visualization
  - Serves the primary API endpoints for vehicles, market data, opportunities, and statistics
  - Note: May have NumPy compatibility issues in some environments

- **Primary Endpoints**
  - `/api/vehicles`: Vehicle inventory data
  - `/api/market-data`: Market analysis data
  - `/api/opportunities`: Market opportunities
  - `/api/statistics`: Statistical analysis
  - `/health`: Health check endpoint

## API Categories

The Auto-Analyst API functionality is categorized into three main sections:

1. **Core Application Routes** – Handles data management, session control, and model configurations.
2. **Chat & AI Analysis Routes** – Provides AI-driven data insights and supports interaction with multiple specialized AI agents.
3. **Attribute Filtering Routes** – Efficient filtering and counting of vehicles by various attributes.

---

### **1. Core Application Routes**

These routes handle **data management, session handling, and model settings**.

- **Data Management**
  - `GET /api/vehicles`: Retrieves vehicle inventory data.
  - `GET /api/market-data`: Retrieves market analysis data.
  - `GET /api/opportunities`: Retrieves market opportunities.
  - `GET /api/statistics`: Retrieves statistical analysis.

- **Model Settings**
  - `GET /api/model-settings`: Retrieves the current AI model settings.
  - `GET /model-settings`: Alternative endpoint for model settings.
  - `POST /settings/model`: Updates model configurations, including provider, temperature, and token limits.

- **Session Management**
  - `GET /api/session-info`: Retrieves session information.
  - Sessions track user interactions, datasets, and configurations.

---

### **2. Chat & AI Analysis Routes**

These routes provide **AI-powered insights and query handling** using specialized agents.

- **AI Analysis**
  - `POST /chat/{agent_name}`: Processes a query using a specified AI agent.
  - `POST /chat`: Executes a query across multiple AI agents and streams responses.
  - `POST /api/chat-attribute`: Chat integration for attribute queries.

- **Available AI Agents**
  - `GET /agents`: Retrieves available agents.
  - `GET /agents/{agent_id}`: Retrieves specific agent details.

- **Agent Integration Flow**
  - Queries are dispatched based on intent.
  - Attribute queries are handled by the Standalone Attribute Server.
  - Complex analysis queries are forwarded to the Main Application Server.
  - Responses are formatted in Markdown and streamed.

---

### **3. Attribute Filtering Routes**

These routes handle **efficient filtering and counting of vehicles by attributes**.

- **Attribute Queries**
  - `POST /api/attribute-query`: Processes natural language attribute queries.
  - `POST /api/direct-count`: Counts vehicles directly by attribute name and value.

- **Example Queries**
  - "How many red Toyota Camrys do we have?"
  - "Count vehicles with less than 30,000 miles"
  - "Show me all Ford F-150s from 2020"

- **Implementation**
  - Zero-dependency implementation avoids NumPy compatibility issues.
  - Efficient filtering with optimized algorithms.
  - Direct integration with chat interface for natural language queries.

## Error Handling and Resilience

The system implements comprehensive error handling and resilience mechanisms:

1. **Attribute Proxy**
   - Routes requests intelligently based on availability
   - Provides mock responses when backends are unavailable
   - Handles CORS issues transparently

2. **Standalone Attribute Server**
   - Zero-dependency implementation to avoid compatibility issues
   - Simple CSV parsing without NumPy/pandas dependencies
   - Mock endpoints for UI compatibility

3. **Main Application Server**
   - Try-except blocks for robust operation
   - Standardized error responses
   - Logging for system monitoring
