import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import time
from datetime import datetime, time as dt_time, timedelta

st.set_page_config(page_title="Real-Time Monitor", page_icon="📊", layout="wide")

st.title("📊 Live Production Monitor")

# --- 1. SETUP & CONFIG ---
@st.cache_resource
def get_database_connection():
    # Connect to the local database file (shared with simulator)
    return create_engine('sqlite:///factory.db')

db_engine = get_database_connection()

# --- 2. SHIFT LOGIC HELPER ---
def get_current_shift_start():
    """
    Calculates the start time of the current shift based on standard Central European patterns:
    - Morning: 06:00 - 14:00
    - Afternoon: 14:00 - 22:00
    - Night: 22:00 - 06:00 (Crosses Midnight)
    """
    now = datetime.now()
    current_time = now.time()
    
    # Define Shift Boundaries
    morning_start = dt_time(6, 0)
    afternoon_start = dt_time(14, 0)
    night_start = dt_time(22, 0)
    
    if morning_start <= current_time < afternoon_start:
        # Morning Shift (Starts Today 06:00)
        start_dt = datetime.combine(now.date(), morning_start)
        shift_name = "Morning (Ranná)"
        
    elif afternoon_start <= current_time < night_start:
        # Afternoon Shift (Starts Today 14:00)
        start_dt = datetime.combine(now.date(), afternoon_start)
        shift_name = "Afternoon (Poobedná)"
        
    else:
        # Night Shift (Nočná)
        shift_name = "Night (Nočná)"
        if current_time >= night_start:
            # It's late night (e.g., 23:00) - Shift started today at 22:00
            start_dt = datetime.combine(now.date(), night_start)
        else:
            # It's early morning (e.g., 03:00) - Shift started Yesterday at 22:00
            start_dt = datetime.combine(now.date() - timedelta(days=1), night_start)
            
    return start_dt, shift_name

# --- 3. CONTROLS ---
col_controls1, col_controls2 = st.columns([1, 4])
with col_controls1:
    live_mode = st.toggle("🔴 Live Mode (Auto-Refresh)")

with col_controls2:
    if st.button("🔄 Manual Refresh"):
        st.rerun()

# --- 4. DATA LOGIC ---
try:
    # A. Get Shift Context
    shift_start, shift_name = get_current_shift_start()
    shift_start_str = shift_start.strftime("%Y-%m-%d %H:%M:%S")
    
    st.caption(f"Current Shift: **{shift_name}** | Data since: {shift_start_str}")

    # B. KPI QUERY (Aggregates for CURRENT SHIFT only)
    kpi_query = f"""
    SELECT 
        SUM(Parts_Produced) as Total_Parts,
        SUM(Scrap_Count) as Total_Scrap
    FROM production_logs
    WHERE Timestamp >= '{shift_start_str}'
    """
    df_kpi = pd.read_sql(kpi_query, db_engine)
    
    # Extract scalar values safely
    total_parts = df_kpi['Total_Parts'].iloc[0] if not df_kpi.empty and pd.notna(df_kpi['Total_Parts'].iloc[0]) else 0
    total_scrap = df_kpi['Total_Scrap'].iloc[0] if not df_kpi.empty and pd.notna(df_kpi['Total_Scrap'].iloc[0]) else 0
    
    # Calculate Rate
    if total_parts > 0:
        scrap_rate = (total_scrap / total_parts) * 100
    else:
        scrap_rate = 0
        
    # C. CHART QUERY (Grouped by Machine, Current Shift only)
    chart_query = f"""
    SELECT 
        Machine_ID, 
        SUM(Parts_Produced) as Machine_Total 
    FROM production_logs 
    WHERE Timestamp >= '{shift_start_str}'
    GROUP BY Machine_ID
    """
    df_chart = pd.read_sql(chart_query, db_engine)
    
    # D. TABLE QUERY (Recent Activity - Last 50 rows regardless of shift)
    table_query = "SELECT * FROM production_logs ORDER BY Timestamp DESC LIMIT 50"
    df_recent = pd.read_sql(table_query, db_engine)
    
    # --- 5. VISUALIZATION ---
    if not df_recent.empty:
        # KPI Cards
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Shift Output", f"{int(total_parts)} units")
        kpi2.metric("Shift Scrap", f"{int(total_scrap)} units")
        kpi3.metric("Scrap Rate", f"{scrap_rate:.2f}%")
        
        col1, col2 = st.columns(2)
        
        # Bar Chart
        with col1:
            st.subheader("Shift Volume by Machine")
            if not df_chart.empty:
                fig1, ax1 = plt.subplots()
                # Plot with custom Orange color
                df_chart.set_index("Machine_ID")["Machine_Total"].plot(kind='bar', ax=ax1, color='#FFA500')
                plt.ylabel("Output")
                plt.xticks(rotation=0)
                st.pyplot(fig1)
            else:
                st.info("No production data for this shift yet.")
            
        # Recent Table
        with col2:
            st.subheader("Live Feed (Last 50 Events)")
            st.dataframe(df_recent, height=300)

    else:
        st.warning("Database connected, but waiting for data...")

except Exception as e:
    st.error(f"Connection Error: {e}")

# --- 6. AUTO-REFRESH ---
if live_mode:
    time.sleep(2)
    st.rerun()