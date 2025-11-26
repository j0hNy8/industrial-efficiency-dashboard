import sqlite3
import pandas as pd

# Connect to the warehouse
conn = sqlite3.connect('factory_data.db')

# --- QUERY 1: The "Select" (Show me everything) ---
print("--- QUERY 1: Top 3 Rows ---")
query1 = "SELECT * FROM production_logs LIMIT 3"
result1 = pd.read_sql(query1, conn)
print(result1)

# --- QUERY 2: The "Filter" (Find the bottleneck) ---
print("\n--- QUERY 2: Only Slow Cycles (> 100 sec) ---")
query2 = "SELECT * FROM production_logs WHERE Cycle_Time_Sec > 100"
result2 = pd.read_sql(query2, conn)
print(result2)

# --- QUERY 3: The "Aggregation" (Manager's Report) ---
# This is the SQL version of the "groupby" we did in Python Day 1
print("\n--- QUERY 3: Total Parts per Machine ---")
query3 = """
SELECT 
    Machine_ID, 
    SUM(Parts_Produced) as Total_Parts 
FROM production_logs 
GROUP BY Machine_ID
"""
result3 = pd.read_sql(query3, conn)
print(result3)

conn.close()