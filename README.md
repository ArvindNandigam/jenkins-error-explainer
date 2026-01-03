# Jenkins Error Explainer

A documentation-grounded system that explains Jenkins pipeline errors using official Jenkins documentation.

This project analyzes raw Jenkins build logs, extracts structured error signals, retrieves relevant documentation sections, and generates clear, human-readable explanations without relying on supervised training data.

---

## Motivation

Jenkins error logs are often verbose, difficult to interpret, and highly contextual.  
There is no standardized dataset of Jenkins errors or canonical explanations.

This project addresses that gap by:
- Using heuristic-based error feature extraction
- Grounding explanations strictly in official Jenkins documentation
- Avoiding hallucinated or unsafe advice

---

## What This Project Does

Given a Jenkins pipeline error log, the system:
1. Extracts key error signals (syntax errors, missing agents, missing plugins, etc.)
2. Retrieves relevant sections from Jenkins documentation
3. Generates a structured explanation including:
   - Error summary
   - Likely causes
   - Links to official documentation

---

## What This Project Does NOT Do

- Does not train or fine-tune a language model
- Does not rely on labeled error datasets
- Does not scrape community forums or StackOverflow

---

## Project Structure
jenkins-error-explainer/
│
├── extract_error_features.py
├── ingest_docs.py
├── retrieve_docs.py
├── explain_error.py
├── prompts.py
├── data/
│ ├── errors/
│ └── docs/
└── README.md


---

## Error Categories Covered

- Pipeline syntax errors (invalid Groovy, missing braces)
- Missing agent or unavailable nodes
- Missing plugins / undefined DSL methods
- Missing credentials
- Workspace and file system errors

---

## Example

**Input:**  
Raw Jenkins console output containing a pipeline failure.

**Output:**
Error Summary:
The pipeline failed due to a Groovy syntax error caused by a missing closing brace.

Likely Causes:

Unbalanced braces in the Jenkinsfile

Incorrect pipeline structure

Relevant Documentation:

https://www.jenkins.io/doc/book/pipeline/syntax/

---

## Design Principles

- Documentation-first retrieval (RAG)
- Heuristic-driven error understanding
- Explicit handling of uncertainty
- Reproducible and explainable behavior

---

## Future Extensions

- Jenkinsfile explanation support
- Plugin-aware error analysis
- CLI or web-based interface
- Version-aware documentation indexing

---

## Disclaimer

This project is an independent personal project and is not affiliated with or endorsed by the Jenkins project.

