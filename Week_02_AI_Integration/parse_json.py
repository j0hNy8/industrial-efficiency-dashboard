import json
import pandas as pd

# 1. Load the raw JSON file
with open('sensor_stream.json', 'r') as f:
    raw_data = json.load(f)

print("--- Raw JSON Loaded ---")
# Accessing specific data point (Navigation)
# Let's get the vibration of the second sensor
print(f"Example Extraction: {raw_data[1]['metrics']['vibration_hz']} Hz")

# 2. The Wrong Way (Loading directly)
df_bad = pd.DataFrame(raw_data)
print("\n--- The Problem (Nested Data) ---")
print(df_bad[['sensor_id', 'metrics']].head())
# Notice how 'metrics' is a dictionary, not a number? You can't graph that.

# 3. The Right Way (Normalization)
# pd.json_normalize flattens the tree
df_clean = pd.json_normalize(
    raw_data, 
    sep='_' # Use underscore to separate levels (metrics_temperature_c)
)

print("\n--- The Solution (Flattened Data) ---")
print(df_clean.columns) # Look at the new column names
print(df_clean[['sensor_id', 'metrics_temperature_c', 'metrics_vibration_hz']])

# 4. Save to Excel (Now it's compatible)
df_clean.to_excel("Sensor_Data_Flattened.xlsx", index=False)
print("\nSaved flat Excel file.")