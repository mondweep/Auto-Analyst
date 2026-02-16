# Automotive Analytics Dataset

This directory contains exported automotive data that can be used with the Auto-Analyst platform for analysis and visualization.

## Files

1. **vehicles.csv** - Complete vehicle inventory data including:
   - Make, model, year, color
   - Price, mileage, condition
   - Fuel type, days in inventory
   - VIN and sold status

2. **market_data.csv** - Market analysis data including:
   - Average market prices
   - Price differences and percentage differences
   - Market demand metrics
   - Sample sizes and average days to sell

3. **automotive_analysis.csv** - Combined dataset merging vehicle and market data:
   - All vehicle details
   - Market pricing information
   - Opportunity indicators
   - Perfect for comprehensive analysis

## How to Use with Auto-Analyst

1. Navigate to the Auto-Analyst chat interface
2. Upload one of these CSV files using the file upload interface
3. Ask questions about the data using natural language
4. Examples:
   - "Analyze the distribution of vehicle prices by make"
   - "Show me opportunities with at least 10% price difference"
   - "Create a scatter plot of mileage vs. price for all vehicles"
   - "What's the correlation between vehicle condition and days in inventory?"
   - "Which make has the highest average market price?"

## Data Fields Explained

### Vehicle Data
- `id`: Unique identifier for the vehicle
- `make`: Vehicle manufacturer (Toyota, Honda, etc.)
- `model`: Vehicle model (Camry, Civic, etc.)
- `year`: Model year
- `color`: Vehicle color
- `price`: Listed price in USD
- `mileage`: Current mileage in miles
- `condition`: Vehicle condition (Excellent, Good, Fair, Poor)
- `fuel_type`: Type of fuel (Gasoline, Diesel, Hybrid, Electric)
- `list_date`: Date when the vehicle was listed
- `days_in_inventory`: Number of days in inventory
- `vin`: Vehicle Identification Number
- `is_sold`: Whether the vehicle has been sold (true/false)

### Market Data
- `vehicle_id`: ID of the associated vehicle
- `avg_market_price`: Average market price for similar vehicles
- `price_difference`: Absolute price difference (market price - listed price)
- `percent_difference`: Percentage price difference
- `is_opportunity`: Whether this vehicle is considered an opportunity (true/false)
- `sample_size`: Number of similar vehicles used for comparison
- `avg_days_to_sell`: Average days to sell similar vehicles
- `market_demand`: Demand category (High, Medium, Low)

## Data Analysis Tips

- **Profit Opportunities**: Focus on vehicles with high percentage differences (10%+)
- **Inventory Management**: Analyze days in inventory against market demand
- **Pricing Strategy**: Compare your prices against market averages by make and model
- **Sales Velocity**: Investigate the relationship between pricing and average days to sell 