# Jenkins Error Explainer

Jenkins Error Explainer is a Python service and CLI that classifies Jenkins pipeline errors, retrieves related Jenkins documentation, and returns deterministic troubleshooting guidance.

## Architecture

```text
Jenkins log
    |
    v
FastAPI/Pydantic validation
    |
    v
Regex-based feature extraction
    |
    +--> Error category, matched signals, line numbers
    |
    v
Category-specific documentation query
    |
    v
Sentence Transformer embedding
    |
    v
FAISS nearest-neighbor search
    |
    v
Deterministic explanation
    |
    v
Summary, likely causes, and references
```

## Built capabilities

- Accepts Jenkins error logs through FastAPI REST endpoints.
- Accepts Jenkins error-log files through a command-line interface.
- Validates API input with Pydantic.
- Detects these categories:
  - Groovy syntax errors
  - Missing agents
  - Unavailable Jenkins nodes
  - Missing plugins or DSL steps
  - Missing credentials
  - Missing workspace files
  - Git authentication failures
  - Timeout errors
  - Out-of-memory errors
  - Permission errors
  - Docker errors
  - Unknown errors
- Extracts matched regex signals and Jenkins source line numbers.
- Generates category-specific summaries and likely causes.
- Retrieves relevant Jenkins documentation with Sentence Transformers and FAISS.
- Stores 610 documentation vectors with 384-dimensional embeddings.
- Provides a LangChain retrieval path using HuggingFace embeddings and an in-memory FAISS store.
- Rebuilds the persistent documentation index from raw Jenkins documentation.
- Supports Docker and Hugging Face Spaces deployment.
- Caches the embedding model after first use.
- Includes benchmark measurements for startup, latency, throughput, and index size.
- Includes focused pytest regression tests and FAISS index consistency checks.

The current explanation output is deterministic and documentation-grounded. The project does not execute Jenkins jobs, connect to a Jenkins controller, modify Jenkinsfiles, or generate responses with a live LLM.

## Technology stack

**Backend:** Python, FastAPI, Uvicorn, Pydantic

**Search and embeddings:** Sentence Transformers, HuggingFace, FAISS, NumPy, PyTorch

**Retrieval framework:** LangChain

**Deployment:** Docker, Hugging Face Spaces

**Testing:** pytest, Python compilation checks, API smoke tests, CLI smoke tests

## Project structure

```text
app.py                    Hugging Face/Docker entry point
main.py                   FastAPI application and request model
cli.py                    Command-line log explainer
error_taxonomy.py         Error categories and regex patterns
extract_error_features.py Classification, signals, and line numbers
explain_error.py          Deterministic explanation generation
retrieve_docs.py          Persistent FAISS retrieval
langchain_rag.py          LangChain retrieval pipeline
ingest_docs.py            Raw-document ingestion and index generation
benchmark.py              Performance benchmark
tests/test_core.py        Regression tests
data/docs/raw/            Jenkins documentation source files
data/docs/docs.index      Persisted FAISS index
data/docs/docs_meta.json  Vector metadata
data/errors/              Sample Jenkins error logs
Dockerfile                Container configuration
requirements.txt          Python dependencies
```

## Setup

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

The `paraphrase-MiniLM-L3-v2` embedding model downloads on first use and is cached in `model_cache/`.

## Run the API

```bash
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

### Endpoints

#### `GET /`

Returns the service name, status, and available endpoints.

#### `POST /explain`

Request:

```json
{
  "log_text": "No such DSL method 'dockerBuild'"
}
```

Response fields:

```json
{
  "error_category": "missing_plugin",
  "summary": "...",
  "likely_causes": ["...", "..."],
  "references": ["..."]
}
```

#### `POST /explain-rag`

Accepts the same request body and returns:

- Detected error category
- Documentation-grounded explanation
- Retrieved documentation snippets
- Retrieval implementation
- Embedding model name

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

The CLI prints the detected category, summary, likely causes, and documentation references. Missing files and unsupported categories are reported explicitly.

## Build the documentation index

```bash
python ingest_docs.py
```

The ingestion pipeline:

1. Reads files from `data/docs/raw/`.
2. Splits documentation into 400-character chunks.
3. Generates `paraphrase-MiniLM-L3-v2` embeddings.
4. Stores vectors in `data/docs/docs.index`.
5. Stores source metadata in `data/docs/docs_meta.json`.

The bundled index contains 610 vectors and 610 matching metadata records. Each vector has 384 dimensions.

## Performance benchmark

```bash
python benchmark.py --iterations 5
python benchmark.py --iterations 5 --json
```

The benchmark reports:

- Model warmup time
- Classification latency
- Semantic retrieval latency
- End-to-end explanation latency
- Minimum, mean, p50, p95, and maximum latency
- Explanation throughput
- FAISS vector count and dimensions

Verified local baseline:

```text
Sample logs:                     8
Model warmup:                    6888.347 ms
Classification mean:             1.49 ms
Retrieval mean:                  47.174 ms
End-to-end explanation mean:     247.571 ms
Measured throughput:             32.314 explanations/second
FAISS vectors:                   610
Embedding dimensions:            384
```

These values are single-process local measurements from the bundled benchmark.

## Testing

```bash
python -m pytest -q
python -m compileall -q .
python cli.py data/errors/error_01.txt
python demo_langchain_rag.py
```

The automated tests cover:

- Error category detection
- Signal and line-number extraction
- Timeout, memory, permission, and Docker categories
- Empty-input handling
- Explanation output
- Retrieval metadata safety
- FastAPI request validation
- FAISS vector and metadata consistency

Verified result: **7 pytest tests passed**.

## Docker

```bash
docker build -t jenkins-error-explainer .
docker run --rm -p 7860:7860 jenkins-error-explainer
```

The container serves `main:app` through Uvicorn on port `7860`.

## Resume description

Built a Python and FastAPI Jenkins troubleshooting service that classifies pipeline failures with deterministic regex patterns, extracts error signals and line numbers, retrieves Jenkins documentation using Sentence Transformers and FAISS, and returns summaries, likely causes, and references. Added a CLI, LangChain retrieval pipeline, persistent vector indexing, Pydantic validation, Docker and Hugging Face Spaces support, regression tests, and reproducible performance benchmarking.
