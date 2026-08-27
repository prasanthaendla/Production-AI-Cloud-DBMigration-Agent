import re
from pathlib import Path

SAMPLE_DATA_DIR = Path("docs/sample-data")

def chunk_sql_file(filepath: Path) -> list[dict]:
    """
    Splits a SQL file into chunks along CREATE statement boundaries.
    Why: each CREATE (TABLE/SEQUENCE/TRIGGER/PACKAGE) is a self-contained
    unit of meaning -- splitting mid-statement would produce a chunk with
    no coherent meaning, which would embed poorly and retrieve badly.
    """
    text = filepath.read_text(encoding="utf-8")

    # Split on lines starting with CREATE (case-insensitive), keeping
    # the CREATE keyword attached to the chunk that follows it.
    pattern = r"(?=^CREATE\s)"
    raw_chunks = re.split(pattern, text, flags=re.MULTILINE | re.IGNORECASE)

    chunks = []
    for raw in raw_chunks:
        cleaned = raw.strip()
        if cleaned:  # skip empty fragments (e.g., leading comments-only block)
            chunks.append({
                "source_file": filepath.name,
                "chunk_type": "sql_statement",
                "text": cleaned
            })
    return chunks


def chunk_markdown_file(filepath: Path) -> list[dict]:
    """
    Splits a Markdown file into chunks along '##' section headers.
    Why: each section is already a self-contained idea (one SCT finding
    per section), so this naturally matches how a user will ask questions
    ("what does the report say about ROWNUM?").
    """
    text = filepath.read_text(encoding="utf-8")

    pattern = r"(?=^#{2,3}\s)"
    raw_chunks = re.split(pattern, text, flags=re.MULTILINE)

    chunks = []
    for raw in raw_chunks:
        cleaned = raw.strip()
        if cleaned:
            chunks.append({
                "source_file": filepath.name,
                "chunk_type": "markdown_section",
                "text": cleaned
            })
    return chunks


def chunk_all_documents() -> list[dict]:
    all_chunks = []
    for filepath in SAMPLE_DATA_DIR.glob("*"):
        if filepath.suffix == ".sql":
            all_chunks.extend(chunk_sql_file(filepath))
        elif filepath.suffix == ".md":
            all_chunks.extend(chunk_markdown_file(filepath))
    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_documents()
    print(f"Total chunks created: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} [{chunk['source_file']} / {chunk['chunk_type']}] ---")
        print(chunk["text"][:150].replace("\n", " ") + "...")
        print()