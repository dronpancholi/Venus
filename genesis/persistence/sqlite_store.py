"""
VENUS-II-PERS-SQL-01: SQLite Storage Providers — VPS Part X

Implements the 5 normative storage roles defined in VPS §10.1:
  - ArtifactStore   (§10.1.1): Content-addressed compilation cache
  - KnowledgeStore  (§10.1.2): Graph nodes and edges
  - HistoryStore    (§10.1.3): Append-only execution history
  - MetadataStore   (§10.1.4): Entity metadata CRUD
  - CheckpointStore (§10.1.5): JSON platform state snapshots

Normative References:
  - VPS Part X §10.1: Storage Providers
  - GENESIS_II_ARCHITECTURE §5: Persistence Architecture
  - ADR-006: Repository Pattern for Persistence, Not Active Record

Design Decisions:
  - All stores share a single SQLite database via SQLiteStore base class
  - Connection uses sqlite3.Row for dict-like row access
  - WAL journal mode for concurrent read performance
  - ISO 8601 timestamps (matching genesis convention)
  - Attributes stored as JSON for schema flexibility
  - Additive — existing in-memory stores continue to work
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SQLiteStore:
    """Base SQLite store with connection management and schema init.

    All 5 VPS §10.1 stores inherit from this class to share a single
    database connection and avoid duplicating schema / connection logic.
    """

    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS metadata_records (
                artifact_id TEXT PRIMARY KEY,
                artifact_path TEXT UNIQUE NOT NULL,
                semantic_type TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '0.1.0',
                owner TEXT NOT NULL DEFAULT 'genesis',
                validation_state TEXT NOT NULL DEFAULT 'unvalidated',
                certification TEXT NOT NULL DEFAULT 'uncertified',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                content_hash TEXT,
                size_bytes INTEGER DEFAULT 0,
                tags TEXT DEFAULT '[]',
                lifecycle TEXT NOT NULL DEFAULT 'active'
            );

            CREATE TABLE IF NOT EXISTS graph_nodes (
                node_id TEXT PRIMARY KEY,
                label TEXT NOT NULL DEFAULT '',
                semantic_type TEXT NOT NULL DEFAULT 'knowledge_node',
                attributes TEXT DEFAULT '{}',
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS graph_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL REFERENCES graph_nodes(node_id),
                target TEXT NOT NULL REFERENCES graph_nodes(node_id),
                edge_type TEXT NOT NULL DEFAULT 'references',
                attributes TEXT DEFAULT '{}',
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS compilation_cache (
                source_path TEXT PRIMARY KEY,
                source_hash TEXT NOT NULL,
                compiled_at TEXT NOT NULL,
                cache_data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                results TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS memory_store (
                namespace TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                stored_at TEXT NOT NULL,
                PRIMARY KEY (namespace, key)
            );
        """)
        self._conn.commit()

    def close(self):
        self._conn.close()

    def clear_all(self):
        """Remove all data from all tables. Used in testing."""
        for table in ["metadata_records", "graph_nodes", "graph_edges",
                       "compilation_cache", "execution_history", "memory_store"]:
            self._conn.execute(f"DELETE FROM {table}")
        self._conn.commit()


class MetadataStore(SQLiteStore):
    """VPS §10.1.4: Entity metadata CRUD operations.

    Stores metadata about artifacts, entities, and platform objects.
    Enforces immutability of identity, type, and creation time.
    """

    def save(self, record: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """INSERT OR REPLACE INTO metadata_records
               (artifact_id, artifact_path, semantic_type, version, owner,
                validation_state, certification, created_at, updated_at,
                content_hash, size_bytes, tags, lifecycle)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.get("artifact_id", record.get("artifact_path", "")),
                record.get("artifact_path", ""),
                record.get("semantic_type", ""),
                record.get("version", "0.1.0"),
                record.get("owner", "genesis"),
                record.get("validation_state", "unvalidated"),
                record.get("certification", "uncertified"),
                record.get("created_at", now),
                record.get("updated_at", now),
                record.get("content_hash"),
                record.get("size_bytes", 0),
                json.dumps(record.get("tags", [])),
                record.get("lifecycle", "active"),
            )
        )
        self._conn.commit()

    def get(self, artifact_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM metadata_records WHERE artifact_id = ?",
            (artifact_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def delete(self, artifact_id: str) -> None:
        self._conn.execute(
            "DELETE FROM metadata_records WHERE artifact_id = ?",
            (artifact_id,)
        )
        self._conn.commit()

    def find(self, **filters: Any) -> list[dict[str, Any]]:
        if not filters:
            return self.all()
        conditions = []
        params = []
        for key, value in filters.items():
            if key in ("semantic_type", "owner", "validation_state", "lifecycle"):
                conditions.append(f"{key} = ?")
                params.append(value)
        if not conditions:
            return self.all()
        rows = self._conn.execute(
            f"SELECT * FROM metadata_records WHERE {' AND '.join(conditions)}",
            params
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM metadata_records"
        ).fetchone()
        return row["cnt"]

    def all(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM metadata_records"
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags", "[]"))
        return d

    def update(self, artifact_id: str, updates: dict[str, Any]) -> None:
        existing = self.get(artifact_id)
        if existing is None:
            return
        existing.update(updates)
        existing["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.save(existing)


class KnowledgeStore(SQLiteStore):
    """VPS §10.1.2: Entity graph nodes and edges.

    Stores the knowledge graph: nodes represent entities, edges
    represent relationships between entities.
    """

    def save_node(self, node: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """INSERT OR REPLACE INTO graph_nodes
               (node_id, label, semantic_type, attributes, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                node.get("node_id", ""),
                node.get("label", ""),
                node.get("semantic_type", "knowledge_node"),
                json.dumps(node.get("attributes", {})),
                json.dumps(node.get("metadata", {})),
                node.get("created_at", now),
            )
        )
        self._conn.commit()

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM graph_nodes WHERE node_id = ?",
            (node_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["attributes"] = json.loads(d.get("attributes", "{}"))
        d["metadata"] = json.loads(d.get("metadata", "{}"))
        return d

    def delete_node(self, node_id: str) -> None:
        self._conn.execute(
            "DELETE FROM graph_edges WHERE source = ? OR target = ?",
            (node_id, node_id)
        )
        self._conn.execute(
            "DELETE FROM graph_nodes WHERE node_id = ?",
            (node_id,)
        )
        self._conn.commit()

    def all_nodes(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM graph_nodes").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["attributes"] = json.loads(d.get("attributes", "{}"))
            d["metadata"] = json.loads(d.get("metadata", "{}"))
            result.append(d)
        return result

    def count_nodes(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM graph_nodes"
        ).fetchone()
        return row["cnt"]

    def query_nodes_by_type(self, semantic_type: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM graph_nodes WHERE semantic_type = ?",
            (semantic_type,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["attributes"] = json.loads(d.get("attributes", "{}"))
            d["metadata"] = json.loads(d.get("metadata", "{}"))
            result.append(d)
        return result

    def save_edge(self, edge: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """INSERT OR REPLACE INTO graph_edges
               (id, source, target, edge_type, attributes, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                edge.get("id"),
                edge.get("source", ""),
                edge.get("target", ""),
                edge.get("edge_type", "references"),
                json.dumps(edge.get("attributes", {})),
                json.dumps(edge.get("metadata", {})),
                edge.get("created_at", now),
            )
        )
        self._conn.commit()

    def get_edges(self, node_id: str | None = None) -> list[dict[str, Any]]:
        if node_id is None:
            rows = self._conn.execute("SELECT * FROM graph_edges").fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM graph_edges WHERE source = ? OR target = ?",
                (node_id, node_id)
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["attributes"] = json.loads(d.get("attributes", "{}"))
            d["metadata"] = json.loads(d.get("metadata", "{}"))
            result.append(d)
        return result

    def delete_edge(self, edge_id: int) -> None:
        self._conn.execute(
            "DELETE FROM graph_edges WHERE id = ?",
            (edge_id,)
        )
        self._conn.commit()

    def count_edges(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM graph_edges"
        ).fetchone()
        return row["cnt"]


class HistoryStore(SQLiteStore):
    """VPS §10.1.3: Append-only execution history.

    Records workflow executions, task results, and validation results.
    Records are append-only — existing records are never modified.
    """

    def save(self, record: dict[str, Any]) -> None:
        self._conn.execute(
            """INSERT INTO execution_history
               (workflow_id, executed_at, status, results)
               VALUES (?, ?, ?, ?)""",
            (
                record.get("workflow_id", ""),
                record.get("executed_at", datetime.now(timezone.utc).isoformat()),
                record.get("status", ""),
                json.dumps(record.get("results", [])),
            )
        )
        self._conn.commit()

    def find(self, **filters: Any) -> list[dict[str, Any]]:
        if not filters:
            return self.all()
        conditions = []
        params = []
        for key, value in filters.items():
            if key in ("workflow_id", "status"):
                conditions.append(f"{key} = ?")
                params.append(value)
        if not conditions:
            return self.all()
        rows = self._conn.execute(
            f"SELECT * FROM execution_history WHERE {' AND '.join(conditions)}",
            params
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def all(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM execution_history ORDER BY id"
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM execution_history"
        ).fetchone()
        return row["cnt"]

    def query_by_time_range(
        self, start: str, end: str
    ) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM execution_history WHERE executed_at >= ? AND executed_at <= ? ORDER BY id",
            (start, end)
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def query_by_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        return self.find(workflow_id=workflow_id)

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["results"] = json.loads(d.get("results", "[]"))
        return d


class ArtifactStore(SQLiteStore):
    """VPS §10.1.1: Content-addressed compilation cache.

    Stores compiled output artifacts keyed by source path and
    content hash for content-addressable retrieval.
    """

    def save(self, artifact: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """INSERT OR REPLACE INTO compilation_cache
               (source_path, source_hash, compiled_at, cache_data)
               VALUES (?, ?, ?, ?)""",
            (
                artifact.get("source_path", ""),
                artifact.get("source_hash", ""),
                artifact.get("compiled_at", now),
                json.dumps(artifact.get("cache_data", {})),
            )
        )
        self._conn.commit()

    def get(self, source_path: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM compilation_cache WHERE source_path = ?",
            (source_path,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def get_by_hash(self, content_hash: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM compilation_cache WHERE source_hash = ?",
            (content_hash,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def delete(self, source_path: str) -> None:
        self._conn.execute(
            "DELETE FROM compilation_cache WHERE source_path = ?",
            (source_path,)
        )
        self._conn.commit()

    def count(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM compilation_cache"
        ).fetchone()
        return row["cnt"]

    def all(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM compilation_cache"
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["cache_data"] = json.loads(d.get("cache_data", "{}"))
        return d


class CheckpointStore:
    """VPS §10.1.5: Platform state snapshots as JSON.

    Saves and loads full platform state as JSON files.
    Each checkpoint is a named snapshot that can be restored
    to reconstruct platform state after restart.
    """

    def __init__(self, checkpoint_dir: str | Path):
        self._dir = Path(checkpoint_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, name: str, state: dict[str, Any]) -> Path:
        path = self._dir / f"{name}.json"
        payload = {
            "checkpoint_name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "state": state,
        }
        path.write_text(json.dumps(payload, indent=2))
        return path

    def load_checkpoint(self, name: str) -> dict[str, Any] | None:
        path = self._dir / f"{name}.json"
        if not path.exists():
            return None
        payload = json.loads(path.read_text())
        return payload.get("state")

    def list_checkpoints(self) -> list[str]:
        return sorted(
            p.stem for p in self._dir.glob("*.json")
        )

    def delete_checkpoint(self, name: str) -> None:
        path = self._dir / f"{name}.json"
        if path.exists():
            path.unlink()

    def checkpoint_exists(self, name: str) -> bool:
        return (self._dir / f"{name}.json").exists()


class MemoryStore(SQLiteStore):
    """Institutional memory store — namespace-based key/value persistence.

    Enables platform services to persist state across sessions.
    Keyed by (namespace, key) composite primary key.
    """

    def store(self, namespace: str, key: str, value: Any) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO memory_store (namespace, key, value, stored_at) VALUES (?, ?, ?, ?)",
            (namespace, key, json.dumps(value), now)
        )
        self._conn.commit()

    def recall(self, namespace: str, key: str) -> Any | None:
        row = self._conn.execute(
            "SELECT value FROM memory_store WHERE namespace = ? AND key = ?",
            (namespace, key)
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["value"])

    def forget(self, namespace: str, key: str) -> bool:
        cursor = self._conn.execute(
            "DELETE FROM memory_store WHERE namespace = ? AND key = ?",
            (namespace, key)
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def list_namespace(self, namespace: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT key, value, stored_at FROM memory_store WHERE namespace = ? ORDER BY stored_at",
            (namespace,)
        ).fetchall()
        result = []
        for r in rows:
            result.append({
                "key": r["key"],
                "value": json.loads(r["value"]),
                "stored_at": r["stored_at"],
            })
        return result

    def list_namespaces(self) -> list[str]:
        rows = self._conn.execute(
            "SELECT DISTINCT namespace FROM memory_store ORDER BY namespace"
        ).fetchall()
        return [r["namespace"] for r in rows]

    def clear_namespace(self, namespace: str) -> int:
        cursor = self._conn.execute(
            "DELETE FROM memory_store WHERE namespace = ?",
            (namespace,)
        )
        self._conn.commit()
        return cursor.rowcount
