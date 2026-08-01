from __future__ import annotations

import socket
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import RLock
from typing import Any


@dataclass
class MetricPoint:
    name: str = ""
    value: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: float = 0.0
    host: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class FabricMetrics:
    """Metrics collection and aggregation for the fabric."""

    def __init__(self, kernel=None):
        self._points: list[MetricPoint] = []
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = RLock()
        self._max_points = 100000
        self._kernel = kernel

    def record(self, name: str, value: float,
               tags: dict[str, str] | None = None):
        with self._lock:
            point = MetricPoint(name=name, value=value, tags=tags or {})
            self._points.append(point)
            if len(self._points) > self._max_points:
                self._points.pop(0)
            self._counters[name] += value
            self._histograms[name].append(value)
        if self._kernel and self._kernel.storage and self._kernel.storage.connected:
            hostname = socket.gethostname()
            self._kernel.storage.store_metric({
                "name": name, "value": value,
                "tags": tags or {},
                "timestamp": point.timestamp,
                "host": hostname,
            })

    def gauge(self, name: str, value: float):
        with self._lock:
            self._gauges[name] = value

    def increment(self, name: str, delta: float = 1.0):
        self.record(name, delta)

    def counter(self, name: str) -> float:
        return self._counters.get(name, 0.0)

    def gauge_value(self, name: str) -> float | None:
        return self._gauges.get(name)

    def histogram(self, name: str) -> dict[str, float]:
        with self._lock:
            values = self._histograms.get(name, [])
            if not values:
                return {}
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            return {
                "min": sorted_vals[0],
                "max": sorted_vals[-1],
                "avg": sum(sorted_vals) / n,
                "median": sorted_vals[n // 2],
                "p95": sorted_vals[int(n * 0.95)],
                "p99": sorted_vals[int(n * 0.99)],
                "count": n,
            }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "total_points": len(self._points),
                "histogram_names": list(self._histograms.keys()),
            }

    def reset(self):
        with self._lock:
            self._points.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
