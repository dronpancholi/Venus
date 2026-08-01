"""Tests for GENESIS XII Programs A–D: Fabric, Unified Graph, Execution Engine, Autonomous Cycle."""

import time
import pytest

# ── Program A: Engineering Fabric ──

from genesis.fabric.kernel import FabricKernel, KernelState
from genesis.fabric.bus import MessageBus, Message, MessagePriority, TypedChannel
from genesis.fabric.contracts import EventContract, ContractSchema, ContractRegistry, ContractViolation
from genesis.fabric.context import Context, CorrelationID, TransactionSpan
from genesis.fabric.discovery import ServiceRegistry, ServiceInstance
from genesis.fabric.scheduler import DistributedScheduler
from genesis.fabric.policy import PolicyEngine, Policy, PolicyEffect, PolicyResult
from genesis.fabric.metrics import FabricMetrics
from genesis.fabric.audit import AuditLog
from genesis.fabric.session import EngineeringSession, SessionStage


class TestFabricKernel:
    def test_singleton(self):
        k1 = FabricKernel.instance()
        k2 = FabricKernel.instance()
        assert k1 is k2

    def test_boot(self):
        k = FabricKernel.instance()
        k.boot()
        assert k.state == KernelState.RUNNING

    def test_register_service(self):
        k = FabricKernel.instance()
        svc = k.register_service("test-svc", "1.0", ["cap_a"])
        assert svc.name == "test-svc"
        assert svc.id is not None

    def test_send_message(self):
        k = FabricKernel.instance()
        received = []
        k.subscribe("test.topic", lambda msg: received.append(msg))
        k.send("test.topic", {"key": "val"})
        assert len(received) >= 1
        assert received[-1].body["key"] == "val"

    def test_begin_session(self):
        k = FabricKernel.instance()
        ctx = k.begin_session("test-session")
        assert ctx.session_id is not None
        assert k.get_context(ctx.session_id) is not None
        k.end_session(ctx.session_id)

    def test_health(self):
        k = FabricKernel.instance()
        h = k.health()
        assert h.status == "running"

    def test_stats(self):
        k = FabricKernel.instance()
        s = k.stats()
        assert s.state == "running"

    def test_on_event(self):
        k = FabricKernel.instance()
        events = []
        k.on("test.event", lambda d: events.append(d))
        k._emit("test.event", {"data": 1})
        assert len(events) == 1


class TestMessageBus:
    def test_publish_subscribe(self):
        bus = MessageBus()
        bus.start()
        received = []
        bus.subscribe("topic.a", lambda msg: received.append(msg))
        bus.publish("topic.a", {"hello": "world"})
        assert len(received) >= 1

    def test_multiple_subscribers(self):
        bus = MessageBus()
        bus.start()
        r1, r2 = [], []
        bus.subscribe("t", lambda m: r1.append(m))
        bus.subscribe("t", lambda m: r2.append(m))
        bus.publish("t", {"x": 1})
        assert len(r1) >= 1 and len(r2) >= 1

    def test_channel_count(self):
        bus = MessageBus()
        bus.start()
        bus.subscribe("a.a", lambda m: None)
        bus.subscribe("b.b", lambda m: None)
        assert bus.channel_count() >= 2

    def test_wildcard_pattern(self):
        bus = MessageBus()
        bus.start()
        received = []
        bus.subscribe("system.*", lambda m: received.append(m))
        bus.publish("system.heartbeat", {})
        bus.publish("system.error", {})
        assert len(received) >= 2

    def test_message_expiry(self):
        import time
        bus = MessageBus()
        msg = Message(topic="t", body={}, timestamp=time.time() - 100, ttl_secs=1)
        assert msg.expired


class TestEventContract:
    def test_schema_validation(self):
        schema = ContractSchema(
            topic="test",
            required_fields=["name", "version"],
            field_types={"name": "string", "version": "string"},
        )
        errors = schema.validate_body({"name": "test"})
        assert len(errors) == 1
        assert "version" in errors[0]

    def test_valid_message(self):
        schema = ContractSchema(
            required_fields=["name"],
            field_types={"name": "string"},
        )
        errors = schema.validate_body({"name": "hello"})
        assert len(errors) == 0

    def test_contract_registry(self):
        reg = ContractRegistry()
        contract = EventContract(topic="sys.boot", schema=ContractSchema())
        reg.register(contract)
        assert reg.get("sys.boot") is not None
        assert len(reg.list_contracts()) == 1

    def test_assert_valid(self):
        schema = ContractSchema(required_fields=["x"])
        contract = EventContract(topic="t", schema=schema)
        with pytest.raises(ContractViolation):
            contract.assert_valid({"y": 1})


class TestContext:
    def test_create(self):
        ctx = Context()
        assert ctx.correlation_id is not None

    def test_set_get(self):
        ctx = Context()
        ctx.set("key", "value")
        assert ctx.get("key") == "value"
        assert ctx.has("key")

    def test_begin_span(self):
        ctx = Context()
        span = ctx.begin_span("test-op", "svc")
        assert span.operation == "test-op"
        ctx.end_span(span.id)
        assert span.status == "success"

    def test_child(self):
        ctx = Context()
        child = ctx.child()
        assert child.correlation_id != ctx.correlation_id


class TestServiceRegistry:
    def test_register_find(self):
        reg = ServiceRegistry()
        inst = reg.register("svc-a", "2.0", ["logging"])
        assert reg.get(inst.id).name == "svc-a"
        assert len(reg.find_by_name("svc-a")) == 1

    def test_find_by_capability(self):
        reg = ServiceRegistry()
        reg.register("a", "1.0", ["auth"])
        reg.register("b", "1.0", ["auth"])
        assert len(reg.find_by_capability("auth")) == 2

    def test_unregister(self):
        reg = ServiceRegistry()
        inst = reg.register("temp")
        assert reg.unregister(inst.id)
        assert reg.get(inst.id) is None

    def test_heartbeat(self):
        reg = ServiceRegistry()
        inst = reg.register("svc")
        reg.heartbeat(inst.id)
        h = reg.health(inst.id)
        assert h.status == "healthy"


class TestDistributedScheduler:
    def test_schedule(self):
        sched = DistributedScheduler()
        sched.start()
        time.sleep(0.02)
        ran = []
        task = sched.schedule(0.01, lambda: ran.append(1), "fast")
        time.sleep(0.1)
        sched.stop()
        assert len(ran) >= 1

    def test_cancel(self):
        sched = DistributedScheduler()
        task = sched.schedule(60, lambda: None)
        assert sched.cancel(task.id)
        assert sched.get_task(task.id) is None

    def test_pause_resume(self):
        sched = DistributedScheduler()
        task = sched.schedule(1, lambda: None)
        assert sched.pause(task.id)
        assert not task.enabled
        assert sched.resume(task.id)
        assert task.enabled


class TestPolicyEngine:
    def test_allow(self):
        pe = PolicyEngine()
        result = pe.evaluate("svc", "read")
        assert result.allowed

    def test_deny(self):
        pe = PolicyEngine()
        pe.add(Policy(name="deny-all", effect=PolicyEffect.DENY, service="svc", action="read"))
        result = pe.evaluate("svc", "read")
        assert not result.allowed

    def test_warn(self):
        pe = PolicyEngine()
        pe.add(Policy(name="warn-op", effect=PolicyEffect.WARN, service="svc", action="write"))
        result = pe.evaluate("svc", "write")
        assert result.allowed
        assert len(result.warnings) == 1

    def test_policy_applies(self):
        p = Policy(name="p1", service="a", action="read")
        assert p.applies_to("a", "read")
        assert not p.applies_to("b", "read")


class TestFabricMetrics:
    def test_record_counter(self):
        m = FabricMetrics()
        m.record("req.count", 1)
        m.record("req.count", 2)
        assert m.counter("req.count") == 3.0

    def test_gauge(self):
        m = FabricMetrics()
        m.gauge("cpu", 50.0)
        assert m.gauge_value("cpu") == 50.0

    def test_histogram(self):
        m = FabricMetrics()
        for v in range(1, 101):
            m.record("latency", float(v))
        h = m.histogram("latency")
        assert h["min"] == 1.0
        assert h["max"] == 100.0
        assert h["count"] == 100
        assert 50 <= h["median"] <= 51


class TestAuditLog:
    def test_log(self):
        log = AuditLog()
        e = log.log("test.action", {"key": "val"}, actor="tester")
        assert e.action == "test.action"
        assert e.actor == "tester"

    def test_query(self):
        log = AuditLog()
        log.log("action.a")
        log.log("action.b")
        assert len(log.query(action="action.a")) >= 1

    def test_search(self):
        log = AuditLog()
        log.log("deploy", {"env": "prod"})
        results = log.search("deploy")
        assert len(results) >= 1


class TestEngineeringSession:
    def test_create(self):
        s = EngineeringSession("test-session")
        assert s.stage == SessionStage.INIT
        assert s.id

    def test_transition(self):
        s = EngineeringSession()
        s.transition(SessionStage.OBSERVE)
        assert s.stage == SessionStage.OBSERVE

    def test_complete_stage(self):
        s = EngineeringSession()
        s.transition(SessionStage.COMPILE)
        s.complete_stage(output={"files": 10})
        assert s._stage_results[SessionStage.COMPILE].status == "completed"

    def test_fail(self):
        s = EngineeringSession()
        s.fail("something broke")
        assert s._status == "failed"

    def test_artifacts(self):
        s = EngineeringSession()
        s.add_artifact("report", {"data": 42})
        assert s.get_artifact("report")["data"] == 42


# ── Program B: Unified Engineering Graph ──

from genesis.graph_v2.core import (
    GraphLayer, GraphNode, GraphEdge, LayerType, UnifiedGraph, GraphSnapshot,
)
from genesis.graph_v2.layers import (
    StructuralGraph, SemanticGraph, CapabilityGraph, ArchitectureGraph,
    RuntimeGraph, DependencyGraph, KnowledgeGraph, MemoryGraph, EvolutionGraph,
    ExperimentGraph, ResearchGraph, OrganizationGraph,
)
from genesis.graph_v2.versioning import GraphVersioning, GraphDiff, GraphMerge
from genesis.graph_v2.analytics import GraphAnalytics
from genesis.graph_v2.index import GraphIndex
from genesis.graph_v2.partition import GraphPartition
from genesis.graph_v2.federation import GraphFederation
from genesis.graph_v2.compression import GraphCompression


class TestGraphLayer:
    def test_add_node(self):
        layer = GraphLayer("test", LayerType.STRUCTURAL)
        nid = layer.add_node(GraphNode(name="module_a", node_type="module"))
        assert layer.get_node(nid).name == "module_a"

    def test_add_edge(self):
        layer = GraphLayer("t", LayerType.DEPENDENCY)
        a = layer.add_node(GraphNode(name="a"))
        b = layer.add_node(GraphNode(name="b"))
        eid = layer.add_edge(GraphEdge(source_id=a, target_id=b, edge_type="depends"))
        assert layer.get_edge(eid).edge_type == "depends"

    def test_remove_node(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        nid = layer.add_node(GraphNode())
        assert layer.remove_node(nid)
        assert layer.get_node(nid) is None

    def test_neighbors(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        a = layer.add_node(GraphNode(name="a"))
        b = layer.add_node(GraphNode(name="b"))
        layer.add_edge(GraphEdge(source_id=a, target_id=b))
        assert len(layer.neighbors(a)) == 1

    def test_find_by_label(self):
        layer = GraphLayer("t", LayerType.SEMANTIC)
        layer.add_node(GraphNode(name="x", labels=["critical"]))
        assert len(layer.find_nodes_by_label("critical")) == 1

    def test_find_by_property(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(name="svc", properties={"lang": "python"}))
        results = layer.find_nodes(property_filter={"lang": "python"})
        assert len(results) == 1

    def test_snapshot(self):
        layer = GraphLayer("t", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode())
        snap = layer.snapshot()
        assert snap.node_count == 1


class TestUnifiedGraph:
    def test_create_layer(self):
        ug = UnifiedGraph()
        layer = ug.create_layer("structural", LayerType.STRUCTURAL)
        assert ug.get_layer("structural") is layer

    def test_remove_layer(self):
        ug = UnifiedGraph()
        ug.create_layer("tmp", LayerType.STRUCTURAL)
        assert ug.remove_layer("tmp")
        assert ug.get_layer("tmp") is None

    def test_list_layers(self):
        ug = UnifiedGraph()
        ug.create_layer("s", LayerType.STRUCTURAL)
        ug.create_layer("d", LayerType.DEPENDENCY)
        assert len(ug.list_layers()) == 2
        assert len(ug.list_layers(LayerType.STRUCTURAL)) == 1

    def test_snapshot(self):
        ug = UnifiedGraph()
        ug.create_layer("s", LayerType.STRUCTURAL)
        snap = ug.snapshot()
        assert snap.node_count >= 0


class TestAllLayers:
    def test_structural(self):
        g = StructuralGraph()
        assert g.layer_type == LayerType.STRUCTURAL

    def test_semantic(self):
        g = SemanticGraph()
        assert g.layer_type == LayerType.SEMANTIC

    def test_capability(self):
        g = CapabilityGraph()
        assert g.layer_type == LayerType.CAPABILITY

    def test_knowledge(self):
        g = KnowledgeGraph()
        assert g.layer_type == LayerType.KNOWLEDGE

    def test_memory(self):
        g = MemoryGraph()
        assert g.layer_type == LayerType.MEMORY

    def test_evolution(self):
        g = EvolutionGraph()
        assert g.layer_type == LayerType.EVOLUTION

    def test_experiment(self):
        g = ExperimentGraph()
        assert g.layer_type == LayerType.EXPERIMENT

    def test_research(self):
        g = ResearchGraph()
        assert g.layer_type == LayerType.RESEARCH

    def test_organization(self):
        g = OrganizationGraph()
        assert g.layer_type == LayerType.ORGANIZATION

    def test_architecture(self):
        g = ArchitectureGraph()
        assert g.layer_type == LayerType.ARCHITECTURE

    def test_runtime(self):
        g = RuntimeGraph()
        assert g.layer_type == LayerType.RUNTIME

    def test_dependency(self):
        g = DependencyGraph()
        assert g.layer_type == LayerType.DEPENDENCY


class TestGraphVersioning:
    def test_snapshot_layer(self):
        gv = GraphVersioning()
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(name="a"))
        snap = gv.snapshot_layer(layer)
        assert snap.node_count == 1

    def test_diff(self):
        gv = GraphVersioning()
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        nid = layer.add_node(GraphNode(name="a"))
        snap1 = gv.snapshot_layer(layer)
        layer.add_node(GraphNode(name="b"))
        snap2 = gv.snapshot_layer(layer)
        diff = gv.diff("t", snap1.id, snap2.id)
        assert diff.total_changes >= 1


class TestGraphMerge:
    def test_merge_layers(self):
        merge = GraphMerge()
        base = GraphLayer("base", LayerType.STRUCTURAL)
        overlay = GraphLayer("over", LayerType.STRUCTURAL)
        base.add_node(GraphNode(id="n1", name="keep"))
        overlay.add_node(GraphNode(id="n2", name="new"))
        result = merge.merge_layers(base, overlay)
        assert result.node_count() == 2


class TestGraphAnalytics:
    def test_density(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        a = layer.add_node(GraphNode(id="a"))
        b = layer.add_node(GraphNode(id="b"))
        layer.add_edge(GraphEdge(source_id=a, target_id=b))
        assert GraphAnalytics.density(layer) > 0

    def test_component_analysis(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(id="a"))
        layer.add_node(GraphNode(id="b"))
        ca = GraphAnalytics.component_analysis(layer)
        assert ca["component_count"] >= 1

    def test_degree_centrality(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        a = layer.add_node(GraphNode(id="a"))
        b = layer.add_node(GraphNode(id="b"))
        layer.add_edge(GraphEdge(source_id=a, target_id=b))
        dc = GraphAnalytics.degree_centrality(layer)
        assert dc["a"] > 0


class TestGraphIndex:
    def test_index_layer(self):
        idx = GraphIndex()
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(name="svc1", node_type="service", labels=["critical"]))
        idx.index_layer(layer)
        assert len(idx.find_by_type("service")) == 1
        assert len(idx.find_by_label("critical")) == 1

    def test_search(self):
        idx = GraphIndex()
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(name="user-service"))
        idx.index_layer(layer)
        results = idx.search("user")
        assert len(results) >= 1


class TestGraphPartition:
    def test_by_label(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(id="a", labels=["critical"]))
        layer.add_node(GraphNode(id="b", labels=["normal"]))
        parts = GraphPartition.by_label(layer)
        assert len(parts) >= 1

    def test_random_shard(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        for i in range(10):
            layer.add_node(GraphNode(id=f"n{i}"))
        shards = GraphPartition.random_shard(layer, 3)
        assert len(shards) == 3


class TestGraphFederation:
    def test_register(self):
        gf = GraphFederation()
        ug = UnifiedGraph()
        gf.register("local", ug)
        assert len(gf.summary()["graph_names"]) == 1

    def test_federated_graph(self):
        gf = GraphFederation()
        ug1 = UnifiedGraph()
        ug2 = UnifiedGraph()
        gf.register("a", ug1)
        gf.register("b", ug2)
        merged = gf.federated_graph()
        assert merged is not None


class TestGraphCompression:
    def test_serialize_deserialize(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(name="test"))
        data = GraphCompression.serialize_layer(layer)
        restored = GraphCompression.deserialize_layer(data)
        assert restored.node_count() == 1
        assert restored.name == "t"

    def test_compression_ratio(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        for i in range(50):
            layer.add_node(GraphNode(name=f"n{i}", properties={"data": "x" * 100}))
        ratio = GraphCompression.compression_ratio(layer)
        assert ratio >= 1.0

    def test_strip_properties(self):
        layer = GraphLayer("t", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(name="n", properties={"secret": "value"}))
        stripped = GraphCompression.strip_properties(layer)
        n = stripped._nodes[list(stripped._nodes.keys())[0]]
        assert n.properties == {}


# ── Program C: Engineering Execution Engine ──

from genesis.execution.engine import ExecutionEngine
from genesis.execution.workflow import WorkflowEngine, WorkflowDAG, WorkflowNode, WorkflowStatus
from genesis.execution.tasks import TaskExecutor, Task, TaskPriority, TaskStatus
from genesis.execution.actors import ActorEngine, Actor
from genesis.execution.pipeline import PipelineEngine, PipelineStage
from genesis.execution.jobs import JobManager, LongRunningJob, JobStatus
from genesis.execution.retry import RetryPolicy, CompensationEngine, CompensationAction


class TestExecutionEngine:
    def test_create(self):
        ee = ExecutionEngine()
        assert ee.workflows is not None
        assert ee.tasks is not None
        assert ee.actors is not None

    def test_execute_task(self):
        ee = ExecutionEngine()
        task = Task(name="simple", handler=lambda: 42)
        result = ee.execute("task", task)
        assert result == 42

    def test_history(self):
        ee = ExecutionEngine()
        task = Task(name="t", handler=lambda: 1)
        ee.execute("task", task)
        assert len(ee.history()) >= 1

    def test_summary(self):
        ee = ExecutionEngine()
        s = ee.summary()
        assert "total_executions" in s


class TestWorkflowEngine:
    def test_create(self):
        we = WorkflowEngine()
        wf = we.create("test-wf")
        assert wf.name == "test-wf"
        assert we.get(wf.id) is wf

    def test_execute_dag(self):
        we = WorkflowEngine()
        wf = we.create("dag")
        n1 = WorkflowNode(name="step1", handler=lambda: "a")
        n2 = WorkflowNode(name="step2", handler=lambda deps: deps.get(n1.id), dependencies=[n1.id])
        wf.add_node(n1)
        wf.add_node(n2)
        results = we.execute(wf)
        assert n1.status == WorkflowStatus.SUCCESS
        assert n2.status == WorkflowStatus.SUCCESS

    def test_execute_skipped_dep(self):
        we = WorkflowEngine()
        wf = we.create("skip")
        n1 = WorkflowNode(name="a")
        n2 = WorkflowNode(name="b", dependencies=["missing"])
        wf.add_node(n1)
        wf.add_node(n2)
        we.execute(wf)
        assert n2.status == WorkflowStatus.SKIPPED

    def test_topological_order(self):
        wf = WorkflowDAG(name="order")
        a = WorkflowNode(name="a")
        b = WorkflowNode(name="b", dependencies=[a.id])
        c = WorkflowNode(name="c", dependencies=[a.id])
        wf.add_node(a)
        wf.add_node(b)
        wf.add_node(c)
        order = wf.topological_order()
        assert order[0].id == a.id


class TestTaskExecutor:
    def test_execute(self):
        te = TaskExecutor()
        task = Task(name="echo", handler=lambda x: x.upper(), args=("hello",))
        result = te.execute(task)
        assert result == "HELLO"
        assert task.status == TaskStatus.SUCCESS

    def test_retry(self):
        te = TaskExecutor()
        attempts = []
        def flaky():
            attempts.append(1)
            if len(attempts) < 2:
                raise ValueError("not yet")
            return "ok"
        task = Task(name="flaky", handler=flaky, max_retries=3)
        te.submit(task)
        te.execute_all()
        assert task.status == TaskStatus.SUCCESS

    def test_submit_execute_all(self):
        te = TaskExecutor()
        t1 = Task(name="a", handler=lambda: 1)
        t2 = Task(name="b", handler=lambda: 2)
        te.submit(t1)
        te.submit(t2)
        te.execute_all()
        assert t1.status == TaskStatus.SUCCESS


class TestActorEngine:
    def test_spawn(self):
        ae = ActorEngine()
        actor = ae.spawn("worker")
        assert actor.name == "worker"

    def test_send_process(self):
        ae = ActorEngine()
        received = []
        actor = ae.spawn("echo", handler=lambda msg, ctx: received.append(msg))
        ae.send(actor.id, {"data": "hello"})
        ae.process(actor.id)
        assert len(received) == 1

    def test_broadcast(self):
        ae = ActorEngine()
        ae.spawn("a")
        ae.spawn("b")
        assert ae.broadcast({"msg": "all"}) == 2


class TestPipelineEngine:
    def test_define_execute(self):
        pe = PipelineEngine()
        pe.define("build", [
            PipelineStage(name="compile", handler=lambda x: {"compiled": True}),
            PipelineStage(name="test", handler=lambda x: {"tested": True}),
        ])
        result = pe.execute("build")
        assert result["compiled"]
        assert result["tested"]

    def test_nonexistent(self):
        pe = PipelineEngine()
        with pytest.raises(ValueError):
            pe.execute("missing")


class TestJobManager:
    def test_submit(self):
        jm = JobManager()
        jid = jm.submit("test-job")
        job = jm.get(jid)
        assert job.name == "test-job"

    def test_progress(self):
        jm = JobManager()
        jid = jm.submit("progress")
        jm.start(jid)
        jm.update_progress(jid, 0.5, {"step": 1})
        job = jm.get(jid)
        assert job.progress == 0.5
        assert job.checkpoint["step"] == 1

    def test_pause_resume(self):
        jm = JobManager()
        jid = jm.submit("pausable")
        jm.start(jid)
        assert jm.pause(jid)
        assert jm.get(jid).status == JobStatus.PAUSED
        assert jm.resume(jid)
        assert jm.get(jid).status == JobStatus.RUNNING

    def test_cancel(self):
        jm = JobManager()
        jid = jm.submit("cancelable")
        assert jm.cancel(jid)
        assert jm.get(jid).status == JobStatus.CANCELLED

    def test_list_by_status(self):
        jm = JobManager()
        jm.submit("a")
        assert len(jm.list_jobs()) >= 1


class TestRetryPolicy:
    def test_delay_backoff(self):
        rp = RetryPolicy()
        assert rp.delay(0) == 1.0
        assert rp.delay(1) == 2.0
        assert rp.delay(2) == 4.0

    def test_should_retry(self):
        rp = RetryPolicy(max_retries=2)
        assert rp.should_retry(0, ValueError("bad"))
        assert rp.should_retry(1, ValueError("bad"))
        assert not rp.should_retry(2, ValueError("bad"))


class TestCompensationEngine:
    def test_register_compensate(self):
        ce = CompensationEngine()
        action = CompensationAction(name="undo-txn")
        ce.register("txn_1", action)
        results = ce.compensate("txn_1")
        assert len(results) == 1

    def test_rollback_all(self):
        ce = CompensationEngine()
        ce.register("txn_a", CompensationAction(name="undo_a"))
        ce.register("txn_b", CompensationAction(name="undo_b"))
        result = ce.rollback_all()
        assert result["total"] >= 1


# ── Program D: Autonomous Engineering Cycle ──

from genesis.autonomous.cycle import AutonomousEngine, CycleStage, CycleRun, CycleResult
from genesis.autonomous.orchestrator import EngineeringOrchestrator


class TestAutonomousEngine:
    def test_run_empty(self):
        ae = AutonomousEngine()
        run = ae.run()
        assert run.status == "completed"

    def test_run_with_handler(self):
        ae = AutonomousEngine()
        ae.register(CycleStage.OBSERVE, lambda ctx: {"observed": True})
        run = ae.run()
        assert run.results["observe"].status == "completed"
        assert run.results["observe"].output["observed"]

    def test_failing_handler(self):
        ae = AutonomousEngine()
        ae.register(CycleStage.OBSERVE, lambda ctx: (_ for _ in ()).throw(RuntimeError("fail")))
        run = ae.run()
        assert run.status == "failed"

    def test_history(self):
        ae = AutonomousEngine()
        ae.run()
        ae.run()
        assert len(ae.history(limit=5)) == 2

    def test_last_run(self):
        ae = AutonomousEngine()
        ae.run({"test": True})
        assert ae.last_run().context.get("test")

    def test_summary(self):
        ae = AutonomousEngine()
        ae.run()
        s = ae.summary()
        assert s["total_cycles"] >= 1


class TestEngineeringOrchestrator:
    def test_create(self):
        orch = EngineeringOrchestrator()
        assert orch.engine is not None

    def test_run_cycle(self):
        orch = EngineeringOrchestrator()
        run = orch.run_cycle({"targets": ["repo_a"]})
        assert run.status == "completed"
        assert len(run.results) >= 1

    def test_summary(self):
        orch = EngineeringOrchestrator()
        s = orch.summary()
        assert "autonomous_engine" in s
