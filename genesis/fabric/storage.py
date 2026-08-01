"""
Storage Engine (Mission 71) — SQLite-backed persistence for the entire Fabric.

Every fabric entity (events, agents, tasks, conversations, audit, metrics,
services) is persisted automatically through this storage layer.

Design:
  StorageEngine — top-level manager, owns connection lifecycle
  SchemaManager — auto-creates and migrates tables
  EntityRepository[T] — typed repository per entity type

All write operations go through the FabricKernel which delegates to StorageEngine.
All fabric components remain in-memory for speed; StorageEngine mirrors state
to SQLite for crash recovery and historical queries.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, TypeVar

from genesis.utils.identity import generate_id

T = TypeVar("T")


class SchemaManager:
    """Manages SQLite schema creation and migration."""

    SCHEMA_VERSION = 1

    TABLES = {
        "events": """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                origin TEXT NOT NULL DEFAULT '',
                correlation_id TEXT NOT NULL DEFAULT '',
                causation_id TEXT NOT NULL DEFAULT '',
                session_id TEXT NOT NULL DEFAULT '',
                repository_id TEXT NOT NULL DEFAULT '',
                priority INTEGER NOT NULL DEFAULT 1,
                severity TEXT NOT NULL DEFAULT 'info',
                payload TEXT NOT NULL DEFAULT '{}',
                metadata TEXT NOT NULL DEFAULT '{}',
                tags TEXT NOT NULL DEFAULT '[]',
                confidence REAL NOT NULL DEFAULT 1.0,
                ttl_secs REAL NOT NULL DEFAULT 86400.0
            )
        """,
        "agents": """
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                name TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                capabilities TEXT NOT NULL DEFAULT '[]',
                max_concurrent_tasks INTEGER NOT NULL DEFAULT 1,
                system_prompt TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'idle',
                task_count INTEGER NOT NULL DEFAULT 0,
                completed_count INTEGER NOT NULL DEFAULT 0,
                failed_count INTEGER NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """,
        "agent_tasks": """
            CREATE TABLE IF NOT EXISTS agent_tasks (
                task_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                objective TEXT NOT NULL,
                context TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'pending',
                started_at REAL NOT NULL DEFAULT 0,
                completed_at REAL NOT NULL DEFAULT 0,
                result TEXT,
                error TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL
            )
        """,
        "agent_messages": """
            CREATE TABLE IF NOT EXISTS agent_messages (
                id TEXT PRIMARY KEY,
                sender_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                message_type TEXT NOT NULL DEFAULT 'text',
                correlation_id TEXT NOT NULL DEFAULT '',
                timestamp REAL NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """,
        "task_graph_nodes": """
            CREATE TABLE IF NOT EXISTS task_graph_nodes (
                id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                parent_id TEXT NOT NULL DEFAULT '',
                dependencies TEXT NOT NULL DEFAULT '[]',
                blocking TEXT NOT NULL DEFAULT '[]',
                estimated_duration_secs REAL NOT NULL DEFAULT 0,
                actual_duration_secs REAL NOT NULL DEFAULT 0,
                confidence REAL NOT NULL DEFAULT 1.0,
                required_capabilities TEXT NOT NULL DEFAULT '[]',
                required_agent_roles TEXT NOT NULL DEFAULT '[]',
                required_providers TEXT NOT NULL DEFAULT '[]',
                assigned_agent_id TEXT NOT NULL DEFAULT '',
                assigned_provider TEXT NOT NULL DEFAULT '',
                evidence TEXT NOT NULL DEFAULT '[]',
                rollback_steps TEXT NOT NULL DEFAULT '[]',
                progress REAL NOT NULL DEFAULT 0.0,
                tags TEXT NOT NULL DEFAULT '[]',
                created_at REAL NOT NULL,
                started_at REAL NOT NULL DEFAULT 0,
                completed_at REAL NOT NULL DEFAULT 0,
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """,
        "conversations": """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '',
                objective TEXT NOT NULL DEFAULT '',
                participants TEXT NOT NULL DEFAULT '[]',
                links TEXT NOT NULL DEFAULT '{}',
                tags TEXT NOT NULL DEFAULT '[]',
                summary TEXT NOT NULL DEFAULT '',
                decisions TEXT NOT NULL DEFAULT '[]',
                parent_id TEXT NOT NULL DEFAULT '',
                branch_of TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """,
        "conversation_messages": """
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                citations TEXT NOT NULL DEFAULT '[]',
                links TEXT NOT NULL DEFAULT '{}',
                metadata TEXT NOT NULL DEFAULT '{}',
                timestamp REAL NOT NULL
            )
        """,
        "audit_entries": """
            CREATE TABLE IF NOT EXISTS audit_entries (
                id TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                actor TEXT NOT NULL DEFAULT '',
                resource TEXT NOT NULL DEFAULT '',
                detail TEXT NOT NULL DEFAULT '{}',
                timestamp REAL NOT NULL,
                severity TEXT NOT NULL DEFAULT 'info',
                correlation_id TEXT NOT NULL DEFAULT '',
                session_id TEXT NOT NULL DEFAULT ''
            )
        """,
        "metric_points": """
            CREATE TABLE IF NOT EXISTS metric_points (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                tags TEXT NOT NULL DEFAULT '{}',
                timestamp REAL NOT NULL,
                host TEXT NOT NULL DEFAULT ''
            )
        """,
        "services": """
            CREATE TABLE IF NOT EXISTS services (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '1.0.0',
                capabilities TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'registered',
                registered_at REAL NOT NULL,
                last_heartbeat REAL NOT NULL DEFAULT 0,
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """,
        "schema_version": """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at REAL NOT NULL
            )
        """,
    }

    INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)",
        "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_events_origin ON events(origin)",
        "CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)",
        "CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent ON agent_tasks(agent_id)",
        "CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status)",
        "CREATE INDEX IF NOT EXISTS idx_agent_messages_recipient ON agent_messages(recipient_id)",
        "CREATE INDEX IF NOT EXISTS idx_task_nodes_status ON task_graph_nodes(status)",
        "CREATE INDEX IF NOT EXISTS idx_task_nodes_parent ON task_graph_nodes(parent_id)",
        "CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at)",
        "CREATE INDEX IF NOT EXISTS idx_conv_messages_conv ON conversation_messages(conversation_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_entries(action)",
        "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_entries(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_metrics_name ON metric_points(name)",
        "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metric_points(timestamp)",
    ]

    @classmethod
    def ensure_schema(cls, conn: sqlite3.Connection):
        for table_ddl in cls.TABLES.values():
            conn.execute(table_ddl)
        for index_ddl in cls.INDEXES:
            conn.execute(index_ddl)
        cls._migrate(conn)
        conn.commit()

    @classmethod
    def _migrate(cls, conn: sqlite3.Connection):
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        current_version = row[0] if row and row[0] else 0
        if current_version < cls.SCHEMA_VERSION:
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (?, ?)",
                (cls.SCHEMA_VERSION, time.time()),
            )
            conn.commit()


class StorageEngine:
    """Top-level persistence manager for the entire Fabric.

    Usage:
        engine = StorageEngine(Path("~/.genesis/genesis.db"))
        engine.connect()
        engine.store_event(event)
        events = engine.query_events(event_type="kernel.booted")
        engine.disconnect()
    """

    def __init__(self, db_path: str | Path | None = None):
        self._db_path = Path(db_path or self._default_path())
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.RLock()
        self._connected = False
        self._write_count = 0
        self._read_count = 0

    @staticmethod
    def _default_path() -> str:
        return str(Path.home() / ".genesis" / "fabric.db")

    @property
    def db_path(self) -> str:
        return str(self._db_path)

    def connect(self):
        with self._lock:
            if self._connected:
                return
            self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.execute("PRAGMA busy_timeout=5000")
            SchemaManager.ensure_schema(self._conn)
            self._connected = True

    def disconnect(self):
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None
                self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "db_path": str(self._db_path),
                "connected": self._connected,
                "write_count": self._write_count,
                "read_count": self._read_count,
            }

    # ── Event Persistence ──────────────────────────────────────────────

    def _write(self, sql: str, params: tuple = ()) -> sqlite3.Cursor | None:
        try:
            return self._conn.execute(sql, params)
        except sqlite3.OperationalError:
            return None

    def store_event(self, event: Any) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO events
                   (id, type, timestamp, origin, correlation_id, causation_id,
                    session_id, repository_id, priority, severity, payload,
                    metadata, tags, confidence, ttl_secs)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.id, event.type, event.timestamp, event.origin,
                    event.correlation_id, event.causation_id,
                    event.session_id, event.repository_id,
                    event.priority.value if hasattr(event.priority, 'value') else event.priority,
                    event.severity.value if hasattr(event.severity, 'value') else event.severity,
                    json.dumps(event.payload), json.dumps(event.metadata),
                    json.dumps(event.tags), event.confidence, event.ttl_secs,
                ),
            )
            self._write_count += 1
            return event.id

    def query_events(self, event_type: str | None = None,
                     origin: str | None = None,
                     session_id: str | None = None,
                     repository_id: str | None = None,
                     severity: str | None = None,
                     min_confidence: float = 0.0,
                     since: float = 0.0, until: float = 0.0,
                     limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        with self._lock:
            where = []
            params = []
            if event_type:
                where.append("type = ?")
                params.append(event_type)
            if origin:
                where.append("origin = ?")
                params.append(origin)
            if session_id:
                where.append("session_id = ?")
                params.append(session_id)
            if repository_id:
                where.append("repository_id = ?")
                params.append(repository_id)
            if severity:
                where.append("severity = ?")
                params.append(severity)
            if min_confidence > 0:
                where.append("confidence >= ?")
                params.append(min_confidence)
            if since > 0:
                where.append("timestamp >= ?")
                params.append(since)
            if until > 0:
                where.append("timestamp <= ?")
                params.append(until)
            where_clause = " AND ".join(where) if where else "1=1"
            cur = self._conn.execute(
                f"SELECT * FROM events WHERE {where_clause} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                params + [limit, offset],
            )
            self._read_count += 1
            return [self._row_to_event(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "type": row[1], "timestamp": row[2],
            "origin": row[3], "correlation_id": row[4],
            "causation_id": row[5], "session_id": row[6],
            "repository_id": row[7], "priority": row[8],
            "severity": row[9],
            "payload": json.loads(row[10]),
            "metadata": json.loads(row[11]),
            "tags": json.loads(row[12]),
            "confidence": row[13], "ttl_secs": row[14],
        }

    def count_events(self) -> int:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(*) FROM events")
            return cur.fetchone()[0]

    def purge_old_events(self, max_age_secs: float = 86400 * 7):
        cutoff = time.time() - max_age_secs
        with self._lock:
            self._write("DELETE FROM events WHERE timestamp < ?", (cutoff,))
            self._conn.commit()

    # ── Agent Persistence ──────────────────────────────────────────────

    def store_agent(self, agent_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO agents
                   (agent_id, role, name, description, capabilities,
                    max_concurrent_tasks, system_prompt, status,
                    task_count, completed_count, failed_count,
                    created_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    agent_data["agent_id"], agent_data["role"],
                    agent_data["name"], agent_data.get("description", ""),
                    json.dumps(agent_data.get("capabilities", [])),
                    agent_data.get("max_concurrent_tasks", 1),
                    agent_data.get("system_prompt", ""),
                    agent_data.get("status", "idle"),
                    agent_data.get("task_count", 0),
                    agent_data.get("completed_count", 0),
                    agent_data.get("failed_count", 0),
                    agent_data.get("created_at", time.time()),
                    json.dumps(agent_data.get("metadata", {})),
                ),
            )
            self._write_count += 1
            return agent_data["agent_id"]

    def query_agents(self, status: str | None = None,
                     role: str | None = None,
                     limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            where = []
            params = []
            if status:
                where.append("status = ?")
                params.append(status)
            if role:
                where.append("role = ?")
                params.append(role)
            where_clause = " AND ".join(where) if where else "1=1"
            cur = self._conn.execute(
                f"SELECT * FROM agents WHERE {where_clause} ORDER BY created_at DESC LIMIT ?",
                params + [limit],
            )
            self._read_count += 1
            return [self._row_to_agent(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_agent(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "agent_id": row[0], "role": row[1], "name": row[2],
            "description": row[3], "capabilities": json.loads(row[4]),
            "max_concurrent_tasks": row[5], "system_prompt": row[6],
            "status": row[7], "task_count": row[8],
            "completed_count": row[9], "failed_count": row[10],
            "created_at": row[11], "metadata": json.loads(row[12]),
        }

    def delete_agent(self, agent_id: str):
        with self._lock:
            self._write("DELETE FROM agents WHERE agent_id = ?", (agent_id,))
            self._write("DELETE FROM agent_tasks WHERE agent_id = ?", (agent_id,))
            self._conn.commit()

    # ── Agent Task Persistence ─────────────────────────────────────────

    def store_agent_task(self, task_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO agent_tasks
                   (task_id, agent_id, objective, context, status,
                    started_at, completed_at, result, error, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task_data.get("task_id", generate_id("atask", 12)),
                    task_data.get("agent_id", ""),
                    task_data.get("objective", ""),
                    json.dumps(task_data.get("context", {})),
                    task_data.get("status", "pending"),
                    task_data.get("started_at", 0),
                    task_data.get("completed_at", 0),
                    json.dumps(task_data.get("result")),
                    task_data.get("error", ""),
                    task_data.get("created_at", time.time()),
                ),
            )
            self._write_count += 1
            return task_data.get("task_id", "")

    def query_agent_tasks(self, agent_id: str | None = None,
                          status: str | None = None,
                          limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            where = []
            params = []
            if agent_id:
                where.append("agent_id = ?")
                params.append(agent_id)
            if status:
                where.append("status = ?")
                params.append(status)
            where_clause = " AND ".join(where) if where else "1=1"
            cur = self._conn.execute(
                f"SELECT * FROM agent_tasks WHERE {where_clause} ORDER BY created_at DESC LIMIT ?",
                params + [limit],
            )
            self._read_count += 1
            return [self._row_to_agent_task(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_agent_task(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "task_id": row[0], "agent_id": row[1], "objective": row[2],
            "context": json.loads(row[3]), "status": row[4],
            "started_at": row[5], "completed_at": row[6],
            "result": row[7], "error": row[8], "created_at": row[9],
        }

    # ── Message Persistence ────────────────────────────────────────────

    def store_message(self, msg_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO agent_messages
                   (id, sender_id, recipient_id, content, message_type,
                    correlation_id, timestamp, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    msg_data.get("id", generate_id("amsg", 12)),
                    msg_data.get("sender_id", ""),
                    msg_data.get("recipient_id", ""),
                    msg_data.get("content", ""),
                    msg_data.get("message_type", "text"),
                    msg_data.get("correlation_id", ""),
                    msg_data.get("timestamp", time.time()),
                    json.dumps(msg_data.get("metadata", {})),
                ),
            )
            self._write_count += 1
            return msg_data.get("id", "")

    def query_messages(self, agent_id: str | None = None,
                       limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            if agent_id:
                cur = self._conn.execute(
                    """SELECT * FROM agent_messages
                       WHERE sender_id = ? OR recipient_id = ?
                       ORDER BY timestamp DESC LIMIT ?""",
                    (agent_id, agent_id, limit),
                )
            else:
                cur = self._conn.execute(
                    "SELECT * FROM agent_messages ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
            self._read_count += 1
            return [self._row_to_message(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_message(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "sender_id": row[1], "recipient_id": row[2],
            "content": row[3], "message_type": row[4],
            "correlation_id": row[5], "timestamp": row[6],
            "metadata": json.loads(row[7]),
        }

    # ── Task Graph Node Persistence ────────────────────────────────────

    def store_task_node(self, node_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO task_graph_nodes
                   (id, node_type, title, description, status,
                    parent_id, dependencies, blocking,
                    estimated_duration_secs, actual_duration_secs,
                    confidence, required_capabilities, required_agent_roles,
                    required_providers, assigned_agent_id, assigned_provider,
                    evidence, rollback_steps, progress, tags,
                    created_at, started_at, completed_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    node_data["id"], node_data.get("node_type", "engineering_task"),
                    node_data.get("title", ""), node_data.get("description", ""),
                    node_data.get("status", "pending"),
                    node_data.get("parent_id", ""),
                    json.dumps(node_data.get("dependencies", [])),
                    json.dumps(node_data.get("blocking", [])),
                    node_data.get("estimated_duration_secs", 0),
                    node_data.get("actual_duration_secs", 0),
                    node_data.get("confidence", 1.0),
                    json.dumps(node_data.get("required_capabilities", [])),
                    json.dumps(node_data.get("required_agent_roles", [])),
                    json.dumps(node_data.get("required_providers", [])),
                    node_data.get("assigned_agent_id", ""),
                    node_data.get("assigned_provider", ""),
                    json.dumps(node_data.get("evidence", [])),
                    json.dumps(node_data.get("rollback_steps", [])),
                    node_data.get("progress", 0.0),
                    json.dumps(node_data.get("tags", [])),
                    node_data.get("created_at", time.time()),
                    node_data.get("started_at", 0),
                    node_data.get("completed_at", 0),
                    json.dumps(node_data.get("metadata", {})),
                ),
            )
            self._write_count += 1
            return node_data["id"]

    def query_task_nodes(self, status: str | None = None,
                         node_type: str | None = None,
                         parent_id: str | None = None,
                         limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            where = []
            params = []
            if status:
                where.append("status = ?")
                params.append(status)
            if node_type:
                where.append("node_type = ?")
                params.append(node_type)
            if parent_id:
                where.append("parent_id = ?")
                params.append(parent_id)
            where_clause = " AND ".join(where) if where else "1=1"
            cur = self._conn.execute(
                f"SELECT * FROM task_graph_nodes WHERE {where_clause} ORDER BY created_at DESC LIMIT ?",
                params + [limit],
            )
            self._read_count += 1
            return [self._row_to_task_node(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_task_node(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "node_type": row[1], "title": row[2],
            "description": row[3], "status": row[4],
            "parent_id": row[5],
            "dependencies": json.loads(row[6]),
            "blocking": json.loads(row[7]),
            "estimated_duration_secs": row[8],
            "actual_duration_secs": row[9],
            "confidence": row[10],
            "required_capabilities": json.loads(row[11]),
            "required_agent_roles": json.loads(row[12]),
            "required_providers": json.loads(row[13]),
            "assigned_agent_id": row[14],
            "assigned_provider": row[15],
            "evidence": json.loads(row[16]),
            "rollback_steps": json.loads(row[17]),
            "progress": row[18],
            "tags": json.loads(row[19]),
            "created_at": row[20],
            "started_at": row[21],
            "completed_at": row[22],
            "metadata": json.loads(row[23]),
        }

    # ── Conversation Persistence ───────────────────────────────────────

    def store_conversation(self, conv_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO conversations
                   (id, title, objective, participants, links, tags,
                    summary, decisions, parent_id, branch_of,
                    created_at, updated_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    conv_data["id"], conv_data.get("title", ""),
                    conv_data.get("objective", ""),
                    json.dumps(conv_data.get("participants", [])),
                    json.dumps(conv_data.get("links", {})),
                    json.dumps(conv_data.get("tags", [])),
                    conv_data.get("summary", ""),
                    json.dumps(conv_data.get("decisions", [])),
                    conv_data.get("parent_id", ""),
                    conv_data.get("branch_of", ""),
                    conv_data.get("created_at", time.time()),
                    conv_data.get("updated_at", time.time()),
                    json.dumps(conv_data.get("metadata", {})),
                ),
            )
            self._write_count += 1
            return conv_data["id"]

    def query_conversations(self, title_contains: str | None = None,
                            participant: str | None = None,
                            limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            if title_contains:
                cur = self._conn.execute(
                    "SELECT * FROM conversations WHERE title LIKE ? ORDER BY updated_at DESC LIMIT ?",
                    (f"%{title_contains}%", limit),
                )
            elif participant:
                cur = self._conn.execute(
                    "SELECT * FROM conversations WHERE participants LIKE ? ORDER BY updated_at DESC LIMIT ?",
                    (f"%{participant}%", limit),
                )
            else:
                cur = self._conn.execute(
                    "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ?",
                    (limit,),
                )
            self._read_count += 1
            return [self._row_to_conversation(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_conversation(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "title": row[1], "objective": row[2],
            "participants": json.loads(row[3]),
            "links": json.loads(row[4]),
            "tags": json.loads(row[5]),
            "summary": row[6], "decisions": json.loads(row[7]),
            "parent_id": row[8], "branch_of": row[9],
            "created_at": row[10], "updated_at": row[11],
            "metadata": json.loads(row[12]),
        }

    def store_conversation_message(self, msg_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO conversation_messages
                   (id, conversation_id, role, content, citations, links,
                    metadata, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    msg_data.get("id", generate_id("cmsg", 12)),
                    msg_data.get("conversation_id", ""),
                    msg_data.get("role", ""), msg_data.get("content", ""),
                    json.dumps(msg_data.get("citations", [])),
                    json.dumps(msg_data.get("links", {})),
                    json.dumps(msg_data.get("metadata", {})),
                    msg_data.get("timestamp", time.time()),
                ),
            )
            self._write_count += 1
            return msg_data.get("id", "")

    def query_conversation_messages(self, conversation_id: str,
                                    limit: int = 200) -> list[dict[str, Any]]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM conversation_messages WHERE conversation_id = ? ORDER BY timestamp ASC LIMIT ?",
                (conversation_id, limit),
            )
            self._read_count += 1
            return [self._row_to_conv_message(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_conv_message(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "conversation_id": row[1], "role": row[2],
            "content": row[3], "citations": json.loads(row[4]),
            "links": json.loads(row[5]),
            "metadata": json.loads(row[6]), "timestamp": row[7],
        }

    # ── Audit Persistence ──────────────────────────────────────────────

    def store_audit_entry(self, entry_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO audit_entries
                   (id, action, actor, resource, detail, timestamp,
                    severity, correlation_id, session_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    entry_data.get("id", generate_id("audit", 16)),
                    entry_data.get("action", ""),
                    entry_data.get("actor", ""),
                    entry_data.get("resource", ""),
                    json.dumps(entry_data.get("detail", {})),
                    entry_data.get("timestamp", time.time()),
                    entry_data.get("severity", "info"),
                    entry_data.get("correlation_id", ""),
                    entry_data.get("session_id", ""),
                ),
            )
            self._write_count += 1
            return entry_data.get("id", "")

    def query_audit(self, action: str | None = None,
                    actor: str | None = None,
                    limit: int = 100,
                    offset: int = 0) -> list[dict[str, Any]]:
        with self._lock:
            where = []
            params = []
            if action:
                where.append("action = ?")
                params.append(action)
            if actor:
                where.append("actor = ?")
                params.append(actor)
            where_clause = " AND ".join(where) if where else "1=1"
            cur = self._conn.execute(
                f"SELECT * FROM audit_entries WHERE {where_clause} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                params + [limit, offset],
            )
            self._read_count += 1
            return [self._row_to_audit(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_audit(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "action": row[1], "actor": row[2],
            "resource": row[3], "detail": json.loads(row[4]),
            "timestamp": row[5], "severity": row[6],
            "correlation_id": row[7], "session_id": row[8],
        }

    def count_audit(self) -> int:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(*) FROM audit_entries")
            return cur.fetchone()[0]

    # ── Metric Persistence ─────────────────────────────────────────────

    def store_metric(self, metric_data: dict[str, Any]) -> str:
        with self._lock:
            mid = metric_data.get("id", generate_id("mpt", 12))
            self._write(
                """INSERT OR REPLACE INTO metric_points
                   (id, name, value, tags, timestamp, host)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    mid,
                    metric_data.get("name", ""),
                    metric_data.get("value", 0.0),
                    json.dumps(metric_data.get("tags", {})),
                    metric_data.get("timestamp", time.time()),
                    metric_data.get("host", ""),
                ),
            )
            self._write_count += 1
            return mid

    def query_metrics(self, name: str | None = None,
                      since: float = 0.0,
                      limit: int = 1000) -> list[dict[str, Any]]:
        with self._lock:
            if name:
                if since > 0:
                    cur = self._conn.execute(
                        "SELECT * FROM metric_points WHERE name = ? AND timestamp >= ? ORDER BY timestamp DESC LIMIT ?",
                        (name, since, limit),
                    )
                else:
                    cur = self._conn.execute(
                        "SELECT * FROM metric_points WHERE name = ? ORDER BY timestamp DESC LIMIT ?",
                        (name, limit),
                    )
            else:
                if since > 0:
                    cur = self._conn.execute(
                        "SELECT * FROM metric_points WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT ?",
                        (since, limit),
                    )
                else:
                    cur = self._conn.execute(
                        "SELECT * FROM metric_points ORDER BY timestamp DESC LIMIT ?",
                        (limit,),
                    )
            self._read_count += 1
            return [self._row_to_metric(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_metric(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "name": row[1], "value": row[2],
            "tags": json.loads(row[3]), "timestamp": row[4],
            "host": row[5],
        }

    # ── Service Persistence ────────────────────────────────────────────

    def store_service(self, svc_data: dict[str, Any]) -> str:
        with self._lock:
            self._write(
                """INSERT OR REPLACE INTO services
                   (id, name, version, capabilities, status,
                    registered_at, last_heartbeat, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    svc_data["id"], svc_data.get("name", ""),
                    svc_data.get("version", "1.0.0"),
                    json.dumps(svc_data.get("capabilities", [])),
                    svc_data.get("status", "registered"),
                    svc_data.get("registered_at", time.time()),
                    svc_data.get("last_heartbeat", 0),
                    json.dumps(svc_data.get("metadata", {})),
                ),
            )
            self._write_count += 1
            return svc_data["id"]

    def query_services(self, name: str | None = None,
                       limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            if name:
                cur = self._conn.execute(
                    "SELECT * FROM services WHERE name = ? ORDER BY registered_at DESC LIMIT ?",
                    (name, limit),
                )
            else:
                cur = self._conn.execute(
                    "SELECT * FROM services ORDER BY registered_at DESC LIMIT ?",
                    (limit,),
                )
            self._read_count += 1
            return [self._row_to_service(row) for row in cur.fetchall()]

    @staticmethod
    def _row_to_service(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row[0], "name": row[1], "version": row[2],
            "capabilities": json.loads(row[3]), "status": row[4],
            "registered_at": row[5], "last_heartbeat": row[6],
            "metadata": json.loads(row[7]),
        }

    def delete_service(self, service_id: str):
        with self._lock:
            self._write("DELETE FROM services WHERE id = ?", (service_id,))

    # ── Database Maintenance ───────────────────────────────────────────

    def vacuum(self):
        with self._lock:
            try:
                self._conn.execute("VACUUM")
            except Exception:
                pass

    def get_table_sizes(self) -> dict[str, int]:
        with self._lock:
            tables = [
                "events", "agents", "agent_tasks", "agent_messages",
                "task_graph_nodes", "conversations", "conversation_messages",
                "audit_entries", "metric_points", "services",
            ]
            sizes = {}
            for table in tables:
                cur = self._conn.execute(f"SELECT COUNT(*) FROM {table}")
                sizes[table] = cur.fetchone()[0]
            return sizes

    def clear_all(self):
        with self._lock:
            for table in SchemaManager.TABLES:
                if table != "schema_version":
                    self._write(f"DELETE FROM {table}")
            self._conn.commit()
