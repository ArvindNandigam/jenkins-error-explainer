# ingest_docs.py

import os
import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DOCS_DIR = PROJECT_ROOT / "data" / "docs" / "raw"
INDEX_PATH = PROJECT_ROOT / "data" / "docs" / "docs.index"
META_PATH = PROJECT_ROOT / "data" / "docs" / "docs_meta.json"

CHUNK_SIZE = 400

def chunk_text(text, size):
    chunks = []
    for i in range(0, len(text), size):
        chunk = text[i:i+size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def main():
    model = SentenceTransformer(
        "paraphrase-MiniLM-L3-v2",
        cache_folder=str(PROJECT_ROOT / "model_cache")
    )

    documents = []
    metadata = []

    for fname in sorted(os.listdir(RAW_DOCS_DIR)):
        path = RAW_DOCS_DIR / fname
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text, CHUNK_SIZE)
        for chunk in chunks:
            documents.append(chunk)
            metadata.append({
                "source_file": fname,
                "source": f"https://www.jenkins.io/doc/"
            })

    embeddings = model.encode(documents)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Ingested {len(documents)} document chunks.")

if __name__ == "__main__":
    main()
