#!/usr/bin/env python3
"""
Venus Schema Validator.

Validates all JSON schema files and checks that artifacts reference
resolvable schema URIs.

Usage:
  python3 validate_schemas.py [--repo-path /path/to/Venus]
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SCHEMA_REF_PATTERN = re.compile(r"venus://schemas/[a-z_/]+/v\d+(\.\d+)?")


def main():
    parser = argparse.ArgumentParser(description="Venus Schema Validator")
    parser.add_argument("--repo-path", type=str, default=str(ROOT_DIR))
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    schema_dir = repo_path / "Layer_1_Foundations" / "_schemas"
    errors = []

    # 1. Validate all JSON schema files
    print("Validating JSON Schema files...")
    schema_map = {}
    for f in sorted(schema_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            schema_id = data.get("$id", "missing")
            schema_map[schema_id] = str(f.relative_to(repo_path))
            print(f"  OK  {f.name} -> {schema_id}")
        except json.JSONDecodeError as e:
            errors.append(f"  FAIL {f.name}: invalid JSON - {e}")
        except Exception as e:
            errors.append(f"  FAIL {f.name}: {e}")

    # 2. Check all $ref URIs resolve within the schema registry
    print("\nChecking $ref resolution...")
    refs_checked = 0
    for f in sorted(schema_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            for ref in _extract_refs(data):
                refs_checked += 1
                if ref.startswith("venus://schemas/"):
                    if ref not in schema_map and ref != "#":
                        errors.append(f"  FAIL {f.name}: unresolved $ref '{ref}'")
        except Exception:
            pass

    # 3. Check that markdown files reference valid schema URIs
    print("\nChecking markdown schema references...")
    refs_found = 0
    for md_file in repo_path.rglob("*.md"):
        if ".venv" in str(md_file) or "__pycache__" in str(md_file):
            continue
        content = md_file.read_text(errors="replace")
        for m in SCHEMA_REF_PATTERN.finditer(content):
            refs_found += 1
            uri = m.group(0)
            if uri not in schema_map:
                rel = md_file.relative_to(repo_path)
                errors.append(f"  UNRESOLVED {rel}: references '{uri}'")

    print(f"\n── Schema Validation Results ──")
    print(f"  Schemas: {len(schema_map)}")
    print(f"  Internal refs checked: {refs_checked}")
    print(f"  Markdown refs found: {refs_found}")
    print(f"  Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)
        sys.exit(1)
    print("  All checks passed.")


def _extract_refs(obj):
    refs = []
    if isinstance(obj, dict):
        if "$ref" in obj:
            refs.append(obj["$ref"])
        for v in obj.values():
            refs.extend(_extract_refs(v))
    elif isinstance(obj, list):
        for item in obj:
            refs.extend(_extract_refs(item))
    return refs


if __name__ == "__main__":
    main()
