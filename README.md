# Jenkins Error Explainer

Jenkins Error Explainer is a Python service and CLI that classifies Jenkins pipeline failures, retrieves related Jenkins documentation with semantic search, and returns deterministic, documentation-grounded troubleshooting guidance.

## Capabilities

- Classifies Groovy syntax, missing agent, unavailable node, missing plugin, missing credentials, missing file, Git authentication, timeout, out-of-memory, permission, Docker, and unknown errors.
- Extracts matched error signals and line numbers from raw Jenkins logs.
- Generates summaries and likely causes for supported categories.
- Uses Sentence Transformers and FAISS to retrieve the most relevant Jenkins documentation.
- Provides a LangChain retrieval path that returns documentation context and recommended actions.
- Serves REST endpoints with FastAPI and validates request bodies with Pydantic.
- Provides a CLI for explaining log files.
- Rebuilds the documentation index from raw Jenkins documentation.
- Runs locally, in Docker, or on Hugging Face Spaces.

This repository currently uses deterministic explanation templates. It does not call a live generative LLM; the semantic component is documentation retrieval.

## Architecture

```text
Jenkins log
    |
    v
Regex feature extraction and category detection
    |
    +--> Deterministic explanation templates
    |
    +--> Sentence Transformer query embedding
              |
              v
        FAISS documentation search
              |
              v
        Documentation references and guidance
```

## Tech stack

Python, FastAPI, Uvicorn, Pydantic, Sentence Transformers, HuggingFace, PyTorch, FAISS, NumPy, LangChain, Docker, Hugging Face Spaces, pytest.

## Repository layout

```text
app.py                    Hugging Face/Docker entry point
main.py                   FastAPI application and request models
cli.py                    Command-line log explainer
extract_error_features.py Regex classification and line extraction
error_taxonomy.py         Supported error patterns
explain_error.py          Deterministic explanation generation
retrieve_docs.py          Persistent FAISS retrieval
langchain_rag.py          In-memory LangChain retrieval pipeline
ingest_docs.py            Raw-document ingestion and FAISS index generation
benchmark.py              Reproducible performance measurements
tests/test_core.py        Focused regression tests
data/docs/raw/            Jenkins documentation source files
data/docs/docs.index      Bundled FAISS index
data/docs/docs_meta.json  Index metadata
data/errors/              Sample Jenkins logs
Dockerfile                Container deployment configuration
requirements.txt          Python dependencies
```

## Local setup

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

The Sentence Transformer model downloads on first use and is cached in `model_cache/`.

## Run the API

```bash
uvicorn main:app --reload
```

The API is available at `http://localhost:8000`. Interactive OpenAPI documentation is available at `/docs`.

### Endpoints

`GET /` returns service name, status, and available endpoints.

`POST /explain` accepts:

```json
{
  "log_text": "No such DSL method 'dockerBuild'"
}
```

`POST /explain-rag` accepts the same payload and returns retrieved documentation context through the LangChain path.

Example:

```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d "{\"log_text\":\"No such DSL method 'dockerBuild'\"}"
```

## Run the CLI

```bash
python cli.py data/errors/error_01.txt
```

The CLI prints the category, summary, likely causes, and documentation references. Missing files and unsupported categories are reported explicitly.

## Rebuild the FAISS index

```bash
python ingest_docs.py
```

The ingestion process reads `data/docs/raw/`, creates 400-character chunks, embeds them with `paraphrase-MiniLM-L3-v2`, and writes `data/docs/docs.index` plus `data/docs/docs_meta.json`.

## Performance measurement

Run the reproducible local benchmark:

```bash
python benchmark.py --iterations 5
python benchmark.py --iterations 5 --json
```

The benchmark reports:

- cold model warmup time
- classification latency
- warmed semantic retrieval latency
- end-to-end explanation latency
- p50 and p95 latency
- minimum, mean, and maximum latency
- explanation throughput in operations per second
- FAISS vector count and embedding dimensions

Model warmup is reported separately because the first run includes model loading. Compare warmed p50/p95 values across code changes, Python versions, and hardware. For production capacity planning, repeat the benchmark on the deployment hardware and include concurrent HTTP-load testing; the included benchmark is single-process and single-threaded.

## Testing and verification

Run the focused automated tests:

```bash
python -m pytest -q
```

The tests cover category detection, line-number extraction, new error categories, invalid input handling, explanation output, FAISS retrieval metadata safety, API validation, and index/metadata consistency.

Additional checks:

```bash
python -m compileall -q .
python cli.py data/errors/error_01.txt
python benchmark.py --iterations 1 --json
```

## Docker

```bash
docker build -t jenkins-error-explainer .
docker run --rm -p 7860:7860 jenkins-error-explainer
```

The container serves `main:app` on port `7860`.

## Deployment

The repository includes a Dockerfile and `app.py` entry point compatible with Hugging Face Spaces using the Docker SDK. Configure the Space to expose port `7860`, or run the same container on another platform.

## Resume-ready project description

### Full version

**Jenkins Error Explainer — AI-Assisted Jenkins Pipeline Troubleshooting System**

- Built a Python and FastAPI service that analyzes raw Jenkins pipeline logs and returns categorized, human-readable troubleshooting explanations.
- Implemented regex-based error feature extraction for Groovy syntax, missing agents, unavailable nodes, missing plugins, missing credentials, missing files, Git authentication, timeout, memory, permission, Docker, and unknown failures.
- Developed a deterministic explanation engine that maps error categories to summaries, likely causes, and documentation references.
- Built semantic Jenkins documentation retrieval using Sentence Transformers, 384-dimensional embeddings, and FAISS vector similarity search.
- Ingested raw Jenkins documentation into a persistent index containing 610 document vectors and metadata records.
- Added a LangChain retrieval pipeline with HuggingFace embeddings, FAISS vector stores, top-five retrieval, and documentation-grounded recommendations.
- Exposed validated REST APIs through FastAPI and added a CLI for processing Jenkins error-log files.
- Added reproducible performance benchmarking for model warmup, classification latency, retrieval latency, end-to-end latency, p50/p95 latency, throughput, and index scale.
- Added Docker and Hugging Face Spaces deployment support, model caching, sample error datasets, focused pytest regression tests, and index integrity checks.

### Short version

Built a FastAPI and CLI-based Jenkins troubleshooting system that classifies pipeline failures, extracts error signals, retrieves relevant Jenkins documentation using Sentence Transformers and FAISS, and produces deterministic explanations. Added LangChain retrieval, Docker deployment, Hugging Face Spaces support, persistent vector indexing, performance benchmarking, and automated regression tests.

### ATS skills

**Languages:** Python, regular expressions, JSON
**Backend:** FastAPI, Uvicorn, Pydantic, REST APIs
**AI/ML:** Sentence Transformers, HuggingFace, PyTorch, embeddings, retrieval-augmented generation
**Search:** FAISS, vector similarity search, metadata indexing
**Frameworks:** LangChain, LangChain Community, LangChain HuggingFace
**DevOps:** Docker, Hugging Face Spaces, model caching, CI/CD fundamentals
**Jenkins:** Jenkins pipelines, Jenkinsfiles, Groovy, agents, nodes, plugins, credentials, workspaces, Git checkout
**Testing:** pytest, smoke testing, API validation, benchmark testing, index integrity testing

## Current scope

The project is intentionally focused on Jenkins error classification and documentation retrieval. It does not execute Jenkins jobs, connect to a live Jenkins controller, modify repositories, or provide a generative LLM response. Those capabilities would be separate future extensions.
