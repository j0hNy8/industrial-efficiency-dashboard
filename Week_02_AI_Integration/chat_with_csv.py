import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("--- Loading Factory Data ---")

# 2. Load the Data from Week 1
# We go "up one level" (..) then down into Week_01
try:
    df = pd.read_csv('../Week_01_Foundations/production_log.csv')
    print("Data Loaded Successfully.")
except FileNotFoundError:
    print("Error: Could not find the CSV. Check your folder structure!")
    exit()

# 3. Prepare the Context (The "Briefing")
# We convert the dataframe to a string so the AI can read it.
# To save money/tokens, we only send the column names and the first 20 rows.
# For small files (like ours), we can send the whole thing.
csv_context = df.to_markdown(index=False)

system_prompt = f"""
You are an AI Data Analyst for a Manufacturing Plant.
You have access to the following production logs:

{csv_context}

Rules:
1. Answer based ONLY on this data.
2. If the user asks for calculations (sums, averages), perform them accurately.
3. Be concise and professional.
"""

# 4. The Chat Loop
print("\n--- AI Analyst Ready (Type 'exit' to stop) ---")

while True:
    user_question = input("\nYou: ")
    
    if user_question.lower() in ['exit', 'quit']:
        print("Closing session.")
        break
        
    # Send to GPT-5
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
    )
    
    answer = response.choices[0].message.content
    print(f"AI: {answer}")