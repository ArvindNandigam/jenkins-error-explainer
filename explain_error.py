# explain_error.py

from extract_error_features import extract_error_features
from retrieve_docs import retrieve_docs

SYSTEM_PROMPT = """
You are a Jenkins CI/CD expert.

Explain the Jenkins error using ONLY the provided documentation context.
If the documentation does not clearly explain the error, say so explicitly.

Output format:

Error Summary:
<short explanation>

Likely Causes:
- cause 1
- cause 2

Relevant Documentation:
- link or source file
"""

def explain_error(log_text: str):
    features = extract_error_features(log_text)
    category = features["category"]

    retrieved = retrieve_docs(category)

    explanation = {
        "error_category": category,
        "summary": "",
        "likely_causes": [],
        "references": []
    }

    # Heuristic explanation (v1, deterministic)
    if category == "groovy_syntax_error":
        explanation["summary"] = (
            "The pipeline failed due to a Groovy syntax error, "
            "most likely caused by an invalid or incomplete Jenkinsfile."
        )
        explanation["likely_causes"] = [
            "Missing or mismatched braces in the Jenkinsfile",
            "Invalid declarative pipeline structure"
        ]

    elif category == "missing_agent":
        explanation["summary"] = (
            "The pipeline attempted to execute a step that requires a node, "
            "but no agent was allocated."
        )
        explanation["likely_causes"] = [
            "Using 'agent none' without defining a stage-level agent",
            "Executing node-dependent steps without a workspace"
        ]

    elif category == "no_node_available":
        explanation["summary"] = (
            "The pipeline could not be scheduled because no Jenkins node "
            "matched the requested label."
        )
        explanation["likely_causes"] = [
            "The specified node label does not exist",
            "All matching nodes are offline or busy"
        ]

    elif category == "missing_plugin":
        explanation["summary"] = (
            "The pipeline referenced a step that is not available, "
            "indicating a missing or uninstalled plugin."
        )
        explanation["likely_causes"] = [
            "Required plugin is not installed",
            "Incorrect step name in the Jenkinsfile"
        ]

    elif category == "missing_credentials":
        explanation["summary"] = (
            "The pipeline referenced credentials that do not exist in Jenkins."
        )
        explanation["likely_causes"] = [
            "Credentials ID is incorrect or misspelled",
            "Credentials were not configured in Jenkins"
        ]

    elif category == "file_not_found":
        explanation["summary"] = (
            "The pipeline attempted to access a file that does not exist "
            "in the workspace."
        )
        explanation["likely_causes"] = [
            "File path is incorrect",
            "File was not generated or checked out"
        ]

    elif category == "git_authentication_error":
        explanation["summary"] = (
            "Jenkins failed to authenticate with the Git repository during checkout."
        )
        explanation["likely_causes"] = [
            "Invalid or missing Git credentials",
            "Repository requires token-based authentication"
        ]

    else:
        explanation["summary"] = (
            "The error could not be confidently explained using the available documentation."
        )

    for r in retrieved:
        explanation["references"].append(
            f"{r['meta']['source_file']} ({r['meta']['source']})"
        )
    if not retrieved:
        explanation["summary"] = (
            "No relevant Jenkins documentation was found for this error. "
            "The error may be plugin-specific or outside the current scope."
        )
        explanation["likely_causes"] = []
        explanation["references"] = []

    return explanation


if __name__ == "__main__":
    with open("data/errors/error_05.txt", "r", encoding="utf-8") as f:
        log = f.read()

    result = explain_error(log)
    for k, v in result.items():
        print(f"\n{k.upper()}:\n{v}")
