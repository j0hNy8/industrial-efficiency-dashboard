import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. The Title
st.title("🏭 Factory Efficiency Dashboard")
st.write("Upload your daily logs to generate instant insights.")

# 2. The File Uploader (The "Magic Button")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # 3. Read the Data (Just like before, but from the memory buffer)
    df = pd.read_csv(uploaded_file)
    
    st.success("File uploaded successfully!")
    
    # 4. Show Raw Data (Optional checkbox)
    if st.checkbox("Show Raw Data"):
        st.write(df)

    # 5. The Metrics (The "KPI Cards")
    total_parts = df['Parts_Produced'].sum()
    avg_cycle = df[df['Status'] == 'RUN']['Cycle_Time_Sec'].mean()
    
    # Create 3 columns for layout
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Parts", f"{total_parts} pcs")
    col2.metric("Avg Cycle Time", f"{avg_cycle:.2f} sec")
    col3.metric("Scrap Rate", "0.5%") # Placeholder logic

    # 6. The Chart
    st.subheader("Production by Machine")
    
    # Create the figure
    fig, ax = plt.subplots()
    summary = df.groupby('Machine_ID')['Parts_Produced'].sum()
    summary.plot(kind='bar', ax=ax, color='teal')
    plt.ylabel("Count")
    
    # Show it in the app
    st.pyplot(fig)

else:
    st.info("Awaiting CSV upload...")