#!/usr/bin/env python3
"""
Venus Cross-Reference Integrity Checker.

Scans all markdown files for broken internal links.

Usage:
  python3 check_references.py [--repo-path /path/to/Venus]
"""

import argparse
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv"}


def main():
    parser = argparse.ArgumentParser(description="Venus Reference Checker")
    parser.add_argument("--repo-path", type=str, default=str(ROOT_DIR))
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()

    # Build set of all existing markdown files
    existing = set()
    for f in repo_path.rglob("*.md"):
        if any(excl in f.parts for excl in EXCLUDE_DIRS):
            continue
        existing.add(f.resolve())

    # Also check .json and .py files
    for ext in ("*.json", "*.py", "*.yaml", "*.yml"):
        for f in repo_path.rglob(ext):
            if any(excl in f.parts for excl in EXCLUDE_DIRS):
                continue
            existing.add(f.resolve())

    errors = []
    checked = 0
    links_found = 0

    for f in sorted(repo_path.rglob("*.md")):
        if any(excl in f.parts for excl in EXCLUDE_DIRS):
            continue
        if ".venv" in str(f):
            continue

        content = f.read_text(errors="replace")
        rel = f.relative_to(repo_path)
        checked += 1

        # Find markdown links: [text](./path/to/file.md)
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", content):
            target_path = m.group(2)
            # Skip absolute URLs and anchors
            if target_path.startswith("http") or target_path.startswith("#"):
                continue
            if target_path.startswith("file://"):
                target_path = target_path.replace("file://", "")

            links_found += 1
            target_abs = (f.parent / target_path).resolve()

            # Check if target file exists
            if target_abs.suffix == "" and target_abs.parent.exists():
                # Maybe it's a directory reference
                continue

            if not target_abs.exists() and target_abs.suffix:
                errors.append(f"  BROKEN {rel}: '{target_path}' -> {target_abs.name}")
                if args.verbose:
                    print(f"    Context: ...{m.group(0)}...")

    print(f"\n── Reference Check Results ──")
    print(f"  Files checked: {checked}")
    print(f"  Links found: {links_found}")
    print(f"  Broken links: {len(errors)}")

    if errors:
        print("\nBroken Links:")
        for e in errors[:30]:
            print(e)
        if len(errors) > 30:
            print(f"  ... and {len(errors) - 30} more")
        sys.exit(1)
    print("  All references resolve correctly.")


if __name__ == "__main__":
    main()
