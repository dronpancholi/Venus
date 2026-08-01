#!/usr/bin/env python3
"""
Venus Naming Convention Validator.

Checks that all files in the repository conform to Venus naming standards.

Usage:
  python3 check_naming.py [--repo-path /path/to/Venus]
"""

import argparse
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Allowed naming patterns
PATTERNS = {
    "OS_ROOT": re.compile(r"^V\d+\.\d+_[A-Z][A-Z_]+\.md$"),
    "PART": re.compile(r"^(PART|MODULE)_\d+_[A-Z][A-Z_\d]+\.md$"),
    "ENGINE": re.compile(r"^ENGINE_[A-Z][A-Z_\d]+\.md$"),
    "TEMPLATE": re.compile(r"^(TEMPLATE_\d+_[A-Z][A-Z_\d]+|[A-Z][A-Z_\d]+)\.md$"),
    "STAGE": re.compile(r"^STAGE_\d+_[A-Z][A-Z_\d]+\.md$"),
    "SCHEMA": re.compile(r"^[A-Z][A-Z_\d]+_SCHEMA\.json$"),
    "CONSTITUTION": re.compile(r"^UVCOS\.md$"),
    "PYTHON": re.compile(r"^[a-z][a-z_]+\.py$"),
    "YAML": re.compile(r"^[a-z][a-z_]+\.(yaml|yml)$"),
    "MARKDOWN_DOC": re.compile(r"^[A-Z][A-Z_]+\.md$"),
}

# Excluded directories
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv"}


def main():
    parser = argparse.ArgumentParser(description="Venus Naming Validator")
    parser.add_argument("--repo-path", type=str, default=str(ROOT_DIR))
    parser.add_argument("--fix", action="store_true", help="Report potential fixes")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    errors = []
    warnings = []
    checked = 0

    for f in sorted(repo_path.rglob("*")):
        if not f.is_file():
            continue
        if any(excl in f.parts for excl in EXCLUDE_DIRS):
            continue
        if f.name.startswith("."):
            continue

        rel = f.relative_to(repo_path)
        parent_name = f.parent.name
        fname = f.name

        # Determine expected pattern based on location
        expected = _expected_pattern(parent_name, fname)

        if expected:
            checked += 1
            if not PATTERNS[expected].match(fname):
                errors.append(f"  FAIL {rel}: expected {expected} pattern")

        # Check for typos in filenames
        typos = _check_typos(fname)
        for typo in typos:
            warnings.append(f"  TYPO {rel}: '{typo[0]}' should be '{typo[1]}'")

    print(f"\n── Naming Validation Results ──")
    print(f"  Files checked: {checked}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print("\nErrors:")
        for e in errors[:20]:
            print(e)
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")

    if warnings:
        print("\nWarnings:")
        for w in warnings[:10]:
            print(w)
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")

    if errors:
        sys.exit(1)


def _expected_pattern(parent: str, fname: str) -> str | None:
    parent_lower = parent.lower()

    if parent_lower.endswith("parts") or parent_lower.endswith("modules"):
        if fname.startswith("ENGINE_"):
            return "ENGINE"
        return "PART"

    if parent_lower.endswith("templates"):
        return "TEMPLATE"

    if parent_lower.endswith("stages"):
        return "STAGE"

    if parent_lower in ("_schemas", "schemas"):
        return "SCHEMA" if fname.endswith(".json") else "MARKDOWN_DOC"

    if parent_lower.startswith("layer_") and parent_lower.endswith("constitution"):
        return "CONSTITUTION" if fname.startswith("UVCOS") else "MARKDOWN_DOC"

    if parent_lower in ("_validation",):
        return "PYTHON" if fname.endswith(".py") else "MARKDOWN_DOC"

    if parent_lower in ("_registry", "_graph"):
        if fname.endswith((".json", ".cypher")):
            return None  # Auto-generated files, naming not enforced
        return "PYTHON" if fname.endswith(".py") else "MARKDOWN_DOC"

    if fname.startswith("V") and "_" in fname and fname.endswith(".md"):
        return "OS_ROOT"

    # Catch-all for markdown files in any directory
    if fname.endswith(".md") and fname[0].isupper():
        return "MARKDOWN_DOC"

    return None


TYPO_MAP = {
    "docker": "DOCKER",
    "dei": "DEI",
    "onboarding": "ONBOARDING",
    "offboarding": "OFFBOARDING",
}


def _check_typos(fname: str) -> list:
    found = []
    stem = Path(fname).stem.upper()
    for wrong, correct in TYPO_MAP.items():
        if wrong.upper() in stem and correct not in stem:
            found.append((wrong, correct))
    return found


if __name__ == "__main__":
    main()
