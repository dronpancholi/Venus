"""
Resource Management (Mission 176) — track, observe, and alert on platform resources.

Not a new engine. Thin observable layer that queries existing subsystems
and provides unified resource tracking.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResourceCategory(Enum):
    MEMORY = "memory"
    THREADS = "threads"
    WORKERS = "workers"
    CACHES = "caches"
    PROVIDERS = "providers"
    CONNECTIONS = "connections"
    STORES = "stores"
    SESSIONS = "sessions"
    EVENTS = "events"
    AGENTS = "agents"


@dataclass
class ResourceMetric:
    category: ResourceCategory
    name: str
    current: float = 0.0
    max: float = 0.0
    limit: float = 0.0
    unit: str = "count"
    tags: list[str] = field(default_factory=list)

    @property
    def pct(self) -> float:
        if self.limit > 0:
            return (self.current / self.limit) * 100.0
        return 0.0

    @property
    def alert(self) -> bool:
        return self.limit > 0 and self.current >= self.limit


@dataclass
class ResourceSnapshot:
    timestamp: float = 0.0
    metrics: list[ResourceMetric] = field(default_factory=list)

    def by_category(self) -> dict[str, list[ResourceMetric]]:
        groups: dict[str, list[ResourceMetric]] = defaultdict(list)
        for m in self.metrics:
            groups[m.category.value].append(m)
        return dict(groups)

    def alerts(self) -> list[ResourceMetric]:
        return [m for m in self.metrics if m.alert]


class ResourceThresholds:
    """Configurable resource thresholds per category."""

    def __init__(self):
        self._limits: dict[str, float] = {
            "memory.engineering_objects": 100_000,
            "threads.active": 100,
            "threads.total": 200,
            "events.store": 50_000,
            "agents.active": 50,
            "sessions.active": 100,
            "services.registered": 500,
        }

    def get(self, key: str, default: float = 0.0) -> float:
        return self._limits.get(key, default)

    def set(self, key: str, limit: float):
        self._limits[key] = limit


class ResourceMonitor:
    """Platform resource monitor.

    Collects resource data from a FabricKernel (or any object with similar attributes).
    Provides snapshots, alerts, and background polling.
    """

    def __init__(self, kernel: Any = None, poll_interval: float = 30.0):
        self._kernel = kernel
        self._poll_interval = poll_interval
        self._snapshots: list[ResourceSnapshot] = []
        self._max_snapshots = 1000
        self._thresholds = ResourceThresholds()
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._alert_callbacks: list[callable] = []

    @property
    def thresholds(self) -> ResourceThresholds:
        return self._thresholds

    @property
    def snapshots(self) -> list[ResourceSnapshot]:
        with self._lock:
            return list(self._snapshots)

    def on_alert(self, callback: callable):
        self._alert_callbacks.append(callback)

    def snapshot(self) -> ResourceSnapshot:
        metrics: list[ResourceMetric] = []
        k = self._kernel

        # Threads
        threads_active = 0
        threads_total = 0
        if k:
            try:
                threads_total = len(k._threads) if hasattr(k, '_threads') else 0
                threads_active = sum(1 for t in k._threads if t.is_alive()) if hasattr(k, '_threads') else 0
            except Exception:
                pass
        metrics.append(ResourceMetric(
            ResourceCategory.THREADS, "threads.active", float(threads_active),
            limit=self._thresholds.get("threads.active", 100), unit="threads",
        ))
        metrics.append(ResourceMetric(
            ResourceCategory.THREADS, "threads.total", float(threads_total),
            limit=self._thresholds.get("threads.total", 200), unit="threads",
        ))

        # Events
        if k and hasattr(k, 'event_store') and k.event_store:
            try:
                event_count = k.event_store.count()
                event_max = getattr(k.event_store, 'max_events', 50_000)
            except Exception:
                event_count = 0
                event_max = 50_000
        else:
            event_count = 0
            event_max = 50_000
        metrics.append(ResourceMetric(
            ResourceCategory.EVENTS, "events.store", float(event_count),
            max=float(event_max), limit=self._thresholds.get("events.store", 50_000), unit="events",
        ))

        # Services
        if k and hasattr(k, 'registry') and k.registry:
            try:
                services = k.registry.count()
            except Exception:
                services = 0
        else:
            services = 0
        metrics.append(ResourceMetric(
            ResourceCategory.STORES, "services.registered", float(services),
            limit=self._thresholds.get("services.registered", 500), unit="services",
        ))

        # Sessions
        if k and hasattr(k, '_contexts'):
            try:
                sessions = len(k._contexts)
            except Exception:
                sessions = 0
        else:
            sessions = 0
        metrics.append(ResourceMetric(
            ResourceCategory.SESSIONS, "sessions.active", float(sessions),
            limit=self._thresholds.get("sessions.active", 100), unit="sessions",
        ))

        # Agents
        agents = 0
        if k and hasattr(k, 'agent_runtime') and k.agent_runtime:
            try:
                from genesis.fabric.agents import AgentStatus
                agents = sum(1 for a in k.agent_runtime._agents.values()
                              if a.status == AgentStatus.RUNNING)
            except Exception:
                pass
        metrics.append(ResourceMetric(
            ResourceCategory.AGENTS, "agents.active", float(agents),
            limit=self._thresholds.get("agents.active", 50), unit="agents",
        ))

        # Engineering objects
        eng_count = 0
        if k and hasattr(k, 'engineering') and k.engineering:
            try:
                eng_count = len(k.engineering._objects) if hasattr(k.engineering, '_objects') else 0
            except Exception:
                pass
        metrics.append(ResourceMetric(
            ResourceCategory.MEMORY, "memory.engineering_objects", float(eng_count),
            limit=self._thresholds.get("memory.engineering_objects", 100_000), unit="objects",
        ))

        snap = ResourceSnapshot(timestamp=time.time(), metrics=metrics)
        with self._lock:
            self._snapshots.append(snap)
            if len(self._snapshots) > self._max_snapshots:
                self._snapshots.pop(0)

        for alert in snap.alerts():
            for cb in self._alert_callbacks:
                try:
                    cb(alert)
                except Exception:
                    pass

        if k and hasattr(k, 'emit'):
            try:
                k.emit("resource.snapshot",
                       {"timestamp": snap.timestamp, "metrics": len(snap.metrics),
                        "alerts": len(snap.alerts())},
                       origin="resources", tags=["resources", "monitor"])
            except Exception:
                pass

        return snap

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True, name="res-monitor")
        self._thread.start()

    def stop(self):
        self._running = False

    def _poll(self):
        while self._running:
            try:
                self.snapshot()
            except Exception:
                pass
            time.sleep(self._poll_interval)

    def summary(self) -> dict[str, Any]:
        snap = self.snapshot()
        return {
            "timestamp": snap.timestamp,
            "metrics": len(snap.metrics),
            "alerts": len(snap.alerts()),
            "by_category": {k: len(v) for k, v in snap.by_category().items()},
        }
