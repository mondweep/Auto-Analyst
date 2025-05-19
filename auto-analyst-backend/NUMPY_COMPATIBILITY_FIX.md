# NumPy Compatibility Fix for Auto-Analyst

## Problem

The Auto-Analyst backend depends on several libraries that were compiled against NumPy 1.x, but your environment has NumPy 2.2.2 installed. This causes errors like:

```
A module that was compiled using NumPy 1.x cannot be run in
NumPy 2.2.2 as it may crash. To support both 1.x and 2.x
versions of NumPy, modules must be compiled with NumPy 2.0.
```

The primary affected dependencies include:
- pandas
- pyarrow
- bottleneck
- numexpr

## Solution Approach

We've implemented a three-part solution to address this issue:

### 1. Standalone Attribute Server

We created a standalone server (`standalone_attribute_server.py`) that:
- Has **zero NumPy/pandas dependencies**
- Provides the same attribute filtering API
- Uses only standard library components
- Handles all attribute-specific queries efficiently

This server implements:
- `/api/attribute-query` - For detecting attribute queries in natural language
- `/api/direct-count` - For directly counting by attribute name/value
- `/api/chat-attribute` - For chat integration of attribute queries

### 2. Attribute Proxy

We created an attribute proxy (`attribute_proxy.py`) that:
- Acts as a bridge between your frontend and backend servers
- Automatically routes requests to the appropriate server
- Provides seamless integration with both implementations
- Gracefully handles failover between servers

The proxy provides:
- `/chat` and `/chat/{agent_name}` - Forwards chat requests
- `/api/attribute-query` - Forwards attribute queries
- `/api/direct-count` - Forwards direct count requests
- All other endpoints - Forwards to the main app if available

### 3. Setup Script

The setup script (`setup_attribute_filtering.sh`) configures your environment:
- Creates necessary directories
- Makes all scripts executable
- Checks for NumPy compatibility issues
- Provides usage instructions

## How to Use

### Option 1: Run Only the Attribute Server (Simplest)

```bash
# Start the standalone attribute server
./standalone_attribute_server.py
```

This allows your frontend to directly query:
- `http://localhost:8002/api/attribute-query`
- `http://localhost:8002/api/direct-count`
- `http://localhost:8002/api/chat-attribute`

### Option 2: Use the Proxy for Seamless Integration

```bash
# Start the standalone attribute server
./standalone_attribute_server.py

# In another terminal, start the proxy
./attribute_proxy.py
```

Configure your frontend to use the proxy at `http://localhost:8080`, which will:
1. Route attribute queries to the standalone server
2. Route all other requests to the main app (if running)
3. Provide consistent API endpoints regardless of backend

### Option 3: Fix NumPy Dependency Issues (Advanced)

If you need to use the full Auto-Analyst backend with all features, you have two options:

1. Downgrade NumPy to 1.x:
   ```bash
   pip install numpy==1.26.4  # or any 1.x version
   ```

2. Create a separate virtual environment specifically for Auto-Analyst:
   ```bash
   python -m venv auto_analyst_env
   source auto_analyst_env/bin/activate
   pip install numpy==1.26.4
   pip install -r requirements.txt
   ```

## Technical Implementation Details

### Attribute Detection

We use regular expressions to detect attribute queries:
- "How many green vehicles do we have?"
- "Count all Toyota cars"
- "Number of vehicles from 2022"
- "Show me the electric vehicles"

### Filtering Implementation

Our zero-dependency filtering:
- Uses CSV module instead of pandas
- Implements case-insensitive matching
- Handles NULL/empty values properly
- Maintains the same API format as the original

### Proxy Server

Our proxy server:
- Health-checks both servers before routing
- Routes attribute queries to standalone server when possible
- Forwards other requests to the main app
- Provides fallback behavior when one server is unavailable

## Conclusion

This implementation allows your frontend to work seamlessly regardless of the NumPy compatibility issues. The standalone server provides fast, accurate attribute filtering without dependencies, while the proxy ensures consistent API access. 