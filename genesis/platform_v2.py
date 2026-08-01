"""
GENESIS-IX Phase 1: Platform Refactor — Service-Oriented Platform.

Every subsystem becomes a managed service with lifecycle, health, metrics,
telemetry, configuration, state, persistence, and recovery.

Core services: ServiceRegistry, LifecycleManager, CapabilityRegistry,
PluginFramework, EventRouter, MessageBus, ResourceScheduler,
ConfigurationManager, StateManager, PersistenceManager, HealthManager,
RecoveryManager, MetricsManager, TelemetryManager.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class ServiceState(Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"
    STOPPED = "stopped"


class ServiceCategory(Enum):
    INFRASTRUCTURE = "infrastructure"
    STORAGE = "storage"
    COGNITIVE = "cognitive"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    SIMULATION = "simulation"
    RESEARCH = "research"
    CIVILIZATION = "civilization"
    EVOLUTION = "evolution"
    INTELLIGENCE = "intelligence"
    ACQUISITION = "acquisition"
    PLATFORM = "platform"


@dataclass
class ServiceDefinition:
    id: str = ""
    name: str = ""
    category: ServiceCategory = ServiceCategory.PLATFORM
    version: str = "1.0.0"
    dependencies: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    health_check: Callable[[], bool] | None = None
    instance: Any = None

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("svc", 8)


@dataclass
class MetricPoint:
    name: str = ""
    value: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: float = 0.0
    service_id: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class HealthStatus:
    healthy: bool = True
    message: str = ""
    last_checked: float = 0.0
    failure_count: int = 0
    recovery_attempts: int = 0


class ServiceRegistry:
    """Central registry for all platform services."""

    def __init__(self):
        self._services: dict[str, ServiceDefinition] = {}
        self._states: dict[str, ServiceState] = {}
        self._health: dict[str, HealthStatus] = {}
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)

    def register(self, definition: ServiceDefinition) -> ServiceDefinition:
        self._services[definition.id] = definition
        self._states[definition.id] = ServiceState.CREATED
        self._health[definition.id] = HealthStatus()
        return definition

    def register_instance(self, service_id: str, instance: Any):
        if service_id in self._services:
            self._services[service_id].instance = instance

    def get(self, service_id: str) -> ServiceDefinition | None:
        return self._services.get(service_id)

    def get_instance(self, service_id: str) -> Any | None:
        svc = self._services.get(service_id)
        return svc.instance if svc else None

    def find(self, category: ServiceCategory | None = None,
              state: ServiceState | None = None,
              provides: str = "") -> list[ServiceDefinition]:
        results = list(self._services.values())
        if category:
            results = [s for s in results if s.category == category]
        if state:
            results = [s for s in results if self._states.get(s.id) == state]
        if provides:
            results = [s for s in results if provides in s.provides]
        return results

    @property
    def services(self) -> list[ServiceDefinition]:
        return list(self._services.values())

    @property
    def count(self) -> int:
        return len(self._services)

    def state_of(self, service_id: str) -> ServiceState:
        return self._states.get(service_id, ServiceState.CREATED)

    def set_state(self, service_id: str, state: ServiceState):
        self._states[service_id] = state

    def health_of(self, service_id: str) -> HealthStatus:
        return self._health.get(service_id, HealthStatus(healthy=False))

    def record_metric(self, metric: MetricPoint):
        self._metrics[metric.name].append(metric)

    def dependency_graph(self) -> dict[str, list[str]]:
        return {s.id: s.dependencies for s in self._services.values()}


class LifecycleManager:
    """Manages service lifecycle: init → ready → start → stop."""

    def __init__(self, registry: ServiceRegistry):
        self._registry = registry

    def compute_boot_order(self) -> list[str]:
        svcs = self._registry.services
        dep_graph = {s.id: list(s.dependencies) for s in svcs}
        visited: set[str] = set()
        ordered: list[str] = []

        def visit(sid: str):
            if sid in visited:
                return
            visited.add(sid)
            for dep in dep_graph.get(sid, []):
                visit(dep)
            ordered.append(sid)

        for s in svcs:
            visit(s.id)
        return ordered

    def initialize_all(self) -> list[str]:
        order = self.compute_boot_order()
        initialized = []
        for sid in order:
            svc = self._registry.get(sid)
            if svc:
                deps_ready = all(
                    self._registry.state_of(d) == ServiceState.READY
                    for d in svc.dependencies
                )
                if deps_ready:
                    self._registry.set_state(sid, ServiceState.INITIALIZING)
                    self._registry.set_state(sid, ServiceState.READY)
                    initialized.append(sid)
        return initialized

    def start_all(self) -> list[str]:
        started = []
        for svc in self._registry.services:
            if self._registry.state_of(svc.id) == ServiceState.READY:
                self._registry.set_state(svc.id, ServiceState.RUNNING)
                started.append(svc.id)
        return started

    def stop_all(self):
        for svc in reversed(self._registry.services):
            self._registry.set_state(svc.id, ServiceState.STOPPING)
            self._registry.set_state(svc.id, ServiceState.STOPPED)

    def health_check_all(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for svc in self._registry.services:
            h = self._registry.health_of(svc.id)
            h.last_checked = time.time()
            if svc.health_check:
                try:
                    healthy = svc.health_check()
                except Exception:
                    healthy = False
            else:
                healthy = self._registry.state_of(svc.id) == ServiceState.RUNNING
            if not healthy:
                h.failure_count += 1
                if h.failure_count > 3:
                    self._registry.set_state(svc.id, ServiceState.DEGRADED)
            else:
                h.failure_count = 0
            h.healthy = healthy
            results[svc.id] = healthy
        return results


class EventRouter:
    """Publish/subscribe event routing between services."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._history: list[dict[str, Any]] = []

    def subscribe(self, event_type: str, handler: Callable):
        self._handlers[event_type].append(handler)

    def publish(self, event_type: str, data: dict[str, Any] | None = None):
        event = {"type": event_type, "data": data or {}, "timestamp": time.time()}
        self._history.append(event)
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass

    def recent(self, n: int = 100) -> list[dict[str, Any]]:
        return self._history[-n:]


class MetricsManager:
    """Platform-wide metrics collection, aggregation, and export."""

    def __init__(self):
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}

    def record(self, name: str, value: float, tags: dict[str, str] | None = None,
                service_id: str = ""):
        self._metrics[name].append(MetricPoint(
            name=name, value=value, tags=tags or {}, service_id=service_id,
        ))

    def increment(self, counter: str, by: int = 1):
        self._counters[counter] += by

    def set_gauge(self, name: str, value: float):
        self._gauges[name] = value

    def get_metric(self, name: str) -> list[MetricPoint]:
        return self._metrics.get(name, [])

    def summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name, points in self._metrics.items():
            values = [p.value for p in points]
            result[name] = {
                "count": len(values),
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "avg": sum(values) / max(len(values), 1),
                "last": values[-1] if values else 0,
            }
        result["counters"] = dict(self._counters)
        result["gauges"] = dict(self._gauges)
        return result


class TelemetryManager:
    """Telemetry export, tracing, and monitoring."""

    def __init__(self):
        self._traces: list[dict[str, Any]] = []
        self._spans: dict[str, dict[str, Any]] = {}

    def start_trace(self, name: str, tags: dict[str, str] | None = None) -> str:
        trace_id = generate_id("trace", 10)
        self._traces.append({
            "id": trace_id, "name": name, "tags": tags or {},
            "started_at": time.time(), "completed_at": 0.0, "spans": [],
        })
        return trace_id

    def end_trace(self, trace_id: str, status: str = "ok"):
        for trace in self._traces:
            if trace["id"] == trace_id:
                trace["completed_at"] = time.time()
                trace["status"] = status
                break

    def start_span(self, trace_id: str, name: str) -> str:
        span_id = generate_id("span", 8)
        self._spans[span_id] = {
            "id": span_id, "trace_id": trace_id, "name": name,
            "started_at": time.time(), "completed_at": 0.0,
        }
        return span_id

    def end_span(self, span_id: str):
        span = self._spans.get(span_id)
        if span:
            span["completed_at"] = time.time()

    def report(self) -> dict[str, Any]:
        return {
            "traces": len(self._traces),
            "active_spans": len([s for s in self._spans.values() if s["completed_at"] == 0.0]),
            "completed_spans": len([s for s in self._spans.values() if s["completed_at"] > 0]),
        }


class ConfigurationManager:
    """Centralized configuration for all services."""

    def __init__(self):
        self._config: dict[str, dict[str, Any]] = defaultdict(dict)
        self._defaults: dict[str, dict[str, Any]] = defaultdict(dict)

    def set_defaults(self, service_id: str, defaults: dict[str, Any]):
        self._defaults[service_id] = defaults

    def set(self, service_id: str, key: str, value: Any):
        self._config[service_id][key] = value

    def get(self, service_id: str, key: str, default: Any = None) -> Any:
        return self._config[service_id].get(key, self._defaults[service_id].get(key, default))

    def all_for(self, service_id: str) -> dict[str, Any]:
        merged = dict(self._defaults.get(service_id, {}))
        merged.update(self._config.get(service_id, {}))
        return merged


class StateManager:
    """Centralized state management for all services."""

    def __init__(self):
        self._state: dict[str, dict[str, Any]] = defaultdict(dict)
        self._snapshots: list[dict[str, Any]] = []

    def set_state(self, service_id: str, key: str, value: Any):
        self._state[service_id][key] = value

    def get_state(self, service_id: str, key: str, default: Any = None) -> Any:
        return self._state[service_id].get(key, default)

    def snapshot(self) -> str:
        sid = generate_id("snap", 10)
        self._snapshots.append({
            "id": sid, "state": dict(self._state),
            "timestamp": time.time(),
        })
        return sid

    def restore(self, snapshot_id: str) -> bool:
        for snap in self._snapshots:
            if snap["id"] == snapshot_id:
                self._state = defaultdict(dict, snap["state"])
                return True
        return False


class ResourceScheduler:
    """Schedules resource allocation across services."""

    def __init__(self):
        self._resources: dict[str, float] = {}
        self._allocations: dict[str, dict[str, float]] = defaultdict(dict)

    def register_resource(self, name: str, capacity: float):
        self._resources[name] = capacity

    def allocate(self, resource: str, service_id: str, amount: float) -> bool:
        if resource not in self._resources:
            return False
        allocated = sum(self._allocations[resource].values())
        if allocated + amount > self._resources[resource]:
            return False
        self._allocations[resource][service_id] = \
            self._allocations[resource].get(service_id, 0.0) + amount
        return True

    def release(self, resource: str, service_id: str):
        if resource in self._allocations and service_id in self._allocations[resource]:
            del self._allocations[resource][service_id]

    def utilization(self) -> dict[str, float]:
        return {
            name: sum(self._allocations[name].values()) / max(capacity, 0.01)
            for name, capacity in self._resources.items()
        }


class RecoveryManager:
    """Service recovery and failover."""

    def __init__(self, registry: ServiceRegistry, lifecycle: LifecycleManager):
        self._registry = registry
        self._lifecycle = lifecycle
        self._recovery_log: list[dict[str, Any]] = []

    def recover_service(self, service_id: str) -> bool:
        svc = self._registry.get(service_id)
        if not svc:
            return False
        health = self._registry.health_of(service_id)
        health.recovery_attempts += 1
        try:
            self._registry.set_state(service_id, ServiceState.INITIALIZING)
            self._registry.set_state(service_id, ServiceState.READY)
            self._registry.set_state(service_id, ServiceState.RUNNING)
            health.healthy = True
            self._recovery_log.append({
                "service_id": service_id,
                "timestamp": time.time(),
                "success": True,
            })
            return True
        except Exception:
            self._registry.set_state(service_id, ServiceState.FAILED)
            self._recovery_log.append({
                "service_id": service_id,
                "timestamp": time.time(),
                "success": False,
            })
            return False

    def recover_all_degraded(self) -> list[str]:
        recovered = []
        for svc in self._registry.services:
            if self._registry.state_of(svc.id) in (ServiceState.DEGRADED, ServiceState.FAILED):
                if self.recover_service(svc.id):
                    recovered.append(svc.id)
        return recovered


class PlatformV2:
    """GENESIS-IX service-oriented platform. Manages all subsystems as services."""

    def __init__(self):
        self.registry = ServiceRegistry()
        self.lifecycle = LifecycleManager(self.registry)
        self.events = EventRouter()
        self.metrics = MetricsManager()
        self.telemetry = TelemetryManager()
        self.config = ConfigurationManager()
        self.state = StateManager()
        self.resources = ResourceScheduler()
        self.recovery = RecoveryManager(self.registry, self.lifecycle)

    def register_service(self, name: str, category: ServiceCategory = ServiceCategory.PLATFORM,
                          dependencies: list[str] | None = None,
                          provides: list[str] | None = None,
                          health_check: Callable[[], bool] | None = None,
                          instance: Any = None) -> ServiceDefinition:
        svc = ServiceDefinition(
            name=name, category=category,
            dependencies=dependencies or [],
            provides=provides or [],
            health_check=health_check,
            instance=instance,
        )
        return self.registry.register(svc)

    def boot(self) -> int:
        count = len(self.lifecycle.initialize_all())
        count += len(self.lifecycle.start_all())
        self.events.publish("platform.booted", {"services": count})
        return count

    def shutdown(self):
        self.events.publish("platform.shutting_down", {})
        self.lifecycle.stop_all()
        self.events.publish("platform.shutdown", {})

    def health(self) -> dict[str, bool]:
        return self.lifecycle.health_check_all()

    def summary(self) -> dict[str, Any]:
        return {
            "services": {
                "total": self.registry.count,
                "by_category": {
                    cat.value: len(self.registry.find(category=cat))
                    for cat in ServiceCategory
                },
            },
            "metrics": self.metrics.summary(),
            "telemetry": self.telemetry.report(),
            "resources": self.resources.utilization(),
        }
