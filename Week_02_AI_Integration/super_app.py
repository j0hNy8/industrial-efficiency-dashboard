import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

from fpdf import FPDF
import base64

# --- 1. SETUP & CONFIG ---
st.set_page_config(layout="wide", page_title="Industrial AI Cockpit")
load_dotenv()

# Initialize AI Client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    st.error("OpenAI API Key not found. Please check your .env file.")

# --- 2. THE INTELLIGENCE ENGINE (RAG Function) ---
def get_ai_response(user_query, manual_text):
    # A. Chunking
    chunks = [c.strip() for c in manual_text.split("\n\n") if c.strip()]
    
    # B. Embedding Helper
    def get_embedding(text):
        return client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding

    # C. Vector Search
    # 1. Embed the user's question
    q_vector = get_embedding(user_query)
    # 2. Embed the manual chunks (In real life, we cache this!)
    chunk_embeddings = [get_embedding(c) for c in chunks]
    
    # 3. Convert to Numpy Arrays (The Fix!)
    q_array = np.array(q_vector).reshape(1, -1)
    chunks_array = np.array(chunk_embeddings)
    
    # 4. Find Match
    similarities = cosine_similarity(q_array, chunks_array)[0]
    best_index = np.argmax(similarities)
    best_chunk = chunks[best_index]
    
    # D. Generate Answer with GPT-5
    prompt = f"""
    You are an expert industrial technician. 
    Answer the question based ONLY on the context below.
    
    CONTEXT:
    {best_chunk}
    
    QUESTION:
    {user_query}
    """
    
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content, best_chunk


def create_pdf(total_parts, scrap_rate, advice):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    # MODERN SYNTAX: 'text=' and 'new_y="NEXT"'
    pdf.cell(200, 10, text="Shift Performance Report", new_x="LMARGIN", new_y="NEXT", align='C')
    
    # Metrics
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, text=f"Total Production: {total_parts} units", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, text=f"Scrap Rate: {scrap_rate:.2f}%", new_x="LMARGIN", new_y="NEXT")
    
    # AI Advice
    pdf.ln(10) # Line break
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, text="AI Maintenance Recommendations:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, text=advice)
    
    # MODERN RETURN: Returns bytes directly, no .encode() needed
    return pdf.output(dest="S")

# --- 3. THE USER INTERFACE ---
st.title("🏭 AI-Powered Industrial Analytics")

# Create two columns: Left for Data, Right for Chat
col1, col2 = st.columns([2, 1]) 

# === LEFT COLUMN: DATA DASHBOARD ===
with col1:
    st.header("📊 Live Production Data")
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload Shift Log (CSV)", type="csv")
    
    if uploaded_file:
        # Load Data
        df = pd.read_csv(uploaded_file)
        
        # KPI Cards
        kpi1, kpi2, kpi3 = st.columns(3)
        total_parts = df['Parts_Produced'].sum()
        # Handle cases where 'Scrap' column might not exist in older CSVs
        total_scrap = df['Scrap_Count'].sum() if 'Scrap_Count' in df.columns else 0
        scrap_rate = (total_scrap / total_parts * 100) if total_parts > 0 else 0

        kpi1.metric("Total Output", f"{total_parts} units")
        kpi2.metric("Total Scrap", f"{total_scrap} units")
        kpi3.metric("Scrap Rate", f"{scrap_rate:.2f}%")
        
        # Charts
        st.subheader("Production by Machine")

        # Create a custom chart figure
        fig, ax = plt.subplots()

        # Plot the data with a specific color (Hex code for Orange is #FFA500)
        # You can also use 'red', 'green', 'purple', etc.
        df.groupby("Machine_ID")["Parts_Produced"].sum().plot(kind='bar', ax=ax, color='#FFA500')

        # Add labels to make it professional
        plt.ylabel("Total Output")
        plt.title("Production Volume per Machine")

        # Display it in Streamlit
        st.pyplot(fig)
        
        # Raw Data Expander
        with st.expander("View Raw Logs"):
            st.dataframe(df)

        # === NEW PDF BUTTON HERE ===
        st.divider() # Adds a nice line

        # Generate PDF logic
        if st.button("📄 Generate PDF Report"):
            # Use dummy advice if they haven't asked the AI yet
            ai_advice_text = "Standard operation. No critical faults detected."
                    
            # Generate the PDF
            pdf_data = create_pdf(total_parts, scrap_rate, ai_advice_text)
                    
            # Create the download link (The "Magic" encoding)
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="shift_report.pdf" style="text-decoration:none; color:black; background-color:#FFA500; padding:10px; border-radius:5px;">Download PDF (Click Here)</a>'
                    
            # Show the link
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("👈 Upload a CSV file to see the dashboard.")

# === RIGHT COLUMN: AI TECHNICIAN ===
with col2:
    st.header("🤖 AI Technician")
    st.markdown("*Ask questions about maintenance protocols.*")
    
    # --- PATH FIX: Get the folder where THIS script is located ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    manual_path = os.path.join(current_dir, "machine_manual.txt")

    # Check if manual exists
    if os.path.exists(manual_path):
        # Read the manual
        with open(manual_path, "r") as f:
            manual_text = f.read()
            
        # Chat Input
        user_question = st.text_area("Question:", height=100, placeholder="e.g., How do I fix Error E-404?")
        
        if st.button("Ask Manual"):
            if user_question:
                with st.spinner("Searching manual..."):
                    try:
                        answer, source = get_ai_response(user_question, manual_text)
                        
                        st.success("Analysis Complete:")
                        st.write(answer)
                        
                        with st.expander("Show Source Context"):
                            st.info(source)
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please type a question.")
    else:
        st.error("⚠️ 'machine_manual.txt' not found in this folder.")