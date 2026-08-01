"""Tests for UCOS CapabilityMetrics."""

import pytest
from genesis.ucos.capability import CapabilityDefinition, CapabilityCategory
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.metrics import CapabilityMetrics


@pytest.fixture
def metrics():
    reg = CapabilityRegistry()
    for i in range(5):
        cat = CapabilityCategory.STORAGE if i % 2 == 0 else CapabilityCategory.KNOWLEDGE
        reg.register(CapabilityDefinition(id=f"met_{i}", name=f"Cap{i}", category=cat))
    m = CapabilityMetrics(reg)
    return reg, m


def test_increment_counter(metrics):
    reg, m = metrics
    m.increment("test.counter")
    m.increment("test.counter")
    report = m.report()
    assert report["counters"]["test.counter"] == 2


def test_counter_with_tags(metrics):
    reg, m = metrics
    m.increment("test.counter", tags={"env": "test"})
    m.increment("test.counter", tags={"env": "test"})
    report = m.report()
    assert sum(v for k, v in report["counters"].items() if k.startswith("test.counter")) == 2


def test_gauge(metrics):
    reg, m = metrics
    m.gauge("test.gauge", 42.0)
    m.gauge("test.gauge", 43.0)
    report = m.report()
    assert "test.gauge" in report["gauges"]


def test_observe_histogram(metrics):
    reg, m = metrics
    for v in [1, 2, 3, 4, 5]:
        m.observe("test.latency", v)
    summary = m.histogram_summary("test.latency")
    assert summary is not None
    assert summary["count"] == 5
    assert summary["min"] == 1.0
    assert summary["max"] == 5.0
    assert summary["mean"] == 3.0


def test_histogram_with_tags(metrics):
    reg, m = metrics
    m.observe("api.latency", 5.0, {"endpoint": "/test"})
    summary = m.histogram_summary("api.latency")
    assert summary is not None
    assert summary["count"] == 1


def test_histogram_percentiles(metrics):
    reg, m = metrics
    for v in range(1, 101):
        m.observe("latency", float(v))
    summary = m.histogram_summary("latency")
    assert summary["p50"] >= 45 and summary["p50"] <= 55
    assert summary["p90"] >= 85 and summary["p90"] <= 95


def test_snapshot_state(metrics):
    reg, m = metrics
    snapshot = m.snapshot_state()
    assert snapshot["total"] == 5
    assert "storage" in snapshot["by_category"]
    assert "knowledge" in snapshot["by_category"]
    assert snapshot["avg_health"] > 0


def test_snapshot_rate(metrics):
    reg, m = metrics
    for _ in range(10):
        m.increment("rate.test")
    rate = m.snapshot_rate()
    assert rate >= 0


def test_report_structure(metrics):
    reg, m = metrics
    report = m.report()
    assert "counters" in report
    assert "gauges" in report
    assert "snapshots" in report


def test_histogram_missing(metrics):
    reg, m = metrics
    assert m.histogram_summary("nonexistent") is None
