import json
import boto3
from pathlib import Path
from chunk_documents import chunk_all_documents

session = boto3.Session(profile_name="migrateiq", region_name="ap-south-2")
client = session.client("bedrock-runtime")

EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
OUTPUT_FILE = Path("ingestion/vector_store.json")


def get_embedding(text: str) -> list[float]:
    """
    Calls Titan Text Embeddings V2 for one chunk of text.
    Why a separate function: we'll call this once per chunk in a loop,
    so isolating it here keeps the API-call logic in one place.
    """
    body = json.dumps({"inputText": text})

    response = client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    return response_body["embedding"]


def build_vector_store():
    chunks = chunk_all_documents()
    print(f"Embedding {len(chunks)} chunks...")

    vector_store = []
    total_input_tokens_estimate = 0

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk["text"])

        # Titan doesn't return token usage in this API version, so we
        # estimate roughly 1 token per 4 characters -- rough, but good
        # enough to sanity-check cost order of magnitude.
        total_input_tokens_estimate += len(chunk["text"]) // 4

        vector_store.append({
            "id": i,
            "source_file": chunk["source_file"],
            "chunk_type": chunk["chunk_type"],
            "text": chunk["text"],
            "embedding": embedding
        })
        print(f"  [{i+1}/{len(chunks)}] embedded chunk from {chunk['source_file']} "
              f"({len(embedding)} dimensions)")

    OUTPUT_FILE.write_text(json.dumps(vector_store, indent=2))
    print(f"\nSaved {len(vector_store)} vectors to {OUTPUT_FILE}")
    print(f"Estimated total input tokens used: ~{total_input_tokens_estimate}")


if __name__ == "__main__":
    build_vector_store()