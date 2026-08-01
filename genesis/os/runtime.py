"""
AutonomousRuntime — persistent, self-healing daemon for the engineering civilization.

Wires all OS subsystems into a living runtime with:
  - Lifecycle management (init → starting → running → stopping → stopped)
  - Continuous main loop: tick → process → checkpoint → watch → sleep
  - Watchdog with automatic health checks and recovery
  - Automatic periodic checkpointing
  - Integration with all subsystems
"""

from __future__ import annotations

import json
import signal
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from genesis.utils.identity import generate_id
from genesis.os.scheduler import PersistentScheduler, ScheduledJob
from genesis.os.planner import PersistentPlanner, Plan
from genesis.os.task_graph import PersistentTaskGraph, Task
from genesis.os.queue import DistributedQueue, QueueItem
from genesis.os.agent_runtime import AgentRuntime, AgentProcess
from genesis.os.resource_allocator import ResourceAllocator, ResourceReservation
from genesis.os.memory_manager import MemoryManager, MemoryEntry
from genesis.os.checkpoint import CheckpointManager, Checkpoint
from genesis.os.recovery import RecoveryManager, RecoveryAction
from genesis.os.observation import ObservationManager, Observation

try:
    from genesis.brain import EngineeringBrain
    HAS_BRAIN = True
except ImportError:
    EngineeringBrain = None  # type: ignore
    HAS_BRAIN = False


class RuntimeStatus(Enum):
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    FAILED = "failed"


class ComponentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"


@dataclass
class ComponentHealth:
    name: str = ""
    status: ComponentStatus = ComponentStatus.HEALTHY
    last_checked: float = 0.0
    last_error: str = ""
    error_count: int = 0
    recovery_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "last_checked": self.last_checked,
            "last_error": self.last_error,
            "error_count": self.error_count,
            "recovery_count": self.recovery_count,
        }


@dataclass
class RuntimeMetrics:
    uptime_seconds: float = 0.0
    ticks_executed: int = 0
    jobs_completed: int = 0
    tasks_processed: int = 0
    checkpoints_created: int = 0
    recoveries_performed: int = 0
    watchers_fired: int = 0
    errors_total: int = 0
    last_tick_duration_ms: float = 0.0
    avg_tick_duration_ms: float = 0.0
    total_tick_duration_ms: float = 0.0

    def to_dict(self, uptime: float = 0.0) -> dict[str, Any]:
        return {
            "uptime_seconds": uptime or self.uptime_seconds,
            "ticks_executed": self.ticks_executed,
            "jobs_completed": self.jobs_completed,
            "tasks_processed": self.tasks_processed,
            "checkpoints_created": self.checkpoints_created,
            "recoveries_performed": self.recoveries_performed,
            "watchers_fired": self.watchers_fired,
            "errors_total": self.errors_total,
            "last_tick_duration_ms": round(self.last_tick_duration_ms, 2),
            "avg_tick_duration_ms": round(self.avg_tick_duration_ms, 2),
        }


class AutonomousRuntime:
    """
    Persistent, self-healing runtime daemon for Genesis.

    Integrates all OS subsystems into a unified lifecycle:
      1. Initialize all components
      2. Start main event loop
      3. Monitor component health
      4. Automatic checkpointing
      5. Graceful shutdown

    The runtime runs in a background thread, leaving the main thread free for CLI interaction.
    """

    def __init__(self, storage_path: str | Path = "", brain: Any = None):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "runtime"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.status: RuntimeStatus = RuntimeStatus.STOPPED
        self.metrics = RuntimeMetrics()
        self._start_time: float = 0.0
        self._last_tick: float = 0.0
        self._running = False
        self._thread: threading.Thread | None = None

        self._health: dict[str, ComponentHealth] = {}
        self._signal_handlers: dict[str, list[Callable]] = {}
        self._tick_handlers: list[Callable] = []
        self._startup_hooks: list[Callable] = []
        self._shutdown_hooks: list[Callable] = []

        self.brain = brain
        self._build()

    def _build(self):
        self.scheduler = PersistentScheduler(
            storage_path=self.storage_path / "scheduler"
        )
        self.planner = PersistentPlanner(
            storage_path=self.storage_path / "planner"
        )
        self.task_graph = PersistentTaskGraph(
            storage_path=self.storage_path / "tasks"
        )
        self.queue = DistributedQueue(
            storage_path=self.storage_path / "queue"
        )
        self.agent_runtime = AgentRuntime(
            storage_path=self.storage_path / "agents"
        )
        self.resources = ResourceAllocator(
            storage_path=self.storage_path / "resources"
        )
        self.memory = MemoryManager(
            storage_path=self.storage_path / "memory"
        )
        self.checkpoints = CheckpointManager(
            storage_path=self.storage_path / "checkpoints"
        )
        self.recovery = RecoveryManager(
            storage_path=self.storage_path / "recovery"
        )
        self.observations = ObservationManager(
            storage_path=self.storage_path / "observations"
        )

        self._register_component("scheduler")
        self._register_component("planner")
        self._register_component("task_graph")
        self._register_component("queue")
        self._register_component("agent_runtime")
        self._register_component("resources")
        self._register_component("memory")
        self._register_component("checkpoints")
        self._register_component("recovery")
        self._register_component("observations")
        if HAS_BRAIN and self.brain is not None:
            self._register_component("brain")

    def _register_component(self, name: str):
        if name not in self._health:
            self._health[name] = ComponentHealth(name=name)

    def on_startup(self, hook: Callable):
        self._startup_hooks.append(hook)

    def on_shutdown(self, hook: Callable):
        self._shutdown_hooks.append(hook)

    def on_tick(self, handler: Callable):
        self._tick_handlers.append(handler)

    def on(self, event: str, handler: Callable):
        self._signal_handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, data: Any = None):
        for handler in self._signal_handlers.get(event, []):
            handler(data)

    def start(self, tick_interval: float = 1.0,
              checkpoint_interval: float = 300.0,
              health_interval: float = 60.0,
              daemon: bool = True) -> bool:
        if self.status in (RuntimeStatus.RUNNING, RuntimeStatus.STARTING):
            return False

        self.status = RuntimeStatus.INITIALIZING
        self._start_time = time.time()
        self._metadata = {
            "tick_interval": tick_interval,
            "checkpoint_interval": checkpoint_interval,
            "health_interval": health_interval,
        }

        for hook in self._startup_hooks:
            hook()

        self.status = RuntimeStatus.STARTING
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(tick_interval, checkpoint_interval, health_interval),
            daemon=daemon,
        )
        self._thread.start()
        self.status = RuntimeStatus.RUNNING

        self.observations.record(
            "runtime", "runtime_started", 1.0,
            tags={"status": self.status.value},
        )
        return True

    def stop(self, timeout: float = 30.0):
        if self.status not in (RuntimeStatus.RUNNING, RuntimeStatus.DEGRADED):
            return

        self.status = RuntimeStatus.STOPPING
        for hook in self._shutdown_hooks:
            hook()

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)

        self.status = RuntimeStatus.STOPPED
        self.observations.record(
            "runtime", "runtime_stopped", float(time.time() - self._start_time),
            tags={"uptime": str(self.metrics.uptime_seconds)},
        )

    def _run_loop(self, tick_interval: float,
                  checkpoint_interval: float,
                  health_interval: float):
        self._last_tick = time.time()
        last_checkpoint = time.time()
        last_health_check = time.time()

        while self._running:
            tick_start = time.time()

            if self._health_check(last_health_check, health_interval):
                last_health_check = tick_start
            self._tick()
            if self._checkpoint(last_checkpoint, checkpoint_interval):
                last_checkpoint = tick_start

            tick_end = time.time()
            tick_duration = (tick_end - tick_start) * 1000

            self.metrics.last_tick_duration_ms = tick_duration
            self.metrics.total_tick_duration_ms += tick_duration
            self.metrics.ticks_executed += 1
            self.metrics.avg_tick_duration_ms = (
                self.metrics.total_tick_duration_ms / self.metrics.ticks_executed
            )

            elapsed = tick_end - tick_start
            sleep_time = max(0, tick_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _tick(self):
        try:
            scheduler_results = self._tick_scheduler()
            self.metrics.jobs_completed += len(scheduler_results)

            queue_count = self._process_queue()
            self.metrics.tasks_processed += queue_count

            if HAS_BRAIN and self.brain is not None:
                try:
                    if self.brain._integration._started:
                        self._health["brain"].last_checked = time.time()
                except Exception:
                    pass

            for handler in self._tick_handlers:
                handler(self)

            self.observations.record(
                "runtime", "tick", float(len(scheduler_results)),
                tags={"queued_tasks": str(self.queue.length())},
            )
            self._health["scheduler"].last_checked = time.time()

        except Exception as e:
            self._handle_error("tick", e)

    def _tick_scheduler(self) -> list[tuple[str, str, Any]]:
        results = []
        for job in self.scheduler.due_jobs():
            job.last_status = "running"
            job.retry_count += 1
            handler = self.scheduler._handlers.get(job.handler)
            if not handler:
                job.last_status = "failed"
                results.append((job.id, "failed", None))
                continue
            try:
                result = handler(**job.params)
                job.last_status = "success"
                job.last_run = time.time()
                if job.job_type == "recurring":
                    job.next_run = time.time() + job.interval_seconds
                    job.retry_count = 0
                results.append((job.id, "success", result))
            except Exception as e:
                job.last_status = "failed"
                job.last_run = time.time()
                if job.job_type == "recurring" and job.retry_count < job.max_retries:
                    job.next_run = time.time() + job.interval_seconds
                results.append((job.id, "failed", str(e)))
        self.scheduler._save()
        return results

    def _process_queue(self) -> int:
        count = 0
        while True:
            item = self.queue.dequeue()
            if not item:
                break
            try:
                handler_name = f"queue:{item.item_type}"
                handler = self.scheduler._handlers.get(handler_name)
                if handler:
                    handler(**item.payload)
                self.queue.ack(item.id)
            except Exception:
                self.queue.nack(item.id, requeue=True)
            count += 1
        return count

    def _checkpoint(self, last_time: float, interval: float) -> bool:
        if time.time() - last_time < interval:
            return False

        try:
            snapshot = {
                "runtime_status": self.status.value,
                "runtime_metrics": self.metrics.to_dict(),
                "scheduler": self.scheduler.summary(),
                "queue": self.queue.summary(),
                "task_graph": self.task_graph.summary(),
                "agent_runtime": self.agent_runtime.summary(),
                "resources": self.resources.summary(),
                "memory": self.memory.summary(),
                "observations": self.observations.summary(),
            }
            cp = Checkpoint(
                id=generate_id("ckpt", 10),
                name=f"auto_checkpoint_{int(time.time())}",
                snapshot=snapshot,
                created_at=time.time(),
                size_bytes=len(json.dumps(snapshot)),
            )
            self.checkpoints.checkpoints[cp.id] = cp
            self.checkpoints._save_checkpoint(cp)
            self.checkpoints._save_index()
            self.metrics.checkpoints_created += 1

            self.observations.record(
                "runtime", "checkpoint_created", float(cp.size_bytes),
                tags={"checkpoint_id": cp.id},
            )
            return True
        except Exception as e:
            self._handle_error("checkpoint", e)
            return False

    def _health_check(self, last_time: float, interval: float) -> bool:
        if interval == 0:
            return False
        if time.time() - last_time < interval:
            return False

        now = time.time()
        for name, health in self._health.items():
            try:
                component = getattr(self, name, None)
                if component is None:
                    health.status = ComponentStatus.DISABLED
                    continue
                summary = component.summary() if hasattr(component, "summary") else {}
                health.last_checked = now
                if health.status == ComponentStatus.UNHEALTHY:
                    self._try_recover(name, health)
            except Exception as e:
                health.status = ComponentStatus.UNHEALTHY
                health.last_error = str(e)
                health.error_count += 1
                self._try_recover(name, health)

        degraded = sum(1 for h in self._health.values()
                       if h.status in (ComponentStatus.DEGRADED, ComponentStatus.UNHEALTHY))
        if degraded > len(self._health) // 2:
            self.status = RuntimeStatus.DEGRADED
        elif self.status == RuntimeStatus.DEGRADED and degraded == 0:
            self.status = RuntimeStatus.RUNNING
        return True

    def _try_recover(self, name: str, health: ComponentHealth):
        try:
            component = getattr(self, name, None)
            if component is None:
                return

            if hasattr(component, "_load"):
                component._load()

            recovery_action = self.recovery.handle(
                f"component_recovery:{name}",
                {"component": name, "last_error": health.last_error},
            )
            health.status = ComponentStatus.HEALTHY
            health.recovery_count += 1
            health.last_error = ""
            self.metrics.recoveries_performed += 1

            self.observations.record(
                "runtime", "component_recovered", float(health.recovery_count),
                tags={"component": name, "action_id": recovery_action.id},
            )
        except Exception as e:
            health.status = ComponentStatus.UNHEALTHY
            health.last_error = f"Recovery failed: {e}"

    def _handle_error(self, context: str, error: Exception):
        self.metrics.errors_total += 1
        self.recovery.handle(
            f"runtime_error:{context}",
            {"context": context, "error": str(error)},
        )
        self.observations.record(
            "runtime", "runtime_error", 1.0,
            tags={"context": context, "error": str(error)[:200]},
        )

    def component_health(self) -> dict[str, dict[str, Any]]:
        return {n: h.to_dict() for n, h in self._health.items()}

    def system_summary(self) -> dict[str, Any]:
        uptime = time.time() - self._start_time if self._start_time > 0 else 0
        return {
            "status": self.status.value,
            "uptime_seconds": uptime,
            "metrics": self.metrics.to_dict(uptime=uptime),
            "component_health": self.component_health(),
            "scheduler": self.scheduler.summary(),
            "planner": self.planner.summary(),
            "task_graph": self.task_graph.summary(),
            "queue": self.queue.summary(),
            "agents": self.agent_runtime.summary(),
            "resources": self.resources.summary(),
            "memory": self.memory.summary(),
            "checkpoints": self.checkpoints.summary(),
            "recovery": self.recovery.summary(),
            "observations": self.observations.summary(),
        }

    def to_dict(self) -> dict[str, Any]:
        uptime = time.time() - self._start_time if self._start_time > 0 else 0
        return {
            "status": self.status.value,
            "started_at": self._start_time,
            "uptime_seconds": uptime,
            "metrics": self.metrics.to_dict(uptime=uptime),
            "health": self.component_health(),
        }
