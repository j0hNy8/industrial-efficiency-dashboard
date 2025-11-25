import pandas as pd
import glob # The "File Finder" tool
import os

print("--- Starting Batch Process ---")

# 1. FIND the files
# glob.glob uses patterns. '*.csv' means "anything ending in .csv"
# This creates a list: ['weekly_data/day_1.csv', 'weekly_data/day_2.csv', ...]
all_files = glob.glob('weekly_data/*.csv')

print(f"Found {len(all_files)} files to process.")

# 2. LOOP through them
# We create an empty list to hold the dataframes
dfs = []

for filename in all_files:
    # Read the individual file
    temp_df = pd.read_csv(filename)
    
    # Add a column so we know which file it came from (Traceability!)
    temp_df['Source_File'] = os.path.basename(filename)
    
    # Add it to our list
    dfs.append(temp_df)
    print(f"Processed: {filename}")

# 3. CONCATENATE (The "Master Merge")
# Stack them all on top of each other
master_df = pd.concat(dfs, ignore_index=True)

# 4. ANALYZE the Master Data
total_production = master_df['Parts_Produced'].sum()
total_scrap = master_df['Scrap_Count'].sum()

print("\n--- Weekly Summary ---")
print(f"Total Files Merged: {len(all_files)}")
print(f"Total Parts: {total_production}")
print(f"Total Scrap: {total_scrap}")

# 5. EXPORT
master_df.to_excel('Weekly_Master_Report.xlsx', index=False)
print("Saved 'Weekly_Master_Report.xlsx'")