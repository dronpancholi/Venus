"""
Repository Miner — clone, update, analyze, fingerprint repositories.

Supports cloning from GitHub, GitLab, and local directories.
Runs USIR compilation on each repository and stores results.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from genesis.observatory.registry import RepositoryRegistry
from genesis.usir.compiler import MultiLanguageCompiler


class RepositoryMiner:
    """Mine repositories: clone, update, analyze, fingerprint."""

    def __init__(self, registry: RepositoryRegistry | None = None,
                 work_dir: str | Path = ""):
        self.registry = registry or RepositoryRegistry()
        if not work_dir:
            work_dir = Path.home() / ".venus" / "repos"
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.compiler = MultiLanguageCompiler()

    # — Public API —

    def ingest_github(self, owner: str, repo: str) -> str:
        """Ingest a GitHub repository."""
        url = f"https://github.com/{owner}/{repo}.git"
        name = f"{owner}/{repo}"
        repo_id = f"github::{name}"

        record = self.registry.register(
            name=name, url=url, source="github",
            clone_path=str(self.work_dir / "github" / owner / repo),
        )
        self._clone(repo_id, url, record.clone_path)
        self._analyze(repo_id)
        return repo_id

    def ingest_local(self, path: str | Path) -> str:
        """Ingest a local directory as a repository."""
        path = Path(path).resolve()
        name = str(path)
        repo_id = f"local::{name}"

        record = self.registry.register(
            name=name, url="", source="local",
            clone_path=str(path),
        )
        self._analyze(repo_id)
        return repo_id

    def ingest_github_trending(self, count: int = 10) -> list[str]:
        """Ingest trending GitHub repositories (via search API or cloned list)."""
        trending = self._fetch_trending_repos(count)
        ingested = []
        for owner, repo in trending:
            try:
                rid = self.ingest_github(owner, repo)
                ingested.append(rid)
            except Exception as e:
                pass
        return ingested

    def analyze_existing(self, repo_id: str | None = None) -> int:
        """Re-analyze all ready repos or a specific one."""
        if repo_id:
            self._analyze(repo_id)
            return 1

        repos = self.registry.list_repos(status="ready")
        for r in repos:
            try:
                self._analyze(r.id)
            except Exception:
                continue
        return len(repos)

    def status(self, repo_id: str) -> dict[str, Any]:
        """Get detailed status of a repository."""
        record = self.registry.get(repo_id)
        if not record:
            return {"error": "not found"}
        result = record.to_dict()
        result["log"] = self.registry.get_log(repo_id, limit=5)
        return result

    def summary(self) -> dict[str, Any]:
        """Get summary of all repositories."""
        s = self.registry.summary()
        s["work_dir"] = str(self.work_dir)
        return s

    # — Internal: Cloning —

    def _clone(self, repo_id: str, url: str, target: str):
        self.registry.update(repo_id, status="cloning")
        self.registry._log(repo_id, "clone_start", url)

        target_path = Path(target)
        if target_path.exists():
            # — already cloned, pull latest —
            try:
                subprocess.run(
                    ["git", "-C", str(target_path), "pull", "--ff-only"],
                    capture_output=True, text=True, timeout=120,
                )
                self.registry._log(repo_id, "pull_complete", "")
            except Exception as e:
                self.registry._log(repo_id, "pull_failed", str(e))
        else:
            # — fresh clone —
            target_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    ["git", "clone", url, str(target_path)],
                    capture_output=True, text=True, timeout=300,
                )
                self.registry._log(repo_id, "clone_complete", "")
            except Exception as e:
                self.registry.update(repo_id, status="failed")
                self.registry._log(repo_id, "clone_failed", str(e))
                return

        # — get latest commit —
        try:
            result = subprocess.run(
                ["git", "-C", str(target_path), "log", "--oneline", "-1"],
                capture_output=True, text=True, timeout=10,
            )
            last_commit = result.stdout.strip()
            self.registry.update(repo_id, last_commit=last_commit)
        except Exception:
            pass

    def _analyze(self, repo_id: str):
        """Compile repository to USIR and update registry."""
        record = self.registry.get(repo_id)
        if not record:
            return

        repo_path = Path(record.clone_path) if record.clone_path else self.work_dir
        if not repo_path.exists():
            self.registry.update(repo_id, status="failed")
            return

        self.registry._log(repo_id, "analysis_start", str(repo_path))

        try:
            # — compile to USIR —
            usir = self.compiler.compile(repo_path)

            # — count files —
            py_files = list(repo_path.rglob("*.py"))
            js_files = list(repo_path.rglob("*.ts")) + list(repo_path.rglob("*.tsx")) + \
                       list(repo_path.rglob("*.js")) + list(repo_path.rglob("*.jsx"))
            total_files = len(py_files) + len(js_files)
            total_lines = 0
            for f in py_files + js_files:
                try:
                    total_lines += len(f.read_text().splitlines())
                except Exception:
                    pass

            # — fingerprint (hash of sorted file paths) —
            all_paths = sorted(
                str(p.relative_to(repo_path))
                for p in py_files + js_files
            )
            fingerprint = hashlib.sha256(
                json.dumps(all_paths).encode()
            ).hexdigest()[:16]

            # — detect primary language —
            lang_counts: dict[str, int] = {}
            if py_files:
                lang_counts["python"] = len(py_files)
            if js_files:
                lang_counts["typescript"] = len(
                    list(repo_path.rglob("*.ts")) + list(repo_path.rglob("*.tsx"))
                )
                lang_counts["javascript"] = len(
                    list(repo_path.rglob("*.js")) + list(repo_path.rglob("*.jsx"))
                )
            primary_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "unknown"

            # — update registry —
            self.registry.update(
                repo_id,
                status="ready",
                file_count=total_files,
                line_count=total_lines,
                language=primary_lang,
                usir_node_count=usir.node_count,
                usir_edge_count=sum(len(el) for el in usir._edges.values()),
                fingerprint=fingerprint,
                last_analyzed=time.time(),
            )
            self.registry._log(
                repo_id, "analysis_complete",
                f"{usir.node_count} nodes, {total_files} files, {total_lines} lines",
            )

        except Exception as e:
            self.registry.update(repo_id, status="failed")
            self.registry._log(repo_id, "analysis_failed", str(e))

    def _fetch_trending_repos(self, count: int = 10) -> list[tuple[str, str]]:
        """Fetch trending repos. Falls back to known high-quality repos."""
        fallback = [
            ("python", "cpython"),
            ("fastapi", "fastapi"),
            ("pallets", "flask"),
            ("django", "django"),
            ("psf", "requests"),
            ("pandas-dev", "pandas"),
            ("numpy", "numpy"),
            ("tiangolo", "uvicorn-gunicorn-fastapi-docker"),
            ("encode", "httpx"),
            ("pytest-dev", "pytest"),
        ]
        return fallback[:count]
