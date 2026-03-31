import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("surveillance-rag")

model = SentenceTransformer("all-MiniLM-L6-v2")

if not os.path.exists("events.txt"):
    print("Run detection first")
    exit()

with open("events.txt") as f:
    events = [line.strip() for line in f if line.strip()]

vectors = []

for i, event in enumerate(events):
    emb = model.encode(event).tolist()
    vectors.append({
        "id": str(i),
        "values": emb,
        "metadata": {"text": event}
    })

batch_size = 1000
for i in range(0, len(vectors), batch_size):
    index.upsert(vectors=vectors[i:i+batch_size])

print("✅ Stored in Pinecone")