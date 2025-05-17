# Automotive Pricing API Documentation

This document outlines the API endpoints available in the Automotive Pricing POV demo.

## Base URL

All API endpoints are relative to the base URL: `http://localhost:8000/api`

## Authentication

API endpoints are secured using the same authentication as the original Auto-Analyst application. Admin endpoints require an admin API key.

## Endpoints

### Vehicle Inventory

#### List Vehicles

```
GET /vehicles
```

Returns a list of vehicles with support for filtering, sorting, and pagination.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| page | integer | Page number (default: 1) |
| limit | integer | Items per page (default: 20, max: 100) |
| sort | string | Sort field (e.g., 'price', 'days_on_lot') |
| order | string | Sort order ('asc' or 'desc') |
| make | string | Filter by make |
| model | string | Filter by model |
| min_year | integer | Minimum year |
| max_year | integer | Maximum year |
| body_type | string | Filter by body type |
| status | string | Filter by status |
| min_price | number | Minimum price |
| max_price | number | Maximum price |

**Response:**

```json
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "vehicle_id": "12345",
      "make": "Audi",
      "model": "A4",
      "year": 2019,
      "trim": "Sport",
      "body_type": "Sedan",
      "mileage": 25000,
      "color_exterior": "Black",
      "current_price": 24995.00,
      "days_on_lot": 30,
      "status": "In Stock"
    },
    // More vehicles...
  ]
}
```

#### Get Vehicle Details

```
GET /vehicles/{vehicle_id}
```

Returns detailed information about a specific vehicle.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| vehicle_id | string | Vehicle ID |

**Response:**

```json
{
  "vehicle_id": "12345",
  "make": "Audi",
  "model": "A4",
  "year": 2019,
  "trim": "Sport",
  "body_type": "Sedan",
  "fuel_type": "Petrol",
  "transmission": "Automatic",
  "engine_size": 2.0,
  "mileage": 25000,
  "color_exterior": "Black",
  "color_interior": "Grey",
  "condition": "Excellent",
  "features": ["Leather Seats", "Navigation", "Sunroof"],
  "acquisition_date": "2023-06-15",
  "acquisition_price": 21500.00,
  "current_price": 24995.00,
  "recommended_price": 25200.00,
  "days_on_lot": 30,
  "images": ["https://example.com/vehicles/12345-1.jpg"],
  "vin": "WAUZZZ8K1JA123456",
  "status": "In Stock",
  "location": "North Showroom"
}
```

### Market Data

#### Get Market Trends

```
GET /market-data
```

Returns market trends for vehicle types with various filtering options.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| make | string | Filter by make |
| model | string | Filter by model |
| year_min | integer | Minimum year |
| year_max | integer | Maximum year |
| region | string | Filter by region |

**Response:**

```json
{
  "data": [
    {
      "vehicle_type": "2019 Audi A4 Sport",
      "average_market_price": 25500.00,
      "lowest_market_price": 23200.00,
      "highest_market_price": 27800.00,
      "price_trend_30d": 2.5,
      "average_days_to_sell": 45,
      "demand_index": 75.2,
      "competitor_count": 8,
      "region": "London",
      "timestamp": "2023-09-15 10:30:45",
      "seasonal_adjustment": 1.05
    },
    // More market data...
  ]
}
```

### Price Recommendations

#### Get Recommendations

```
GET /recommendations
```

Returns price recommendations for vehicles in inventory.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| vehicle_id | string | Filter by vehicle ID |
| min_confidence | number | Minimum confidence score (0-1) |
| action | string | Filter by recommended action ("increase", "decrease", "maintain") |

**Response:**

```json
{
  "data": [
    {
      "recommendation_id": "rec123",
      "vehicle_id": "12345",
      "current_price": 24995.00,
      "recommended_price": 25500.00,
      "price_change": 505.00,
      "confidence_score": 0.87,
      "reasoning": [
        "Market pricing is trending upward",
        "Low local competition",
        "High demand for this model"
      ],
      "expected_days_to_sell": 25,
      "expected_profit": 3500.00,
      "competitive_position": "Underpriced",
      "timestamp": "2023-09-15 10:30:45",
      "expiration": "2023-09-22 10:30:45"
    },
    // More recommendations...
  ]
}
```

### Market Opportunities

#### Get Opportunities

```
GET /opportunities
```

Returns market opportunities for acquiring new vehicles.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| min_profit | number | Minimum potential profit |
| min_confidence | number | Minimum confidence score (0-1) |
| opportunity_type | string | Type of opportunity |
| source | string | Source type |

**Response:**

```json
{
  "data": [
    {
      "opportunity_id": "op123",
      "vehicle_type": "2020 BMW 3 Series Sport",
      "make": "BMW",
      "model": "3 Series",
      "year": 2020,
      "trim": "Sport",
      "estimated_market_value": 29800.00,
      "target_acquisition_price": 26500.00,
      "potential_profit": 3300.00,
      "confidence_score": 0.92,
      "source": "Auction",
      "opportunity_type": "Undervalued",
      "days_available": 5,
      "reasoning": [
        "Recent auction prices below market",
        "Strong demand in local area",
        "Similar vehicles selling quickly"
      ],
      "timestamp": "2023-09-15 10:30:45"
    },
    // More opportunities...
  ]
}
```

### Historical Sales

#### Get Sales History

```
GET /sales-history
```

Returns historical sales data with various filtering options.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | Start date (YYYY-MM-DD) |
| end_date | string | End date (YYYY-MM-DD) |
| make | string | Filter by make |
| model | string | Filter by model |
| min_profit | number | Minimum profit amount |

**Response:**

```json
{
  "data": [
    {
      "sale_id": "sale123",
      "vehicle_id": "veh456",
      "sale_date": "2023-08-20",
      "sale_price": 22500.00,
      "asking_price": 23995.00,
      "days_on_lot": 42,
      "customer_type": "Retail",
      "financing_type": "Finance",
      "salesperson": "John Smith",
      "profit": 2700.00,
      "cost_of_preparation": 800.00,
      "notes": "Customer traded in older vehicle"
    },
    // More sales...
  ]
}
```

### Daily Digest

#### Get Daily Summary

```
GET /daily-digest
```

Returns a summary of today's important information and actions.

**Response:**

```json
{
  "date": "2023-09-15",
  "summary": {
    "new_opportunities": 8,
    "price_adjustments_needed": 12,
    "aging_inventory": 5,
    "market_shifts": [
      {
        "vehicle_type": "SUVs",
        "change": "+2.5%",
        "note": "Increasing demand for SUVs in the South East region"
      },
      {
        "vehicle_type": "Electric Vehicles",
        "change": "+4.1%",
        "note": "EV prices rising due to new government incentives"
      }
    ]
  },
  "urgent_actions": [
    {
      "action_type": "Price Adjustment",
      "vehicle_id": "12345",
      "make": "Audi",
      "model": "A4",
      "year": 2019,
      "current_price": 24995.00,
      "recommended_price": 26500.00,
      "urgency": "High",
      "reason": "Market prices have increased substantially for this model"
    },
    // More actions...
  ],
  "performance_metrics": {
    "average_days_to_sell": 38,
    "average_profit_margin": 12.5,
    "inventory_turnover_rate": 3.2,
    "top_performing_models": [
      {
        "type": "2021 Toyota RAV4 Hybrid",
        "avg_days_to_sell": 15,
        "profit_margin": 18.2
      },
      // More models...
    ]
  }
}
```

### Chat and Query Endpoints

#### Submit Query

```
POST /query
```

Submits a natural language query about inventory or market data.

**Request Body:**

```json
{
  "query": "Show me underpriced SUVs with high profit potential",
  "context": {
    "page": "inventory",
    "filters": {
      "body_type": "SUV"
    }
  }
}
```

**Response:**

```json
{
  "query_id": "q123",
  "results": {
    "vehicles": [
      {
        "vehicle_id": "12345",
        "make": "Audi",
        "model": "Q5",
        "year": 2020,
        "current_price": 32500.00,
        "recommended_price": 35800.00,
        "potential_profit": 3300.00,
        "days_on_lot": 18,
        "reasoning": [
          "Market price trending upward",
          "Low local competition",
          "High demand for this model"
        ]
      },
      // More vehicles...
    ],
    "explanation": "I found 5 SUVs that appear to be underpriced relative to current market value with profit potential above £3,000. These vehicles are priced at least 8% below comparable vehicles in the market and have strong demand indicators.",
    "visualization_data": {
      "chart_type": "scatter",
      "x_axis": "current_price",
      "y_axis": "potential_profit",
      "data_points": [
        // Chart data...
      ]
    }
  }
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (missing or invalid authentication)
- 404: Not Found (resource doesn't exist)
- 500: Server Error

Error response body:

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid parameter: min_year must be a number",
    "details": {
      "parameter": "min_year",
      "value": "abc"
    }
  }
}