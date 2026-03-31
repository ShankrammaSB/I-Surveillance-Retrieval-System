from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("surveillance-rag")

model = SentenceTransformer("all-MiniLM-L6-v2")


def query_rag(query):
    emb = model.encode(query).tolist()

    res = index.query(vector=emb, top_k=50, include_metadata=True)

    events = [m["metadata"]["text"] for m in res["matches"]]

    # remove duplicates + limit
    events = list(set(events))[:20]

    people_counts = []
    suspicious_count = 0

    for e in events:
        if "people=" in e:
            try:
                num = int(e.split("people=")[1].split(",")[0])
                people_counts.append(num)
            except:
                pass

        if "Suspicious" in e:
            suspicious_count += 1

    query = query.lower()

    if "people" in query:
        return f"Max people detected: {max(people_counts) if people_counts else 0}"

    elif "suspicious" in query:
        return f"Suspicious events detected: {suspicious_count}"

    else:
        return f"Summary → Max people: {max(people_counts) if people_counts else 0}, Suspicious: {suspicious_count}"