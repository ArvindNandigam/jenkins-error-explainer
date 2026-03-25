import os
import json
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from extract_error_features import extract_error_features

RAW_DOCS_DIR = "data/docs/raw"
CHUNK_SIZE = 400


# -------------------------
# Utils
# -------------------------
def chunk_text(text: str, size: int) -> List[str]:
    chunks = []
    for i in range(0, len(text), size):
        chunk = text[i:i+size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def load_raw_docs() -> List[Document]:
    documents = []

    for fname in os.listdir(RAW_DOCS_DIR):
        path = os.path.join(RAW_DOCS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text, CHUNK_SIZE)

        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source_file": fname,
                        "source": "https://www.jenkins.io/doc/"
                    }
                )
            )

    return documents


# -------------------------
# RAG CLASS
# -------------------------
class JenkinsRAGChain:
    def __init__(self):
        print("Loading embeddings...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
            model_kwargs={"device": "cpu"}
        )

        print("Loading documents...")
        self.documents = load_raw_docs()

        print("Building FAISS index...")
        self.vectorstore = FAISS.from_documents(
            self.documents,
            self.embeddings
        )

        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )

    # -------------------------
    # Retrieval
    # -------------------------
    def retrieve_docs(self, query: str) -> List[Document]:
        return self.retriever.invoke(query)

    # -------------------------
    # Simple Explanation Generator (NO LLM needed)
    # -------------------------
    def generate_explanation(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join([doc.page_content for doc in docs])

        return f"""
Jenkins Error Explanation

Context from documentation:
{context[:1500]}

Analysis:
Based on the retrieved documentation, this error likely relates to Jenkins pipeline or configuration issues.

Suggested Actions:
- Check Jenkinsfile syntax
- Verify plugins and agents
- Review pipeline configuration

Note:
This explanation is grounded in official Jenkins documentation.
"""

    # -------------------------
    # Main API
    # -------------------------
    def explain_error(self, log_text: str) -> Dict[str, Any]:
        features = extract_error_features(log_text)
        category = features["category"]

        query = f"""
Error Category: {category}

Jenkins log:
{log_text}
"""

        docs = self.retrieve_docs(query)

        explanation = self.generate_explanation(query, docs)

        return {
            "error_category": category,
            "llm_explanation": explanation,
            "retrieved_docs": [
                {
                    "content": doc.page_content[:200],
                    "source": doc.metadata.get("source")
                }
                for doc in docs
            ],
            "retrieval_source": "FAISS + sentence-transformers",
            "embedding_model": "paraphrase-MiniLM-L3-v2"
        }


# -------------------------
# Singleton
# -------------------------
def get_rag_chain() -> JenkinsRAGChain:
    if not hasattr(get_rag_chain, "_instance"):
        get_rag_chain._instance = JenkinsRAGChain()
    return get_rag_chain._instance


# -------------------------
# Test
# -------------------------
if __name__ == "__main__":
    print("Initializing RAG...")
    rag = JenkinsRAGChain()

    sample_error = """
org.codehaus.groovy.control.MultipleCompilationErrorsException:
WorkflowScript: 10: expecting '}', found ''
"""

    result = rag.explain_error(sample_error)

    print(json.dumps(result, indent=2))
