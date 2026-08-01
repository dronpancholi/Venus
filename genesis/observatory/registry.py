"""
Repository Registry — SQLite-backed persistent registry of all known repositories.

Tracks:
  - id, name, url, source (github/gitlab/local)
  - clone status, last analyzed, last commit
  - language distribution, file counts, sizes
  - USIR compilation status
  - fingerprints for change detection
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RepositoryRecord:
    id: str
    name: str
    url: str = ""
    source: str = "local"
    clone_path: str = ""
    status: str = "pending"  # pending, cloning, ready, failed
    language: str = "unknown"
    file_count: int = 0
    line_count: int = 0
    last_commit: str = ""
    last_analyzed: float = 0.0
    usir_node_count: int = 0
    usir_edge_count: int = 0
    fingerprint: str = ""
    metadata_json: str = "{}"
    created_at: float = 0.0

    @property
    def metadata(self) -> dict[str, Any]:
        return json.loads(self.metadata_json or "{}")

    @metadata.setter
    def metadata(self, value: dict[str, Any]):
        self.metadata_json = json.dumps(value)

    def to_dict(self) -> dict[str, Any]:
        d = {}
        for k, v in self.__dict__.items():
            if k == "metadata_json":
                d["metadata"] = json.loads(v or "{}")
            else:
                d[k] = v
        return d


class RepositoryRegistry:
    """Persistent registry of repositories known to the Observatory."""

    def __init__(self, db_path: str | Path = ""):
        if not db_path:
            db_path = Path.home() / ".venus" / "observatory.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT DEFAULT '',
                source TEXT DEFAULT 'local',
                clone_path TEXT DEFAULT '',
                status TEXT DEFAULT 'pending',
                language TEXT DEFAULT 'unknown',
                file_count INTEGER DEFAULT 0,
                line_count INTEGER DEFAULT 0,
                last_commit TEXT DEFAULT '',
                last_analyzed REAL DEFAULT 0.0,
                usir_node_count INTEGER DEFAULT 0,
                usir_edge_count INTEGER DEFAULT 0,
                fingerprint TEXT DEFAULT '',
                metadata_json TEXT DEFAULT '{}',
                created_at REAL DEFAULT 0.0
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                action TEXT NOT NULL,
                details TEXT DEFAULT ''
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_repo_status
            ON repositories(status)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_repo_source
            ON repositories(source)
        """)
        self.conn.commit()

    def register(self, name: str, url: str = "", source: str = "local",
                 clone_path: str = "") -> RepositoryRecord:
        """Register a new repository."""
        now = time.time()
        repo_id = f"{source}::{name}"
        existing = self.get(repo_id)
        if existing:
            return existing

        self.conn.execute(
            """INSERT INTO repositories (id, name, url, source, clone_path,
               status, created_at, last_analyzed)
               VALUES (?, ?, ?, ?, ?, 'pending', ?, 0.0)""",
            (repo_id, name, url, source, clone_path, now),
        )
        self.conn.commit()
        self._log(repo_id, "registered", f"url={url}, source={source}")
        return self.get(repo_id)

    def get(self, repo_id: str) -> RepositoryRecord | None:
        row = self.conn.execute(
            "SELECT * FROM repositories WHERE id = ?", (repo_id,)
        ).fetchone()
        if row is None:
            return None
        return RepositoryRecord(**dict(row))

    def update(self, repo_id: str, **kwargs):
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(repo_id)
        self.conn.execute(
            f"UPDATE repositories SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        self.conn.commit()

    def list_repos(self, status: str | None = None, source: str | None = None,
                   limit: int = 100) -> list[RepositoryRecord]:
        query = "SELECT * FROM repositories WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if source:
            query += " AND source = ?"
            params.append(source)
        query += " ORDER BY last_analyzed DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [RepositoryRecord(**dict(r)) for r in rows]

    def count(self, status: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM repositories"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        return self.conn.execute(query, params).fetchone()[0]

    def summary(self) -> dict[str, Any]:
        total = self.count()
        ready = self.count("ready")
        pending = self.count("pending")
        failed = self.count("failed")

        row = self.conn.execute(
            "SELECT SUM(file_count), SUM(line_count), SUM(usir_node_count) "
            "FROM repositories WHERE status = 'ready'"
        ).fetchone()
        total_files = row[0] or 0
        total_lines = row[1] or 0
        total_usir_nodes = row[2] or 0

        return {
            "total_repos": total,
            "ready": ready,
            "pending": pending,
            "failed": failed,
            "total_files": total_files,
            "total_lines": total_lines,
            "total_usir_nodes": total_usir_nodes,
        }

    def _log(self, repo_id: str, action: str, details: str = ""):
        self.conn.execute(
            "INSERT INTO analysis_log (repo_id, timestamp, action, details) "
            "VALUES (?, ?, ?, ?)",
            (repo_id, time.time(), action, details),
        )
        self.conn.commit()

    def get_log(self, repo_id: str, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM analysis_log WHERE repo_id = ? "
            "ORDER BY timestamp DESC LIMIT ?",
            (repo_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
