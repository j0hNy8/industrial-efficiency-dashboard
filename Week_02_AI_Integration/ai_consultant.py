import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load the Secret Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Define the "Context"
machine_status = """
Machine: CNC_Lathe_05
Timestamp: 08:45 AM
Vibration: 4.5 mm/s (High)
Temperature: 65C (Normal)
Last Maintenance: 6 months ago
Error Code: E-404 (Spindle overload)
"""

print("--- Sending Data to AI Engineer (GPT-5) ---")

# 3. The Request
try:
    response = client.chat.completions.create(
        model="gpt-5", 
        messages=[
            {"role": "system", "content": "You are a Senior Maintenance Engineer. Analyze the machine status. Be concise. Suggest 3 immediate actions."},
            {"role": "user", "content": f"Here is the current machine log: {machine_status}"}
        ]
    )

    # 4. Extract the Answer (With Safety Net)
    advice = response.choices[0].message.content or "Error: AI returned no text."

    print("\n--- AI Diagnosis ---")
    print(advice)

    # 5. Save the Report
    with open("maintenance_advice.txt", "w") as f:
        f.write(advice)
    print("\nReport saved to 'maintenance_advice.txt'")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    print("Check your API Key or Model Name.")