"""
Temporal Engine — time-aware entities, snapshots, mutations, replay, simulation.

Every entity has a birth, evolution, and history.
Time is a first-class dimension.
"""

from __future__ import annotations

import json
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from genesis.datalake import DataLakeEntity, VersionedStore, VersionRecord
from genesis.metamodel.entity import EntityType
from genesis.utils.identity import generate_id


# ── Temporal Snapshot ──

@dataclass
class TemporalSnapshot:
    """A point-in-time snapshot of entity state."""
    uid: str = ""
    entity_uid: str = ""
    version: int = 1
    timestamp: float = 0.0
    state: dict[str, Any] = field(default_factory=dict)
    snapshot_type: str = "manual"  # manual, automatic, mutation, checkpoint
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.uid:
            self.uid = generate_id("tsnap", 8)

    def to_dict(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "entity_uid": self.entity_uid,
            "version": self.version,
            "timestamp": self.timestamp,
            "state": dict(self.state),
            "snapshot_type": self.snapshot_type,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TemporalSnapshot:
        return cls(
            uid=d.get("uid", ""),
            entity_uid=d.get("entity_uid", ""),
            version=d.get("version", 1),
            timestamp=d.get("timestamp", 0),
            state=dict(d.get("state", {})),
            snapshot_type=d.get("snapshot_type", "manual"),
            metadata=dict(d.get("metadata", {})),
        )


# ── Time Series Store ──

@dataclass
class TimeSeriesPoint:
    """A single time-series data point."""
    timestamp: float = 0.0
    value: float = 0.0
    metric: str = ""
    entity_uid: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "value": self.value,
            "metric": self.metric,
            "entity_uid": self.entity_uid,
            "tags": dict(self.tags),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TimeSeriesPoint:
        return cls(
            timestamp=d.get("timestamp", 0),
            value=d.get("value", 0.0),
            metric=d.get("metric", ""),
            entity_uid=d.get("entity_uid", ""),
            tags=dict(d.get("tags", {})),
            metadata=dict(d.get("metadata", {})),
        )


class TimeSeriesStore:
    """
    Time-series store for entity metrics over time.

    Stores time-series data as JSONL files partitioned by metric name.
    """

    def __init__(self, base_path: str = ""):
        self.base_path = Path(base_path or "~/.venus/temporal/timeseries").expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._buffer: list[TimeSeriesPoint] = []
        self._buffer_size = 100
        self._metrics: set[str] = set()

    def record(self, point: TimeSeriesPoint):
        self._buffer.append(point)
        self._metrics.add(point.metric)
        if len(self._buffer) >= self._buffer_size:
            self.flush()

    def record_many(self, points: list[TimeSeriesPoint]):
        self._buffer.extend(points)
        for p in points:
            self._metrics.add(p.metric)
        if len(self._buffer) >= self._buffer_size:
            self.flush()

    def flush(self):
        if not self._buffer:
            return
        by_metric: dict[str, list[TimeSeriesPoint]] = defaultdict(list)
        for p in self._buffer:
            by_metric[p.metric].append(p)
        for metric, points in by_metric.items():
            metric_file = self.base_path / f"{metric.replace('/', '_')}.jsonl"
            lines = [json.dumps(p.to_dict(), default=str) + "\n" for p in points]
            with open(str(metric_file), "a") as f:
                f.writelines(lines)
        self._buffer.clear()

    def query(self, metric: str, start_time: float = 0, end_time: float = float("inf"),
              entity_uid: str = "", aggregation: str = "raw",
              window_seconds: float = 0) -> list[dict[str, Any]]:
        self.flush()
        metric_file = self.base_path / f"{metric.replace('/', '_')}.jsonl"
        if not metric_file.exists():
            return []
        points: list[TimeSeriesPoint] = []
        with open(str(metric_file)) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    p = TimeSeriesPoint.from_dict(json.loads(line))
                except (json.JSONDecodeError, KeyError):
                    continue
                if p.timestamp < start_time or p.timestamp > end_time:
                    continue
                if entity_uid and p.entity_uid != entity_uid:
                    continue
                points.append(p)
        if aggregation == "raw":
            return [p.to_dict() for p in sorted(points, key=lambda x: x.timestamp)]
        if aggregation == "avg":
            return self._aggregate_avg(points, window_seconds or 3600)
        if aggregation == "min":
            return self._aggregate_min(points, window_seconds or 3600)
        if aggregation == "max":
            return self._aggregate_max(points, window_seconds or 3600)
        if aggregation == "count":
            return self._aggregate_count(points, window_seconds or 3600)
        return [p.to_dict() for p in sorted(points, key=lambda x: x.timestamp)]

    def latest(self, metric: str, entity_uid: str = "") -> dict[str, Any] | None:
        results = self.query(metric, entity_uid=entity_uid)
        return results[-1] if results else None

    def metric_names(self) -> list[str]:
        self.flush()
        names = set()
        for f in self.base_path.iterdir():
            if f.suffix == ".jsonl":
                names.add(f.stem)
        return sorted(names)

    def _aggregate_avg(self, points: list[TimeSeriesPoint], window: float) -> list[dict[str, Any]]:
        return self._aggregate(points, window, lambda vals: sum(vals) / len(vals))

    def _aggregate_min(self, points: list[TimeSeriesPoint], window: float) -> list[dict[str, Any]]:
        return self._aggregate(points, window, min)

    def _aggregate_max(self, points: list[TimeSeriesPoint], window: float) -> list[dict[str, Any]]:
        return self._aggregate(points, window, max)

    def _aggregate_count(self, points: list[TimeSeriesPoint], window: float) -> list[dict[str, Any]]:
        return self._aggregate(points, window, len)

    def _aggregate(self, points: list[TimeSeriesPoint], window: float,
                   agg_fn: Callable) -> list[dict[str, Any]]:
        if not points:
            return []
        sorted_pts = sorted(points, key=lambda x: x.timestamp)
        result = []
        window_start = sorted_pts[0].timestamp
        bucket: list[float] = []
        for p in sorted_pts:
            if p.timestamp - window_start < window:
                bucket.append(p.value)
            else:
                if bucket:
                    result.append({
                        "timestamp": window_start,
                        "value": agg_fn(bucket),
                        "metric": p.metric,
                        "count": len(bucket),
                    })
                bucket = [p.value]
                window_start = p.timestamp
        if bucket:
            result.append({
                "timestamp": window_start,
                "value": agg_fn(bucket),
                "metric": sorted_pts[-1].metric,
                "count": len(bucket),
            })
        return result


# ── Temporal Query Engine ──

class TemporalQueryEngine:
    """
    Time-travel query engine for the Engineering Data Lake.

    Supports:
      - at_time: entity state as of a specific timestamp
      - between: entity states in a time range
      - before: entity states before a timestamp
      - after: entity states after a timestamp
    """

    def __init__(self, store: VersionedStore, ts_store: TimeSeriesStore):
        self._store = store
        self._ts = ts_store

    def at_time(self, uid: str, timestamp: float) -> DataLakeEntity | None:
        records = self._store.get_versions(uid)
        if not records:
            return None
        # Find the last version before or at the given timestamp
        target: VersionRecord | None = None
        for r in records:
            if r.timestamp <= timestamp:
                target = r
            else:
                break
        if target is None:
            return None
        return self._store.get(uid, target.version)

    def between(self, uid: str, start: float, end: float) -> list[DataLakeEntity]:
        records = self._store.get_versions(uid)
        entities: list[DataLakeEntity] = []
        for r in records:
            if start <= r.timestamp <= end:
                entity = self._store.get(uid, r.version)
                if entity:
                    entities.append(entity)
        return entities

    def before(self, uid: str, timestamp: float) -> DataLakeEntity | None:
        return self.at_time(uid, timestamp)

    def after(self, uid: str, timestamp: float) -> DataLakeEntity | None:
        records = self._store.get_versions(uid)
        for r in records:
            if r.timestamp >= timestamp:
                return self._store.get(uid, r.version)
        return None

    def all_entities_at_time(self, timestamp: float,
                             entity_type: EntityType | None = None) -> list[DataLakeEntity]:
        entities: list[DataLakeEntity] = []
        for info in self._store.list_entities():
            uid = info["uid"]
            entity = self.at_time(uid, timestamp)
            if entity and (entity_type is None or entity.entity_type == entity_type):
                entities.append(entity)
        return entities

    def metric_at_time(self, metric: str, timestamp: float,
                       entity_uid: str = "") -> dict[str, Any] | None:
        results = self._ts.query(metric, end_time=timestamp, entity_uid=entity_uid)
        return results[-1] if results else None

    def metric_between(self, metric: str, start: float, end: float,
                       entity_uid: str = "", aggregation: str = "raw",
                       window: float = 0) -> list[dict[str, Any]]:
        return self._ts.query(metric, start_time=start, end_time=end,
                              entity_uid=entity_uid, aggregation=aggregation,
                              window_seconds=window)


# ── Replay Engine ──

class ReplayEngine:
    """
    Replay entity history forward or backward.

    Supports stepping through every version of an entity in order.
    """

    def __init__(self, store: VersionedStore):
        self._store = store
        self._listeners: list[Callable[[DataLakeEntity, VersionRecord], None]] = []

    def on_step(self, listener: Callable[[DataLakeEntity, VersionRecord], None]):
        self._listeners.append(listener)

    def replay_forward(self, uid: str, from_version: int = 1,
                       to_version: int | None = None) -> list[DataLakeEntity]:
        records = self._store.get_versions(uid)
        if to_version is None:
            to_version = records[-1].version if records else 1
        entities: list[DataLakeEntity] = []
        for r in records:
            if r.version < from_version:
                continue
            if r.version > to_version:
                break
            entity = self._store.get(uid, r.version)
            if entity:
                entities.append(entity)
                for listener in self._listeners:
                    listener(entity, r)
        return entities

    def replay_backward(self, uid: str, from_version: int | None = None,
                        to_version: int = 1) -> list[DataLakeEntity]:
        records = self._store.get_versions(uid)
        if from_version is None:
            from_version = records[-1].version if records else 1
        entities: list[DataLakeEntity] = []
        for r in reversed(records):
            if r.version > from_version:
                continue
            if r.version < to_version:
                break
            entity = self._store.get(uid, r.version)
            if entity:
                entities.append(entity)
                for listener in self._listeners:
                    listener(entity, r)
        return entities

    def replay_all(self, uid: str) -> list[DataLakeEntity]:
        return self.replay_forward(uid)


# ── Simulation Engine ──

@dataclass
class SimulationStep:
    """A single step in a simulation."""
    step: int = 0
    timestamp: float = 0.0
    entity_state: dict[str, Any] = field(default_factory=dict)
    action: str = ""
    result: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "timestamp": self.timestamp,
            "entity_state": dict(self.entity_state),
            "action": self.action,
            "result": self.result,
        }


class SimulationEngine:
    """
    Simulate entity evolution over time.

    Uses a delta function to predict how entities change.
    Supports what-if analysis.
    """

    def __init__(self, store: VersionedStore, ts_store: TimeSeriesStore):
        self._store = store
        self._ts = ts_store
        self._models: dict[str, Callable[[DataLakeEntity, float], dict[str, Any]]] = {}

    def register_model(self, name: str,
                       model_fn: Callable[[DataLakeEntity, float], dict[str, Any]]):
        self._models[name] = model_fn

    def simulate(self, uid: str, model_name: str = "default",
                 steps: int = 10, interval: float = 86400.0,
                 start_time: float | None = None) -> list[SimulationStep]:
        entity = self._store.get_latest(uid)
        if not entity:
            return []
        now = start_time or time.time()
        result: list[SimulationStep] = []
        current_state = entity.to_dict()
        model_fn = self._models.get(model_name, self._default_model)
        for i in range(steps):
            step_time = now + (i * interval)
            delta = model_fn(entity, step_time)
            for key, value in delta.items():
                if isinstance(current_state.get(key), (int, float)) and isinstance(value, (int, float)):
                    current_state[key] = current_state[key] + value
                else:
                    current_state[key] = value
            result.append(SimulationStep(
                step=i + 1,
                timestamp=step_time,
                entity_state=dict(current_state),
                action=f"simulate_{model_name}",
                result=f"Step {i + 1} at {datetime.fromtimestamp(step_time, tz=timezone.utc).isoformat()}",
            ))
        return result

    def what_if(self, uid: str, attribute: str, new_value: Any,
                propagate: bool = True) -> list[SimulationStep]:
        entity = self._store.get_latest(uid)
        if not entity:
            return []
        modified = DataLakeEntity.from_dict(entity.to_dict())
        modified.attributes[attribute] = new_value
        result = self.simulate(uid, steps=5)
        result.insert(0, SimulationStep(
            step=0,
            timestamp=time.time(),
            entity_state=modified.to_dict(),
            action=f"what_if:{attribute}={new_value}",
            result=f"What-if: {attribute} changed to {new_value}",
        ))
        return result

    def _default_model(self, entity: DataLakeEntity, current_time: float) -> dict[str, Any]:
        return {
            "confidence": -0.01,
            "simulated_at": current_time,
        }


# ── Temporal Manager ──

class TemporalManager:
    """
    Top-level manager for the Temporal Engine.

    Integrates with:
      - VersionedStore (from Data Lake)
      - TimeSeriesStore (metrics over time)
      - TemporalQueryEngine (time travel)
      - ReplayEngine (history replay)
      - SimulationEngine (what-if)
      - UnifiedGraph (temporal entity mirror)
    """

    def __init__(self, store: VersionedStore, base_path: str = ""):
        self.base_path = Path(base_path or "~/.venus/temporal").expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.ts_store = TimeSeriesStore(base_path=str(self.base_path / "timeseries"))
        self.temporal_snapshots_path = self.base_path / "snapshots"
        self.temporal_snapshots_path.mkdir(parents=True, exist_ok=True)
        self._store = store
        self.query = TemporalQueryEngine(store, self.ts_store)
        self.replay = ReplayEngine(store)
        self.simulation = SimulationEngine(store, self.ts_store)
        self._auto_snapshot_interval: float = 0.0
        self._last_auto_snapshot: float = 0.0

    def set_auto_snapshot(self, interval_seconds: float):
        self._auto_snapshot_interval = interval_seconds
        self._last_auto_snapshot = time.time()

    def take_snapshot(self, entity_uid: str, snapshot_type: str = "manual") -> TemporalSnapshot:
        entity = self._store.get_latest(entity_uid)
        if not entity:
            raise ValueError(f"Entity not found: {entity_uid}")
        snapshot = TemporalSnapshot(
            entity_uid=entity_uid,
            version=entity.version,
            state=entity.to_dict(),
            snapshot_type=snapshot_type,
        )
        self._save_snapshot(snapshot)
        return snapshot

    def take_snapshot_of_all(self, snapshot_type: str = "checkpoint") -> list[TemporalSnapshot]:
        snapshots: list[TemporalSnapshot] = []
        for info in self._store.list_entities():
            try:
                snap = self.take_snapshot(info["uid"], snapshot_type=snapshot_type)
                snapshots.append(snap)
            except ValueError:
                continue
        return snapshots

    def get_snapshots(self, entity_uid: str) -> list[TemporalSnapshot]:
        snap_dir = self.temporal_snapshots_path / entity_uid
        if not snap_dir.exists():
            return []
        snapshots: list[TemporalSnapshot] = []
        for f in sorted(snap_dir.iterdir(), key=lambda x: x.name):
            if f.suffix == ".json":
                snapshots.append(TemporalSnapshot.from_dict(json.loads(f.read_text())))
        return sorted(snapshots, key=lambda x: x.timestamp)

    def check_auto_snapshot(self) -> list[TemporalSnapshot]:
        if self._auto_snapshot_interval <= 0:
            return []
        now = time.time()
        if now - self._last_auto_snapshot < self._auto_snapshot_interval:
            return []
        self._last_auto_snapshot = now
        return self.take_snapshot_of_all(snapshot_type="automatic")

    def record_metric(self, metric: str, value: float, entity_uid: str = "",
                      tags: dict[str, str] | None = None):
        self.ts_store.record(TimeSeriesPoint(
            timestamp=time.time(),
            value=value,
            metric=metric,
            entity_uid=entity_uid,
            tags=tags or {},
        ))

    def summary(self) -> dict[str, Any]:
        return {
            "entity_count": self._store.count(),
            "metric_count": len(self.ts_store.metric_names()),
            "auto_snapshot_interval": self._auto_snapshot_interval,
            "metrics": self.ts_store.metric_names()[:20],
        }

    def _save_snapshot(self, snapshot: TemporalSnapshot):
        snap_dir = self.temporal_snapshots_path / snapshot.entity_uid
        snap_dir.mkdir(parents=True, exist_ok=True)
        snap_file = snap_dir / f"{snapshot.uid}.json"
        snap_file.write_text(json.dumps(snapshot.to_dict(), indent=2, default=str))
