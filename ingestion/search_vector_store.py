import json
import boto3
import numpy as np
from pathlib import Path

session = boto3.Session(profile_name="migrateiq", region_name="ap-south-2")
client = session.client("bedrock-runtime")

EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
VECTOR_STORE_FILE = Path("ingestion/vector_store.json")


def embed_query(text: str) -> list[float]:
    """
    Embeds the USER'S QUESTION the exact same way we embedded our
    document chunks. This is critical: query and chunks must go through
    the same embedding model, or their vectors won't be comparable at all
    -- it's like measuring one thing in miles and another in kilometers.
    """
    body = json.dumps({"inputText": text})
    response = client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )
    return json.loads(response["body"].read())["embedding"]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search(query: str, top_k: int = 3):
    vector_store = json.loads(VECTOR_STORE_FILE.read_text())

    print(f"Query: {query}\n")
    query_embedding = embed_query(query)

    # Compute similarity of the query against EVERY stored chunk.
    # This is "brute-force" search -- fine at 16 chunks, would not
    # scale to millions (that's what a real vector DB like OpenSearch
    # optimizes with indexing algorithms like HNSW).
    scored_chunks = []
    for chunk in vector_store:
        score = cosine_similarity(query_embedding, chunk["embedding"])
        scored_chunks.append((score, chunk))

    # Sort by score descending, take the top_k most similar
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_matches = scored_chunks[:top_k]

    print(f"Top {top_k} matches:\n")
    for rank, (score, chunk) in enumerate(top_matches, 1):
        print(f"#{rank} | score={score:.4f} | {chunk['source_file']}")
        print(f"    {chunk['text'][:150].replace(chr(10), ' ')}...")
        print()

    return top_matches


if __name__ == "__main__":
    # Try a question that uses DIFFERENT words than the source text,
    # to prove semantic search works, not just keyword matching.
    search("How does Oracle simulate auto-incrementing primary keys?")