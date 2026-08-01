"""Tests for Resource Management (Mission 176)."""

import time
from unittest.mock import MagicMock

from genesis.resources import (
    ResourceMonitor, ResourceSnapshot, ResourceMetric,
    ResourceCategory, ResourceThresholds,
)


class TestResourceThresholds:
    def test_defaults(self):
        t = ResourceThresholds()
        assert t.get("threads.active") == 100
        assert t.get("nonexistent", 42) == 42

    def test_set(self):
        t = ResourceThresholds()
        t.set("threads.active", 200)
        assert t.get("threads.active") == 200


class TestResourceMetric:
    def test_pct(self):
        m = ResourceMetric(ResourceCategory.THREADS, "test", current=50, limit=100)
        assert m.pct == 50.0

    def test_alert(self):
        m = ResourceMetric(ResourceCategory.THREADS, "test", current=100, limit=100)
        assert m.alert is True

    def test_no_alert(self):
        m = ResourceMetric(ResourceCategory.THREADS, "test", current=50, limit=100)
        assert m.alert is False

    def test_no_limit_no_alert(self):
        m = ResourceMetric(ResourceCategory.THREADS, "test", current=100)
        assert m.alert is False


class TestResourceSnapshot:
    def test_by_category(self):
        metrics = [
            ResourceMetric(ResourceCategory.THREADS, "t1"),
            ResourceMetric(ResourceCategory.THREADS, "t2"),
            ResourceMetric(ResourceCategory.MEMORY, "m1"),
        ]
        snap = ResourceSnapshot(metrics=metrics)
        cats = snap.by_category()
        assert len(cats["threads"]) == 2
        assert len(cats["memory"]) == 1

    def test_alerts(self):
        metrics = [
            ResourceMetric(ResourceCategory.THREADS, "t1", current=100, limit=50),
            ResourceMetric(ResourceCategory.THREADS, "t2", current=10, limit=100),
        ]
        snap = ResourceSnapshot(metrics=metrics)
        assert len(snap.alerts()) == 1


class TestResourceMonitor:
    def test_snapshot_without_kernel(self):
        rm = ResourceMonitor()
        snap = rm.snapshot()
        assert snap.timestamp > 0
        assert len(snap.metrics) > 0

    def test_snapshot_with_kernel(self):
        kernel = MagicMock()
        kernel._threads = []
        engine_mock = MagicMock()
        engine_mock._objects = {"a": 1, "b": 2}
        kernel.engineering = engine_mock
        kernel.event_store = MagicMock()
        kernel.event_store.count.return_value = 42
        kernel.event_store.max_events = 50_000
        kernel.registry = MagicMock()
        kernel.registry.count.return_value = 10
        kernel._contexts = {"s1": 1, "s2": 2}

        rm = ResourceMonitor(kernel=kernel)
        snap = rm.snapshot()
        assert snap.timestamp > 0
        assert len(snap.metrics) > 0

    def test_start_stop(self):
        rm = ResourceMonitor(poll_interval=0.1)
        rm.start()
        assert rm._running is True
        time.sleep(0.15)
        rm.stop()
        assert rm._running is False

    def test_alert_callback(self):
        kernel = MagicMock()
        kernel._threads = []
        kernel.event_store = MagicMock()
        kernel.event_store.count.return_value = 100_000
        kernel.event_store.max_events = 50_000
        kernel.registry = MagicMock()
        kernel.registry.count.return_value = 10
        kernel._contexts = {}

        alerts = []
        rm = ResourceMonitor(kernel=kernel)
        rm.on_alert(lambda m: alerts.append(m.name))
        snap = rm.snapshot()
        assert len(alerts) > 0

    def test_summary(self):
        rm = ResourceMonitor()
        s = rm.summary()
        assert "timestamp" in s
        assert "metrics" in s
        assert "alerts" in s
