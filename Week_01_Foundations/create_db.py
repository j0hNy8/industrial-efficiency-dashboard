import pandas as pd
import sqlite3 # This is the Database tool

# 1. EXTRACT (Load the CSV)
# We read the raw material just like before
df = pd.read_csv('production_log.csv')

# 2. TRANSFORM (Clean the data)
# Databases are strict. They hate missing numbers.
df['Cycle_Time_Sec'] = df['Cycle_Time_Sec'].fillna(0)

# 3. LOAD (Put it into the Warehouse)
# Connect to a new database file (it will be created automatically)
conn = sqlite3.connect('factory_data.db')

# Write the data to a table named 'production_logs'
# if_exists='replace': If the table exists, wipe it and write fresh.
df.to_sql('production_logs', conn, if_exists='replace', index=False)

print("Success! Data has been moved from CSV to SQL Database.")

# Close the door
conn.close()