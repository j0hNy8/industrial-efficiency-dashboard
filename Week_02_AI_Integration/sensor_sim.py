import time
import random
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# 1. CONNECT to a local database file
# If 'factory.db' doesn't exist, this will create it automatically.
db_engine = create_engine('sqlite:///factory.db')

print("--- 🏭 Machine Simulator Started ---")
print("Generating live data... (Press Ctrl+C to stop)")

machines = ['PRESS_01', 'CNC_02', 'WELD_03', 'ASSEMBLY_04']

while True:
    # 2. GENERATE random sensor data
    # Force time to match Slovakia (UTC + 1 hour)
    # Note: Docker's 'now' is UTC. So we take 'now' and add 1 hour.
    slovak_time = datetime.now() + timedelta(hours=1) 
    current_time = slovak_time.strftime('%Y-%m-%d %H:%M:%S')
    machine = random.choice(machines)
    
    # Simulate: 90% chance of 'RUN', 10% chance of 'STOP'
    status = 'RUN' if random.random() > 0.1 else 'STOP'
    
    # Simulate: Output and Scrap
    parts = random.randint(1, 10) if status == 'RUN' else 0
    scrap = random.randint(0, 2) if status == 'RUN' else 0
    
    # Create a single row of data
    data = {
        'Timestamp': [current_time],
        'Machine_ID': [machine],
        'Status': [status],
        'Parts_Produced': [parts],
        'Scrap_Count': [scrap]
    }
    
    df = pd.DataFrame(data)
    
    # 3. WRITE to the Database
    # 'append': Add to the bottom of the table
    df.to_sql('production_logs', db_engine, if_exists='append', index=False)
    
    print(f"[{current_time}] {machine}: {status} | +{parts} Parts")
    
    # 4. SLEEP (Wait 5 seconds to simulate real-time)
    time.sleep(5)