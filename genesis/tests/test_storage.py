"""
Tests for Storage Engine (Mission 71) — SQLite persistence for Fabric.
"""

import json
import os
import tempfile
import time

from genesis.fabric.events import EngineeringEvent, EventPriority, EventSeverity
from genesis.fabric.storage import SchemaManager, StorageEngine


class TestSchemaManager:
    def test_schema_creates_tables(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            SchemaManager.ensure_schema(conn)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = {row[0] for row in cursor.fetchall()}
            expected = {
                "events", "agents", "agent_tasks", "agent_messages",
                "task_graph_nodes", "conversations", "conversation_messages",
                "audit_entries", "metric_points", "services", "schema_version",
            }
            for t in expected:
                assert t in tables, f"Missing table: {t}"
            conn.close()
        finally:
            os.unlink(db_path)

    def test_schema_version(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            SchemaManager.ensure_schema(conn)
            cursor = conn.execute("SELECT MAX(version) FROM schema_version")
            assert cursor.fetchone()[0] == SchemaManager.SCHEMA_VERSION
            conn.close()
        finally:
            os.unlink(db_path)


class TestStorageEngine:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        self.engine = StorageEngine(self.db_path)
        self.engine.connect()

    def teardown_method(self):
        try:
            self.engine.disconnect()
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_connect_disconnect(self):
        e = StorageEngine(self.db_path)
        assert not e.connected
        e.connect()
        assert e.connected
        e.disconnect()
        assert not e.connected

    def test_store_and_query_events(self):
        ev = EngineeringEvent(
            type="test.event", origin="test",
            payload={"key": "value"},
            tags=["test", "unit"],
            priority=EventPriority.HIGH,
            severity=EventSeverity.WARNING,
        )
        eid = self.engine.store_event(ev)
        assert eid == ev.id

        results = self.engine.query_events(event_type="test.event")
        assert len(results) == 1
        assert results[0]["type"] == "test.event"
        assert results[0]["payload"]["key"] == "value"
        assert results[0]["tags"] == ["test", "unit"]

    def test_query_events_with_filters(self):
        ev1 = EngineeringEvent(type="a.b", origin="src1", payload={"n": 1})
        ev2 = EngineeringEvent(type="x.y", origin="src2", payload={"n": 2})
        ev3 = EngineeringEvent(type="a.b", origin="src2", payload={"n": 3})
        self.engine.store_event(ev1)
        self.engine.store_event(ev2)
        self.engine.store_event(ev3)

        assert len(self.engine.query_events(event_type="a.b")) == 2
        assert len(self.engine.query_events(event_type="a.b", origin="src1")) == 1
        assert len(self.engine.query_events(event_type="x.y")) == 1
        assert len(self.engine.query_events(origin="src2")) == 2

    def test_count_events(self):
        assert self.engine.count_events() == 0
        self.engine.store_event(EngineeringEvent(type="t1"))
        self.engine.store_event(EngineeringEvent(type="t2"))
        assert self.engine.count_events() == 2

    def test_purge_old_events(self):
        ev = EngineeringEvent(type="old", payload={})
        ev.timestamp = time.time() - 100  # 100 seconds old
        self.engine.store_event(ev)
        self.engine.purge_old_events(max_age_secs=50)
        assert self.engine.count_events() == 0

    def test_store_and_query_agents(self):
        self.engine.store_agent({
            "agent_id": "agent-1", "role": "backend_engineer",
            "name": "Test Agent", "description": "Test",
            "capabilities": ["code"], "max_concurrent_tasks": 2,
            "system_prompt": "", "status": "idle",
            "task_count": 0, "completed_count": 0,
            "failed_count": 0, "created_at": time.time(),
            "metadata": {},
        })
        agents = self.engine.query_agents()
        assert len(agents) == 1
        assert agents[0]["name"] == "Test Agent"
        assert agents[0]["role"] == "backend_engineer"

        agents = self.engine.query_agents(status="idle")
        assert len(agents) == 1

        agents = self.engine.query_agents(status="running")
        assert len(agents) == 0

    def test_delete_agent(self):
        self.engine.store_agent({
            "agent_id": "agent-del", "role": "test",
            "name": "Delete Me", "description": "",
            "capabilities": [], "max_concurrent_tasks": 1,
            "system_prompt": "", "status": "idle",
            "task_count": 0, "completed_count": 0,
            "failed_count": 0, "created_at": time.time(),
            "metadata": {},
        })
        assert len(self.engine.query_agents()) == 1
        self.engine.delete_agent("agent-del")
        assert len(self.engine.query_agents()) == 0

    def test_store_and_query_agent_tasks(self):
        self.engine.store_agent_task({
            "task_id": "task-1", "agent_id": "agent-1",
            "objective": "Do something", "context": {"x": 1},
            "status": "running", "started_at": time.time(),
            "completed_at": 0, "result": None,
            "error": "", "created_at": time.time(),
        })
        tasks = self.engine.query_agent_tasks(agent_id="agent-1")
        assert len(tasks) == 1
        assert tasks[0]["objective"] == "Do something"
        assert tasks[0]["context"] == {"x": 1}

        tasks = self.engine.query_agent_tasks(status="running")
        assert len(tasks) == 1

        tasks = self.engine.query_agent_tasks(status="completed")
        assert len(tasks) == 0

    def test_store_and_query_messages(self):
        self.engine.store_message({
            "id": "msg-1", "sender_id": "agent-a",
            "recipient_id": "agent-b", "content": "Hello!",
            "message_type": "text", "correlation_id": "",
            "timestamp": time.time(), "metadata": {},
        })
        msgs = self.engine.query_messages(agent_id="agent-a")
        assert len(msgs) >= 1

        msgs = self.engine.query_messages(agent_id="agent-b")
        assert len(msgs) >= 1

    def test_store_and_query_task_nodes(self):
        self.engine.store_task_node({
            "id": "node-1", "node_type": "engineering_task",
            "title": "Fix bug", "description": "Fix the critical bug",
            "status": "ready", "parent_id": "",
            "dependencies": [], "blocking": [],
            "estimated_duration_secs": 3600,
            "actual_duration_secs": 0,
            "confidence": 0.9,
            "required_capabilities": [], "required_agent_roles": [],
            "required_providers": [], "assigned_agent_id": "",
            "assigned_provider": "", "evidence": [],
            "rollback_steps": [], "progress": 0.0,
            "tags": ["bug"], "created_at": time.time(),
            "started_at": 0, "completed_at": 0,
            "metadata": {},
        })
        nodes = self.engine.query_task_nodes(status="ready")
        assert len(nodes) == 1
        assert nodes[0]["title"] == "Fix bug"

    def test_store_and_query_conversations(self):
        self.engine.store_conversation({
            "id": "conv-1", "title": "Architecture Review",
            "objective": "Review the architecture",
            "participants": ["alice", "bob"],
            "links": {}, "tags": ["architecture"],
            "summary": "", "decisions": [],
            "parent_id": "", "branch_of": "",
            "created_at": time.time(),
            "updated_at": time.time(),
            "metadata": {},
        })
        convs = self.engine.query_conversations()
        assert len(convs) == 1
        assert convs[0]["title"] == "Architecture Review"
        assert "alice" in convs[0]["participants"]

        convs = self.engine.query_conversations(title_contains="Architecture")
        assert len(convs) == 1

    def test_store_and_query_conversation_messages(self):
        self.engine.store_conversation({
            "id": "conv-msg", "title": "Test",
            "objective": "", "participants": [],
            "links": {}, "tags": [],
            "summary": "", "decisions": [],
            "parent_id": "", "branch_of": "",
            "created_at": time.time(),
            "updated_at": time.time(),
            "metadata": {},
        })
        self.engine.store_conversation_message({
            "id": "cmsg-1", "conversation_id": "conv-msg",
            "role": "user", "content": "Hello",
            "citations": [], "links": {},
            "metadata": {}, "timestamp": time.time(),
        })
        msgs = self.engine.query_conversation_messages("conv-msg")
        assert len(msgs) == 1
        assert msgs[0]["content"] == "Hello"

    def test_store_and_query_audit(self):
        self.engine.store_audit_entry({
            "id": "audit-1", "action": "user.login",
            "actor": "admin", "resource": "system",
            "detail": {"ip": "127.0.0.1"},
            "timestamp": time.time(), "severity": "info",
            "correlation_id": "", "session_id": "",
        })
        entries = self.engine.query_audit(action="user.login")
        assert len(entries) == 1
        assert entries[0]["actor"] == "admin"
        assert entries[0]["detail"]["ip"] == "127.0.0.1"

    def test_store_and_query_metrics(self):
        self.engine.store_metric({
            "name": "test.metric", "value": 42.0,
            "tags": {"env": "test"},
            "timestamp": time.time(), "host": "localhost",
        })
        metrics = self.engine.query_metrics(name="test.metric")
        assert len(metrics) == 1
        assert metrics[0]["value"] == 42.0
        assert metrics[0]["tags"] == {"env": "test"}

    def test_store_and_query_services(self):
        self.engine.store_service({
            "id": "svc-1", "name": "my-service",
            "version": "2.0.0", "capabilities": ["http"],
            "status": "registered",
            "registered_at": time.time(),
            "last_heartbeat": time.time(),
            "metadata": {},
        })
        svcs = self.engine.query_services(name="my-service")
        assert len(svcs) == 1
        assert svcs[0]["version"] == "2.0.0"

    def test_delete_service(self):
        self.engine.store_service({
            "id": "svc-del", "name": "del-me",
            "version": "1.0", "capabilities": [],
            "status": "registered",
            "registered_at": time.time(),
            "last_heartbeat": 0, "metadata": {},
        })
        assert len(self.engine.query_services()) == 1
        self.engine.delete_service("svc-del")
        assert len(self.engine.query_services()) == 0

    def test_get_table_sizes(self):
        sizes = self.engine.get_table_sizes()
        assert isinstance(sizes, dict)
        assert "events" in sizes
        assert "agents" in sizes

    def test_clear_all(self):
        self.engine.store_event(EngineeringEvent(type="clear.test"))
        assert self.engine.count_events() > 0
        self.engine.clear_all()
        assert self.engine.count_events() == 0

    def test_stats(self):
        stats = self.engine.stats()
        assert stats["connected"] is True
        assert stats["db_path"] == self.db_path
        assert stats["write_count"] >= 0
        assert stats["read_count"] >= 0
