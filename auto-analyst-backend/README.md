---
title: Auto Analyst Backend
emoji: 🦀
colorFrom: green
colorTo: indigo
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

## Attribute-Specific Filtering Enhancements

Auto-Analyst now includes improved attribute-specific filtering capabilities that better handle questions like "how many green vehicles do we have?" with precise counts and visualizations.

### Using Attribute-Specific Querying

The system will now automatically detect and process queries that are asking for counts or details of specific attributes, such as:

- "How many green vehicles do we have?"  
- "Count of Toyota vehicles"
- "Number of vehicles from 2022"
- "Vehicles with condition is Excellent"

### Lightweight Query Tools

For cases where you only need to query attributes without the full AI capabilities:

#### 1. Simple Command-Line Tool (No Dependencies)

Use our lightweight CSV-based query tool that doesn't require NumPy or pandas:

```bash
# Interactive mode
./query_vehicle_attributes.py --interactive

# Ask a specific question
./query_vehicle_attributes.py --query "How many green vehicles do we have?"

# Query by attribute and value
./query_vehicle_attributes.py --attribute color --value green
```

#### 2. API Server

For web-based querying, we've created a lightweight attribute query server:

```bash
# Run the attribute query server on port 8001
./attribute_query_app.py
```

You can test the attribute query server with the included test client:

```bash
# Test a specific query
./test_attribute_api.py --query "How many green vehicles do we have?"

# Test a direct attribute count
./test_attribute_api.py --attribute color green

# Run all tests
./test_attribute_api.py --test-all
```

### Setup and Configuration

For easy setup of all attribute filtering tools, run:

```bash
./setup_attribute_filtering.sh
```

This script will:
1. Make all tools executable
2. Set up the necessary directories
3. Check for the vehicles dataset
4. Verify NumPy compatibility and provide recommendations

### NumPy Compatibility Fix

If you encounter NumPy compatibility issues (common when using NumPy 2.x with libraries expecting NumPy 1.x APIs), you have two options:

1. **Use our compatibility wrapper**:
   ```bash
   # Run the Auto-Analyst backend with NumPy compatibility fixes
   ./run_auto_analyst.py
   ```

2. **Use our lightweight tool** (doesn't require NumPy or pandas):
   ```bash
   # Interactive query tool
   ./query_vehicle_attributes.py --interactive
   ```

See the detailed documentation in `README_ATTRIBUTE_FILTERING.md` for more information.

# Auto-Analyst Backend

The backend server for the Auto-Analyst platform, providing powerful data analysis capabilities.

## Attribute Filtering

The Auto-Analyst backend now supports efficient attribute-based filtering for vehicle data. This feature allows users to quickly get counts and statistics about vehicles with specific attributes.

### Integration Options

#### 1. Chat Integration (Automatic)

The system automatically detects attribute queries in chat messages. For example:
- "How many green vehicles do we have?"
- "Count all Toyota cars"
- "Show me the electric vehicles"

These queries are intercepted and processed efficiently, bypassing the ML pipeline for faster, more accurate results.

#### 2. Direct API Endpoints

For frontend developers who want direct control, two dedicated endpoints are available:

##### A. Attribute Query Detection

Determine if a user's query is about counting vehicles with specific attributes.

```
POST /api/attribute-query
Content-Type: application/json

{
    "query": "How many green vehicles do we have?"
}
```

Response:
```json
{
    "is_attribute_query": true,
    "detected": true,
    "attribute_detected": true,
    "success": true,
    "count": 17,
    "total": 200,
    "percentage": 8.5,
    "attribute_name": "color",
    "attribute_value": "green",
    "message": "Found 17 vehicles (8.5%) with color 'green' out of 200 total vehicles."
}
```

##### B. Direct Count Endpoint

Count vehicles with specific attribute values.

```
POST /api/direct-count
Content-Type: application/json

{
    "attribute_name": "color",
    "attribute_value": "green"
}
```

Response:
```json
{
    "success": true,
    "count": 17,
    "total": 200,
    "percentage": 8.5,
    "attribute_name": "color",
    "attribute_value": "green",
    "message": "Found 17 vehicles (8.5%) with color 'green' out of 200 total vehicles."
}
```

### Supported Attributes

Currently, the system recognizes these attribute types:

1. **Color** - common vehicle colors (black, white, red, blue, green, etc.)
2. **Make/Brand** - vehicle manufacturers (Toyota, Honda, Ford, etc.)
3. **Year** - model years (2020, 2021, 2022, etc.)
4. **Fuel Type** - propulsion methods (electric, gasoline, hybrid, diesel)

### Technical Notes

- **Zero-Dependency Implementation**: The attribute filtering feature uses standard library components and avoids NumPy/pandas dependencies to prevent compatibility issues.
- **Case-Insensitive Matching**: All filtering is case-insensitive for better user experience.
- **Performance**: Direct attribute queries are processed much faster than going through the ML pipeline.

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the server:
   ```
   python app.py
   ```

3. Access the API at `http://localhost:8000`

## Available Endpoints

- `/chat/{agent_name}` - Chat with a specific agent
- `/chat` - Chat with all agents
- `/api/attribute-query` - Attribute query detection
- `/api/direct-count` - Direct vehicle count by attribute
