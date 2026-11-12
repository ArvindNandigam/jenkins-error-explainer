import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Callable, List

import faiss

from explain_error import explain_error
from extract_error_features import extract_error_features
from retrieve_docs import retrieve_docs


ROOT = Path(__file__).resolve().parent
ERRORS_DIR = ROOT / "data" / "errors"


def percentile(values: List[float], value: float) -> float:
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[value - 1]


def measure(operation: Callable[[], object], iterations: int) -> List[float]:
    timings = []
    for _ in range(iterations):
        started = time.perf_counter()
        operation()
        timings.append((time.perf_counter() - started) * 1000)
    return timings


def summarize(values: List[float]) -> dict:
    return {
        "iterations": len(values),
        "min_ms": round(min(values), 3),
        "mean_ms": round(statistics.mean(values), 3),
        "p50_ms": round(percentile(values, 50), 3),
        "p95_ms": round(percentile(values, 95), 3),
        "max_ms": round(max(values), 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Jenkins Error Explainer")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("--iterations must be at least 1")

    logs = [
        path.read_text(encoding="utf-8")
        for path in sorted(ERRORS_DIR.glob("*.txt"))
    ]
    if not logs:
        raise RuntimeError(f"No sample logs found in {ERRORS_DIR}")

    # Warm up model loading before reporting steady-state operation timings.
    started = time.perf_counter()
    retrieve_docs("groovy_syntax_error", top_k=1)
    model_warmup_ms = (time.perf_counter() - started) * 1000

    classification_times = measure(
        lambda: [extract_error_features(log) for log in logs],
        args.iterations,
    )
    retrieval_times = measure(
        lambda: retrieve_docs("groovy_syntax_error", top_k=5),
        args.iterations,
    )
    explanation_times = measure(
        lambda: [explain_error(log) for log in logs],
        args.iterations,
    )

    index = faiss.read_index(str(ROOT / "data" / "docs" / "docs.index"))
    metrics = {
        "sample_logs": len(logs),
        "model_warmup_ms": round(model_warmup_ms, 3),
        "classification": summarize(classification_times),
        "retrieval": summarize(retrieval_times),
        "end_to_end_explanation": summarize(explanation_times),
        "throughput_explanations_per_second": round(
            len(logs) * args.iterations / (sum(explanation_times) / 1000),
            3,
        ),
        "faiss_vectors": index.ntotal,
        "faiss_dimensions": index.d,
    }

    if args.as_json:
        print(json.dumps(metrics, indent=2))
    else:
        print("Jenkins Error Explainer benchmark")
        for name, value in metrics.items():
            print(f"{name}: {value}")


if __name__ == "__main__":
    main()
