# langchain_rag.py
# LangChain-based RAG pipeline for Jenkins error explanation

import os
import json
import tempfile
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
from langchain.chains import RetrievalQA

from extract_error_features import extract_error_features

RAW_DOCS_DIR = "data/docs/raw"
CHUNK_SIZE = 400

def load_raw_docs() -> List[Document]:
    """Load raw Jenkins documentation files and convert to LangChain Documents."""
    documents = []
    
    for fname in os.listdir(RAW_DOCS_DIR):
        path = os.path.join(RAW_DOCS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        
        chunks = chunk_text(text, CHUNK_SIZE)
        for chunk in chunks:
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "source_file": fname,
                    "source": "https://www.jenkins.io/doc/"
                }
            ))
    
    return documents

def chunk_text(text: str, size: int) -> List[str]:
    """Split text into chunks."""
    chunks = []
    for i in range(0, len(text), size):
        chunk = text[i:i+size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks

class JenkinsRAGChain:
    """LangChain-based RAG chain for Jenkins error explanation."""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        self.documents = load_raw_docs()
        self.vectorstore = FAISS.from_documents(
            self.documents,
            self.embeddings
        )
        
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        
        self.llm = HuggingFaceHub(
            repo_id="google/flan-t5-base",
            model_kwargs={"temperature": 0.3, "max_new_tokens": 256}
        )
        
        self.prompt = PromptTemplate(
            template="""You are a Jenkins CI/CD expert. Use the following context from 
official Jenkins documentation to explain the error.

Context from Jenkins documentation:
{context}

Error log to explain:
{question}

Provide a clear explanation with:
1. Error Summary
2. Likely Causes
3. Relevant Documentation links

If the documentation doesn't cover this error, say so explicitly.""",
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt},
            output_parser=StrOutputParser()
        )
    
    def explain_error(self, log_text: str) -> Dict[str, Any]:
        """Explain a Jenkins error using LangChain RAG."""
        features = extract_error_features(log_text)
        category = features["category"]
        
        enhanced_query = f"""
Error Category: {category}

Jenkins log:
{log_text}

Explain this error using the retrieved documentation.
"""
        
        result = self.qa_chain.invoke(enhanced_query)
        
        return {
            "error_category": category,
            "llm_explanation": result,
            "retrieval_source": "LangChain RAG (FAISS + HuggingFace)",
            "model_used": "google/flan-t5-base",
            "embedding_model": "paraphrase-MiniLM-L3-v2"
        }

def get_rag_chain() -> JenkinsRAGChain:
    """Get or create the RAG chain (singleton pattern for efficiency)."""
    if not hasattr(get_rag_chain, '_instance'):
        get_rag_chain._instance = JenkinsRAGChain()
    return get_rag_chain._instance


if __name__ == "__main__":
    print("Initializing LangChain RAG Chain...")
    print("=" * 50)
    
    rag = JenkinsRAGChain()
    
    sample_error = """
Started by user admin
org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:
WorkflowScript: 10: expecting '}', found '' @ line 10, column 1.
1 error
    at org.codehaus.groovy.control.ErrorNode.accept(ErrorNode.java:36)
    at org.codehaus.groovy.control.CompilationUnit$3.call(CompilationUnit.java:698)
    """
    
    print("\nSample Jenkins Error:")
    print(sample_error)
    print("=" * 50)
    
    result = rag.explain_error(sample_error)
    
    print("\nResult from LangChain RAG:")
    print(json.dumps(result, indent=2))
