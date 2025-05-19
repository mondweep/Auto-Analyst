import pandas as pd
import os
import sys

def count_vehicles_by_attribute(attribute_name, attribute_value):
    """
    Count vehicles in the dataset that match a specific attribute value.
    
    Args:
        attribute_name (str): The column name to filter on (e.g., 'color', 'make')
        attribute_value (str): The value to match (case-insensitive)
        
    Returns:
        tuple: (count, percentage, matching_vehicles_df)
    """
    # Get the path to the vehicles dataset
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exports_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "exports")
    vehicles_path = os.path.join(exports_dir, "vehicles.csv")
    
    # Load the dataset
    if not os.path.exists(vehicles_path):
        print(f"Error: Dataset not found at {vehicles_path}")
        return 0, 0, None
    
    try:
        df = pd.read_csv(vehicles_path)
        
        # Convert both the column values and the attribute value to lowercase for case-insensitive matching
        if attribute_name in df.columns:
            # Convert column to string first in case it's not already
            df[attribute_name] = df[attribute_name].astype(str).str.lower()
            attribute_value = str(attribute_value).lower()
            
            # Filter the dataframe for matching rows
            matching_vehicles = df[df[attribute_name] == attribute_value]
            
            # Calculate count and percentage
            count = len(matching_vehicles)
            percentage = (count / len(df)) * 100 if len(df) > 0 else 0
            
            return count, percentage, matching_vehicles
        else:
            print(f"Error: Column '{attribute_name}' not found in dataset")
            return 0, 0, None
            
    except Exception as e:
        print(f"Error processing dataset: {str(e)}")
        return 0, 0, None

def main():
    """Run as a standalone script."""
    if len(sys.argv) < 3:
        print("Usage: python direct_count_query.py <attribute_name> <attribute_value>")
        print("Example: python direct_count_query.py color green")
        return
        
    attribute_name = sys.argv[1]
    attribute_value = sys.argv[2]
    
    count, percentage, vehicles = count_vehicles_by_attribute(attribute_name, attribute_value)
    
    if vehicles is not None:
        print(f"\nFound {count} vehicles with {attribute_name}='{attribute_value}' ({percentage:.1f}% of inventory)")
        print("\nSample of matching vehicles:")
        print(vehicles[['id', 'make', 'model', 'year', attribute_name]].head(5))
    
if __name__ == "__main__":
    main() 