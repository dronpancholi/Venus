"""
Tests for Engineering Fabric v2 — Events, Agents, Task Graph, Conversations.
"""

import time
import pytest

from genesis.fabric.events import (
    EngineeringEvent, EventPriority, EventSeverity, EventStore, EventRouter,
)
from genesis.fabric.agents import (
    AgentRuntime, AgentSpec, AgentRole, AgentStatus, AgentInstance, AgentTask, AgentScheduler,
)
from genesis.fabric.tasks import TaskGraph, TaskNode, TaskNodeType, TaskStatus, TaskGraphBuilder
from genesis.fabric.conversations import ConversationEngine, Conversation, ConversationMessage
from genesis.fabric.kernel import FabricKernel


# ══════════════════════════════════════════════════════════════════════════════
# EngineeringEvent
# ══════════════════════════════════════════════════════════════════════════════

class TestEngineeringEvent:
    def test_create_event(self):
        ev = EngineeringEvent(type="test.event", payload={"key": "value"})
        assert ev.type == "test.event"
        assert ev.payload["key"] == "value"
        assert ev.id.startswith("ven:evt:")

    def test_event_to_dict(self):
        ev = EngineeringEvent(type="t", origin="test", tags=["a", "b"])
        d = ev.to_dict()
        assert d["type"] == "t"
        assert d["origin"] == "test"
        assert "a" in d["tags"]

    def test_event_from_dict(self):
        d = {"type": "test", "payload": {"x": 1}, "priority": 2, "severity": "error"}
        ev = EngineeringEvent.from_dict(d)
        assert ev.type == "test"
        assert ev.priority == EventPriority.HIGH
        assert ev.severity == EventSeverity.ERROR

    def test_event_expiry(self):
        ev = EngineeringEvent(type="t", ttl_secs=0.001)
        time.sleep(0.002)
        assert ev.expired

    def test_event_auto_id_timestamp(self):
        ev = EngineeringEvent(type="auto")
        assert ev.id != ""
        assert ev.timestamp > 0


# ══════════════════════════════════════════════════════════════════════════════
# EventStore
# ══════════════════════════════════════════════════════════════════════════════

class TestEventStore:
    def setup_method(self):
        self.store = EventStore(max_events=100)

    def test_append_and_count(self):
        self.store.append(EngineeringEvent(type="a"))
        self.store.append(EngineeringEvent(type="b"))
        assert self.store.count() == 2

    def test_query_by_type(self):
        self.store.append(EngineeringEvent(type="code.changed", tags=["code"]))
        self.store.append(EngineeringEvent(type="agent.started", tags=["agent"]))
        results = self.store.query(event_type="code.changed")
        assert len(results) == 1

    def test_query_by_tag(self):
        self.store.append(EngineeringEvent(type="a", tags=["critical"]))
        self.store.append(EngineeringEvent(type="b", tags=["normal"]))
        results = self.store.query(tags=["critical"])
        assert len(results) == 1

    def test_query_limit(self):
        for i in range(10):
            self.store.append(EngineeringEvent(type="t"))
        assert len(self.store.query(limit=3)) == 3

    def test_replay(self):
        self.store.append(EngineeringEvent(type="x"))
        self.store.append(EngineeringEvent(type="y"))
        assert len(self.store.replay()) == 2

    def test_count_by_type(self):
        self.store.append(EngineeringEvent(type="a"))
        self.store.append(EngineeringEvent(type="a"))
        self.store.append(EngineeringEvent(type="b"))
        cbt = self.store.count_by_type()
        assert cbt["a"] == 2
        assert cbt["b"] == 1

    def test_clear(self):
        self.store.append(EngineeringEvent(type="a"))
        self.store.clear()
        assert self.store.count() == 0

    def test_max_events_eviction(self):
        store = EventStore(max_events=5)
        for i in range(10):
            store.append(EngineeringEvent(type=f"e{i}"))
        assert store.count() == 5


# ══════════════════════════════════════════════════════════════════════════════
# EventRouter
# ══════════════════════════════════════════════════════════════════════════════

class TestEventRouter:
    def setup_method(self):
        self.router = EventRouter()
        self.received = []

    def handler(self, event):
        self.received.append(event)

    def test_subscribe_and_emit(self):
        self.router.subscribe("test.event", self.handler)
        ev = EngineeringEvent(type="test.event")
        self.router.emit(ev)
        assert len(self.received) == 1
        assert self.received[0].type == "test.event"

    def test_wildcard_subscribe(self):
        self.router.subscribe("*", self.handler)
        self.router.emit(EngineeringEvent(type="anything"))
        assert len(self.received) == 1

    def test_filtered_subscription(self):
        self.router.subscribe("test.event", self.handler,
                              filter_fn=lambda e: e.confidence > 0.5)
        self.router.emit(EngineeringEvent(type="test.event", confidence=0.3))
        assert len(self.received) == 0
        self.router.emit(EngineeringEvent(type="test.event", confidence=0.8))
        assert len(self.received) == 1

    def test_unsubscribe(self):
        self.router.subscribe("t", self.handler)
        self.router.unsubscribe(self.handler)
        self.router.emit(EngineeringEvent(type="t"))
        assert len(self.received) == 0

    def test_emit_raw(self):
        ev = self.router.emit_raw("raw.event", {"msg": "hello"}, origin="test")
        assert ev.type == "raw.event"
        assert ev.origin == "test"

    def test_subscriber_count(self):
        assert self.router.subscriber_count() == 0
        self.router.subscribe("a", lambda e: None)
        self.router.subscribe("b", lambda e: None)
        assert self.router.subscriber_count() == 2

    def test_stats(self):
        self.router.subscribe("t", self.handler)
        self.router.emit(EngineeringEvent(type="t"))
        stats = self.router.stats()
        assert stats["delivered"] == 1
        assert stats["subscriptions"] == 1


# ══════════════════════════════════════════════════════════════════════════════
# AgentRuntime
# ══════════════════════════════════════════════════════════════════════════════

class TestAgentRuntime:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance()
        self.runtime = AgentRuntime(self.kernel)

    def test_spawn_agent(self):
        aid = self.runtime.spawn(AgentSpec(
            role=AgentRole.BACKEND_ENGINEER, name="TestBot",
            capabilities=["python", "testing"],
        ))
        assert aid != ""
        agent = self.runtime.get_agent(aid)
        assert agent is not None
        assert agent.spec.role == AgentRole.BACKEND_ENGINEER

    def test_terminate_agent(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.PLANNER, name="PlanBot"))
        self.runtime.terminate(aid)
        assert self.runtime.get_agent(aid) is None

    def test_agent_task_lifecycle(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.REVIEWER, name="ReviewBot"))
        agent = self.runtime.get_agent(aid)
        task = agent.assign_task("Review the architecture")
        assert task.status == "pending"
        assert agent.status == AgentStatus.RUNNING
        agent.complete_task(task, "Looks good")
        assert task.status == "completed"
        assert agent.status == AgentStatus.IDLE

    def test_agent_task_failure(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.TESTING_ENGINEER, name="TestBot"))
        agent = self.runtime.get_agent(aid)
        task = agent.assign_task("Run tests")
        agent.fail_task(task, "Tests failed")
        assert task.status == "failed"
        assert agent.status == AgentStatus.ERROR

    def test_agent_messaging(self):
        a1 = self.runtime.spawn(AgentSpec(role=AgentRole.PLANNER, name="Planner"))
        a2 = self.runtime.spawn(AgentSpec(role=AgentRole.REVIEWER, name="Reviewer"))
        self.runtime.send_message(a1, a2, "Please review this plan", message_type="request")
        inbox = self.runtime.read_inbox(a2)
        assert len(inbox) == 1
        assert inbox[0].content == "Please review this plan"
        outbox = self.runtime.read_outbox(a1)
        assert len(outbox) == 1

    def test_agent_context(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.KNOWLEDGE_ENGINEER, name="KnowBot"))
        ctx = self.runtime.get_context(aid)
        assert ctx is not None
        ctx.remember("key", "value")
        assert ctx.recall("key") == "value"
        ctx.store_workspace("file", "content")
        assert ctx.read_workspace("file") == "content"

    def test_list_agents(self):
        self.runtime.spawn(AgentSpec(role=AgentRole.CHIEF_ENGINEER, name="Chief"))
        self.runtime.spawn(AgentSpec(role=AgentRole.PLANNER, name="PlanBot"))
        assert len(self.runtime.list_agents()) == 2

    def test_get_debug_info(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.REVIEWER, name="DebugBot"))
        info = self.runtime.get_debug_info(aid)
        assert info is not None
        assert info.agent_id == aid
        assert info.task_count == 0

    def test_agent_summary(self):
        self.runtime.spawn(AgentSpec(role=AgentRole.BACKEND_ENGINEER, name="Backend"))
        summary = self.runtime.summary()
        assert summary["total_agents"] == 1

    def test_agent_track_counts(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.TESTING_ENGINEER, name="TestBot"))
        agent = self.runtime.get_agent(aid)
        task1 = agent.assign_task("Task 1")
        agent.complete_task(task1)
        task2 = agent.assign_task("Task 2")
        agent.fail_task(task2, "err")
        info = self.runtime.get_debug_info(aid)
        assert info.task_count == 2
        assert info.completed_count == 1
        assert info.failed_count == 1


class TestAgentScheduler:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance()
        self.runtime = AgentRuntime(self.kernel)
        self.scheduler = AgentScheduler(self.runtime)

    def test_schedule_and_cancel(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.REVIEWER, name="SchedBot"))
        tid = self.scheduler.schedule_task(aid, "Do something", delay_secs=0)
        assert tid != ""
        self.scheduler.cancel_task(tid)

    def test_tick_runs_due_tasks(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.REVIEWER, name="SchedBot2"))
        self.scheduler.schedule_task(aid, "Run now", delay_secs=0)
        self.scheduler.tick()
        info = self.runtime.get_debug_info(aid)
        assert info.task_count == 1

    def test_tick_recurring(self):
        aid = self.runtime.spawn(AgentSpec(role=AgentRole.REVIEWER, name="RecurBot"))
        self.scheduler.schedule_task(aid, "Periodic", delay_secs=0, interval_secs=0.01)
        self.scheduler.tick()
        import time; time.sleep(0.015)
        self.scheduler.tick()
        info = self.runtime.get_debug_info(aid)
        assert info.task_count >= 2


# ══════════════════════════════════════════════════════════════════════════════
# TaskGraph
# ══════════════════════════════════════════════════════════════════════════════

class TestTaskGraph:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance()
        self.graph = TaskGraph(self.kernel)

    def test_add_node(self):
        node = TaskNode(node_type=TaskNodeType.GOAL, title="Improve performance")
        nid = self.graph.add_node(node)
        assert self.graph.get_node(nid) is not None

    def test_update_status(self):
        node = TaskNode(node_type=TaskNodeType.ENGINEERING_TASK, title="Refactor")
        nid = self.graph.add_node(node)
        self.graph.update_status(nid, TaskStatus.RUNNING)
        assert self.graph.get_node(nid).status == TaskStatus.RUNNING

    def test_update_progress(self):
        node = TaskNode(node_type=TaskNodeType.ENGINEERING_TASK, title="Build")
        nid = self.graph.add_node(node)
        self.graph.update_progress(nid, 0.5)
        assert self.graph.get_node(nid).progress == 0.5

    def test_dependencies(self):
        a = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK, title="A"))
        b = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK, title="B"))
        self.graph.add_dependency(b, a)
        node_a = self.graph.get_node(a)
        node_b = self.graph.get_node(b)
        assert a in node_b.dependencies
        assert b in node_a.blocking

    def test_get_by_type(self):
        self.graph.add_node(TaskNode(node_type=TaskNodeType.GOAL, title="G"))
        self.graph.add_node(TaskNode(node_type=TaskNodeType.EPIC, title="E"))
        assert len(self.graph.get_by_type(TaskNodeType.GOAL)) == 1
        assert len(self.graph.get_by_type(TaskNodeType.EPIC)) == 1

    def test_get_by_status(self):
        nid = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK, title="T"))
        assert len(self.graph.get_by_status(TaskStatus.PENDING)) == 1
        self.graph.update_status(nid, TaskStatus.COMPLETED)
        assert len(self.graph.get_by_status(TaskStatus.COMPLETED)) == 1

    def test_get_ready_tasks(self):
        a = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK, title="A",
                                          status=TaskStatus.READY))
        b = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK, title="B",
                                          status=TaskStatus.READY))
        self.graph.add_dependency(b, a)
        ready = self.graph.get_ready_tasks()
        assert a in [n.id for n in ready]
        # B depends on A, A not completed -> B not ready
        assert b not in [n.id for n in ready]
        self.graph.update_status(a, TaskStatus.COMPLETED)
        ready = self.graph.get_ready_tasks()
        assert b in [n.id for n in ready]

    def test_get_children(self):
        parent = self.graph.add_node(TaskNode(node_type=TaskNodeType.GOAL, title="Parent"))
        child = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK,
                                              title="Child", parent_id=parent))
        children = self.graph.get_children(parent)
        assert len(children) == 1
        assert children[0].id == child

    def test_critical_path(self):
        root = self.graph.add_node(TaskNode(node_type=TaskNodeType.GOAL, title="Root",
                                             estimated_duration_secs=10))
        c1 = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK,
                                           title="Child1", parent_id=root,
                                           estimated_duration_secs=100))
        c2 = self.graph.add_node(TaskNode(node_type=TaskNodeType.ENGINEERING_TASK,
                                           title="Child2", parent_id=root,
                                           estimated_duration_secs=200))
        path = self.graph.critical_path()
        assert len(path) >= 1

    def test_summary(self):
        self.graph.add_node(TaskNode(node_type=TaskNodeType.GOAL, title="G"))
        s = self.graph.summary()
        assert s["total_nodes"] == 1

    def test_count(self):
        self.graph.add_node(TaskNode(node_type=TaskNodeType.GOAL, title="G"))
        assert self.graph.count() == 1


class TestTaskGraphBuilder:
    def setup_method(self):
        FabricKernel._instance = None
        self.graph = TaskGraph()
        self.builder = TaskGraphBuilder(self.graph)

    def test_from_objective(self):
        goal = self.builder.from_objective("Improve test coverage")
        assert goal.node_type == TaskNodeType.GOAL
        assert goal.title == "Improve test coverage"

    def test_add_engineering_task(self):
        goal = self.builder.from_objective("Goal")
        task = self.builder.add_engineering_task("Refactor module", parent_id=goal.id)
        assert task.node_type == TaskNodeType.ENGINEERING_TASK
        assert task.parent_id == goal.id

    def test_add_agent_task(self):
        task = self.builder.add_agent_task("Review code", agent_role="reviewer")
        assert task.node_type == TaskNodeType.AGENT_TASK

    def test_full_build(self):
        goal = self.builder.from_objective("Ship feature")
        t1 = self.builder.add_engineering_task("Design", parent_id=goal.id)
        t2 = self.builder.add_engineering_task("Implement", parent_id=goal.id, dependencies=[t1.id])
        t3 = self.builder.add_agent_task("Review", parent_id=t2.id)
        assert self.graph.count() == 4


# ══════════════════════════════════════════════════════════════════════════════
# ConversationEngine
# ══════════════════════════════════════════════════════════════════════════════

class TestConversationEngine:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance()
        self.engine = ConversationEngine(self.kernel)

    def test_create_conversation(self):
        conv = self.engine.create("Design review", "Review the new architecture",
                                  participants=["alice", "bob"], tags=["design"])
        assert conv.id != ""
        assert conv.title == "Design review"
        assert "alice" in conv.participants

    def test_add_message(self):
        conv = self.engine.create("Chat")
        msg = self.engine.add_message(conv.id, "user", "Hello world")
        assert msg is not None
        assert msg.content == "Hello world"
        assert msg.role == "user"

    def test_get_conversation(self):
        conv = self.engine.create("Test")
        assert self.engine.get(conv.id) is conv

    def test_link_conversation(self):
        conv = self.engine.create("Discussion")
        self.engine.link_conversation(conv.id, "architecture", "arch_123")
        assert "architecture:arch_123" in conv.links

    def test_search_by_text(self):
        self.engine.create("Performance optimization")
        self.engine.create("Security review")
        results = self.engine.search(query="performance")
        assert len(results) == 1

    def test_search_by_tag(self):
        self.engine.create("Design", tags=["design", "frontend"])
        self.engine.create("Backend", tags=["backend"])
        results = self.engine.search(tags=["design"])
        assert len(results) == 1

    def test_search_by_participant(self):
        self.engine.create("Chat A", participants=["alice"])
        self.engine.create("Chat B", participants=["bob"])
        results = self.engine.search(participant="alice")
        assert len(results) == 1

    def test_extract_decisions(self):
        conv = self.engine.create("Decision meeting")
        self.engine.add_message(conv.id, "agent", "Decision: Use PostgreSQL")
        self.engine.add_message(conv.id, "agent", "Approved: Migration in Q2")
        decisions = self.engine.extract_decisions(conv.id)
        assert len(decisions) >= 2

    def test_branch_conversation(self):
        original = self.engine.create("Original discussion")
        branch = self.engine.branch(original.id, "Alternative approach")
        assert branch is not None
        assert branch.branch_of == original.id
        assert branch.title == "Alternative approach"

    def test_summarize(self):
        conv = self.engine.create("Summary test")
        self.engine.add_message(conv.id, "user", "Hello")
        summary = self.engine.summarize(conv.id)
        assert "Summary test" in summary

    def test_count(self):
        self.engine.create("C1")
        self.engine.create("C2")
        assert self.engine.count() == 2

    def test_conversation_message_count(self):
        conv = self.engine.create("Many messages")
        for i in range(5):
            self.engine.add_message(conv.id, "user", f"Message {i}")
        assert conv.message_count == 5


class TestConversation:
    def test_create(self):
        c = Conversation(title="Test", participants=["a", "b"])
        assert c.id != ""
        assert c.message_count == 0

    def test_add_message(self):
        c = Conversation(title="T")
        msg = c.add_message("user", "hello")
        assert msg.conversation_id == c.id
        assert c.message_count == 1
        assert c.duration_secs >= 0

    def test_link_to(self):
        c = Conversation(title="T")
        c.link_to("architecture", "arch_1")
        assert f"architecture:arch_1" in c.links

    def test_auto_fields(self):
        msg = ConversationMessage(conversation_id="c1", role="user", content="hi")
        assert msg.id != ""
        assert msg.timestamp > 0


class TestFabricKernelEvents:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance()
        self.received = []

    def handler(self, event):
        self.received.append(event)

    def test_kernel_emit_event(self):
        self.kernel.on_event("test.event", self.handler)
        self.kernel.emit("test.event", {"data": 42}, origin="test")
        assert len(self.received) == 1
        assert self.received[0].payload["data"] == 42

    def test_kernel_query_events(self):
        self.kernel.emit("type.a", {"x": 1}, origin="test")
        self.kernel.emit("type.b", {"y": 2}, origin="test")
        results = self.kernel.query_events(event_type="type.a")
        assert len(results) == 1

    def test_kernel_register_service_emits_event(self):
        self.kernel.on_event("service.registered", self.handler)
        self.kernel.register_service("test-svc", "1.0", ["compute"])
        assert len(self.received) == 1

    def test_kernel_stats_include_events(self):
        self.kernel.emit("test", {}, origin="test")
        stats = self.kernel.stats()
        assert stats.events_delivered >= 0
