import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Page Config
st.set_page_config(page_title="AI Technician", page_icon="🤖", layout="wide")
load_dotenv()

st.title("🤖 AI Maintenance Technician")

# --- 1. SETUP AI ---
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    st.error("OpenAI API Key not found. Please check your .env file.")

# --- 2. RAG ENGINE ---
def get_ai_response(user_query, manual_text):
    # Chunking
    chunks = [c.strip() for c in manual_text.split("\n\n") if c.strip()]
    
    # Embedding Helper
    def get_embedding(text):
        return client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding

    # Vector Search
    q_vector = get_embedding(user_query)
    chunk_embeddings = [get_embedding(c) for c in chunks]
    
    # Numpy Fix
    q_array = np.array(q_vector).reshape(1, -1)
    chunks_array = np.array(chunk_embeddings)
    
    # Find Match
    similarities = cosine_similarity(q_array, chunks_array)[0]
    best_index = np.argmax(similarities)
    best_chunk = chunks[best_index]
    
    # Generate Answer (GPT-5.1)
    prompt = f"""
    You are an expert industrial technician. 
    Answer the question based ONLY on the context below.
    
    CONTEXT:
    {best_chunk}
    
    QUESTION:
    {user_query}
    """
    
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content, best_chunk

# --- 3. MAIN UI ---
st.markdown("### Ask questions about maintenance protocols.")

# PATH FIX: We are inside 'pages/', so we need to go UP one level to find the manual
# OR we just find the absolute path to be safe.
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the main folder
parent_dir = os.path.dirname(current_dir)
manual_path = os.path.join(parent_dir, "machine_manual.txt")

if os.path.exists(manual_path):
    with open(manual_path, "r") as f:
        manual_text = f.read()
        
    # Chat Input
    user_question = st.text_area("Question:", height=100, placeholder="e.g., How do I fix Error E-404?")
    
    if st.button("Ask Manual"):
        if user_question:
            with st.spinner("Analyzing technical docs..."):
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
    st.error(f"⚠️ 'machine_manual.txt' not found at: {manual_path}")