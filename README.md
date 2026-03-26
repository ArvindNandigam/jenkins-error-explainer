# 🔧 Jenkins Error Explainer

<p align="center">
  <img src="https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=Jenkins&logoColor=white" alt="Jenkins">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-FF6B6B?style=for-the-badge&logo=Chainlink&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/FAISS-4A90D9?style=for-the-badge" alt="FAISS">
  <img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=HuggingFace&logoColor=black" alt="HuggingFace">
</p>

An AI-powered system that explains Jenkins pipeline errors using **Retrieval-Augmented Generation (RAG)** and **LangChain**. The system analyzes raw Jenkins build logs, extracts error signals, retrieves relevant documentation, and generates clear, human-readable explanations.

---

## 🚀 Demo

**Live Demo:** [Jenkins Error Explainer on HuggingFace Spaces](https://huggingface.co/spaces/Arvind2006/jenkins-error-explainer)

Try pasting a Jenkins error log like:
```
org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:
WorkflowScript: 10: expecting '}', found '' @ line 10, column 1
```

---

## 🏗️ Architecture

This project implements a **RAG (Retrieval-Augmented Generation)** pipeline using:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Error Log      │────▶│  Error Detection │────▶│  Category       │
│  (User Input)   │     │  (Heuristics)    │     │  Classification │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌────────┴────────┐
│  User-Friendly  │◀────│  Explanation     │◀────│  Documentation  │
│  Response       │     │  Generation      │     │  Retrieval      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          ▲
                                                          │
                                                  ┌───────┴───────┐
                                                  │   FAISS       │
                                                  │   Vector Store │
                                                  │   + LangChain  │
                                                  └───────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **LLM Framework** | LangChain |
| **Vector Database** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | Sentence-Transformers (all-MiniLM-L6-v2) |
| **LLM** | Google FLAN-T5-Base (via HuggingFace Hub) |
| **API Framework** | FastAPI |
| **Frontend** | Gradio / HTML + JavaScript |
| **Deployment** | HuggingFace Spaces |

---

## 📁 Project Structure

```
jenkins-error-explainer/
├── app.py                    # FastAPI app with Gradio UI
├── main.py                   # Original FastAPI endpoints
├── explain_error.py          # Core error explanation logic
├── extract_error_features.py # Error feature extraction
├── retrieve_docs.py          # FAISS-based document retrieval
├── langchain_rag.py          # LangChain RAG pipeline
├── ingest_docs.py            # Build FAISS index from docs
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── README.md                 # This file
├── data/
│   ├── docs/
│   │   ├── docs.index        # FAISS vector index
│   │   ├── docs_meta.json    # Document metadata
│   │   └── raw/              # Raw Jenkins documentation
│   └── errors/               # Sample error logs
└── model_cache/              # Cached embedding models
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- pip or conda

### Clone the Repository

```bash
git clone https://github.com/ArvindNandigam/jenkins-error-explainer.git
cd jenkins-error-explainer
```

### Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Using conda
conda create -n jenkins-env python=3.10
conda activate jenkins-env
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Download Models (First Run)

Models are automatically downloaded on first use. To pre-download:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## 💻 Usage

### Option 1: Run Locally with FastAPI

```bash
uvicorn app:app --reload
```

Then open http://localhost:8000 in your browser.

### Option 2: Run with Gradio Interface

```bash
python app.py
```

Then open http://localhost:7860 in your browser.

### Option 3: Use the LangChain RAG Chain Directly

```python
from langchain_rag import JenkinsRAGChain

rag = JenkinsRAGChain()
result = rag.explain_error("""
org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:
WorkflowScript: 10: expecting '}', found ''
""")

print(result)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with UI |
| `/explain` | POST | Explain a Jenkins error |

### Example Request

```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"log_text": "org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed"}'
```

---

## 📦 Build the RAG Index

If you want to rebuild the FAISS vector index from documentation:

```bash
python ingest_docs.py
```

This will:
1. Load raw Jenkins documentation from `data/docs/raw/`
2. Chunk the documents
3. Generate embeddings using sentence-transformers
4. Store in FAISS index at `data/docs/docs.index`

---

## ☁️ Deployment

### Deploy to HuggingFace Spaces

1. **Create a HuggingFace Space:**
   - Go to https://huggingface.co/spaces/new
   - Select "Static" SDK for instant deployment
   - Or "Docker" for FastAPI/Gradio

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update"
   git push origin master
   ```

3. **Or use the upload script:**
   ```bash
   python upload_to_hf_spaces.py
   ```

### Deploy to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Configure for Python/Flask/FastAPI

---

## 🎯 Error Categories Supported

| Category | Description |
|----------|-------------|
| `groovy_syntax_error` | Pipeline syntax errors (missing braces, invalid structure) |
| `missing_agent` | No agent allocated for pipeline execution |
| `no_node_available` | No Jenkins node matches requested label |
| `missing_plugin` | Required plugin not installed or step unavailable |
| `missing_credentials` | Referenced credentials don't exist |
| `file_not_found` | File doesn't exist in workspace |
| `git_authentication_error` | Git authentication failed during checkout |
| `timeout_error` | Pipeline or step exceeded timeout |
| `out_of_memory` | Build ran out of memory |
| `permission_denied` | Insufficient permissions |
| `docker_error` | Docker build/pull failed |

---

## 🔬 How It Works

### 1. Error Feature Extraction (`extract_error_features.py`)

Uses heuristic pattern matching to detect error categories from log text:

```python
def extract_error_features(log_text: str) -> dict:
    # Pattern matching for different error types
    if "groovy" in log.lower() and "syntax" in log.lower():
        category = "groovy_syntax_error"
    # ... more patterns
    return {"category": category, "features": features}
```

### 2. Documentation Retrieval (`retrieve_docs.py`)

Uses FAISS vector similarity search:

```python
def retrieve_docs(error_category: str):
    # Load FAISS index
    index = faiss.read_index(INDEX_PATH)
    
    # Generate query embedding
    query_embedding = model.encode([query])
    
    # Search similar documents
    distances, indices = index.search(query_embedding, TOP_K)
    return results
```

### 3. LangChain RAG Chain (`langchain_rag.py`)

Full LangChain implementation for LLM-powered explanations:

```python
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub

chain = RetrievalQA.from_chain_type(
    llm=HuggingFaceHub(repo_id="google/flan-t5-base"),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)
```

---

## 📝 Example Output

**Input:**
```
Started by user admin
org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:
WorkflowScript: 10: expecting '}', found '' @ line 10, column 1
```

**Output:**
```json
{
  "error_category": "groovy_syntax_error",
  "summary": "The pipeline failed due to a Groovy syntax error, most likely caused by an invalid or incomplete Jenkinsfile.",
  "likely_causes": [
    "Missing or mismatched braces in the Jenkinsfile",
    "Invalid declarative pipeline structure"
  ],
  "references": [
    "Pipeline Syntax Reference (Jenkins.io)",
    "Declarative Pipeline Documentation"
  ]
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [Jenkins Documentation](https://www.jenkins.io/doc/) - For providing the documentation used in RAG
- [LangChain](https://python.langchain.com/) - For the RAG framework
- [HuggingFace](https://huggingface.co/) - For models and Spaces hosting
- [FAISS](https://faiss.ai/) - For efficient vector similarity search

---

## 📞 Contact

- **Author:** Arvind Nandigam
- **GitHub:** [@ArvindNandigam](https://github.com/ArvindNandigam)
- **HuggingFace:** [@Arvind2006](https://huggingface.co/Arvind2006)

---

<p align="center">Made with ❤️ for Jenkins Developers</p>
