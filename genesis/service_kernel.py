from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.orchestration import PlatformOrchestrator, ServiceDef, ServiceStatus, BootReport


class ServiceState(Enum):
    PENDING = "pending"
    BOOTING = "booting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPED = "stopped"


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RecoveryAction(Enum):
    RESTART = "restart"
    FAILOVER = "failover"
    DEGRADE = "degrade"
    IGNORE = "ignore"


@dataclass
class CircuitBreaker:
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    threshold: int = 5
    recovery_timeout: float = 30.0
    last_failure: float = 0.0
    last_recovery_attempt: float = 0.0


@dataclass
class RecoveryPolicy:
    max_retries: int = 3
    retry_delay_ms: float = 1000.0
    backoff_factor: float = 2.0
    action: RecoveryAction = RecoveryAction.RESTART
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 30.0


@dataclass
class ServiceMetrics:
    service_id: str
    uptime_seconds: float = 0.0
    health_check_count: int = 0
    health_check_failures: int = 0
    failure_count: int = 0
    recovery_count: int = 0
    restarts: int = 0
    last_health_check: float = 0.0
    last_failure: float = 0.0
    last_recovery: float = 0.0
    avg_health_latency_ms: float = 0.0
    started_at: float = 0.0


@dataclass
class ServiceHealth:
    service_id: str
    healthy: bool = True
    last_check: float = 0.0
    last_latency_ms: float = 0.0
    consecutive_failures: int = 0
    error: str | None = None


@dataclass(frozen=True)
class HeartbeatRecord:
    service_id: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


class LifecycleManager:
    VALID_TRANSITIONS: dict[ServiceState, set[ServiceState]] = {
        ServiceState.PENDING: {ServiceState.BOOTING, ServiceState.HEALTHY, ServiceState.DEGRADED, ServiceState.FAILED},
        ServiceState.BOOTING: {ServiceState.HEALTHY, ServiceState.DEGRADED, ServiceState.FAILED},
        ServiceState.HEALTHY: {ServiceState.DEGRADED, ServiceState.STOPPED},
        ServiceState.DEGRADED: {ServiceState.HEALTHY, ServiceState.FAILED, ServiceState.STOPPED},
        ServiceState.FAILED: {ServiceState.BOOTING, ServiceState.STOPPED},
        ServiceState.STOPPED: {ServiceState.BOOTING},
    }

    def __init__(self):
        self._states: dict[str, ServiceState] = {}
        self._lock = threading.Lock()

    def register(self, service_id: str):
        with self._lock:
            self._states[service_id] = ServiceState.PENDING

    def unregister(self, service_id: str) -> bool:
        with self._lock:
            return self._states.pop(service_id, None) is not None

    def transition(self, service_id: str, to_state: ServiceState) -> bool:
        with self._lock:
            current = self._states.get(service_id)
            if current is None:
                return False
            if to_state not in self.VALID_TRANSITIONS.get(current, set()):
                return False
            self._states[service_id] = to_state
            return True

    def get_state(self, service_id: str) -> ServiceState | None:
        return self._states.get(service_id)

    def force_set(self, service_id: str, state: ServiceState):
        with self._lock:
            self._states[service_id] = state

    def all_states(self) -> dict[str, ServiceState]:
        return dict(self._states)

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for s in self._states.values():
            counts[s.value] = counts.get(s.value, 0) + 1
        return counts


class HealthManager:
    def __init__(self):
        self._checks: dict[str, ServiceHealth] = {}
        self._functions: dict[str, Callable[[Any], bool] | None] = {}
        self._intervals: dict[str, float] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._on_unhealthy: list[Callable[[str, ServiceHealth], None]] = []

    def register(self, service_id: str, check_fn: Callable[[Any], bool] | None = None,
                 interval_ms: float = 30000.0, instance: Any = None):
        with self._lock:
            self._checks[service_id] = ServiceHealth(service_id=service_id)
            self._functions[service_id] = check_fn
            self._intervals[service_id] = interval_ms

    def unregister(self, service_id: str) -> bool:
        with self._lock:
            self._checks.pop(service_id, None)
            self._functions.pop(service_id, None)
            self._intervals.pop(service_id, None)
            return True

    def on_unhealthy(self, callback: Callable[[str, ServiceHealth], None]):
        self._on_unhealthy.append(callback)

    def record_result(self, service_id: str, healthy: bool, latency_ms: float = 0.0, error: str | None = None):
        with self._lock:
            health = self._checks.get(service_id)
            if health is None:
                return
            health.last_check = time.time()
            health.last_latency_ms = latency_ms
            health.error = error
            if healthy:
                health.consecutive_failures = 0
                health.healthy = True
            else:
                health.consecutive_failures += 1
                health.healthy = False
        if not healthy:
            for cb in self._on_unhealthy:
                try:
                    cb(service_id, health)
                except Exception:
                    pass

    def get_health(self, service_id: str) -> ServiceHealth | None:
        return self._checks.get(service_id)

    def all_health(self) -> dict[str, ServiceHealth]:
        return dict(self._checks)

    def unhealthy_services(self) -> list[str]:
        return [sid for sid, h in self._checks.items() if not h.healthy]

    def check_service(self, service_id: str, instance: Any) -> ServiceHealth:
        with self._lock:
            health = self._checks.get(service_id)
            if health is None:
                health = ServiceHealth(service_id=service_id)
                self._checks[service_id] = health
            fn = self._functions.get(service_id)
        started = time.time()
        if fn and instance is not None:
            try:
                result = fn(instance)
                self.record_result(service_id, bool(result), (time.time() - started) * 1000)
            except Exception as e:
                self.record_result(service_id, False, (time.time() - started) * 1000, str(e))
        else:
            self.record_result(service_id, True, (time.time() - started) * 1000)
        return health

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run_loop(self):
        while self._running:
            for sid in list(self._checks.keys()):
                if not self._running:
                    return
                instance = None
                self.check_service(sid, instance)
                interval_ms = self._intervals.get(sid, 30000.0)
                time.sleep(interval_ms / 1000.0)

    def summary(self) -> dict[str, Any]:
        return {
            "monitored": len(self._checks),
            "healthy": len([h for h in self._checks.values() if h.healthy]),
            "unhealthy": len([h for h in self._checks.values() if not h.healthy]),
            "running": self._running,
        }


class FailureManager:
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._policies: dict[str, RecoveryPolicy] = {}
        self._retry_counts: dict[str, int] = {}
        self._lock = threading.Lock()
        self._on_failure: list[Callable[[str, str | None], None]] = []

    def on_failure(self, callback: Callable[[str, str | None], None]):
        self._on_failure.append(callback)

    def register_policy(self, service_id: str, policy: RecoveryPolicy | None = None):
        with self._lock:
            self._policies[service_id] = policy or RecoveryPolicy()
            self._breakers[service_id] = CircuitBreaker(
                threshold=self._policies[service_id].circuit_breaker_threshold,
                recovery_timeout=self._policies[service_id].circuit_breaker_timeout,
            )
            self._retry_counts[service_id] = 0

    def record_failure(self, service_id: str, error: str | None = None) -> RecoveryAction:
        with self._lock:
            breaker = self._breakers.get(service_id)
            policy = self._policies.get(service_id)
            if breaker is None or policy is None:
                return RecoveryAction.IGNORE

            breaker.failure_count += 1
            breaker.last_failure = time.time()

            if breaker.failure_count >= breaker.threshold:
                breaker.state = CircuitState.OPEN
                return RecoveryAction.IGNORE

            self._retry_counts[service_id] = self._retry_counts.get(service_id, 0) + 1
            retry_count = self._retry_counts[service_id]

            if retry_count > policy.max_retries:
                return RecoveryAction.DEGRADE

            action = policy.action

        for cb in self._on_failure:
            try:
                cb(service_id, error)
            except Exception:
                pass
        return action

    def record_success(self, service_id: str):
        with self._lock:
            breaker = self._breakers.get(service_id)
            if breaker is None:
                return
            breaker.failure_count = 0
            breaker.state = CircuitState.CLOSED
            self._retry_counts[service_id] = 0

    def get_breaker(self, service_id: str) -> CircuitBreaker | None:
        return self._breakers.get(service_id)

    def get_policy(self, service_id: str) -> RecoveryPolicy | None:
        return self._policies.get(service_id)

    def retry_delay_ms(self, service_id: str) -> float:
        policy = self._policies.get(service_id)
        if policy is None:
            return 0.0
        retry_count = self._retry_counts.get(service_id, 0)
        if retry_count <= 1:
            return policy.retry_delay_ms
        return policy.retry_delay_ms * (policy.backoff_factor ** (retry_count - 1))

    def reset(self, service_id: str):
        with self._lock:
            breaker = self._breakers.get(service_id)
            if breaker:
                breaker.failure_count = 0
                breaker.state = CircuitState.CLOSED
            self._retry_counts[service_id] = 0

    def summary(self) -> dict[str, Any]:
        open_count = 0
        closed_count = 0
        for b in self._breakers.values():
            if b.state == CircuitState.OPEN:
                open_count += 1
            else:
                closed_count += 1
        return {
            "circuits": len(self._breakers),
            "open": open_count,
            "closed": closed_count,
            "active_retries": sum(1 for c in self._retry_counts.values() if c > 0),
        }


class CapabilityPublisher:
    def __init__(self):
        self._publishments: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def publish(self, service_id: str, capability_name: str,
                interfaces: list[dict[str, Any]] | None = None,
                version: str = "1.0.0", description: str = ""):
        cap = {
            "service_id": service_id,
            "capability_name": capability_name,
            "interfaces": interfaces or [],
            "version": version,
            "description": description,
        }
        self._publishments[service_id].append(cap)

    def unpublish(self, service_id: str, capability_name: str) -> bool:
        caps = self._publishments.get(service_id, [])
        before = len(caps)
        self._publishments[service_id] = [c for c in caps if c["capability_name"] != capability_name]
        return len(self._publishments[service_id]) < before

    def unpublish_all(self, service_id: str) -> bool:
        return self._publishments.pop(service_id, None) is not None

    def find_by_interface(self, method: str, path: str) -> list[dict[str, Any]]:
        results = []
        for caps in self._publishments.values():
            for cap in caps:
                for iface in cap["interfaces"]:
                    if iface.get("method") == method and iface.get("path") == path:
                        results.append(cap)
        return results

    def find_by_service(self, service_id: str) -> list[dict[str, Any]]:
        return list(self._publishments.get(service_id, []))

    def all_published(self) -> list[dict[str, Any]]:
        return [cap for caps in self._publishments.values() for cap in caps]

    def summary(self) -> dict[str, Any]:
        return {
            "services_publishing": len(self._publishments),
            "total_capabilities": len(self.all_published()),
        }


class MetricsCollector:
    def __init__(self):
        self._metrics: dict[str, ServiceMetrics] = {}

    def register(self, service_id: str):
        self._metrics[service_id] = ServiceMetrics(service_id=service_id)

    def record_start(self, service_id: str):
        m = self._metrics.get(service_id)
        if m:
            m.started_at = time.time()

    def record_health_check(self, service_id: str, healthy: bool, latency_ms: float = 0.0):
        m = self._metrics.get(service_id)
        if m is None:
            return
        m.health_check_count += 1
        m.last_health_check = time.time()
        if not healthy:
            m.health_check_failures += 1
        n = m.health_check_count
        m.avg_health_latency_ms = ((m.avg_health_latency_ms * (n - 1)) + latency_ms) / n

    def record_failure(self, service_id: str):
        m = self._metrics.get(service_id)
        if m is None:
            return
        m.failure_count += 1
        m.last_failure = time.time()

    def record_recovery(self, service_id: str):
        m = self._metrics.get(service_id)
        if m is None:
            return
        m.recovery_count += 1
        m.last_recovery = time.time()

    def record_restart(self, service_id: str):
        m = self._metrics.get(service_id)
        if m is None:
            return
        m.restarts += 1

    def get_metrics(self, service_id: str) -> ServiceMetrics | None:
        m = self._metrics.get(service_id)
        if m and m.started_at > 0:
            m.uptime_seconds = time.time() - m.started_at
        return m

    def all_metrics(self) -> dict[str, ServiceMetrics]:
        for m in self._metrics.values():
            if m.started_at > 0:
                m.uptime_seconds = time.time() - m.started_at
        return dict(self._metrics)

    def summary(self) -> dict[str, Any]:
        return {
            "services": len(self._metrics),
            "total_health_checks": sum(m.health_check_count for m in self._metrics.values()),
            "total_failures": sum(m.failure_count for m in self._metrics.values()),
            "total_recoveries": sum(m.recovery_count for m in self._metrics.values()),
            "total_restarts": sum(m.restarts for m in self._metrics.values()),
        }


class HeartbeatManager:
    def __init__(self):
        self._heartbeats: dict[str, HeartbeatRecord] = {}
        self._lock = threading.Lock()
        self._stale_callbacks: list[Callable[[str], None]] = []

    def on_stale(self, callback: Callable[[str], None]):
        self._stale_callbacks.append(callback)

    def record(self, service_id: str, metadata: dict[str, Any] | None = None):
        with self._lock:
            self._heartbeats[service_id] = HeartbeatRecord(
                service_id=service_id,
                timestamp=time.time(),
                metadata=metadata or {},
            )

    def is_alive(self, service_id: str, timeout_ms: float = 60000.0) -> bool:
        record = self._heartbeats.get(service_id)
        if record is None:
            return False
        return (time.time() - record.timestamp) < (timeout_ms / 1000.0)

    def last_heartbeat(self, service_id: str) -> float | None:
        record = self._heartbeats.get(service_id)
        return record.timestamp if record else None

    def get_stale_services(self, timeout_ms: float = 60000.0) -> list[str]:
        now = time.time()
        return [
            sid for sid, r in self._heartbeats.items()
            if (now - r.timestamp) > (timeout_ms / 1000.0)
        ]

    def check_for_stale(self, timeout_ms: float = 60000.0):
        stale = self.get_stale_services(timeout_ms)
        for sid in stale:
            for cb in self._stale_callbacks:
                try:
                    cb(sid)
                except Exception:
                    pass

    def all_heartbeats(self) -> dict[str, HeartbeatRecord]:
        return dict(self._heartbeats)

    def summary(self) -> dict[str, Any]:
        return {
            "active": len(self._heartbeats),
            "stale": len(self.get_stale_services()),
        }


class ServiceKernel:
    def __init__(self, orchestrator: PlatformOrchestrator | None = None):
        self.orchestrator = orchestrator or PlatformOrchestrator()
        self.lifecycle = LifecycleManager()
        self.health = HealthManager()
        self.failure = FailureManager()
        self.capabilities = CapabilityPublisher()
        self.metrics = MetricsCollector()
        self.heartbeat = HeartbeatManager()

        self._event_handlers: dict[str, list[Callable]] = defaultdict(list)
        self._running = False
        self._shutdown_requested = False
        self._main_thread: threading.Thread | None = None

        self.health.on_unhealthy(self._on_unhealthy_service)

    def on(self, event: str, handler: Callable):
        self._event_handlers[event].append(handler)

    def _emit(self, event: str, data: dict[str, Any] | None = None):
        for handler in self._event_handlers.get(event, []):
            try:
                handler(data or {})
            except Exception:
                pass

    def _on_unhealthy_service(self, service_id: str, health: ServiceHealth):
        action = self.failure.record_failure(service_id, health.error)
        self.metrics.record_failure(service_id)
        self._emit("service.unhealthy", {
            "service_id": service_id,
            "error": health.error,
            "action": action.value,
        })

    def register(self, svc: ServiceDef, recovery_policy: RecoveryPolicy | None = None):
        self.orchestrator.register(svc)
        self.lifecycle.register(svc.id)
        self.health.register(svc.id, svc.health_check, svc.estimated_startup_ms)
        self.failure.register_policy(svc.id, recovery_policy)
        self.metrics.register(svc.id)

    def register_many(self, services: list[ServiceDef]):
        for svc in services:
            self.register(svc)

    def boot(self, provider: Any = None) -> BootReport:
        self._shutdown_requested = False
        report = self.orchestrator.boot(provider)
        for sid in list(self.orchestrator.all_status().keys()):
            status = self.orchestrator.get_status(sid)
            if status == ServiceStatus.HEALTHY:
                self.lifecycle.transition(sid, ServiceState.HEALTHY)
                self.metrics.record_start(sid)
                self.failure.record_success(sid)
            elif status == ServiceStatus.DEGRADED:
                self.lifecycle.transition(sid, ServiceState.DEGRADED)
                self.metrics.record_start(sid)
            elif status == ServiceStatus.FAILED:
                self.lifecycle.transition(sid, ServiceState.FAILED)
            else:
                self.lifecycle.transition(sid, ServiceState.BOOTING)
        self.health.start()
        self._running = True
        self._emit("kernel.booted", {
            "healthy": report.healthy_count,
            "degraded": report.degraded_count,
            "failed": report.failed_count,
        })
        return report

    def shutdown(self):
        self._shutdown_requested = True
        self.health.stop()
        self._running = False
        for sid, state in self.lifecycle.all_states().items():
            if state in (ServiceState.HEALTHY, ServiceState.DEGRADED):
                self.lifecycle.transition(sid, ServiceState.STOPPED)
        self.orchestrator.shutdown()
        self._emit("kernel.shutdown", {})

    def get_status(self, service_id: str) -> dict[str, Any]:
        return {
            "lifecycle": self.lifecycle.get_state(service_id),
            "health": self.health.get_health(service_id),
            "metrics": self.metrics.get_metrics(service_id),
            "boot_status": self.orchestrator.get_status(service_id),
            "alive": self.heartbeat.is_alive(service_id),
            "capabilities": self.capabilities.find_by_service(service_id),
        }

    def all_status(self) -> dict[str, dict[str, Any]]:
        return {sid: self.get_status(sid) for sid in self.orchestrator.all_status()}

    def restart_service(self, service_id: str) -> bool:
        state = self.lifecycle.get_state(service_id)
        if state not in (ServiceState.FAILED, ServiceState.STOPPED):
            return False
        svc = self.orchestrator._services.get(service_id)
        if svc is None:
            return False
        self.lifecycle.transition(service_id, ServiceState.BOOTING)
        self.metrics.record_restart(service_id)
        try:
            if svc.factory:
                instance = svc.factory()
                self.orchestrator._instances[service_id] = instance
            self.lifecycle.transition(service_id, ServiceState.HEALTHY)
            self.failure.record_success(service_id)
            self.metrics.record_recovery(service_id)
            self._emit("service.restarted", {"service_id": service_id})
            return True
        except Exception as e:
            self.lifecycle.transition(service_id, ServiceState.FAILED)
            self.failure.record_failure(service_id, str(e))
            return False

    def record_heartbeat(self, service_id: str):
        self.heartbeat.record(service_id)

    def summary(self) -> dict[str, Any]:
        return {
            "services": {
                "registered": len(self.orchestrator._services),
                "booted": len(self.orchestrator.all_status()),
            },
            "lifecycle": self.lifecycle.summary(),
            "health": self.health.summary(),
            "failure": self.failure.summary(),
            "capabilities": self.capabilities.summary(),
            "metrics": self.metrics.summary(),
            "heartbeat": self.heartbeat.summary(),
            "running": self._running,
        }
