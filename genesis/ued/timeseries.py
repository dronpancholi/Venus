from __future__ import annotations

import math
import time
from collections import defaultdict
from typing import Any, Callable

from genesis.ued.types import Query, QueryResult
from genesis.utils.identity import generate_id


class TimeSeriesStore:
    """Time-series data store with ingestion, downsampling, and retention."""

    def __init__(self, retention_days: int = 365):
        self._retention_days = retention_days
        self._series: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._tags: dict[str, dict[str, str]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._subscriptions: dict[str, list[Callable]] = defaultdict(list)

    def create_series(self, name: str, tags: dict[str, str] | None = None,
                      metadata: dict[str, Any] | None = None) -> str:
        if name not in self._series:
            self._tags[name] = tags or {}
            self._metadata[name] = metadata or {}
        return name

    def insert(self, series: str, timestamp: float, value: float,
               labels: dict[str, str] | None = None):
        point = {
            "timestamp": timestamp,
            "value": value,
            "labels": labels or {},
        }
        self._series[series].append(point)
        for cb in self._subscriptions.get(series, []):
            try:
                cb(series, point)
            except Exception:
                pass

    def query_range(self, series: str, start: float, end: float) -> list[dict[str, Any]]:
        return [p for p in self._series.get(series, [])
                if start <= p["timestamp"] <= end]

    def last_n(self, series: str, n: int = 1) -> list[dict[str, Any]]:
        points = self._series.get(series, [])
        return points[-n:]

    def aggregate(self, series: str, start: float, end: float,
                  window_secs: float, fn: str = "avg") -> list[dict[str, Any]]:
        points = [p for p in self._series.get(series, [])
                  if start <= p["timestamp"] <= end]
        if not points:
            return []
        buckets: dict[int, list[float]] = defaultdict(list)
        for p in points:
            bucket = int(p["timestamp"] / window_secs) * int(window_secs)
            buckets[bucket].append(p["value"])
        results: list[dict[str, Any]] = []
        for ts in sorted(buckets):
            vals = buckets[ts]
            if fn == "avg":
                v = sum(vals) / len(vals)
            elif fn == "sum":
                v = sum(vals)
            elif fn == "min":
                v = min(vals)
            elif fn == "max":
                v = max(vals)
            elif fn == "count":
                v = len(vals)
            elif fn == "stddev":
                mean = sum(vals) / len(vals)
                v = math.sqrt(sum((x - mean) ** 2 for x in vals) / len(vals))
            else:
                v = sum(vals) / len(vals)
            results.append({"timestamp": float(ts), "value": v, "fn": fn, "count": len(vals)})
        return results

    def downsample(self, series: str, factor: int) -> list[dict[str, Any]]:
        points = self._series.get(series, [])
        if not points:
            return []
        grouped: list[list[dict[str, Any]]] = []
        for i in range(0, len(points), factor):
            group = points[i:i + factor]
            grouped.append(group)
        results: list[dict[str, Any]] = []
        for group in grouped:
            avg = sum(p["value"] for p in group) / len(group)
            ts = group[0]["timestamp"]
            results.append({"timestamp": ts, "value": round(avg, 4), "points": len(group)})
        return results

    def subscribe(self, series: str, callback: Callable):
        self._subscriptions[series].append(callback)

    def list_series(self) -> list[str]:
        return list(self._series.keys())

    def series_count(self) -> int:
        return len(self._series)

    def total_points(self) -> int:
        return sum(len(p) for p in self._series.values())

    def summary(self) -> dict[str, Any]:
        return {
            "series_count": self.series_count(),
            "total_points": self.total_points(),
            "retention_days": self._retention_days,
        }


class EventStore:
    """Append-only event log with subscription and replay."""

    def __init__(self):
        self._events: list[dict[str, Any]] = []
        self._streams: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._subscriptions: dict[str, list[Callable]] = defaultdict(list)
        self._global_subscriptions: list[Callable] = []
        self._next_seq = 0

    def append(self, event_type: str, data: dict[str, Any],
               stream: str | None = None) -> dict[str, Any]:
        self._next_seq += 1
        event = {
            "id": generate_id("evt", 12),
            "seq": self._next_seq,
            "type": event_type,
            "data": data,
            "stream": stream,
            "timestamp": time.time(),
        }
        self._events.append(event)
        if stream:
            self._streams[stream].append(event)
        for cb in self._global_subscriptions:
            try:
                cb(event)
            except Exception:
                pass
        if stream:
            for cb in self._subscriptions.get(stream, []):
                try:
                    cb(event)
                except Exception:
                    pass
        return event

    def replay(self, from_seq: int = 0, stream: str | None = None) -> list[dict[str, Any]]:
        if stream:
            return [e for e in self._streams.get(stream, []) if e["seq"] > from_seq]
        return [e for e in self._events if e["seq"] > from_seq]

    def subscribe(self, stream: str | None = None, callback: Callable | None = None):
        if stream:
            if callback:
                self._subscriptions[stream].append(callback)
        else:
            if callback:
                self._global_subscriptions.append(callback)

    def filter(self, event_type: str | None = None, stream: str | None = None,
               from_seq: int = 0) -> list[dict[str, Any]]:
        results = self.replay(from_seq, stream)
        if event_type:
            results = [e for e in results if e["type"] == event_type]
        return results

    def event_count(self) -> int:
        return len(self._events)

    def stream_count(self) -> int:
        return len(self._streams)

    def last_seq(self) -> int:
        return self._next_seq

    def clear(self):
        self._events.clear()
        self._streams.clear()
        self._next_seq = 0

    def summary(self) -> dict[str, Any]:
        return {
            "total_events": self.event_count(),
            "streams": self.stream_count(),
            "last_seq": self.last_seq(),
        }
