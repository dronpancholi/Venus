"""
UCOS: CapabilityMetrics — Metrics collection, tracking, and reporting for UCOS.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.ucos.capability import Capability, CapabilityState


@dataclass
class MetricsSnapshot:
    timestamp: float = 0.0
    metric_type: str = ""
    metric_name: str = ""
    value: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class CapabilityMetrics:
    """Metrics collection, tracking, and reporting for all capabilities."""

    def __init__(self, registry):
        self._registry = registry
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._snapshots: list[MetricsSnapshot] = []
        self._latency_buckets: list[float] = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 5000]

    def increment(self, name: str, amount: int = 1, tags: dict[str, str] | None = None):
        key = f"{name}:{tags}" if tags else name
        self._counters[key] += amount
        self._snapshots.append(MetricsSnapshot(
            metric_type="counter",
            metric_name=name,
            value=self._counters[key],
            tags=tags or {},
        ))

    def gauge(self, name: str, value: float, tags: dict[str, str] | None = None):
        key = f"{name}:{tags}" if tags else name
        self._gauges[key] = value
        self._snapshots.append(MetricsSnapshot(
            metric_type="gauge",
            metric_name=name,
            value=value,
            tags=tags or {},
        ))

    def observe(self, name: str, value: float, tags: dict[str, str] | None = None):
        key = f"{name}:{tags}" if tags else name
        self._histograms[key].append(value)
        self._snapshots.append(MetricsSnapshot(
            metric_type="histogram",
            metric_name=name,
            value=value,
            tags=tags or {},
        ))

    def snapshot_state(self) -> dict[str, Any]:
        total = self._registry.count
        by_state: dict[str, int] = defaultdict(int)
        by_category: dict[str, int] = defaultdict(int)
        total_health = 0.0
        for cap in self._registry.all:
            by_state[cap.state.value] += 1
            by_category[cap.definition.category.value] += 1
            total_health += cap.definition.health.score

        self.gauge("capabilities.total", total)
        self.gauge("capabilities.health_avg", total_health / max(total, 1))
        for state, count in by_state.items():
            self.gauge(f"capabilities.state.{state}", count)
        for cat, count in by_category.items():
            self.gauge(f"capabilities.category.{cat}", count)

        return {
            "total": total,
            "by_state": dict(by_state),
            "by_category": dict(by_category),
            "avg_health": total_health / max(total, 1),
            "timestamp": time.time(),
        }

    def histogram_summary(self, name: str) -> dict[str, float] | None:
        key_candidates = [k for k in self._histograms if k.startswith(name)]
        if not key_candidates:
            return None
        values = []
        for k in key_candidates:
            values.extend(self._histograms[k])
        if not values:
            return None
        values.sort()
        n = len(values)
        return {
            "count": n,
            "min": values[0],
            "max": values[-1],
            "mean": sum(values) / n,
            "p50": values[int(n * 0.5)],
            "p90": values[int(n * 0.9)],
            "p99": values[int(n * 0.99)],
        }

    def snapshot_rate(self) -> float:
        if len(self._snapshots) < 2:
            return 0.0
        duration = self._snapshots[-1].timestamp - self._snapshots[0].timestamp
        return len(self._snapshots) / max(duration, 0.001)

    def report(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "snapshots": len(self._snapshots),
            "snapshot_rate": self.snapshot_rate(),
            "health": self.snapshot_state(),
        }
