# cli.py

import sys
from explain_error import explain_error

def main():
    if len(sys.argv) != 2:
        print("Usage: python cli.py <path_to_jenkins_error_log>")
        sys.exit(1)

    log_path = sys.argv[1]

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            log_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found -> {log_path}")
        sys.exit(1)

    result = explain_error(log_text)

    if result["error_category"] == "unknown":
        print(
            "Warning: This error is not currently supported by the explainer. "
            "The explanation may be incomplete.\n"
        )

    print("\n=== Jenkins Error Explanation ===\n")
    print(f"Error Category:\n{result['error_category']}\n")

    print("Error Summary:")
    print(result["summary"], "\n")

    print("Likely Causes:")
    for cause in result["likely_causes"]:
        print(f"- {cause}")
    print()

    print("Relevant Documentation:")
    for ref in result["references"]:
        print(f"- {ref}")

    print("\n================================\n")


if __name__ == "__main__":
    main()
