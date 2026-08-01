"""Tests for Performance Engineering (Mission 177)."""

import time
from unittest.mock import MagicMock

from genesis.performance import PerformanceMonitor, Benchmark, BenchmarkSummary


class TestBenchmark:
    def test_default_timestamp(self):
        b = Benchmark(name="test")
        assert b.timestamp > 0

    def test_fields(self):
        b = Benchmark(name="op", duration_ms=42.5, tags=["fast"])
        assert b.name == "op"
        assert b.duration_ms == 42.5


class TestBenchmarkSummary:
    def test_empty(self):
        s = BenchmarkSummary.from_samples("empty", [])
        assert s.count == 0

    def test_computes_percentiles(self):
        samples = [Benchmark(name="x", duration_ms=i * 10) for i in range(1, 101)]
        s = BenchmarkSummary.from_samples("x", samples)
        assert s.count == 100
        assert s.min_ms == 10.0
        assert s.max_ms == 1000.0
        assert s.p50_ms == 510.0
        assert s.p95_ms == 960.0
        assert s.p99_ms == 1000.0


class TestPerformanceMonitor:
    def test_measure(self):
        pm = PerformanceMonitor()
        result = pm.measure("add", lambda a, b: a + b, 2, 3)
        assert result == 5
        summary = pm.summary("add")
        assert "add" in summary
        assert summary["add"].count == 1

    def test_record(self):
        pm = PerformanceMonitor()
        pm.record("op", 10.5)
        pm.record("op", 20.3)
        s = pm.summary("op")["op"]
        assert s.count == 2
        assert 10.0 <= s.min_ms <= 11.0
        assert 20.0 <= s.max_ms <= 21.0

    def test_detect_regressions(self):
        pm = PerformanceMonitor()
        pm.record("op", 100.0)
        pm.record("op", 200.0)
        baseline = pm.summary()
        pm.record("op", 500.0)
        pm.record("op", 600.0)
        regressions = pm.detect_regressions(baseline, threshold_pct=10)
        assert len(regressions) >= 1
        assert regressions[0]["current_avg_ms"] > regressions[0]["previous_avg_ms"]

    def test_slow_operation_emits_event(self):
        kernel = MagicMock()
        pm = PerformanceMonitor(kernel=kernel, slow_threshold_ms=0.0)
        pm.measure("slow_op", time.sleep, 0.01)
        assert kernel.emit.called

    def test_instrument_decorator(self):
        pm = PerformanceMonitor()
        @pm.instrument("decorated")
        def add(a, b):
            return a + b
        assert add(2, 3) == 5
        assert "decorated" in pm.summary()

    def test_summary_all(self):
        pm = PerformanceMonitor()
        pm.record("a", 10)
        pm.record("b", 20)
        all_s = pm.summary()
        assert len(all_s) == 2
