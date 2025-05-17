# Automotive Pricing Data Schema

This document outlines the data schema for the synthetic automotive data used in the POV demo.

## Core Data Entities

### Vehicle Inventory

```json
{
  "vehicle_id": "string",
  "make": "string",
  "model": "string",
  "year": "integer",
  "trim": "string",
  "body_type": "string",
  "fuel_type": "string",
  "transmission": "string",
  "engine_size": "float",
  "mileage": "integer",
  "color_exterior": "string",
  "color_interior": "string",
  "condition": "string", // "Excellent", "Good", "Fair", "Poor"
  "features": ["string"],
  "acquisition_date": "date",
  "acquisition_price": "float",
  "current_price": "float",
  "recommended_price": "float",
  "days_on_lot": "integer",
  "images": ["string"], // URLs
  "vin": "string",
  "status": "string", // "In Stock", "Sold", "On Hold", "In Transit"
  "location": "string"
}
```

### Market Data

```json
{
  "market_id": "string",
  "vehicle_type": "string", // Combination of make, model, year, trim
  "average_market_price": "float",
  "lowest_market_price": "float",
  "highest_market_price": "float",
  "price_trend_30d": "float", // Percentage change
  "average_days_to_sell": "integer",
  "demand_index": "float", // 0-100 scale
  "competitor_count": "integer",
  "region": "string",
  "timestamp": "datetime",
  "seasonal_adjustment": "float" // Seasonal price adjustment factor
}
```

### Historical Sales

```json
{
  "sale_id": "string",
  "vehicle_id": "string",
  "sale_date": "date",
  "sale_price": "float",
  "asking_price": "float",
  "days_on_lot": "integer",
  "customer_type": "string", // "Retail", "Wholesale", "Trade-In"
  "financing_type": "string",
  "salesperson": "string",
  "profit": "float",
  "cost_of_preparation": "float",
  "notes": "string"
}
```

### Price Recommendations

```json
{
  "recommendation_id": "string",
  "vehicle_id": "string",
  "current_price": "float",
  "recommended_price": "float",
  "price_change": "float",
  "confidence_score": "float", // 0-1 scale
  "reasoning": ["string"], // Array of factors behind recommendation
  "expected_days_to_sell": "integer",
  "expected_profit": "float",
  "competitive_position": "string", // "Underpriced", "Competitive", "Overpriced"
  "timestamp": "datetime",
  "expiration": "datetime" // When recommendation expires/should be refreshed
}
```

### Market Opportunities

```json
{
  "opportunity_id": "string",
  "vehicle_type": "string",
  "make": "string",
  "model": "string",
  "year": "integer",
  "trim": "string",
  "estimated_market_value": "float",
  "target_acquisition_price": "float",
  "potential_profit": "float",
  "confidence_score": "float", // 0-1 scale
  "source": "string", // e.g., "Auction", "Private Sale", "Trade", "Competitor"
  "opportunity_type": "string", // "Undervalued", "High Demand", "Seasonal"
  "days_available": "integer", // How long this opportunity might last
  "reasoning": ["string"], // Factors making this an opportunity
  "timestamp": "datetime"
}
```

## Relationship Diagram

```
Vehicle Inventory 1──* Historical Sales
       │
       │
       ▼
Market Data ───* Price Recommendations
       │
       │
       ▼
Market Opportunities
```

## Synthetic Data Generation Guidelines

When generating synthetic data for the POV demo, consider the following guidelines:

1. **Realistic Vehicle Models**: Use actual makes, models, trims that exist in the real world
2. **Price Consistency**: Ensure prices align with real-world expectations for vehicle type/age
3. **Temporal Patterns**: Include seasonal trends and weekday/weekend patterns
4. **Market Correlation**: Ensure market data correctly influences recommendations
5. **Profit Margins**: Typically 8-12% for new vehicles, 10-20% for used vehicles
6. **Days on Lot**: Average 30-60 days with significant variance
7. **Depreciation Curves**: Different vehicle types depreciate at different rates
8. **Price Elasticity**: How price changes affect time-to-sell
9. **Condition Impact**: Vehicle condition significantly affects pricing
10. **Regional Variations**: Include regional market differences

## API Access Patterns

The synthetic data will be accessible through the following API patterns:

1. **GET /api/vehicles** - List inventory with filtering/sorting
2. **GET /api/vehicles/{id}** - Get single vehicle details
3. **GET /api/market-data** - Get market trends and pricing data
4. **GET /api/recommendations** - Get price recommendations
5. **GET /api/opportunities** - Get market opportunities
6. **GET /api/sales-history** - Get historical sales data
7. **GET /api/daily-digest** - Get daily summary and urgent actions

## Sample Queries

Examples of natural language queries the system should handle:

- "Show me underpriced SUVs with high profit potential"
- "Which vehicles have been on the lot for more than 45 days?"
- "What's the optimal price for a 2019 Audi A4 with 50,000 miles?"
- "How is the market trending for hybrid vehicles this month?"
- "Which vehicles should I adjust pricing for today?"
- "What's the average profit margin for luxury vehicles we sold last quarter?"
- "Which vehicle type has the fastest turnover rate?"
- "Show me opportunities to buy vehicles at 10% below market value" 