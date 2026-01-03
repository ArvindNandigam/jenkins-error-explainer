# extract_error_features.py

import re
from error_taxonomy import ERROR_CATEGORIES

def extract_error_features(log_text: str) -> dict:
    result = {
        "category": "unknown",
        "matched_signals": [],
        "line_numbers": []
    }

    # Find error category
    for category, patterns in ERROR_CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, log_text):
                result["category"] = category
                result["matched_signals"].append(pattern)

    # Extract line numbers if present
    result["line_numbers"] = re.findall(r"line (\d+)", log_text)

    return result

if __name__ == "__main__":
    import os

    error_dir = "data/errors"

    for fname in os.listdir(error_dir):
        path = os.path.join(error_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            log = f.read()

        features = extract_error_features(log)
        print(f"\nFILE: {fname}")
        print(features)
