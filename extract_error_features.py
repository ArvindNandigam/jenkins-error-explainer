import re
from error_taxonomy import ERROR_CATEGORIES

COMPILED_PATTERNS = {
    cat: [re.compile(p) for p in pats]
    for cat, pats in ERROR_CATEGORIES.items()
}

def extract_error_features(log_text: str) -> dict:
    result = {
        "category": "unknown",
        "matched_signals": [],
        "line_numbers": []
    }

    for category, patterns in COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(log_text):
                result["category"] = category
                result["matched_signals"].append(pattern.pattern)

    result["line_numbers"] = re.findall(r"line (\d+)", log_text)

    return result
