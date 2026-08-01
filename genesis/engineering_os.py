"""
GENESIS-VIII Program 7: Universal Engineering Operating System.

Everything becomes services.
Scheduler, Runtime, Agents, Memory, Research, Simulation, Knowledge,
Planner, Compiler, GraphDB, Observatory, Brain, Civilization, Experiments,
Benchmarks, Validation, Telemetry, Checkpointing, Recovery, Distributed exec.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class ServiceStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    ERROR = "error"
    STOPPING = "stopping"


class ServiceRole(Enum):
    CORE = "core"
    COGNITIVE = "cognitive"
    MEMORY = "memory"
    RESEARCH = "research"
    SIMULATION = "simulation"
    KNOWLEDGE = "knowledge"
    PLANNING = "planning"
    COMPILATION = "compilation"
    STORAGE = "storage"
    OBSERVATION = "observation"
    CIVILIZATION = "civilization"
    EXPERIMENT = "experiment"
    BENCHMARK = "benchmark"
    VALIDATION = "validation"
    TELEMETRY = "telemetry"
    RECOVERY = "recovery"
    DISTRIBUTED = "distributed"


@dataclass
class Service:
    id: str = ""
    name: str = ""
    role: ServiceRole = ServiceRole.CORE
    status: ServiceStatus = ServiceStatus.STOPPED
    health_score: float = 1.0
    dependencies: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    started_at: float = 0.0
    last_heartbeat: float = 0.0
    error_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("svc", 8)

    def start(self):
        self.status = ServiceStatus.STARTING
        self.started_at = time.time()
        self.last_heartbeat = time.time()
        self.status = ServiceStatus.RUNNING

    def stop(self):
        self.status = ServiceStatus.STOPPING
        self.status = ServiceStatus.STOPPED

    def heartbeat(self):
        self.last_heartbeat = time.time()
        self.health_score = min(1.0, self.health_score + 0.05)

    def record_error(self):
        self.error_count += 1
        self.health_score = max(0.0, self.health_score - 0.1)
        if self.health_score < 0.3:
            self.status = ServiceStatus.DEGRADED


@dataclass
class ServiceManifest:
    """Declarative service definition."""
    name: str = ""
    role: ServiceRole = ServiceRole.CORE
    dependencies: list[str] = field(default_factory=list)
    implements: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


class ServiceRegistry:
    """Registry of all platform services."""

    def __init__(self):
        self._services: dict[str, Service] = {}
        self._manifests: dict[str, ServiceManifest] = {}

    def register(self, manifest: ServiceManifest) -> Service:
        svc = Service(
            name=manifest.name,
            role=manifest.role,
            dependencies=manifest.dependencies,
            metadata={"manifest": manifest.name, "implements": manifest.implements},
        )
        self._services[svc.id] = svc
        self._manifests[svc.id] = manifest
        return svc

    def get(self, service_id: str) -> Service | None:
        return self._services.get(service_id)

    def find(self, role: ServiceRole | None = None,
              status: ServiceStatus | None = None,
              name_contains: str = "") -> list[Service]:
        results = list(self._services.values())
        if role:
            results = [s for s in results if s.role == role]
        if status:
            results = [s for s in results if s.status == status]
        if name_contains:
            results = [s for s in results if name_contains.lower() in s.name.lower()]
        return results

    def all_services(self) -> list[Service]:
        return list(self._services.values())

    def dependency_graph(self) -> dict[str, list[str]]:
        return {s.id: s.dependencies for s in self._services.values()}


class ServiceScheduler:
    """Schedules service lifecycle: start order, health checks, recovery."""

    def __init__(self, registry: ServiceRegistry):
        self._registry = registry
        self._start_order: list[str] = []

    def compute_start_order(self) -> list[str]:
        services = self._registry.all_services()
        dep_graph = {s.id: s.dependencies for s in services}
        visited: set[str] = set()
        ordered: list[str] = []

        def visit(sid: str):
            if sid in visited:
                return
            visited.add(sid)
            for dep in dep_graph.get(sid, []):
                visit(dep)
            ordered.append(sid)

        for s in services:
            visit(s.id)
        self._start_order = ordered
        return ordered

    def start_all(self, on_start: Callable[[Service], None] | None = None) -> list[Service]:
        order = self.compute_start_order()
        started = []
        for sid in order:
            svc = self._registry.get(sid)
            if svc:
                all_deps_running = all(
                    self._registry.get(d) and self._registry.get(d).status == ServiceStatus.RUNNING
                    for d in svc.dependencies
                )
                if all_deps_running:
                    svc.start()
                    if on_start:
                        on_start(svc)
                    started.append(svc)
        return started

    def stop_all(self) -> list[Service]:
        stopped = []
        for svc in reversed(self._registry.all_services()):
            svc.stop()
            stopped.append(svc)
        return stopped

    def health_check(self) -> dict[str, Any]:
        now = time.time()
        healthy = 0
        degraded = 0
        errors = 0
        for svc in self._registry.all_services():
            if now - svc.last_heartbeat > 300:
                svc.status = ServiceStatus.DEGRADED
            if svc.status == ServiceStatus.RUNNING:
                healthy += 1
            elif svc.status == ServiceStatus.DEGRADED:
                degraded += 1
            elif svc.status == ServiceStatus.ERROR:
                errors += 1
        return {
            "healthy": healthy,
            "degraded": degraded,
            "error": errors,
            "total": len(self._registry.all_services()),
        }


class TelemetryCollector:
    """Collects metrics from all services."""

    def __init__(self):
        self._metrics: dict[str, list[dict[str, Any]]] = {}
        self._collectors: dict[str, Callable[[], dict[str, Any]]] = {}

    def register_collector(self, name: str, collector: Callable[[], dict[str, Any]]):
        self._collectors[name] = collector

    def collect_all(self) -> dict[str, Any]:
        results = {}
        for name, collector in self._collectors.items():
            try:
                results[name] = collector()
            except Exception:
                results[name] = {"error": "collector_failed"}
        return results

    def record(self, metric_name: str, value: float, tags: dict[str, str] | None = None):
        self._metrics.setdefault(metric_name, []).append({
            "value": value, "tags": tags or {}, "timestamp": time.time(),
        })

    def summary(self) -> dict[str, Any]:
        return {
            metric: {
                "count": len(values),
                "last": values[-1]["value"] if values else None,
                "avg": sum(v["value"] for v in values) / max(len(values), 1),
            }
            for metric, values in self._metrics.items()
        }


class CheckpointManager:
    """Manages system checkpoints for recovery."""

    def __init__(self, base_path: str = "/tmp/venus_checkpoints"):
        self._base_path = base_path
        self._checkpoints: dict[str, dict[str, Any]] = {}

    def save(self, name: str, state: dict[str, Any]) -> str:
        cpid = generate_id("cp", 10)
        self._checkpoints[cpid] = {
            "name": name, "state": state, "timestamp": time.time(),
        }
        return cpid

    def restore(self, checkpoint_id: str) -> dict[str, Any] | None:
        cp = self._checkpoints.get(checkpoint_id)
        return cp["state"] if cp else None

    def list_checkpoints(self) -> list[dict[str, Any]]:
        return [
            {"id": cpid, "name": cp["name"], "timestamp": cp["timestamp"]}
            for cpid, cp in self._checkpoints.items()
        ]


class EngineeringOS:
    """Universal Engineering Operating System."""

    def __init__(self):
        self._registry = ServiceRegistry()
        self._scheduler = ServiceScheduler(self._registry)
        self._telemetry = TelemetryCollector()
        self._checkpoints = CheckpointManager()
        self._booted = False

    @property
    def registry(self) -> ServiceRegistry:
        return self._registry

    @property
    def scheduler(self) -> ServiceScheduler:
        return self._scheduler

    @property
    def telemetry(self) -> TelemetryCollector:
        return self._telemetry

    @property
    def checkpoints(self) -> CheckpointManager:
        return self._checkpoints

    def register_service(self, manifest: ServiceManifest) -> Service:
        return self._registry.register(manifest)

    def boot(self) -> int:
        started = self._scheduler.start_all()
        self._booted = True
        return len(started)

    def shutdown(self):
        self._scheduler.stop_all()
        self._booted = False

    def health(self) -> dict[str, Any]:
        return self._scheduler.health_check()

    def system_graph(self) -> dict[str, Any]:
        return {
            "services": len(self._registry.all_services()),
            "dependency_graph": self._registry.dependency_graph(),
            "telemetry": self._telemetry.summary(),
            "checkpoints": self._checkpoints.list_checkpoints(),
        }

    def summary(self) -> dict[str, Any]:
        return {
            "booted": self._booted,
            "services": {
                "total": len(self._registry.all_services()),
                "by_role": {r.value: len(self._registry.find(role=r))
                           for r in ServiceRole},
                "by_status": {s.value: len(self._registry.find(status=s))
                             for s in ServiceStatus},
            },
            "health": self.health(),
        }
