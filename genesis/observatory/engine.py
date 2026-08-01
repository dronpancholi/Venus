from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class MetricSample:
    timestamp: float
    value: float
    label: str = ""


@dataclass
class TrendReport:
    metric: str
    samples: list[MetricSample] = field(default_factory=list)
    current: float = 0.0
    min: float = 0.0
    max: float = 0.0
    avg: float = 0.0
    trend: str = "stable"
    change_pct: float = 0.0


class EngineeringObservatory:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._samples: dict[str, list[MetricSample]] = defaultdict(list)
        self._max_samples = 1000
        self._obs_obj: EngineeringObject | None = None
        self._booted = False

    def boot(self):
        if self._booted:
            return
        self._booted = True
        self._obs_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="EngineeringObservatory",
            description="Historical engineering analytics and trend analysis",
            tags=["observatory", "analytics"],
        )
        self._registry.register(self._obs_obj)

    def record(self, metric: str, value: float, label: str = ""):
        samples = self._samples[metric]
        samples.append(MetricSample(timestamp=time.time(), value=value, label=label))
        if len(samples) > self._max_samples:
            self._samples[metric] = samples[-self._max_samples:]

    def trend(self, metric: str, window: int = 100) -> TrendReport | None:
        samples = self._samples.get(metric)
        if not samples or len(samples) < 2:
            return None
        recent = samples[-window:]
        values = [s.value for s in recent]
        avg_val = sum(values) / len(values)
        mid = len(values) // 2
        first_half = sum(values[:mid]) / max(mid, 1)
        second_half = sum(values[mid:]) / max(len(values) - mid, 1)
        change = ((second_half - first_half) / max(abs(first_half), 0.001)) * 100
        if change > 10:
            direction = "increasing"
        elif change < -10:
            direction = "decreasing"
        else:
            direction = "stable"
        return TrendReport(
            metric=metric,
            samples=recent,
            current=values[-1],
            min=min(values),
            max=max(values),
            avg=avg_val,
            trend=direction,
            change_pct=round(change, 1),
        )

    def snapshot(self) -> dict[str, Any]:
        trends = {}
        for metric in list(self._samples.keys()):
            t = self.trend(metric)
            if t:
                trends[metric] = {
                    "current": t.current,
                    "min": t.min,
                    "max": t.max,
                    "avg": t.avg,
                    "trend": t.trend,
                    "change_pct": t.change_pct,
                    "samples": len(t.samples),
                }
        return {
            "metrics": len(self._samples),
            "total_samples": sum(len(v) for v in self._samples.values()),
            "trends": trends,
        }

    def auto_record(self):
        if not self._kernel:
            return
        try:
            stats = self._kernel.stats()
            self.record("events_delivered", stats.events_delivered)
            self.record("services", stats.services)
            self.record("messages_sent", stats.messages_sent)
            self.record("executor_executions", stats.executor_executions)
            self.record("executor_failed", stats.executor_failed)
        except Exception:
            pass
