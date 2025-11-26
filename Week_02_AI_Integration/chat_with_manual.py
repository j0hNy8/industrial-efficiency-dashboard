import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 1. Setup
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("--- Indexing Knowledge Base ---")

# 2. Load and Chunk the Manual
# We split the manual into "Sections" so we can search them individually.
with open("machine_manual.txt", "r") as f:
    text = f.read()

# Split by double newlines (paragraphs)
chunks = text.split("\n\n")
chunks = [c.strip() for c in chunks if c.strip()] # Clean up empty lines

print(f"Found {len(chunks)} sections in the manual.")

# 3. Create Embeddings (Turn Text into Numbers)
# We ask OpenAI to convert our text chunks into vector lists
def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small" # Efficient and cheap model
    )
    return response.data[0].embedding

# Store the vectors in memory (In a real app, this goes into a Vector DB like Pinecone)
chunk_embeddings = []
for chunk in chunks:
    vector = get_embedding(chunk)
    chunk_embeddings.append(vector)

print("Knowledge Base Indexed! Ready for questions.")

# 4. The RAG Loop
print("\n--- Technical Support Bot (Type 'exit' to stop) ---")

while True:
    question = input("\nTechnician: ")
    if question.lower() in ['exit', 'quit']:
        break

    # A. Embed the User's Question
    question_vector = get_embedding(question)

    # B. Find the Best Match (Cosine Similarity)
    # Compare the question vector to all manual vectors
    similarities = cosine_similarity([question_vector], chunk_embeddings)[0]
    
    # Get the index of the highest score
    best_index = np.argmax(similarities)
    best_chunk = chunks[best_index]
    
    # C. Send ONLY the Best Chunk to GPT-5
    # This saves money and improves accuracy
    print(f"(Found relevant section: {best_chunk[:30]}...)") # Debug info
    
    prompt = f"""
    You are an expert maintenance assistant. 
    Answer the question based ONLY on the following context from the manual:
    
    CONTEXT:
    {best_chunk}
    
    QUESTION:
    {question}
    """
    
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )
    
    print(f"AI: {response.choices[0].message.content}")