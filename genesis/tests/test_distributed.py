"""
test_distributed.py — Tests for the Distributed Runtime (Phase 3).
"""

from __future__ import annotations

import time

from genesis.os.distributed import (
    Worker, WorkerStatus, HealthStatus,
    WorkerPool, LoadBalancer, HealthMonitor,
    DistributedTask, ClusterManager,
)


# ── Worker Tests ──

class TestWorker:
    def test_defaults(self):
        w = Worker(id="w:1", name="test")
        assert w.id == "w:1"
        assert w.name == "test"
        assert w.status == WorkerStatus.IDLE
        assert w.current_load == 0
        assert w.max_load == 10

    def test_is_available(self):
        w = Worker(id="w:1", name="test")
        assert w.is_available()
        w.status = WorkerStatus.BUSY
        assert not w.is_available()
        w.status = WorkerStatus.IDLE
        w.current_load = 10
        assert not w.is_available()

    def test_load_percentage(self):
        w = Worker(id="w:1", name="test", max_load=10, current_load=5)
        assert w.load_percentage() == 0.5

    def test_health_healthy(self):
        w = Worker(id="w:1", name="test", last_heartbeat=time.time())
        assert w.health() == HealthStatus.HEALTHY

    def test_health_degraded(self):
        w = Worker(id="w:1", name="test", max_load=10, current_load=10)
        assert w.health() == HealthStatus.DEGRADED

    def test_health_unhealthy(self):
        w = Worker(id="w:1", name="test", last_heartbeat=0)
        assert w.health() == HealthStatus.UNHEALTHY

    def test_health_down(self):
        w = Worker(id="w:1", name="test", status=WorkerStatus.DOWN)
        assert w.health() == HealthStatus.UNHEALTHY

    def test_to_dict_roundtrip(self):
        w = Worker(id="w:1", name="test-worker", host="10.0.0.1", port=8080,
                   capabilities=["python", "rust"], current_load=3, max_load=8,
                   tags={"env": "prod"})
        d = w.to_dict()
        w2 = Worker.from_dict(d)
        assert w2.id == "w:1"
        assert w2.name == "test-worker"
        assert w2.host == "10.0.0.1"
        assert w2.port == 8080
        assert "python" in w2.capabilities
        assert w2.current_load == 3
        assert w2.max_load == 8


# ── DistributedTask Tests ──

class TestDistributedTask:
    def test_defaults(self):
        t = DistributedTask(id="t:1", name="test-task")
        assert t.id == "t:1"
        assert t.name == "test-task"
        assert t.status == "pending"
        assert t.retry_count == 0

    def test_duration_ms(self):
        t = DistributedTask(id="t:1", name="test", started_at=100.0, completed_at=102.0)
        assert t.duration_ms() == 2000.0

    def test_duration_no_completion(self):
        t = DistributedTask(id="t:1", name="test")
        assert t.duration_ms() == 0.0

    def test_to_dict_roundtrip(self):
        t = DistributedTask(id="t:1", name="test", priority=5,
                            required_capability="python", timeout=120.0)
        d = t.to_dict()
        t2 = DistributedTask.from_dict(d)
        assert t2.id == "t:1"
        assert t2.name == "test"
        assert t2.priority == 5
        assert t2.required_capability == "python"
        assert t2.timeout == 120.0


# ── WorkerPool Tests ──

class TestWorkerPool:
    def test_register(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        assert pool.worker_count() == 1

    def test_unregister(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        pool.unregister("w:1")
        assert pool.worker_count() == 0

    def test_get(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        assert pool.get("w:1") is not None
        assert pool.get("nonexistent") is None

    def test_available_workers(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        pool.register(Worker(id="w:2", name="w2", status=WorkerStatus.BUSY))
        pool.register(Worker(id="w:3", name="w3", current_load=10))
        available = pool.available_workers()
        assert len(available) == 1
        assert available[0].id == "w:1"

    def test_available_workers_by_capability(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", capabilities=["python"]))
        pool.register(Worker(id="w:2", name="w2", capabilities=["rust"]))
        python_workers = pool.available_workers(capability="python")
        assert len(python_workers) == 1
        assert python_workers[0].id == "w:1"

    def test_all_workers(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        pool.register(Worker(id="w:2", name="w2"))
        assert len(pool.all_workers()) == 2

    def test_assign_and_complete_task(self):
        pool = WorkerPool()
        w = Worker(id="w:1", name="w1")
        pool.register(w)
        pool.assign_task("w:1")
        assert pool.get("w:1").current_load == 1
        assert pool.get("w:1").status == WorkerStatus.BUSY
        pool.complete_task("w:1", latency_ms=100.0)
        assert pool.get("w:1").current_load == 0
        assert pool.get("w:1").status == WorkerStatus.IDLE
        assert pool.get("w:1").total_tasks_completed == 1
        assert pool.get("w:1").avg_latency_ms > 0

    def test_complete_task_with_error(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        pool.assign_task("w:1")
        pool.complete_task("w:1", had_error=True)
        assert pool.get("w:1").total_errors == 1

    def test_heartbeat(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        pool.heartbeat("w:1")
        assert pool.get("w:1").last_heartbeat > 0

    def test_health_summary(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", last_heartbeat=time.time()))
        pool.register(Worker(id="w:2", name="w2", last_heartbeat=time.time()))
        summary = pool.health_summary()
        assert summary.get("healthy", 0) >= 2

    def test_event_handler(self):
        pool = WorkerPool()
        events: list[str] = []
        pool.on("worker_registered", lambda w: events.append(w.id))
        pool.register(Worker(id="ev:1", name="ev"))
        assert "ev:1" in events


# ── LoadBalancer Tests ──

class TestLoadBalancer:
    def test_select_worker_empty(self):
        pool = WorkerPool()
        lb = LoadBalancer(pool)
        assert lb.select_worker() is None

    def test_select_worker_random(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        pool.register(Worker(id="w:2", name="w2"))
        lb = LoadBalancer(pool, strategy="random")
        worker = lb.select_worker()
        assert worker is not None
        assert worker.id in ("w:1", "w:2")

    def test_select_worker_least_load(self):
        pool = WorkerPool()
        w1 = Worker(id="w:1", name="w1", current_load=5, max_load=10)
        w2 = Worker(id="w:2", name="w2", current_load=1, max_load=10)
        pool.register(w1)
        pool.register(w2)
        lb = LoadBalancer(pool, strategy="least_load")
        worker = lb.select_worker()
        assert worker is not None
        assert worker.id == "w:2"  # lower load

    def test_select_worker_round_robin(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1"))
        pool.register(Worker(id="w:2", name="w2"))
        lb = LoadBalancer(pool, strategy="round_robin")
        first = lb.select_worker()
        second = lb.select_worker()
        assert first is not None
        assert second is not None
        assert first.id != second.id

    def test_select_worker_most_capable(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", capabilities=["py"]))
        pool.register(Worker(id="w:2", name="w2", capabilities=["py", "rs", "go"]))
        lb = LoadBalancer(pool, strategy="most_capable")
        worker = lb.select_worker()
        assert worker.id == "w:2"

    def test_select_worker_fastest(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", avg_latency_ms=100.0))
        pool.register(Worker(id="w:2", name="w2", avg_latency_ms=50.0))
        lb = LoadBalancer(pool, strategy="fastest")
        worker = lb.select_worker()
        assert worker.id == "w:2"

    def test_select_worker_with_capability(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", capabilities=["python"]))
        pool.register(Worker(id="w:2", name="w2", capabilities=["rust"]))
        lb = LoadBalancer(pool)
        worker = lb.select_worker(capability="rust")
        assert worker is not None
        assert worker.id == "w:2"

    def test_select_n_workers(self):
        pool = WorkerPool()
        for i in range(5):
            pool.register(Worker(id=f"w:{i}", name=f"w{i}"))
        lb = LoadBalancer(pool)
        selected = lb.select_n_workers(3)
        assert len(selected) == 3
        # All unique
        assert len(set(w.id for w in selected)) == 3


# ── HealthMonitor Tests ──

class TestHealthMonitor:
    def test_check_empty(self):
        pool = WorkerPool()
        hm = HealthMonitor(pool, check_interval=-1)
        issues = hm.check()
        # First check should return empty since no workers
        assert issues == []

    def test_check_unhealthy(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", last_heartbeat=0))
        hm = HealthMonitor(pool, check_interval=-1)
        issues = hm.check()
        assert len(issues) >= 1
        assert issues[0]["type"] == "unhealthy"

    def test_check_degraded(self):
        pool = WorkerPool()
        w = Worker(id="w:1", name="w1", current_load=10, max_load=10,
                   last_heartbeat=time.time())
        pool.register(w)
        hm = HealthMonitor(pool, check_interval=-1)
        issues = hm.check()
        assert len(issues) >= 1
        assert issues[0]["type"] == "degraded"

    def test_alerts(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", last_heartbeat=0))
        hm = HealthMonitor(pool, check_interval=-1)
        hm.check()
        assert len(hm.alerts()) >= 1

    def test_event_handler(self):
        pool = WorkerPool()
        pool.register(Worker(id="w:1", name="w1", last_heartbeat=0))
        hm = HealthMonitor(pool, check_interval=-1)
        events: list[str] = []
        hm.on("worker_unhealthy", lambda w: events.append(w.id))
        hm.check()
        assert "w:1" in events


# ── ClusterManager Tests ──

class TestClusterManager:
    def test_start_local_worker(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        w = cm.start_local_worker(name="local", capabilities=["python"])
        assert w is not None
        assert w.name == "local"
        assert cm.pool.worker_count() == 1

    def test_stop_local_worker(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        cm.stop_local_worker()
        assert cm.pool.worker_count() == 0

    def test_submit_task_no_worker(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        task = DistributedTask(id="t:1", name="test")
        result = cm.submit_task(task)
        assert result is None  # No worker available

    def test_submit_task_with_worker(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker(capabilities=["general"])
        task = DistributedTask(id="t:1", name="test", required_capability="general")
        result = cm.submit_task(task)
        assert result is not None
        assert result.worker_id != ""
        assert result.status == "running"

    def test_submit_task_with_capability_filter(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker(capabilities=["rust"])
        task = DistributedTask(id="t:1", name="test", required_capability="python")
        result = cm.submit_task(task)
        assert result is None  # No worker with python capability

    def test_complete_task(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        task = DistributedTask(id="t:1", name="test")
        cm.submit_task(task)
        cm.complete_task("t:1", result={"success": True})
        assert cm.get_task("t:1") is None  # Moved to history
        assert cm.task_count() >= 1

    def test_complete_task_with_error(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        task = DistributedTask(id="t:2", name="failing")
        cm.submit_task(task)
        cm.complete_task("t:2", error="Something failed")
        assert cm.task_count() >= 1

    def test_submit_and_complete(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        task = DistributedTask(id="t:3", name="auto")
        result = cm.submit_and_complete(task)
        assert result["status"] == "completed"

    def test_submit_and_complete_no_worker(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        task = DistributedTask(id="t:4", name="no-worker")
        result = cm.submit_and_complete(task)
        assert result["status"] == "no_worker_available"

    def test_submit_batch(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        tasks = [DistributedTask(id=f"b:{i}", name=f"batch-{i}") for i in range(3)]
        results = cm.submit_batch(tasks)
        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)

    def test_cluster_summary(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        s = cm.cluster_summary()
        assert s["workers"] == 1
        assert s["running"] is True
        assert s["local_worker"] is True

    def test_get_metrics(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        task = DistributedTask(id="m:1", name="metric-test")
        cm.submit_and_complete(task)
        metrics = cm.get_metrics()
        assert metrics["worker_count"] == 1
        assert metrics["total_completed"] >= 1

    def test_multiple_workers(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        for i in range(3):
            from genesis.utils.identity import generate_id
            worker = Worker(
                id=f"mw:{i}",
                name=f"multi-w{i}",
                capabilities=["general"],
            )
            cm.pool.register(worker)
        tasks = [DistributedTask(id=f"mt:{i}", name=f"t{i}") for i in range(10)]
        results = cm.submit_batch(tasks)
        completed = [r for r in results if r["status"] == "completed"]
        assert len(completed) == 10

    def test_task_with_priority(self, tmp_path):
        cm = ClusterManager(persistence_dir=str(tmp_path))
        cm.start_local_worker()
        task = DistributedTask(id="p:1", name="high-priority", priority=10)
        result = cm.submit_and_complete(task)
        assert result["status"] == "completed"

    def test_worker_tags(self):
        w = Worker(id="w:1", name="tagged", tags={"region": "us-east", "env": "prod"})
        assert w.tags["region"] == "us-east"
        assert w.tags["env"] == "prod"
