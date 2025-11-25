import pandas as pd
import os
import random

# Create a folder for the raw files if it doesn't exist
os.makedirs('weekly_data', exist_ok=True)

# Machines
machines = ['PRESS_01', 'CNC_02', 'WELD_03']

# Generate 7 files (simulating Monday to Sunday)
for i in range(1, 8):
    # Create dummy data
    data = {
        'Timestamp': [f'2025-11-{24+i} 08:00:00'] * 3,
        'Machine_ID': machines,
        'Parts_Produced': [random.randint(50, 150) for _ in range(3)],
        'Scrap_Count': [random.randint(0, 10) for _ in range(3)]
    }
    
    df = pd.DataFrame(data)
    
    # Save as separate CSVs: day_1.csv, day_2.csv, etc.
    filename = f'weekly_data/day_{i}.csv'
    df.to_csv(filename, index=False)
    print(f"Created: {filename}")

print("Simulation Complete. 7 files created in 'weekly_data' folder.")