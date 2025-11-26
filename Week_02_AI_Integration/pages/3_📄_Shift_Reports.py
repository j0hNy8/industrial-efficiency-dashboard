import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from fpdf import FPDF
import base64
from datetime import datetime

st.set_page_config(page_title="Shift Reports", page_icon="📄", layout="wide")

st.title("📄 Shift Reporting Module")
st.markdown("Generate and download formal production reports.")

# --- 1. SETUP ---
@st.cache_resource
def get_database_connection():
    return create_engine('sqlite:///factory.db')

db_engine = get_database_connection()

# --- 2. PDF GENERATOR (Cleaned for FPDF2 Warnings) ---
def create_pdf(total_parts, scrap_rate, advice, timestamp):
    pdf = FPDF()
    pdf.add_page()
    # FIX 1: Use 'Helvetica' instead of 'Arial' to stop the warnings
    pdf.set_font("Helvetica", size=12)
    
    # Header
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, text="Official Shift Report", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(200, 10, text=f"Generated: {timestamp}", new_x="LMARGIN", new_y="NEXT", align='C')
    
    # Metrics Section
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(200, 10, text="Production Summary", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, text=f"Total Units Produced: {total_parts}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, text=f"Scrap Rate: {scrap_rate:.2f}%", new_x="LMARGIN", new_y="NEXT")
    
    # AI/Notes Section
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(200, 10, text="Operational Notes", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 10, text=advice)
    
    # FIX 2: Remove 'dest="S"'. Calling .output() without args returns the bytes automatically.
    return pdf.output()

# --- 3. REPORT INTERFACE ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Report Settings")
    # In a real app, you would pick dates here. For now, we get "All Data"
    report_type = st.selectbox("Select Report Type", ["Current Shift", "Last 24 Hours"])
    
    # Input for AI Notes (Optional manual override)
    manager_notes = st.text_area("Add Manager Notes:", "Standard operation. No critical faults detected.")
    
    generate_btn = st.button("Generate Report")

with col2:
    st.subheader("Preview")
    
    if generate_btn:
        # Fetch Data on Demand
        # In a real scenario, you'd filter WHERE Timestamp > ...
        df = pd.read_sql("SELECT * FROM production_logs", db_engine)
        
        if not df.empty:
            total_parts = df['Parts_Produced'].sum()
            total_scrap = df['Scrap_Count'].sum()
            scrap_rate = (total_scrap / total_parts * 100) if total_parts > 0 else 0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Show a quick summary on screen
            st.info(f"Report Period: All Data | Total Output: {total_parts}")
            
            # Generate PDF
            pdf_data = create_pdf(total_parts, scrap_rate, manager_notes, timestamp)
            b64 = base64.b64encode(pdf_data).decode()
            
            # Download Button
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Production_Report_{datetime.now().date()}.pdf" style="text-decoration:none; color:white; background-color:#d32f2f; padding:12px 24px; border-radius:5px; font-weight:bold;">⬇️ Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
            
        else:
            st.warning("No data found to generate report.")