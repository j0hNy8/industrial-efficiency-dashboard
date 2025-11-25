import pandas as pd

# 1. Load the Data
# We use try/except just in case the file isn't found
try:
    df = pd.read_csv('production_log.csv', delimiter=',')
    print("--- Raw Data Loaded Successfully ---")
    print(df.head()) # Shows first 5 rows in the terminal
except FileNotFoundError:
    print("ERROR: Could not find production_log.csv. Make sure it is in the same folder as this script!")
    exit()

# 2. Clean the Data
# Fill missing Cycle Times with 0 so math doesn't break
df['Cycle_Time_Sec'] = df['Cycle_Time_Sec'].fillna(0)

# 3. The Analysis (The "Pivot Table" replacement)

# A. Total parts produced per Machine
summary = df.groupby('Machine_ID')['Parts_Produced'].sum().reset_index()

# B. Calculate average cycle time (ONLY for 'RUN' status)
# We filter for rows where Status is 'RUN', then group by Machine, then average the Cycle Time
run_data = df[df['Status'] == 'RUN']
performance = run_data.groupby('Machine_ID')['Cycle_Time_Sec'].mean().reset_index()

# Rename the column to be clear
performance.rename(columns={'Cycle_Time_Sec': 'Avg_Cycle_Time_Sec'}, inplace=True)

print("\n--- Production Summary ---")
print(summary)

print("\n--- Average Cycle Time (Run Status Only) ---")
print(performance)

# 4. Export the Report
# We will create a new Excel file with two sheets
with pd.ExcelWriter('Shift_Report_Generated.xlsx') as writer:
    summary.to_excel(writer, sheet_name='Production_Totals', index=False)
    performance.to_excel(writer, sheet_name='Efficiency_Metrics', index=False)

print("\nSuccess! Report saved as 'Shift_Report_Generated.xlsx'")