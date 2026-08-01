#!/usr/bin/env python3
"""
Venus Template Placeholder Checker.

Scans template files for placeholder patterns that should not appear
in production-ready artifacts.

Usage:
  python3 check_templates.py [--repo-path /path/to/Venus] [--fix]
"""

import argparse
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

PLACEHOLDER_PATTERNS = [
    # Bracketed text that is NOT a markdown link [text](url), NOT a checkbox, NOT a numbered ref
    (re.compile(r"(?<!!)\[(?!\s*[xX]\s*\])(?!\s*\])(?!\d+\])(?!.*?\]\()([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\]"), "camel-case bracket [Like This]"),
    (re.compile(r"\be\.g\.,?\s", re.IGNORECASE), "'e.g.' example pattern"),
    (re.compile(r"\bTODO\b", re.IGNORECASE), "'TODO' marker"),
    (re.compile(r"\bFIXME\b", re.IGNORECASE), "'FIXME' marker"),
    (re.compile(r"\binsert\s+(your\s+)?(text|code|content|name|details)\s+here\b", re.IGNORECASE), "'insert ... here' pattern"),
    # Bracket patterns with descriptor keywords
    (re.compile(r"\[(?:Name|Description|Title|Value|Count|ID|UUID|Date|Timestamp|Owner|Status|Action|Reason|Notes?|Details|Summary)\]"), "descriptor keyword placeholder [Name]"),
]

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "_validation"}


def main():
    parser = argparse.ArgumentParser(description="Venus Template Checker")
    parser.add_argument("--repo-path", type=str, default=str(ROOT_DIR))
    parser.add_argument("--fix", action="store_true",
                        help="Print fix suggestions")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    errors = []
    warnings = []
    checked = 0

    for f in sorted(repo_path.rglob("*.md")):
        if any(excl in f.parts for excl in EXCLUDE_DIRS):
            continue
        if ".venv" in str(f):
            continue

        # Only check files in templates directories
        if "templates" not in str(f.parent).lower():
            continue

        content = f.read_text(errors="replace")
        rel = f.relative_to(repo_path)
        checked += 1
        file_errors = []

        for pattern, desc in PLACEHOLDER_PATTERNS:
            for m in pattern.finditer(content):
                line_num = content[:m.start()].count("\n") + 1
                file_errors.append(f"    L{line_num}: {desc} -> '{m.group()[:60]}'")

        if file_errors:
            errors.append(f"  {rel}")
            errors.extend(file_errors)

    print(f"\n── Template Validation Results ──")
    print(f"  Templates checked: {checked}")
    print(f"  Files with placeholders: {len(errors)}")

    if errors:
        print("\nDetails:")
        for e in errors[:50]:
            print(e)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more")

        if args.fix:
            print("\nRecommended fix: Replace bracket placeholders with ")
            print("  descriptive field names (e.g., [Project Name] -> PROJECT_NAME)")
            print("  or remove them if the template is meant to be abstract.")
    else:
        print("  All templates pass placeholder check.")


if __name__ == "__main__":
    main()
