import pandas as pd
import os

# Define paths
base_path = '/home/innereye/alarms/'
data_path = os.path.join(base_path, 'data/earthquakes.csv')
duplicates_path = os.path.join(base_path, 'data/earthquakes_duplicates_removed.csv')

def deduplicate():
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    print(f"Reading {data_path}...")
    df = pd.read_csv(data_path)
    
    initial_count = len(df)
    print(f"Initial row count: {initial_count}")

    # Remove duplicates based on 'epiid', keeping the last (most recent) one
    # We do this before the sort to ensure 'keep=last' respects the original order
    # (where newer data from merges was appended to the bottom)
    
    # Identify duplicates for the separate file
    duplicates = df[df.duplicated(subset=['epiid'], keep='last')]
    if len(duplicates) > 0:
        duplicates.to_csv(duplicates_path, index=False)
        print(f"Saved {len(duplicates)} duplicate records to {duplicates_path}")

    # Keep only the last instance of each epiid
    df_cleaned = df.drop_duplicates(subset=['epiid'], keep='last')
    
    # Now sort the cleaned data
    df_cleaned = df_cleaned.sort_values('DateTime(UTC)', ignore_index=True)
    
    final_count = len(df_cleaned)
    removed_count = initial_count - final_count
    
    print(f"Cleaned row count: {final_count}")
    print(f"Removed {removed_count} duplicates.")

    # Overwrite the original file with cleaned data
    df_cleaned.to_csv(data_path, index=False)
    print(f"Updated {data_path} with cleaned data.")

if __name__ == "__main__":
    deduplicate()
