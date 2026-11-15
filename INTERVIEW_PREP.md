# Jenkins Error Explainer: Interview Preparation Guide

This guide turns the repository into a chapter-based interview curriculum. Study the
chapters in order, then use the question sections to rehearse your explanation.

## Project summary

Jenkins Error Explainer is a Python service and CLI that:

1. Accepts raw Jenkins pipeline logs.
2. Validates the input through FastAPI and Pydantic.
3. Classifies common Jenkins failures with compiled regular expressions.
4. Extracts matched signals and source line numbers.
5. Retrieves related Jenkins documentation with Sentence Transformers and FAISS.
6. Produces deterministic summaries, likely causes, and documentation references.

The project also includes a LangChain retrieval path, Docker/Hugging Face Spaces
deployment support, a persistent documentation index, regression tests, and a
reproducible benchmark.

**Truthful scope:** the current project analyzes logs and retrieves documentation. It
does not execute Jenkins jobs, connect to a Jenkins controller, modify Jenkinsfiles,
or generate explanations with a live LLM.

---

# Chapter 1: Problem, users, and scope

## Chapter summary

Jenkins logs contain useful diagnostic information, but the important failure signal
can be buried in a long build log. This project creates a small troubleshooting
service that turns recurring Jenkins failure messages into structured guidance.

## Subtopics

### 1.1 The problem

- Jenkins failures can be difficult for beginners to interpret.
- Similar failures may use different wording.
- Users need both a likely explanation and relevant Jenkins documentation.
- A useful first version should be predictable, easy to test, and easy to deploy.

### 1.2 The user workflow

```text
User copies Jenkins log
        |
        v
POST /explain or CLI command
        |
        v
Category + signals + line numbers
        |
        v
Documentation retrieval
        |
        v
Summary + causes + references
```

### 1.3 Implemented scope

- REST API through FastAPI.
- CLI for saved log files.
- Regex-based error categories.
- Semantic documentation retrieval.
- Deterministic explanation templates.
- Persistent FAISS index.
- LangChain retrieval demonstration.
- Docker and Hugging Face Spaces entry points.
- Tests and benchmark tooling.

### 1.4 Explicitly excluded scope

- Live Jenkins execution.
- Automatic Jenkinsfile editing.
- Direct Jenkins controller integration.
- Production monitoring.
- Live generative LLM responses.
- React or Gradio frontend.

## Interview questions

**What problem does the project solve?**

> It helps users interpret Jenkins pipeline errors by classifying raw logs, extracting
> useful signals, retrieving relevant Jenkins documentation, and returning concise
> troubleshooting guidance.

**Who would use it?**

> Developers, DevOps engineers, or Jenkins users who have a failed build log and need
> a quick explanation and documentation references.

---

# Chapter 2: System architecture

## Chapter summary

The system is intentionally modular. The API handles requests, the taxonomy stores
patterns, feature extraction identifies categories, retrieval searches documentation,
and explanation logic creates the response.

## Architecture flow

```text
                         +----------------------+
                         |  Jenkins error log   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | FastAPI + Pydantic   |
                         | request validation   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Feature extraction   |
                         | compiled regexes     |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Error category       |
                         | signals + line nums  |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Query template       |
                         | for detected class   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Sentence Transformer |
                         | 384-dim embedding    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | FAISS vector search  |
                         | top five results     |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Deterministic        |
                         | explanation template |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | JSON response        |
                         | summary + causes     |
                         +----------------------+
```

## Subtopics

### 2.1 Why a modular architecture?

- Each concern can be tested independently.
- The classifier can change without rewriting the API.
- Retrieval can change without rewriting explanation templates.
- The CLI and API share the same explanation function.
- Model loading and index access are isolated.

### 2.2 Why combine regex and embeddings?

Regex and embeddings solve different problems:

- Regex identifies known error categories precisely and cheaply.
- Embeddings find semantically related documentation despite wording differences.

### 2.3 Control path versus semantic path

The **control path** is deterministic:

```text
log -> regex -> category -> explanation
```

The **semantic path** supports documentation lookup:

```text
category -> query -> embedding -> FAISS -> references
```

This separation makes the output explainable and prevents the project from claiming
that a generative model produced the answer.

## Interview questions

**Why not use an LLM for the entire workflow?**

> Known Jenkins signatures are easier to classify deterministically. Regex is faster,
> cheaper, reproducible, and explainable. Semantic embeddings are used where they add
> value: finding related documentation.

**What is the main architectural limitation?**

> The system retrieves documentation but does not verify a fix against a live Jenkins
> build. It is an analysis assistant, not a Jenkins execution engine.

---

# Chapter 3: API layer and request contract

## Chapter summary

`main.py` exposes the application through FastAPI. Pydantic validates the input
before the core explanation logic runs.

## File: `main.py`

### Application creation

```python
app = FastAPI()
```

This creates the ASGI application used by Uvicorn.

### Request model

```python
class ExplainRequest(BaseModel):
    log_text: str = Field(..., min_length=1)
```

This defines the request contract:

- `log_text` must exist.
- It must be a string.
- It must contain at least one character.
- Invalid requests receive FastAPI validation errors, normally HTTP 422.

### Root endpoint

```python
@app.get("/")
def home():
    return {
        "name": "Jenkins Error Explainer API",
        "status": "ok",
        "endpoints": ["/explain", "/explain-rag"]
    }
```

The endpoint provides a simple service status response. It is informational rather
than a full dependency health check.

### Deterministic endpoint

```python
@app.post("/explain")
def explain(payload: ExplainRequest):
    return explain_error(payload.log_text)
```

The route is intentionally thin:

1. FastAPI validates the body.
2. The route extracts `log_text`.
3. `explain_error` performs the actual work.
4. The returned dictionary becomes JSON.

### LangChain endpoint

```python
@app.post("/explain-rag")
def explain_with_rag(payload: ExplainRequest):
    rag_chain = get_rag_chain()
    return rag_chain.explain_error(payload.log_text)
```

This uses the alternate LangChain retrieval path.

## API contract

### `POST /explain`

Request:

```json
{
  "log_text": "No such DSL method 'dockerBuild'"
}
```

Response shape:

```json
{
  "error_category": "missing_plugin",
  "summary": "...",
  "likely_causes": ["...", "..."],
  "references": ["..."]
}
```

### `POST /explain-rag`

Returns:

- `error_category`
- `documentation_explanation`
- `retrieved_docs`
- `retrieval_source`
- `embedding_model`

## Interview questions

**Why use Pydantic?**

> It moves input validation to the API boundary, gives clients predictable errors,
> and prevents missing or malformed request fields from reaching business logic.

**Why keep route functions thin?**

> Thin routes make the system easier to test and reuse. The CLI can call the same
> explanation function without duplicating API logic.

---

# Chapter 4: Error taxonomy and feature extraction

## Chapter summary

The classification system is built from a category dictionary and a compiled-pattern
layer. The classifier returns the primary category, every matched signal, and any
line numbers found in the log.

## File: `error_taxonomy.py`

The `ERROR_CATEGORIES` dictionary maps category names to regex patterns.

Implemented categories:

- `groovy_syntax_error`
- `missing_agent`
- `no_node_available`
- `git_authentication_error`
- `missing_credentials`
- `missing_plugin`
- `file_not_found`
- `timeout_error`
- `out_of_memory`
- `permission_denied`
- `docker_error`

If no pattern matches, extraction returns `unknown`.

## Pattern examples

### Groovy syntax

```python
"groovy_syntax_error": [
    r"MultipleCompilationErrorsException",
    r"expecting '\}'",
    r"WorkflowScript"
]
```

These patterns target common Jenkinsfile parser errors.

### Missing plugin

```python
"missing_plugin": [
    r"No such DSL method",
    r"No such step"
]
```

These messages commonly indicate an unavailable pipeline step.

### Git authentication

```python
"git_authentication_error": [
    r"Authentication failed",
    r"Invalid username or token",
    r"Error cloning remote repo"
]
```

## File: `extract_error_features.py`

### Pattern compilation

```python
COMPILED_PATTERNS = {
    cat: [re.compile(p) for p in pats]
    for cat, pats in ERROR_CATEGORIES.items()
}
```

Patterns are compiled once when the module loads rather than repeatedly during
each request.

### Type validation

```python
if not isinstance(log_text, str):
    raise TypeError("log_text must be a string")
```

This prevents regex operations from receiving unsupported values.

### Initial result

```python
result = {
    "category": "unknown",
    "matched_signals": [],
    "line_numbers": []
}
```

Unknown is the safe default.

### Category detection

```python
for category, patterns in COMPILED_PATTERNS.items():
    for pattern in patterns:
        if pattern.search(log_text):
            if result["category"] == "unknown":
                result["category"] = category
            result["matched_signals"].append(pattern.pattern)
```

Important behavior:

- Every pattern is checked.
- The first matching category becomes primary.
- Additional matching patterns are retained as signals.
- Dictionary order therefore acts as an implicit precedence rule.

### Line-number extraction

```python
result["line_numbers"] = re.findall(
    r"(?:line\s+|WorkflowScript:\s*)(\d+)",
    log_text,
    flags=re.IGNORECASE,
)
```

This recognizes examples such as:

```text
line 10
WorkflowScript: 10
```

## Trade-offs

### Strengths

- Fast.
- Deterministic.
- Easy to debug.
- Easy to test.
- No generation model required.

### Limitations

- Unknown wording can be missed.
- Overlapping categories can create precedence issues.
- Regex patterns need maintenance.
- No confidence score is returned.

## Interview questions

**What happens when multiple categories match?**

> The first matching category becomes primary, while every matching pattern is stored
> in `matched_signals`. The dictionary order currently determines precedence.

**How would you make this more robust?**

> Add explicit priorities or confidence scores, normalize log text, add labeled test
> fixtures, and evaluate precision, recall, and F1 across real Jenkins logs.

---

# Chapter 5: Deterministic explanation generation

## Chapter summary

`explain_error.py` is the application layer that combines classification, retrieval,
and user-facing explanation text.

## Input guard

```python
if not isinstance(log_text, str) or not log_text.strip():
    raise ValueError("log_text must be a non-empty string")
```

This catches direct Python calls containing empty or whitespace-only input.

## Explanation flow

```python
features = extract_error_features(log_text)
category = features["category"]
retrieved = retrieve_docs(category)
```

The category is detected first, then used to select a semantic search query.

## Stable response schema

```python
explanation = {
    "error_category": category,
    "summary": "",
    "likely_causes": [],
    "references": []
}
```

A stable schema makes the response easy for API clients and CLI formatting.

## Category-specific behavior

Each supported category fills:

- A short summary.
- Two likely causes.

Examples:

### Missing plugin

Summary:

> The pipeline referenced a step that is not available, indicating a missing or
> uninstalled plugin.

Causes:

- Required plugin is not installed.
- Incorrect step name in the Jenkinsfile.

### Permission denied

Summary:

> The Jenkins process lacks permission to access a file, command, or resource.

Causes:

- The Jenkins service account lacks permission.
- Workspace or external-resource ownership is restrictive.

### Unknown category

The system communicates uncertainty instead of inventing a diagnosis.

## Reference construction

```python
for r in retrieved:
    explanation["references"].append(
        f"{r['meta']['source_file']} ({r['meta']['source']})"
    )
```

Retrieved metadata becomes readable source references.

## Empty retrieval behavior

If no documents are retrieved:

- The summary is replaced with an uncertainty message.
- Likely causes are cleared.
- References are cleared.

This prevents the service from presenting unsupported advice as reliable.

## Interview questions

**Why deterministic explanations instead of generated text?**

> The current repository does not actually call a generative LLM. Deterministic
> templates are predictable, testable, and truthful about the implementation.

**What is the role of retrieved documents if the summary is templated?**

> Retrieval supplies relevant documentation references and supports the documentation
> grounded nature of the response. The category explanation remains deterministic.

---

# Chapter 6: Embeddings and FAISS retrieval

## Chapter summary

The project uses semantic retrieval to find Jenkins documentation related to the
detected error category.

## File: `retrieve_docs.py`

### Project-root paths

```python
PROJECT_ROOT = Path(__file__).resolve().parent
INDEX_PATH = PROJECT_ROOT / "data" / "docs" / "docs.index"
META_PATH = PROJECT_ROOT / "data" / "docs" / "docs_meta.json"
```

Using source-relative paths makes execution independent of the current working
directory.

### Query templates

Examples:

```python
"groovy_syntax_error":
    "Jenkins pipeline Groovy syntax error missing brace"

"missing_plugin":
    "Jenkins No such DSL method pipeline step"
```

The templates convert a category into a more descriptive semantic search query.

### Lazy model loading

```python
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(...)
    return _model
```

Benefits:

- Importing the API does not immediately load the model.
- Tests can import modules without paying the full model startup cost.
- The model is loaded once and reused.

### Input validation

```python
if top_k < 1:
    raise ValueError("top_k must be at least 1")
```

Invalid retrieval sizes fail explicitly.

### FAISS loading

```python
index = faiss.read_index(str(INDEX_PATH))
```

The path is converted to a string because the FAISS Python binding expects a
string path in this environment.

### Query embedding

```python
query_embedding = np.asarray(
    get_embedding_model().encode([query]),
    dtype=np.float32
)
```

FAISS expects numeric arrays in a compatible format. The query becomes a
384-dimensional float32 vector.

### Search

```python
_, indices = index.search(
    query_embedding,
    min(top_k, index.ntotal)
)
```

The search returns the nearest vector positions. The number of requested results
is capped by the number of vectors actually in the index.

### Metadata bounds safety

```python
if 0 <= idx < len(metadata):
    results.append({"text": None, "meta": metadata[idx]})
```

This prevents invalid positions from producing incorrect metadata references.

## Retrieval scale

Verified bundled data:

```text
Raw documentation files: 7
Indexed chunks:          610
Vector dimensions:       384
Default top_k:           5
```

## FAISS design choice

The project uses `IndexFlatL2`, an exact nearest-neighbor index.

Why it fits this project:

- The corpus is small.
- Exact search is simple.
- No separate vector service is required.
- Behavior is easy to understand and test.

## Interview questions

**What is an embedding?**

> It is a numeric representation of text. Semantically related text tends to have
> vectors that are closer together under the selected distance function.

**What does FAISS store?**

> FAISS stores vectors and returns nearest-vector positions. Human-readable source
> metadata is stored separately in JSON.

**Why do vector count and metadata count need to match?**

> FAISS returns integer positions. Each position must map to the correct metadata
> record, otherwise references could point to the wrong documentation.

---

# Chapter 7: LangChain retrieval path

## Chapter summary

`langchain_rag.py` demonstrates a LangChain-based retrieval implementation. It
loads raw documents, chunks them, embeds them, builds an in-memory FAISS store,
retrieves five documents, and formats the retrieved context.

## Chunking

```python
def chunk_text(text: str, size: int) -> List[str]:
    chunks = []
    for i in range(0, len(text), size):
        chunk = text[i:i+size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks
```

The current chunk size is 400 characters.

## Document loading

Each chunk becomes a LangChain `Document`:

```python
Document(
    page_content=chunk,
    metadata={
        "source_file": fname,
        "source": "https://www.jenkins.io/doc/"
    }
)
```

## Chain initialization

The constructor:

1. Creates CPU HuggingFace embeddings.
2. Loads raw documents.
3. Builds a LangChain FAISS vector store.
4. Creates a retriever with `k=5`.

## Explanation formatting

`generate_explanation`:

- Joins retrieved document content.
- Limits the context to 1,500 characters.
- Adds a generic analysis.
- Adds suggested Jenkins troubleshooting actions.
- States that the explanation is grounded in Jenkins documentation.

## Singleton behavior

```python
if not hasattr(get_rag_chain, "_instance"):
    get_rag_chain._instance = JenkinsRAGChain()
return get_rag_chain._instance
```

This avoids rebuilding the in-memory chain for every `/explain-rag` request within
the process.

## Important distinction

This is retrieval plus deterministic formatting. It is not a live FLAN-T5 or
other generative LLM pipeline.

---

# Chapter 8: Offline ingestion and data preparation

## Chapter summary

`ingest_docs.py` builds the persisted FAISS index used by `retrieve_docs.py`.

## Ingestion flow

```text
Raw Jenkins text files
        |
        v
Sorted file iteration
        |
        v
400-character chunks
        |
        v
Sentence Transformer embeddings
        |
        v
IndexFlatL2 FAISS index
        |
        +--> docs.index
        |
        +--> docs_meta.json
```

## Important implementation decisions

### Sorted files

Files are processed in sorted order to make document ordering reproducible.

### Metadata

Each chunk receives:

- `source_file`
- `source`

### Index dimension

```python
index = faiss.IndexFlatL2(embeddings.shape[1])
```

The index dimension is derived from the model output rather than hardcoded.

### Persistence

The index is written to:

```text
data/docs/docs.index
```

Metadata is written to:

```text
data/docs/docs_meta.json
```

## Interview questions

**Why generate the index offline?**

> Embedding documentation is a preparation step. Building the index ahead of
> requests avoids re-embedding every document for every user request.

**What happens if the raw documentation changes?**

> Running `python ingest_docs.py` rebuilds the vector index and metadata file from
> the current raw documents.

---

# Chapter 9: CLI and deployment

## Chapter summary

The repository supports direct CLI usage and containerized API deployment.

## File: `cli.py`

### Argument handling

The CLI requires exactly one file path:

```text
python cli.py <path_to_jenkins_error_log>
```

### File handling

The log is read as UTF-8. Missing files produce a clear message and exit code 1.

### Shared logic

The CLI calls the same `explain_error` function as the API. This avoids behavior
drift between interfaces.

### Human-readable output

The CLI prints:

- Error category.
- Error summary.
- Likely causes.
- Relevant documentation.

## File: `app.py`

`app.py` imports the FastAPI application and starts Uvicorn at:

```text
0.0.0.0:7860
```

This supports hosted environments such as Hugging Face Spaces.

## File: `Dockerfile`

The container:

1. Uses `python:3.10-slim`.
2. Sets `/app` as the working directory.
3. Copies the repository.
4. Installs `requirements.txt`.
5. Starts `uvicorn main:app` on port 7860.

## Commands

```bash
uvicorn main:app --reload
python cli.py data/errors/error_01.txt
docker build -t jenkins-error-explainer .
docker run --rm -p 7860:7860 jenkins-error-explainer
```

---

# Chapter 10: Testing and verification

## Chapter summary

The repository contains focused regression tests and additional smoke checks.

## Test file: `tests/test_core.py`

### Category and signal test

Verifies:

- Groovy syntax category detection.
- `WorkflowScript` signal capture.
- Line-number extraction.

### New-category test

Verifies:

- `OutOfMemoryError` maps to `out_of_memory`.
- Docker daemon failure maps to `docker_error`.

### Input validation test

Verifies whitespace-only input raises `ValueError`.

### Explanation test

Monkeypatches retrieval and verifies:

- Permission category selection.
- Causes are populated.
- References are formatted correctly.

### Retrieval test

Uses a fake embedding model and the real index to verify:

- Requested result count.
- Returned metadata belongs to the bundled metadata set.

### API test

Uses FastAPI `TestClient` to verify:

- A valid plugin error returns HTTP 200.
- Empty input returns HTTP 422.

### Index consistency test

Verifies:

```text
FAISS vector count == metadata record count
FAISS dimension == 384
```

## Verified commands

```bash
python -m pytest -q
python -m compileall -q .
python cli.py data/errors/error_01.txt
python demo_langchain_rag.py
```

Verified result:

```text
7 pytest tests passed
compileall passed
API smoke test passed
CLI smoke test passed
LangChain demo passed
```

## What the tests do not prove

- Classification accuracy on a large labeled dataset.
- Retrieval relevance quality.
- Concurrent production throughput.
- Live Jenkins compatibility.
- Deployment networking.
- LLM hallucination behavior.

## Interview questions

**Why test index consistency?**

> The index returns vector positions, while metadata is stored separately. Matching
> counts are a basic integrity guarantee that positions map safely to metadata.

**What would you test next?**

> I would add labeled category accuracy, retrieval Recall@5, MRR, concurrent HTTP
> tests, malformed-index tests, and fixtures for every supported category.

---

# Chapter 11: Performance metrics

## Chapter summary

`benchmark.py` measures the cost of the main processing stages and records
retrieval scale.

## Benchmark command

```bash
python benchmark.py --iterations 5
python benchmark.py --iterations 5 --json
```

## Metrics measured

### Model warmup

Measures the first retrieval call, including embedding model loading.

Verified value:

```text
6888.347 ms
```

Why it matters:

- Shows cold-start cost.
- Matters for hosted or autoscaling environments.
- Should be separated from warmed request latency.

### Classification latency

Measures regex classification over all eight bundled logs.

Verified mean:

```text
1.49 ms
```

### Retrieval latency

Measures semantic query embedding and FAISS lookup.

Verified mean:

```text
47.174 ms
```

### End-to-end explanation latency

Measures explanation processing over the sample logs.

Verified mean:

```text
247.571 ms
```

### Throughput

The benchmark calculates:

```text
number of explanations processed
--------------------------------
total elapsed seconds
```

Verified local value:

```text
32.314 explanations/second
```

### p50 and p95

- p50 shows typical middle-case latency.
- p95 exposes tail latency.
- Mean alone can hide occasional slow runs.

## Metric interpretation

These are local, single-process baselines. They are not production SLAs because
the benchmark does not include concurrent HTTP users, multiple workers, deployment
networking, CPU/memory monitoring, or long repeated runs.

## Interview answer

**How did you measure performance?**

> I used `time.perf_counter()` around classification, retrieval, and end-to-end
> operations. I measured model warmup separately, summarized min/mean/p50/p95/max,
> calculated throughput from total explanations divided by elapsed seconds, and
> reported FAISS vector count and embedding dimensions as scale metrics.

---

# Chapter 12: Design decisions and trade-offs

## Chapter summary

The project favors a small, explainable, local architecture over a distributed
production platform.

## Decision 1: Regex classification

**Why chosen**

- Fast.
- Deterministic.
- Easy to debug.
- Easy to test.
- Works well for recognizable Jenkins messages.

**Trade-off**

- New wording may not match.
- Patterns require maintenance.

## Decision 2: Sentence Transformers

**Why chosen**

- Captures semantic similarity.
- Works locally.
- Produces compact vectors.

**Trade-off**

- Model download and warmup add startup cost.
- Retrieval quality depends on model and query design.

## Decision 3: FAISS

**Why chosen**

- Simple local vector search.
- No separate service.
- Appropriate for 610 vectors.

**Trade-off**

- Not a distributed vector database.
- Persistent and in-memory paths are separate implementations.

## Decision 4: Deterministic templates

**Why chosen**

- Truthful current implementation.
- Predictable output.
- Easy to test.
- Avoids unsupported generation claims.

**Trade-off**

- Less flexible language than an LLM.
- Explanations must be manually maintained.

## Decision 5: Pydantic validation

**Why chosen**

- Clear request contract.
- Automatic API documentation.
- Consistent validation errors.

## Decision 6: Lazy model loading

**Why chosen**

- Avoids model loading during every import.
- Improves test startup.
- Reuses the model after first use.

## Decision 7: Source-relative paths

**Why chosen**

- Works from different working directories.
- Works on Windows.
- Works in Docker and hosted environments.

## Decision 8: Shared core between API and CLI

**Why chosen**

- Prevents duplicate logic.
- Keeps behavior consistent.
- Makes both interfaces easier to maintain.

---

# Chapter 13: Stabilization work and corrections

## Chapter summary

The repository was reviewed against its actual runtime behavior. Documentation and
code were corrected when claims and implementation did not match.

## Corrections made

- Removed unsupported live FLAN-T5 generation claims.
- Corrected frontend claims; the repository provides FastAPI and CLI interfaces.
- Added formal pytest regression tests.
- Added timeout, out-of-memory, permission, and Docker categories.
- Fixed Windows `Path` objects passed to FAISS by converting them to strings.
- Fixed line-number extraction for `WorkflowScript: 10`.
- Added source-relative paths for indexes, documents, and model cache.
- Added lazy embedding-model loading.
- Fixed Windows console encoding issues in the demo.
- Added benchmark tooling.
- Updated README to describe implemented behavior only.

## Interview answer

**What did you personally improve?**

> I validated the project against its actual runtime behavior, corrected unsupported
> claims, made file paths portable, added input validation and missing categories,
> added regression tests, fixed demo/runtime issues, and added reproducible
> performance measurement.

---

# Chapter 14: Complete file map

| File | Interview topic |
|---|---|
| `main.py` | FastAPI application and API contract |
| `app.py` | Uvicorn/Hugging Face entry point |
| `error_taxonomy.py` | Error categories and pattern design |
| `extract_error_features.py` | Regex matching and line extraction |
| `explain_error.py` | Deterministic explanation generation |
| `retrieve_docs.py` | Persistent FAISS retrieval |
| `langchain_rag.py` | LangChain document retrieval |
| `ingest_docs.py` | Offline document indexing |
| `cli.py` | Log-file command-line workflow |
| `benchmark.py` | Latency and throughput measurement |
| `tests/test_core.py` | Regression and API tests |
| `Dockerfile` | Container packaging |
| `requirements.txt` | Runtime dependencies |
| `data/docs/raw/` | Jenkins documentation source |
| `data/docs/docs.index` | Persisted vectors |
| `data/docs/docs_meta.json` | Vector metadata |
| `data/errors/` | Sample error logs |
| `README.md` | Crisp implementation documentation |

---

# Chapter 15: Interview scripts

## 15.1 Thirty-second answer

> I built a Jenkins troubleshooting service using Python and FastAPI. It accepts
> Jenkins logs, classifies common failures with deterministic regex patterns,
> extracts signals and line numbers, retrieves relevant Jenkins documentation with
> Sentence Transformers and FAISS, and returns summaries, likely causes, and
> references. I also added a CLI, LangChain retrieval path, Docker support,
> regression tests, and reproducible performance benchmarking.

## 15.2 Two-minute answer

> The project has two processing paths. The main `/explain` path validates the log,
> uses compiled regex patterns to identify the first matching Jenkins error category,
> records all matched signals and line numbers, retrieves category-specific Jenkins
> documentation through a Sentence Transformer and FAISS, and creates a deterministic
> explanation. The `/explain-rag` path demonstrates LangChain document loading,
> embeddings, in-memory FAISS retrieval, and deterministic formatting of retrieved
> context.
>
> I selected regex because common Jenkins signatures are highly recognizable and
> deterministic classification is easy to test. I selected embeddings and FAISS
> because documentation may use different wording from the raw error. The index
> contains 610 vectors with 384 dimensions. I added Pydantic validation, source-
> relative paths, lazy model loading, Docker support, a CLI, regression tests, and
> a benchmark. The local benchmark measured 6.888 seconds of model warmup,
> 1.49 ms classification, 47.174 ms retrieval, 247.571 ms end-to-end explanation,
> and 32.314 explanations per second in a single-process run.

## 15.3 Honest limitation answer

> The system is an explainability and documentation-retrieval tool, not a Jenkins
> execution platform. It does not connect to a live controller, verify fixes, or
> generate text with a live LLM. That limitation is intentional in the current
> implementation and is documented clearly.

---

# Final study checklist

- [ ] Explain the problem in one sentence.
- [ ] Draw the request-to-response architecture.
- [ ] Explain why regex and embeddings are both used.
- [ ] Explain how 610 vectors and 384 dimensions were obtained.
- [ ] Explain the difference between the persistent and LangChain retrieval paths.
- [ ] Name the API endpoints and response fields.
- [ ] Explain the CLI workflow.
- [ ] Describe all test categories.
- [ ] Explain warmup, latency, p50, p95, and throughput.
- [ ] State the exact limitations without overclaiming.
- [ ] Explain at least three trade-offs.
- [ ] Give the thirty-second and two-minute project descriptions.
