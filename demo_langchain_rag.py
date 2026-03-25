# demo_langchain_rag.py
# Demo script showcasing LangChain and RAG for internship interview
# Run: python demo_langchain_rag.py

import json
from langchain_rag import JenkinsRAGChain, get_rag_chain

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    print_section("LangChain + RAG Demo for Textify.ai Internship")
    print("\nThis demo showcases:")
    print("  • LangChain framework for building LLM chains")
    print("  • RAG (Retrieval-Augmented Generation) pattern")
    print("  • Vector search with FAISS + HuggingFace embeddings")
    print("  • Integration with Jenkins documentation")

    print_section("1. Initializing LangChain RAG Chain")
    print("Loading Jenkins documentation...")
    print("Creating vector embeddings with paraphrase-MiniLM-L3-v2...")
    print("Setting up RetrievalQA chain with FLAN-T5...")
    
    rag = JenkinsRAGChain()
    print("\n✓ RAG Chain initialized successfully!")
    print(f"  - Documents indexed: {len(rag.documents)}")
    print(f"  - Embedding model: {rag.embeddings.model_name}")
    print(f"  - LLM: {rag.llm.repo_id}")

    test_errors = [
        {
            "name": "Groovy Syntax Error",
            "log": """
Started by user admin
org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:
WorkflowScript: 10: expecting '}', found '' @ line 10, column 1.
1 error
    at org.codehaus.groovy.control.ErrorNode.accept(ErrorNode.java:36)
"""
        },
        {
            "name": "Missing Agent Error",
            "log": """
[Pipeline] node
Running on in /var/jenkins/workspace/test
[Pipeline] {
java.lang.IllegalStateException: agent none is specified, but no stage has an agent assigned
    at org.jenkinsci.plugins.workflow.cps.CpsFlowExecution.initialize(CpsFlowExecution.java:123)
"""
        },
        {
            "name": "Missing Plugin Error",
            "log": """
No such DSL method 'dockerBuild'
Available DSL methods: 
  archive
  bat
  build
  checkout
  deleteDir
  dir
  echo
  emailext
  fileExists
"""
        }
    ]

    for i, test in enumerate(test_errors, 1):
        print_section(f"2.{i} Testing: {test['name']}")
        print(f"\nInput Error Log:\n{test['log'][:200]}...")
        
        result = rag.explain_error(test['log'])
        
        print(f"\n--- Result ---")
        print(f"Error Category: {result['error_category']}")
        print(f"\nLLM Explanation (from RAG):")
        print(result['llm_explanation'])
        print(f"\n[Metadata]")
        print(f"  Retrieval: {result['retrieval_source']}")
        print(f"  LLM Model: {result['model_used']}")
        print(f"  Embeddings: {result['embedding_model']}")

    print_section("3. LangChain Architecture Summary")
    print("""
┌─────────────────────────────────────────────────────────────┐
│                    LangChain RAG Pipeline                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  User Error  │───▶│   Retriever  │───▶│     LLM      │  │
│  │    Log       │    │  (FAISS)     │    │  (FLAN-T5)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Feature    │    │   Context    │    │   Generated  │  │
│  │  Extraction  │    │  (Docs +     │    │   Explanation│  │
│  │              │    │  Prompt)     │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Key Components:
  • LangChain Core: Document, Prompt, OutputParser
  • LangChain Community: FAISS vectorstore
  • LangChain HuggingFace: Embeddings & LLM integration
  • RetrievalQA: End-to-end RAG chain
""")

    print_section("4. API Endpoint Demo")
    print("""
POST /explain-rag
{
  "log_text": "org.codehaus.groovy.control.MultipleCompilationErrorsException..."
}

Response:
{
  "error_category": "groovy_syntax_error",
  "llm_explanation": "The error indicates...",
  "retrieval_source": "LangChain RAG (FAISS + HuggingFace)",
  "model_used": "google/flan-t5-base",
  "embedding_model": "paraphrase-MiniLM-L3-v2"
}
""")

    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("=" * 60)
    print("""
To run the API server:
  uvicorn main:app --reload

To test the /explain-rag endpoint:
  curl -X POST http://localhost:8000/explain-rag \\
       -H "Content-Type: application/json" \\
       -d '{"log_text": "your error log here"}'
""")

if __name__ == "__main__":
    main()
