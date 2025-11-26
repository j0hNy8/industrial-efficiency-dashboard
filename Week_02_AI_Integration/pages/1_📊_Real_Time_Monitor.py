import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import time

st.set_page_config(page_title="Real-Time Monitor", page_icon="📊", layout="wide")

st.title("📊 Live Production Monitor")

# 1. CONNECT to the Simulator Database
# We use a function with @st.cache_resource so we don't reconnect every second
@st.cache_resource
def get_database_connection():
    return create_engine('sqlite:///factory.db')

db_engine = get_database_connection()

# 2. REFRESH BUTTON
# In a real app, we might use st.empty() for auto-refresh, but a button is safer for now.
if st.button("🔄 Refresh Live Data"):
    st.rerun()

# 3. READ DATA (Last 1000 records)
try:
    # We query the DB directly
    df = pd.read_sql("SELECT * FROM production_logs", db_engine)
    
    if not df.empty:
        # Convert timestamp
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # --- KPIS ---
        total_parts = df['Parts_Produced'].sum()
        total_scrap = df['Scrap_Count'].sum()
        scrap_rate = (total_scrap / total_parts * 100) if total_parts > 0 else 0
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Output", f"{total_parts} units")
        kpi2.metric("Total Scrap", f"{total_scrap} units")
        kpi3.metric("Scrap Rate", f"{scrap_rate:.2f}%")
        
        # --- CHARTS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Volume by Machine")
            fig1, ax1 = plt.subplots()
            df.groupby("Machine_ID")["Parts_Produced"].sum().plot(kind='bar', ax=ax1, color='#FFA500')
            st.pyplot(fig1)
            
        with col2:
            st.subheader("Recent Activity (Timeline)")
            # Resample to show activity per minute (Advanced Pandas skill!)
            # We set 'Timestamp' as index to resample
            df_time = df.set_index('Timestamp')
            # Group by 1 Minute (1T) and sum parts
            timeline = df_time.resample('1min')['Parts_Produced'].sum()
            
            st.line_chart(timeline)

        # --- RAW DATA ---
        with st.expander("Live Database Feed"):
            # Show latest rows first
            st.dataframe(df.sort_values(by='Timestamp', ascending=False))
            
    else:
        st.warning("Database connected, but waiting for data... (Is the simulator running?)")

except Exception as e:
    st.info("Waiting for factory connection... (Start sensor_sim.py!)")
    st.error(f"Debug Info: {e}")