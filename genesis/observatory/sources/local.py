"""
Local source integration for the Observatory.

Supports ingesting local directories as repositories.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class LocalSource:
    """Local directory repository source."""

    def __init__(self):
        pass

    def discover(self, root_path: str | Path, max_depth: int = 3) -> list[dict[str, Any]]:
        """Discover Python/TypeScript repositories in a directory tree."""
        root = Path(root_path)
        if not root.exists():
            return []

        candidates = []
        for item in root.iterdir():
            if not item.is_dir() or item.name.startswith("."):
                continue
            if item.name in ("node_modules", "venv", ".venv", "__pycache__", ".git"):
                continue

            py_files = list(item.rglob("*.py"))
            ts_files = list(item.rglob("*.ts")) + list(item.rglob("*.tsx"))
            js_files = list(item.rglob("*.js"))

            if py_files or ts_files or js_files:
                candidates.append({
                    "name": item.name,
                    "path": str(item.resolve()),
                    "python_files": len(py_files),
                    "typescript_files": len(ts_files) + len(js_files),
                })

        return candidates

    def validate(self, path: str | Path) -> dict[str, Any]:
        """Validate that a path is a valid repository."""
        p = Path(path)
        if not p.exists():
            return {"valid": False, "reason": "not found"}
        if not p.is_dir():
            return {"valid": False, "reason": "not a directory"}

        has_code = False
        for ext in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.rs", "*.go", "*.java"):
            if list(p.rglob(ext)):
                has_code = True
                break

        return {
            "valid": has_code,
            "reason": "contains code files" if has_code else "no recognized code files",
            "path": str(p.resolve()),
        }
