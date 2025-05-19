import pandas as pd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

def direct_count_attributes(attribute_name, attribute_value):
    """
    Directly count items in the vehicles dataset with the specified attribute value
    """
    # Try to load the dataset from the exports directory
    try:
        vehicles_path = "exports/vehicles.csv"
        df = pd.read_csv(vehicles_path)
        print(f"✅ Loaded dataset with {len(df)} vehicles")
        
        # Make sure the attribute exists
        if attribute_name not in df.columns:
            return f"❌ Attribute '{attribute_name}' not found in dataset. Available columns: {', '.join(df.columns)}"
        
        # For string attributes, do case-insensitive matching
        if df[attribute_name].dtype == 'object':
            filtered_df = df[df[attribute_name].str.lower() == attribute_value.lower()]
        # For numeric attributes
        else:
            try:
                attribute_value = float(attribute_value)
                filtered_df = df[df[attribute_name] == attribute_value]
            except ValueError:
                return f"❌ Error: Attribute value '{attribute_value}' cannot be converted to a number for comparison"
        
        count = len(filtered_df)
        percentage = (count / len(df)) * 100
        
        print(f"Count of vehicles with {attribute_name}='{attribute_value}': {count} ({percentage:.1f}%)")
        
        # Create a visualization
        fig = go.Figure()
        
        # Create a pie chart showing the proportion
        labels = [f"{attribute_name}='{attribute_value}'", "Other vehicles"]
        values = [count, len(df) - count]
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            textinfo='label+percent',
            insidetextorientation='radial',
            marker=dict(colors=['#4CAF50', '#ccc']),
            title=f"Count of Vehicles with {attribute_name.capitalize()}='{attribute_value}': {count} ({percentage:.1f}%)"
        ))
        
        fig.update_layout(
            title=f"Distribution of Vehicles by {attribute_name.capitalize()}",
            height=500,
            width=700
        )
        
        # Display the chart in the browser
        fig.show()
        
        # If there are matches, return a sample
        if count > 0:
            print("\nSample of matching vehicles:")
            return filtered_df.head(5).to_string()
        else:
            return "No matching vehicles found."
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    # Get user input or use default values
    attribute_name = input("Enter attribute name (e.g., color): ") or "color"
    attribute_value = input(f"Enter {attribute_name} value (e.g., green): ") or "green"
    
    # Run the direct count
    result = direct_count_attributes(attribute_name, attribute_value)
    print(result) 