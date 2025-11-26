import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Industrial Analytics Home",
    page_icon="🏭",
    layout="wide"
)

# The Main "Lobby" UI
st.title("🏭 Industrial AI Cockpit")
st.sidebar.success("Select a module above.")

st.markdown("""
### Welcome to the Intelligent Plant Manager.

This application is split into two specialized modules:

**1. 📊 Real-Time Monitor**
   - Visualize production data from CSV or SQL.
   - Track KPIs: Output, Scrap, Efficiency.
   - Generate PDF Shift Reports.

**2. 🤖 AI Technician**
   - RAG-Powered Chatbot.
   - Diagnoses machine faults using the Technical Manual.
   - Provides actionable maintenance steps (GPT-5.1).

---
**👈 Please select a module from the sidebar to begin.**
""")