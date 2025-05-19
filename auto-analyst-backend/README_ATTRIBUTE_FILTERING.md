# Attribute-Specific Filtering in Auto-Analyst

This documentation describes the improved attribute-specific filtering capabilities in Auto-Analyst, enabling direct answers to questions like "how many green vehicles do we have?" with precise counts and visualizations.

## Overview of Improvements

We've enhanced Auto-Analyst with robust attribute-specific querying capabilities:

1. **Enhanced Query Detection**: Better recognition of attribute-specific questions using improved patterns for common automotive queries.

2. **Direct Count Functionality**: New utility (`direct_count_query.py`) for precise filtering and counting of attributes like color, make, and year.

3. **NumPy Compatibility Fixes**: Ensured compatibility between newer NumPy versions (2.x+) and libraries expecting NumPy 1.x API.

4. **Case-Insensitive Matching**: Properly handles string comparisons with case-insensitivity and NULL value handling.

5. **Comprehensive Visualization**: Creates charts clearly stating the count and percentage in titles.

## Using Attribute-Specific Filtering

### Example Queries That Now Work Better

- "How many green vehicles do we have?"
- "Count of Toyota vehicles"
- "Number of vehicles that are from 2022"
- "Show me vehicles under $30,000"
- "How many vehicles with condition is excellent"

### Running the Enhanced Backend

We've created a special wrapper script that sets up the necessary compatibility fixes:

```bash
cd Auto-Analyst/auto-analyst-backend
./run_auto_analyst.py
```

Options:
- `--port 8080`: Run on a specific port (default is 8000)
- `--skip-checks`: Skip compatibility checks
- `--no-debug`: Disable debug mode

### Testing Attribute Filtering Directly

To test the attribute filtering functionality, we provide several options:

#### Option 1: Lightweight Query Tool (No NumPy/Pandas Dependencies)

Use our lightweight CSV-based query tool that doesn't require NumPy or pandas:

```bash
cd Auto-Analyst/auto-analyst-backend
./query_vehicle_attributes.py --interactive
```

Or query directly from the command line:

```bash
# Ask a natural language question
./query_vehicle_attributes.py --query "How many green vehicles do we have?"

# Query directly by attribute and value
./query_vehicle_attributes.py --attribute color --value green
```

#### Option 2: Full Test Suite

Run our comprehensive test suite (requires NumPy/Pandas):

```bash
cd Auto-Analyst/auto-analyst-backend
./test_attribute_filtering.py
```

This will test:
1. Direct attribute counting for various attributes (color, make, year)
2. Query detection capabilities for different question formats

## Technical Implementation

### Query Detection

We've enhanced query detection through regex patterns that capture common attribute query formats:

```python
patterns = [
    r"how many (\w+) (vehicles|cars) (?:do we have|are there)",  # "how many green vehicles do we have"
    r"count (?:of|the) (\w+) (vehicles|cars)",  # "count of green vehicles"
    r"how many (vehicles|cars) (?:are|with) (\w+) (is|are|=|equal to) (\w+)",  # "how many vehicles with color is green"
    # More patterns...
]
```

### Case-Insensitive Filtering

We ensure all string comparisons are case-insensitive and handle NULL/NaN values properly:

```python
# Convert to string first to handle NaN values
df[attribute_name] = df[attribute_name].astype(str)
filtered_df = df[df[attribute_name].str.lower() == attribute_value.lower()]
```

### NumPy Compatibility

For systems running NumPy 2.x, we use compatibility flags to maintain support for libraries expecting NumPy 1.x API:

```python
os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION_ENABLED'] = '1'
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '1'
```

## Troubleshooting

### Common Issues

1. **NumPy Compatibility Errors**: If you see errors about NumPy APIs, ensure you're running the backend with `./run_auto_analyst.py` which sets the necessary compatibility flags.

2. **Dataset Not Found**: Ensure the vehicles dataset is accessible. The system will look in these locations:
   - `exports/vehicles.csv`
   - `data/vehicles.csv`

3. **Attribute Not Recognized**: Some query patterns might not be detected. Try rephrasing your query to match the supported patterns or use the direct test tool.

### Manual Testing

To test specific attribute filtering directly:

```python
from src.utils.direct_count_query import direct_count_attributes

# Check how many green vehicles
result = direct_count_attributes("color", "green")
print(result)
```

## Integration with Visualization

The data visualization agent has been updated to better handle attribute-specific queries with improved filtering syntax and clearer visual presentation of results. 