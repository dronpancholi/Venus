from __future__ import annotations

import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class HealthDimension(Enum):
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERRORS = "errors"
    MEMORY = "memory"
    QUEUE_DEPTH = "queue_depth"
    STATE_FRESHNESS = "state_freshness"
    KNOWLEDGE_FRESHNESS = "knowledge_freshness"
    AI_PROVIDER_HEALTH = "ai_provider_health"
    WORKFLOW_HEALTH = "workflow_health"
    WORKSPACE_HEALTH = "workspace_health"
    GRAPH_HEALTH = "graph_health"
    THREAD_HEALTH = "thread_health"
    BOOT_HEALTH = "boot_health"
    EVENT_BUS_HEALTH = "event_bus_health"

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()


@dataclass
class HealthMetric:
    dimension: HealthDimension
    value: float
    max_value: float = 1.0
    weight: float = 1.0
    label: str = ""

    @property
    def normalized(self) -> float:
        if self.max_value <= 0:
            return 0.0
        return min(1.0, max(0.0, self.value / self.max_value))

    @property
    def score(self) -> float:
        return self.normalized * self.weight


@dataclass
class HealthEntry:
    subsystem: str
    metrics: list[HealthMetric] = field(default_factory=list)
    timestamp: float = 0.0
    custom_score: float | None = None

    def add_metric(self, dimension: HealthDimension, value: float,
                   max_value: float = 1.0, weight: float = 1.0,
                   label: str = "") -> HealthMetric:
        metric = HealthMetric(
            dimension=dimension, value=value,
            max_value=max_value, weight=weight, label=label or dimension.display_name,
        )
        self.metrics.append(metric)
        return metric

    @property
    def score(self) -> float:
        if self.custom_score is not None:
            return self.custom_score
        if not self.metrics:
            return 0.0
        total_weight = sum(m.weight for m in self.metrics)
        if total_weight <= 0:
            return 0.0
        return sum(m.score for m in self.metrics) / total_weight


@dataclass
class HealthSnapshot:
    timestamp: float = 0.0
    entries: dict[str, HealthEntry] = field(default_factory=dict)
    overall_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "overall_score": round(self.overall_score, 4),
            "subsystems": {
                name: {
                    "score": round(entry.score, 4),
                    "metrics": [
                        {
                            "dimension": m.dimension.value,
                            "label": m.label,
                            "value": m.value,
                            "max": m.max_value,
                            "normalized": round(m.normalized, 4),
                            "weight": m.weight,
                        }
                        for m in entry.metrics
                    ],
                }
                for name, entry in sorted(entry.items())
            },
        }


@dataclass
class HealthTrend:
    subsystem: str
    dimension: HealthDimension
    values: list[tuple[float, float]] = field(default_factory=list)

    def add_point(self, timestamp: float, value: float) -> None:
        self.values.append((timestamp, value))

    @property
    def current(self) -> float:
        return self.values[-1][1] if self.values else 0.0

    @property
    def average(self) -> float:
        if not self.values:
            return 0.0
        return sum(v for _, v in self.values) / len(self.values)

    @property
    def trend(self) -> str:
        if len(self.values) < 5:
            return "insufficient_data"
        recent = [v for _, v in self.values[-5:]]
        older = [v for _, v in self.values[-10:-5]]
        if not older:
            return "stable"
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older)
        if avg_recent > avg_older * 1.1:
            return "improving"
        elif avg_recent < avg_older * 0.9:
            return "declining"
        return "stable"


@dataclass
class EngineeringHealthScore:
    overall: float = 0.0
    subsystem_scores: dict[str, float] = field(default_factory=dict)
    dimension_scores: dict[str, float] = field(default_factory=dict)
    trend: str = "stable"
    snapshot_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": round(self.overall, 4),
            "subsystems": {k: round(v, 4) for k, v in sorted(self.subsystem_scores.items())},
            "dimensions": {k: round(v, 4) for k, v in sorted(self.dimension_scores.items())},
            "trend": self.trend,
            "snapshots": self.snapshot_count,
        }


class HealthCollector:
    def __init__(self, subsystem: str, collect_fn: Callable[[], HealthEntry]) -> None:
        self.subsystem = subsystem
        self.collect_fn = collect_fn

    def collect(self) -> HealthEntry:
        try:
            return self.collect_fn()
        except Exception as e:
            entry = HealthEntry(subsystem=self.subsystem, timestamp=time.time())
            entry.add_metric(HealthDimension.AVAILABILITY, 0.0, label=f"Collect failed: {e}")
            return entry


_WEIGHT_BY_DIMENSION: dict[HealthDimension, float] = {
    HealthDimension.AVAILABILITY: 3.0,
    HealthDimension.LATENCY: 1.5,
    HealthDimension.ERRORS: 2.0,
    HealthDimension.MEMORY: 1.0,
    HealthDimension.QUEUE_DEPTH: 1.0,
    HealthDimension.STATE_FRESHNESS: 1.5,
    HealthDimension.KNOWLEDGE_FRESHNESS: 1.0,
    HealthDimension.AI_PROVIDER_HEALTH: 2.0,
    HealthDimension.WORKFLOW_HEALTH: 1.5,
    HealthDimension.WORKSPACE_HEALTH: 1.0,
    HealthDimension.GRAPH_HEALTH: 1.5,
    HealthDimension.THREAD_HEALTH: 1.0,
    HealthDimension.BOOT_HEALTH: 2.0,
    HealthDimension.EVENT_BUS_HEALTH: 1.5,
}


class SystemHealthEngine:
    def __init__(self, kernel: Any) -> None:
        self._kernel = kernel
        self._collectors: dict[str, HealthCollector] = {}
        self._snapshots: list[HealthSnapshot] = []
        self._max_snapshots = 100000
        self._trends: dict[tuple[str, str], HealthTrend] = {}
        self._lock = threading.RLock()
        self._booted = False

    def boot(self) -> None:
        if self._booted:
            return
        self._booted = True

    @property
    def snapshot_count(self) -> int:
        return len(self._snapshots)

    @property
    def latest_snapshot(self) -> HealthSnapshot | None:
        return self._snapshots[-1] if self._snapshots else None

    def register_collector(self, subsystem: str, collect_fn: Callable[[], HealthEntry]) -> HealthCollector:
        collector = HealthCollector(subsystem, collect_fn)
        self._collectors[subsystem] = collector
        return collector

    def unregister_collector(self, subsystem: str) -> None:
        self._collectors.pop(subsystem, None)

    def snapshot(self) -> HealthSnapshot:
        snap = HealthSnapshot(timestamp=time.time())

        for name, collector in self._collectors.items():
            entry = collector.collect()
            entry.timestamp = snap.timestamp
            snap.entries[name] = entry
            for metric in entry.metrics:
                key = (name, metric.dimension.value)
                if key not in self._trends:
                    self._trends[key] = HealthTrend(
                        subsystem=name, dimension=metric.dimension,
                    )
                self._trends[key].add_point(snap.timestamp, metric.normalized)

        snap.overall_score = self._compute_overall(snap)

        with self._lock:
            self._snapshots.append(snap)
            if len(self._snapshots) > self._max_snapshots:
                self._snapshots = self._snapshots[-self._max_snapshots:]

        return snap

    def _compute_overall(self, snap: HealthSnapshot) -> float:
        if not snap.entries:
            return 0.0
        total_weight = 0.0
        weighted_sum = 0.0
        for entry in snap.entries.values():
            weight = _WEIGHT_BY_DIMENSION.get(HealthDimension.AVAILABILITY, 1.0)
            weighted_sum += entry.score * weight
            total_weight += weight
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def score(self) -> EngineeringHealthScore:
        snap = self.latest_snapshot
        if not snap:
            return EngineeringHealthScore()

        dimension_aggregates: dict[str, list[float]] = defaultdict(list)
        subsystem_scores: dict[str, float] = {}

        for name, entry in snap.entries.items():
            subsystem_scores[name] = entry.score
            for metric in entry.metrics:
                dimension_aggregates[metric.dimension.value].append(metric.normalized)

        dimension_scores = {
            dim: sum(vals) / len(vals) for dim, vals in dimension_aggregates.items()
        }

        trends: dict[str, str] = {}
        for (sub_name, dim), trend in self._trends.items():
            key = f"{sub_name}.{dim}"
            t = trend.trend
            if t != "stable":
                trends[key] = t

        improving = sum(1 for t in trends.values() if t == "improving")
        declining = sum(1 for t in trends.values() if t == "declining")
        if declining > improving * 2:
            overall_trend = "declining"
        elif improving > declining * 2:
            overall_trend = "improving"
        else:
            overall_trend = "stable"

        return EngineeringHealthScore(
            overall=snap.overall_score,
            subsystem_scores=subsystem_scores,
            dimension_scores=dimension_scores,
            trend=overall_trend,
            snapshot_count=len(self._snapshots),
        )

    def get_trend(self, subsystem: str, dimension: HealthDimension) -> HealthTrend | None:
        return self._trends.get((subsystem, dimension.value))

    def get_dimension_trends(self, dimension: HealthDimension) -> list[HealthTrend]:
        return [
            trend for (sub, dim), trend in self._trends.items()
            if dim == dimension.value
        ]

    def history(self, subsystem: str | None = None,
                dimension: HealthDimension | None = None,
                limit: int = 100) -> list[HealthSnapshot]:
        snapshots = list(self._snapshots)
        if limit > 0:
            snapshots = snapshots[-limit:]

        if subsystem or dimension:
            filtered: list[HealthSnapshot] = []
            for snap in snapshots:
                entries = {}
                for name, entry in snap.entries.items():
                    if subsystem and name != subsystem:
                        continue
                    if dimension:
                        entry.metrics = [m for m in entry.metrics if m.dimension == dimension]
                        if not entry.metrics:
                            continue
                    entries[name] = entry
                if entries:
                    new_snap = HealthSnapshot(
                        timestamp=snap.timestamp,
                        entries=entries,
                    )
                    new_snap.overall_score = self._compute_overall(new_snap)
                    filtered.append(new_snap)
            return filtered

        return snapshots

    def health_by_dimension(self) -> dict[str, float]:
        snap = self.latest_snapshot
        if not snap:
            return {}
        dim_values: dict[str, list[float]] = defaultdict(list)
        for entry in snap.entries.values():
            for metric in entry.metrics:
                dim_values[metric.dimension.value].append(metric.normalized)
        return {
            dim: sum(vals) / len(vals) for dim, vals in dim_values.items()
        }
