import json
from pathlib import Path

import faiss
import numpy as np
import pytest
from fastapi.testclient import TestClient

import explain_error as explanation_module
from extract_error_features import extract_error_features
from main import app
from retrieve_docs import retrieve_docs


ROOT = Path(__file__).resolve().parents[1]


def test_extracts_category_signals_and_line_number():
    result = extract_error_features(
        "MultipleCompilationErrorsException: WorkflowScript: 10: expecting '}'"
    )

    assert result["category"] == "groovy_syntax_error"
    assert "WorkflowScript" in result["matched_signals"]
    assert result["line_numbers"] == ["10"]


def test_extracts_new_error_categories():
    assert extract_error_features("java.lang.OutOfMemoryError: Java heap space")[
        "category"
    ] == "out_of_memory"
    assert extract_error_features("docker: Cannot connect to the Docker daemon")[
        "category"
    ] == "docker_error"


def test_explain_error_rejects_empty_input():
    with pytest.raises(ValueError, match="non-empty"):
        explanation_module.explain_error(" ")


def test_explain_error_returns_documented_explanation(monkeypatch):
    monkeypatch.setattr(
        explanation_module,
        "retrieve_docs",
        lambda category: [
            {"meta": {"source_file": "pipeline_syntax.txt", "source": "https://jenkins.io"}}
        ],
    )

    result = explanation_module.explain_error("Permission denied while accessing workspace")

    assert result["error_category"] == "permission_denied"
    assert result["likely_causes"]
    assert result["references"] == ["pipeline_syntax.txt (https://jenkins.io)"]


def test_retrieve_docs_uses_valid_metadata(monkeypatch):
    class FakeModel:
        def encode(self, texts):
            return np.zeros((len(texts), 384), dtype=np.float32)

    monkeypatch.setattr("retrieve_docs.get_embedding_model", lambda: FakeModel())
    results = retrieve_docs("groovy_syntax_error", top_k=2)

    metadata = json.loads(
        (ROOT / "data" / "docs" / "docs_meta.json").read_text(encoding="utf-8")
    )
    assert len(results) == 2
    assert all(result["meta"] in metadata for result in results)


def test_api_validates_requests_and_explains_error():
    client = TestClient(app)

    response = client.post(
        "/explain",
        json={"log_text": "No such DSL method 'dockerBuild'"},
    )
    assert response.status_code == 200
    assert response.json()["error_category"] == "missing_plugin"

    invalid_response = client.post("/explain", json={"log_text": ""})
    assert invalid_response.status_code == 422


def test_bundled_index_matches_metadata():
    index = faiss.read_index(str(ROOT / "data" / "docs" / "docs.index"))
    metadata = json.loads(
        (ROOT / "data" / "docs" / "docs_meta.json").read_text(encoding="utf-8")
    )

    assert index.ntotal == len(metadata)
    assert index.d == 384
