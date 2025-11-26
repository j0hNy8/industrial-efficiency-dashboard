import requests
import pandas as pd
from datetime import date

print("--- Connecting to European Central Bank Data ---")

# 1. DEFINE the Target
# We want to know: 1 EUR = How many USD?
# We also want to know the history (for the last 30 days) to see the trend.
today = date.today()
start_date = "2025-01-01" # Let's pull data from start of year
url = f"https://api.frankfurter.app/{start_date}..?to=USD"

# 2. REQUEST the Data (The "Handshake")
response = requests.get(url)

# 3. CHECK status
if response.status_code == 200:
    print("Success! Connection established.")
    
    # 4. PARSE the JSON (Convert web-text to Python-dictionary)
    data = response.json()
    
    # Extract the 'rates' part
    # Structure is: {'2024-01-01': {'USD': 1.09}, ...}
    rates_dict = data['rates']
    
    # 5. CONVERT to DataFrame
    # oriented 'index' because dates are the keys
    df = pd.DataFrame.from_dict(rates_dict, orient='index')
    
    # Clean up
    df.index.name = 'Date'
    df.reset_index(inplace=True)
    df.columns = ['Date', 'USD_Rate']
    
    # Ensure date is actually a Date object
    df['Date'] = pd.to_datetime(df['Date'])
    
    print(f"\nDownloaded {len(df)} days of exchange rates.")
    print(df.tail()) # Show the last 5 days
    
    # 1. Create a full timeline (Every single day)
    all_days = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='D')

    # 2. Reindex the data to match this full timeline
    df = df.set_index('Date').reindex(all_days)

    # 3. Fill the blanks (Take Friday's value and paste it into Sat/Sun)
    df['USD_Rate'] = df['USD_Rate'].ffill()

    # Reset index to make 'Date' a column again
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Date'}, inplace=True)

    # 6. SAVE
    df.to_csv('exchange_rates.csv', index=False)
    print("Saved to 'exchange_rates.csv'")

else:
    print(f"Error: Server returned status {response.status_code}")