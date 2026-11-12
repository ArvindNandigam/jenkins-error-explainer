# retrieve_docs.py

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent
INDEX_PATH = PROJECT_ROOT / "data" / "docs" / "docs.index"
META_PATH = PROJECT_ROOT / "data" / "docs" / "docs_meta.json"
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
_model = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(
            "paraphrase-MiniLM-L3-v2",
            cache_folder=str(PROJECT_ROOT / "model_cache")
        )
    return _model


def retrieve_docs(error_category: str, top_k: int = TOP_K):
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    query = QUERY_TEMPLATES.get(
        error_category,
        "Jenkins pipeline error"
    )

    query_embedding = np.asarray(
        get_embedding_model().encode([query]),
        dtype=np.float32
    )
    _, indices = index.search(query_embedding, min(top_k, index.ntotal))

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(metadata):
            results.append({"text": None, "meta": metadata[idx]})

    return results


if __name__ == "__main__":
    results = retrieve_docs("Started by user Arvind Nandigam org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed: WorkflowScript: 10: expecting '}', found '' @ line 10, column 1.1 error")
    for r in results:
        print(r)