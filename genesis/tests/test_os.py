"""
test_os.py — Engineering Operating System tests.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from genesis.os.scheduler import PersistentScheduler, ScheduledJob
from genesis.os.planner import PersistentPlanner, Plan, PlanStep
from genesis.os.task_graph import PersistentTaskGraph, Task
from genesis.os.queue import DistributedQueue, QueueItem
from genesis.os.agent_runtime import AgentRuntime, AgentProcess
from genesis.os.resource_allocator import ResourceAllocator, ResourceReservation
from genesis.os.memory_manager import MemoryManager, MemoryEntry
from genesis.os.checkpoint import CheckpointManager, Checkpoint
from genesis.os.recovery import RecoveryManager, RecoveryAction
from genesis.os.observation import ObservationManager, Observation


# ── Shared Fixtures ──


@pytest.fixture
def temp_path(tmp_path):
    return tmp_path / "os_test"


# ── Scheduler Tests ──


def test_scheduler_add_job(temp_path):
    s = PersistentScheduler(storage_path=temp_path / "scheduler")
    jid = s.add_job(ScheduledJob(name="test", handler="test_handler"))
    assert jid
    assert s.job_count() == 1


def test_scheduler_add_recurring(temp_path):
    s = PersistentScheduler(storage_path=temp_path / "scheduler")
    jid = s.add_recurring("hourly", "handler", 3600)
    assert s.get_job(jid) is not None
    assert s.get_job(jid).job_type == "recurring"


def test_scheduler_add_once(temp_path):
    s = PersistentScheduler(storage_path=temp_path / "scheduler")
    jid = s.add_once("oneoff", "handler", delay_seconds=5)
    assert s.get_job(jid).job_type == "once"


def test_scheduler_cancel(temp_path):
    s = PersistentScheduler(storage_path=temp_path / "scheduler")
    jid = s.add_job(ScheduledJob(name="test", handler="h"))
    s.cancel(jid)
    assert s.get_job(jid) is None


def test_scheduler_due_jobs(temp_path):
    s = PersistentScheduler(storage_path=temp_path / "scheduler")
    s.add_job(ScheduledJob(name="due", handler="h", next_run=time.time() - 10))
    assert len(s.due_jobs()) == 1

    s.add_job(ScheduledJob(name="future", handler="h", next_run=time.time() + 3600))
    assert len(s.due_jobs()) == 1  # still 1, the future one is not due


def test_scheduler_execute(temp_path):
    s = PersistentScheduler(storage_path=temp_path / "scheduler")

    results = []

    def my_handler(value=0):
        results.append(value)
        return value * 2

    s.register_handler("my_handler", my_handler)
    jid = s.add_job(ScheduledJob(
        name="exec", handler="my_handler", next_run=time.time() - 5,
        params={"value": 42},
    ))
    s.tick()
    assert results == [42]


def test_scheduler_summary(temp_path):
    s = PersistentScheduler(storage_path=temp_path / "scheduler")
    s.add_job(ScheduledJob(name="t1", handler="h"))
    summary = s.summary()
    assert summary["total_jobs"] == 1
    assert "handlers_registered" in summary


def test_scheduler_persistence(temp_path):
    s1 = PersistentScheduler(storage_path=temp_path / "sched_persist")
    s1.add_job(ScheduledJob(name="persist", handler="h"))

    s2 = PersistentScheduler(storage_path=temp_path / "sched_persist")
    assert s2.job_count() == 1


# ── Planner Tests ──


def test_planner_create_plan(temp_path):
    p = PersistentPlanner(storage_path=temp_path / "planner")
    plan = p.create_plan("analyze repository")
    assert plan.id
    assert plan.goal == "analyze repository"
    assert len(plan.steps) >= 1


def test_planner_with_decomposer(temp_path):
    p = PersistentPlanner(storage_path=temp_path / "planner")

    def my_decomposer(goal, context):
        return [
            PlanStep(id="s1", action="step1"),
            PlanStep(id="s2", action="step2", dependencies=["s1"]),
        ]

    p.register_decomposer("test", my_decomposer)
    plan = p.create_plan("run test analysis")
    assert len(plan.steps) == 2
    assert plan.steps[1].dependencies == ["s1"]


def test_planner_get_next_step(temp_path):
    p = PersistentPlanner(storage_path=temp_path / "planner")
    p.register_decomposer("test", lambda g, c: [
        PlanStep(id="s1", action="a"),
        PlanStep(id="s2", action="b", dependencies=["s1"]),
    ])
    plan = p.create_plan("run test")
    next_step = p.get_next_step(plan.id)
    assert next_step is not None
    assert next_step.id == "s1"


def test_planner_update_step(temp_path):
    p = PersistentPlanner(storage_path=temp_path / "planner")
    p.register_decomposer("test", lambda g, c: [
        PlanStep(id="s1", action="a"),
        PlanStep(id="s2", action="b", dependencies=["s1"]),
    ])
    plan = p.create_plan("run test")
    p.update_step(plan.id, "s1", "success")
    next_step = p.get_next_step(plan.id)
    assert next_step is not None
    assert next_step.id == "s2"


def test_planner_cancel(temp_path):
    p = PersistentPlanner(storage_path=temp_path / "planner")
    plan = p.create_plan("test")
    p.cancel_plan(plan.id)
    assert p.get_plan(plan.id).status == "cancelled"


def test_planner_summary(temp_path):
    p = PersistentPlanner(storage_path=temp_path / "planner")
    p.create_plan("test1")
    p.create_plan("test2")
    summary = p.summary()
    assert summary["total_plans"] == 2


def test_planner_persistence(temp_path):
    p1 = PersistentPlanner(storage_path=temp_path / "plan_persist")
    p1.create_plan("persist test")

    p2 = PersistentPlanner(storage_path=temp_path / "plan_persist")
    assert p2.summary()["total_plans"] == 1


# ── Task Graph Tests ──


def test_task_graph_add_task(temp_path):
    tg = PersistentTaskGraph(storage_path=temp_path / "tasks")
    tid = tg.add_task(Task(name="task1", task_type="test"))
    assert tid
    assert tg.task_count() == 1


def test_task_graph_dependencies(temp_path):
    tg = PersistentTaskGraph(storage_path=temp_path / "tasks")
    t1 = tg.add_task(Task(name="t1"))
    t2 = tg.add_task(Task(name="t2"))
    tg.add_dependency(t2, t1)

    ready = tg.ready_tasks()
    assert len(ready) == 1
    assert ready[0].name == "t1"


def test_task_graph_update(temp_path):
    tg = PersistentTaskGraph(storage_path=temp_path / "tasks")
    tid = tg.add_task(Task(name="t1"))
    tg.update_task(tid, status="success")
    assert tg.get_task(tid).status == "success"


def test_task_graph_blocked(temp_path):
    tg = PersistentTaskGraph(storage_path=temp_path / "tasks")
    t1 = tg.add_task(Task(name="t1"))
    t2 = tg.add_task(Task(name="t2"))
    tg.add_dependency(t2, t1)
    tg.update_task(t1, status="failed")

    blocked = tg.blocked_tasks()
    assert len(blocked) == 1
    assert blocked[0].name == "t2"


def test_task_graph_execution_order(temp_path):
    tg = PersistentTaskGraph(storage_path=temp_path / "tasks")
    t1 = tg.add_task(Task(name="t1"))
    t2 = tg.add_task(Task(name="t2"))
    t3 = tg.add_task(Task(name="t3"))
    tg.add_dependency(t2, t1)
    tg.add_dependency(t3, t2)

    order = tg.execution_order()
    names = [t.name for t in order]
    assert names.index("t1") < names.index("t2")
    assert names.index("t2") < names.index("t3")


def test_task_graph_no_cycles(temp_path):
    tg = PersistentTaskGraph(storage_path=temp_path / "tasks")
    t1 = tg.add_task(Task(name="t1"))
    t2 = tg.add_task(Task(name="t2"))
    tg.add_dependency(t1, t2)
    tg.add_dependency(t2, t1)
    assert len(tg.detect_cycles()) > 0


def test_task_graph_summary(temp_path):
    tg = PersistentTaskGraph(storage_path=temp_path / "tasks")
    tg.add_task(Task(name="t1"))
    tg.add_task(Task(name="t2"))
    summary = tg.summary()
    assert summary["total_tasks"] == 2


def test_task_graph_persistence(temp_path):
    tg1 = PersistentTaskGraph(storage_path=temp_path / "tg_persist")
    tg1.add_task(Task(name="persist"))

    tg2 = PersistentTaskGraph(storage_path=temp_path / "tg_persist")
    assert tg2.task_count() == 1


# ── Queue Tests ──


def test_queue_enqueue_dequeue(temp_path):
    q = DistributedQueue(storage_path=temp_path / "queue")
    qid = q.enqueue_raw("test", {"key": "value"})
    assert qid
    item = q.dequeue()
    assert item is not None
    assert item.id == qid


def test_queue_priority(temp_path):
    q = DistributedQueue(storage_path=temp_path / "queue")
    q.enqueue_raw("low", {"v": 1}, priority=0.1)
    q.enqueue_raw("high", {"v": 2}, priority=0.9)
    first = q.dequeue()
    assert first.payload["v"] == 2


def test_queue_ack(temp_path):
    q = DistributedQueue(storage_path=temp_path / "queue")
    qid = q.enqueue_raw("test", {"v": 1})
    q.dequeue()
    q.ack(qid)
    assert q.processing_count() == 0


def test_queue_nack_requeue(temp_path):
    q = DistributedQueue(storage_path=temp_path / "queue")
    item = QueueItem(item_type="test", payload={}, max_retries=3, retry_count=0)
    qid = q.enqueue(item)
    q.dequeue()
    q.nack(qid, requeue=True)
    assert q.length() == 1  # requeued


def test_queue_clear(temp_path):
    q = DistributedQueue(storage_path=temp_path / "queue")
    q.enqueue_raw("test", {})
    q.clear()
    assert q.length() == 0


def test_queue_summary(temp_path):
    q = DistributedQueue(storage_path=temp_path / "queue")
    q.enqueue_raw("type_a", {})
    q.enqueue_raw("type_b", {})
    summary = q.summary()
    assert summary["total"] == 2


def test_queue_persistence(temp_path):
    q1 = DistributedQueue(storage_path=temp_path / "q_persist")
    q1.enqueue_raw("test", {"persist": True})

    q2 = DistributedQueue(storage_path=temp_path / "q_persist")
    assert q2.length() == 1


# ── Agent Runtime Tests ──


def test_agent_runtime_start(temp_path):
    ar = AgentRuntime(storage_path=temp_path / "agents")
    pid = ar.start_agent("worker", config={"key": "val"})
    assert pid
    proc = ar.get_process(pid)
    assert proc.agent_type == "worker"
    assert proc.status == "starting"


def test_agent_runtime_stop(temp_path):
    ar = AgentRuntime(storage_path=temp_path / "agents")
    pid = ar.start_agent("worker")
    ar.stop_agent(pid)
    assert ar.get_process(pid).status == "stopped"


def test_agent_runtime_metrics(temp_path):
    ar = AgentRuntime(storage_path=temp_path / "agents")
    pid = ar.start_agent("worker")
    ar.update_metrics(pid, {"cpu": 0.5, "mem": 128})
    assert ar.get_process(pid).metrics["cpu"] == 0.5


def test_agent_runtime_running(temp_path):
    ar = AgentRuntime(storage_path=temp_path / "agents")
    pid = ar.start_agent("worker")
    ar.set_status(pid, "running")
    assert len(ar.running_agents()) == 1


def test_agent_runtime_restart_failed(temp_path):
    ar = AgentRuntime(storage_path=temp_path / "agents")
    pid = ar.start_agent("worker")
    ar.set_status(pid, "failed")
    restarted = ar.restart_failed()
    assert len(restarted) == 1


def test_agent_runtime_summary(temp_path):
    ar = AgentRuntime(storage_path=temp_path / "agents")
    ar.start_agent("worker")
    summary = ar.summary()
    assert summary["total_agents"] == 1


def test_agent_runtime_persistence(temp_path):
    ar1 = AgentRuntime(storage_path=temp_path / "ar_persist")
    ar1.start_agent("worker")

    ar2 = AgentRuntime(storage_path=temp_path / "ar_persist")
    assert ar2.summary()["total_agents"] == 1


# ── Resource Allocator Tests ──


def test_resource_allocator_defaults(temp_path):
    ra = ResourceAllocator(storage_path=temp_path / "resources")
    assert ra.total["cpu_cores"] == 32
    assert ra.total["memory_mb"] == 65536


def test_resource_allocator_reserve(temp_path):
    ra = ResourceAllocator(storage_path=temp_path / "resources")
    res = ra.reserve("test", cpu_cores=2, memory_mb=4096, duration_seconds=60)
    assert res is not None
    assert res.owner == "test"


def test_resource_allocator_insufficient(temp_path):
    ra = ResourceAllocator(storage_path=temp_path / "resources")
    res = ra.reserve("test", cpu_cores=999, memory_mb=999999)
    assert res is None  # not enough


def test_resource_allocator_release(temp_path):
    ra = ResourceAllocator(storage_path=temp_path / "resources")
    res = ra.reserve("test", cpu_cores=2)
    ra.release(res.id)
    assert ra.available()["cpu_cores"] == pytest.approx(32.0)


def test_resource_allocator_used(temp_path):
    ra = ResourceAllocator(storage_path=temp_path / "resources")
    ra.reserve("test", cpu_cores=4)
    used = ra.used()
    assert used["cpu_cores"] == 4.0


def test_resource_allocator_summary(temp_path):
    ra = ResourceAllocator(storage_path=temp_path / "resources")
    ra.reserve("test", cpu_cores=2)
    summary = ra.summary()
    assert summary["available"]["cpu_cores"] == 30.0


def test_resource_allocator_set_total(temp_path):
    ra = ResourceAllocator(storage_path=temp_path / "resources")
    ra.set_total(cpu_cores=64)
    assert ra.total["cpu_cores"] == 64


def test_resource_allocator_persistence(temp_path):
    ra1 = ResourceAllocator(storage_path=temp_path / "ra_persist")
    ra1.reserve("test", cpu_cores=2)

    ra2 = ResourceAllocator(storage_path=temp_path / "ra_persist")
    assert ra2.used()["cpu_cores"] == 2.0


# ── Memory Manager Tests ──


def test_memory_manager_store_get(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    mid = mm.store("key1", "value1", tier="working")
    assert mid
    assert mm.get("key1") == "value1"


def test_memory_manager_get_default(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    assert mm.get("nonexistent", "default") == "default"


def test_memory_manager_tiers(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    mm.store("k1", "v1", tier="working")
    mm.store("k2", "v2", tier="long_term")
    assert mm.tier_count("working") == 1
    assert mm.tier_count("long_term") == 1


def test_memory_manager_search(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    mm.store("api_config", {"host": "example.com"}, tags=["api", "config"])
    mm.store("db_config", {"host": "db.local"}, tags=["db"])
    results = mm.search("api")
    assert len(results) == 1


def test_memory_manager_forget(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    mm.store("key", "value")
    mm.forget("key")
    assert mm.get("key") is None


def test_memory_manager_clear_tier(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    mm.store("k1", "v1", tier="working")
    mm.store("k2", "v2", tier="long_term")
    mm.clear_tier("working")
    assert mm.tier_count("working") == 0
    assert mm.tier_count("long_term") == 1


def test_memory_manager_promotion(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    eid = mm.store("freq", "value", tier="working")
    for _ in range(15):
        mm.get("freq")
    # Should promote to short_term after 10+ accesses
    entry = next(iter(mm.entries.values()))
    assert entry.tier == "short_term"


def test_memory_manager_summary(temp_path):
    mm = MemoryManager(storage_path=temp_path / "memory")
    mm.store("k1", "v1")
    mm.store("k2", "v2")
    summary = mm.summary()
    assert summary["total_entries"] == 2


def test_memory_manager_persistence(temp_path):
    mm1 = MemoryManager(storage_path=temp_path / "mem_persist")
    mm1.store("persist_key", "persist_value")

    mm2 = MemoryManager(storage_path=temp_path / "mem_persist")
    assert mm2.get("persist_key") == "persist_value"


# ── Checkpoint Tests ──


def test_checkpoint_create(temp_path):
    cm = CheckpointManager(storage_path=temp_path / "checkpoints")

    def hook():
        return {"test_key": "test_value"}

    cm.register_hook(hook)
    cp = cm.create("test_checkpoint")
    assert cp.id
    assert cp.name == "test_checkpoint"


def test_checkpoint_restore(temp_path):
    cm = CheckpointManager(storage_path=temp_path / "checkpoints")

    def hook():
        return {"restore_key": "restore_value"}

    cm.register_hook(hook)
    cp = cm.create("test")
    snapshot = cm.restore(cp.id)
    assert snapshot is not None
    assert snapshot.get("restore_key") == "restore_value"


def test_checkpoint_latest(temp_path):
    cm = CheckpointManager(storage_path=temp_path / "checkpoints")
    cm.create("first")
    cm.create("latest_cp")
    latest = cm.latest()
    assert latest.name == "latest_cp"


def test_checkpoint_summary(temp_path):
    cm = CheckpointManager(storage_path=temp_path / "checkpoints")
    cm.create("test")
    summary = cm.summary()
    assert summary["total_checkpoints"] == 1


def test_checkpoint_persistence(temp_path):
    cm1 = CheckpointManager(storage_path=temp_path / "ckpt_persist")

    def hook():
        return {"key": "val"}

    cm1.register_hook(hook)
    cp = cm1.create("persist")

    cm2 = CheckpointManager(storage_path=temp_path / "ckpt_persist")
    snapshot = cm2.restore(cp.id)
    assert snapshot is not None


# ── Recovery Tests ──


def test_recovery_handle(temp_path):
    rm = RecoveryManager(storage_path=temp_path / "recovery")

    def my_handler(msg=""):
        return f"handled: {msg}"

    rm.register_handler("test_event", my_handler)
    action = rm.handle("test_event", {"msg": "hello"})
    assert action.status == "success"
    assert "handled: hello" in action.details


def test_recovery_no_handler(temp_path):
    rm = RecoveryManager(storage_path=temp_path / "recovery")
    action = rm.handle("unknown")
    assert action.status == "failed"


def test_recovery_restore_from_checkpoint(temp_path):
    rm = RecoveryManager(storage_path=temp_path / "recovery")

    def restore_handler(value):
        return f"restored: {value}"

    rm.register_handler("restore:config", restore_handler)
    result = rm.restore_from_checkpoint({"config": {"key": "val"}})
    assert "restored: " in str(result)


def test_recovery_recent_actions(temp_path):
    rm = RecoveryManager(storage_path=temp_path / "recovery")

    def h():
        return "ok"

    rm.register_handler("e", h)
    rm.handle("e")
    recent = rm.recent_actions()
    assert len(recent) == 1


def test_recovery_failure_rate(temp_path):
    rm = RecoveryManager(storage_path=temp_path / "recovery")
    # No actions
    assert rm.failure_rate() == 0.0
    # One failure
    action = rm.handle("unknown")
    assert rm.failure_rate() == 1.0


def test_recovery_summary(temp_path):
    rm = RecoveryManager(storage_path=temp_path / "recovery")
    summary = rm.summary()
    assert summary["total_actions"] >= 0


def test_recovery_persistence(temp_path):
    rm1 = RecoveryManager(storage_path=temp_path / "rec_persist")
    rm1.handle("unknown")

    rm2 = RecoveryManager(storage_path=temp_path / "rec_persist")
    assert rm2.summary()["total_actions"] == 1


# ── Observation Tests ──


def test_observation_record(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    oid = om.record("sensor", "temperature", 25.5, tags={"unit": "celsius"})
    assert oid


def test_observation_query(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    om.record("sensor", "temperature", 25.5)
    om.record("sensor", "temperature", 26.0)
    results = om.query(metric="temperature")
    assert len(results) == 2


def test_observation_query_by_source(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    om.record("sensor_a", "temp", 25.0)
    om.record("sensor_b", "temp", 30.0)
    results = om.query(metric="temp", source="sensor_a")
    assert len(results) == 1


def test_observation_latest(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    om.record("sensor", "temp", 25.0)
    om.record("sensor", "temp", 26.0)
    assert om.latest("temp") == 26.0


def test_observation_latest_default(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    assert om.latest("unknown", default=42.0) == 42.0


def test_observation_time_series(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    om.record("sensor", "temp", 25.0)
    om.record("sensor", "temp", 26.0)
    ts = om.time_series("temp")
    assert len(ts) == 2


def test_observation_time_series_aggregated(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    om.record("sensor", "temp", 25.0)
    om.record("sensor", "temp", 26.0)
    ts = om.time_series("temp", aggregation="avg_1h")
    assert len(ts) >= 1


def test_observation_metric_names(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    om.record("s1", "cpu", 0.5)
    om.record("s1", "mem", 128)
    names = om.metric_names()
    assert "cpu" in names
    assert "mem" in names


def test_observation_summary(temp_path):
    om = ObservationManager(storage_path=temp_path / "obs")
    om.record("s1", "cpu", 0.5)
    summary = om.summary()
    assert summary["total_observations"] == 1


def test_observation_persistence(temp_path):
    om1 = ObservationManager(storage_path=temp_path / "obs_persist")
    om1.record("sensor", "temp", 25.0)

    om2 = ObservationManager(storage_path=temp_path / "obs_persist")
    assert om2.count() == 1
