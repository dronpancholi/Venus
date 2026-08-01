"""
ObservationManager — collects, stores, and queries system observations.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class Observation:
    """A single observation about the system."""
    id: str = ""
    source: str = ""
    metric: str = ""
    value: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservationManager:
    """
    Collects, stores, and queries system observations.

    Observations are time-series data points tagged with metadata.
    Used for monitoring, alerting, analytics, and ML training.
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "observations"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.observations: list[Observation] = []
        self._metrics_index: dict[str, list[int]] = defaultdict(list)  # metric -> indices
        self._source_index: dict[str, list[int]] = defaultdict(list)   # source -> indices
        self._load()

    def record(self, source: str, metric: str, value: float,
                tags: dict[str, str] | None = None,
                metadata: dict[str, Any] | None = None) -> str:
        """Record an observation."""
        obs = Observation(
            id=generate_id("obs", 10),
            source=source, metric=metric, value=value,
            tags=tags or {}, timestamp=time.time(),
            metadata=metadata or {},
        )
        idx = len(self.observations)
        self.observations.append(obs)
        self._metrics_index[metric].append(idx)
        self._source_index[source].append(idx)
        self._save()
        return obs.id

    def query(self, metric: str = "", source: str = "",
               start_time: float = 0, end_time: float = 0,
               limit: int = 100) -> list[Observation]:
        """Query observations with filters."""
        indices = set(range(len(self.observations)))

        if metric:
            indices &= set(self._metrics_index.get(metric, []))
        if source:
            indices &= set(self._source_index.get(source, []))

        results = [self.observations[i] for i in indices]

        if start_time:
            results = [o for o in results if o.timestamp >= start_time]
        if end_time:
            results = [o for o in results if o.timestamp <= end_time]

        return sorted(results, key=lambda o: -o.timestamp)[:limit]

    def latest(self, metric: str, source: str = "",
                default: float = 0.0) -> float:
        """Get the latest value for a metric."""
        results = self.query(metric=metric, source=source, limit=1)
        return results[0].value if results else default

    def time_series(self, metric: str, source: str = "",
                     aggregation: str = "raw") -> list[tuple[float, float]]:
        """Get time series data for a metric."""
        results = self.query(metric=metric, source=source)
        data = [(o.timestamp, o.value) for o in results]
        data.sort(key=lambda x: x[0])

        if aggregation == "avg_1m":
            return self._aggregate_time(data, 60)
        elif aggregation == "avg_5m":
            return self._aggregate_time(data, 300)
        elif aggregation == "avg_1h":
            return self._aggregate_time(data, 3600)
        return data

    def _aggregate_time(self, data: list[tuple[float, float]],
                         window: float) -> list[tuple[float, float]]:
        if not data:
            return []
        aggregated = []
        current_window_start = data[0][0]
        window_values = []
        for ts, val in data:
            if ts - current_window_start > window:
                if window_values:
                    avg = sum(window_values) / len(window_values)
                    aggregated.append((current_window_start, avg))
                current_window_start = ts
                window_values = [val]
            else:
                window_values.append(val)
        if window_values:
            avg = sum(window_values) / len(window_values)
            aggregated.append((current_window_start, avg))
        return aggregated

    def metric_names(self) -> list[str]:
        return sorted(self._metrics_index.keys())

    def source_names(self) -> list[str]:
        return sorted(self._source_index.keys())

    def count(self) -> int:
        return len(self.observations)

    def summary(self) -> dict[str, Any]:
        return {
            "total_observations": len(self.observations),
            "unique_metrics": len(self._metrics_index),
            "unique_sources": len(self._source_index),
            "metrics": self.metric_names()[:20],
            "sources": self.source_names()[:10],
        }

    def _state_path(self) -> Path:
        return self.storage_path / "observations.json"

    def _save(self):
        data = {
            "observations": [o.__dict__ for o in self.observations],
            "metrics_index": dict(self._metrics_index),
            "source_index": dict(self._source_index),
        }
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for od in data.get("observations", []):
                    self.observations.append(Observation(**od))
                self._metrics_index = defaultdict(list, data.get("metrics_index", {}))
                self._source_index = defaultdict(list, data.get("source_index", {}))
            except Exception:
                pass
