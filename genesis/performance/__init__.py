"""
Performance Engineering (Mission 177) — instrument the platform.

Not a new engine. Thin measurement wrapper that benchmarks operations,
emits events, and detects regressions.
"""

from __future__ import annotations

import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Benchmark:
    name: str
    duration_ms: float = 0.0
    timestamp: float = 0.0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class BenchmarkSummary:
    name: str
    count: int = 0
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    last_ms: float = 0.0

    @classmethod
    def from_samples(cls, name: str, samples: list[Benchmark]) -> BenchmarkSummary:
        if not samples:
            return cls(name=name)
        durations = sorted(s.duration_ms for s in samples)
        n = len(durations)
        return cls(
            name=name,
            count=n,
            min_ms=durations[0],
            max_ms=durations[-1],
            avg_ms=sum(durations) / n,
            p50_ms=durations[int(n * 0.50)],
            p95_ms=durations[int(n * 0.95)],
            p99_ms=durations[int(n * 0.99)],
            last_ms=durations[-1],
        )


class PerformanceMonitor:
    """Platform-wide performance instrumentation.

    Wraps any callable with timing. Stores benchmark history.
    Emits Fabric events for slow operations.
    """

    def __init__(self, kernel: Any = None, slow_threshold_ms: float = 1000.0):
        self._kernel = kernel
        self._slow_threshold_ms = slow_threshold_ms
        self._history: dict[str, list[Benchmark]] = defaultdict(list)
        self._max_samples = 1000
        self._lock = threading.RLock()

    def measure(self, name: str, fn: Callable, *args,
                tags: list[str] | None = None, **kwargs) -> Any:
        t0 = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
            return result
        finally:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            b = Benchmark(
                name=name, duration_ms=elapsed_ms,
                tags=tags or [],
                metadata={"args": str(args)[:100], "kwargs": str(kwargs)[:100]},
            )
            with self._lock:
                self._history[name].append(b)
                if len(self._history[name]) > self._max_samples:
                    self._history[name].pop(0)

            if elapsed_ms > self._slow_threshold_ms and self._kernel:
                try:
                    self._kernel.emit(
                        "performance.slow_operation",
                        {"name": name, "duration_ms": elapsed_ms, "threshold_ms": self._slow_threshold_ms},
                        origin="performance", tags=["performance", "slow"] + (tags or []),
                    )
                except Exception:
                    pass

    def record(self, name: str, duration_ms: float, tags: list[str] | None = None):
        b = Benchmark(name=name, duration_ms=duration_ms, tags=tags or [])
        with self._lock:
            self._history[name].append(b)
            if len(self._history[name]) > self._max_samples:
                self._history[name].pop(0)

    def summary(self, name: str | None = None) -> dict[str, BenchmarkSummary]:
        with self._lock:
            if name:
                targets = {name: list(self._history.get(name, []))}
            else:
                targets = dict(self._history)
        return {
            n: BenchmarkSummary.from_samples(n, samples)
            for n, samples in targets.items()
        }

    def detect_regressions(self, baseline: dict[str, BenchmarkSummary] | None = None,
                           threshold_pct: float = 20.0) -> list[dict[str, Any]]:
        regressions: list[dict[str, Any]] = []
        current = self.summary()
        baseline = baseline or {}
        for name, cur in current.items():
            prev = baseline.get(name)
            if prev and prev.avg_ms > 0 and cur.count > 0:
                change_pct = ((cur.avg_ms - prev.avg_ms) / prev.avg_ms) * 100
                if change_pct > threshold_pct:
                    regressions.append({
                        "name": name,
                        "previous_avg_ms": prev.avg_ms,
                        "current_avg_ms": cur.avg_ms,
                        "change_pct": change_pct,
                    })
        return regressions

    def instrument(self, name: str, tags: list[str] | None = None):
        """Decorator: @pm.instrument('operation_name')"""
        tags = tags or []

        def decorator(fn):
            def wrapper(*args, **kwargs):
                return self.measure(name, fn, *args, tags=tags, **kwargs)
            return wrapper

        return decorator
