# retrieve_docs.py

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "data/docs/docs.index"
META_PATH = "data/docs/docs_meta.json"
TOP_K = 5

QUERY_TEMPLATES = {
    "groovy_syntax_error": "Jenkins pipeline Groovy syntax error missing brace",
    "missing_agent": "Jenkins pipeline agent none requires node context",
    "no_node_available": "Jenkins no nodes with label scheduling executor",
    "missing_plugin": "Jenkins No such DSL method pipeline step",
    "missing_credentials": "Jenkins credentials not found pipeline",
    "file_not_found": "Jenkins pipeline workspace file not found",
    "git_authentication_error": "Jenkins git authentication failed checkout"
}
model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    cache_folder="./model_cache"
)

def retrieve_docs(error_category: str):

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    query = QUERY_TEMPLATES.get(
        error_category,
        "Jenkins pipeline error"
    )

    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, TOP_K)

    results = []
    for idx in indices[0]:
        results.append({
            "text": None,
            "meta": metadata[idx]
        })

    return results


if __name__ == "__main__":
    results = retrieve_docs("groovy_syntax_error")
    for r in results:
        print(r)