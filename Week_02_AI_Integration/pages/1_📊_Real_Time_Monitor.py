import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import time

st.set_page_config(page_title="Real-Time Monitor", page_icon="📊", layout="wide")

st.title("📊 Live Production Monitor")

# --- SETUP ---
@st.cache_resource
def get_database_connection():
    return create_engine('sqlite:///factory.db')

db_engine = get_database_connection()

# --- CONTROLS ---
col_controls1, col_controls2 = st.columns([1, 4])
with col_controls1:
    live_mode = st.toggle("🔴 Live Mode (Auto-Refresh)")

with col_controls2:
    if st.button("🔄 Manual Refresh"):
        st.rerun()

# --- DATA LOGIC ---
try:
    # Query: Get newest 50 rows
    query = "SELECT * FROM production_logs ORDER BY Timestamp DESC LIMIT 50"
    df = pd.read_sql(query, db_engine)
    
    if not df.empty:
        # KPIS
        total_parts = df['Parts_Produced'].sum()
        total_scrap = df['Scrap_Count'].sum()
        scrap_rate = (total_scrap / total_parts * 100) if total_parts > 0 else 0
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Current Output", f"{total_parts} units")
        kpi2.metric("Current Scrap", f"{total_scrap} units")
        kpi3.metric("Scrap Rate", f"{scrap_rate:.2f}%")
        
        # CHARTS
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Volume by Machine")
            fig1, ax1 = plt.subplots()
            df.groupby("Machine_ID")["Parts_Produced"].sum().plot(kind='bar', ax=ax1, color='#FFA500')
            plt.ylabel("Output")
            st.pyplot(fig1)
            
        with col2:
            st.subheader("Live Feed")
            st.dataframe(df, height=300)

    else:
        st.warning("Database connected, but waiting for data...")

except Exception as e:
    st.error(f"Connection Error: {e}")

# --- AUTO-REFRESH ---
if live_mode:
    time.sleep(2)
    st.rerun()