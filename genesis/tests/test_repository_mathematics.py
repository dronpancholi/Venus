import math

from genesis.mathematics_v2 import RepositoryMathematics, MetricHistory


def test_record_and_get():
    rm = RepositoryMathematics()
    rm.record("architecture_entropy", 0.5)
    h = rm.get("architecture_entropy")
    assert h is not None
    assert h.current == 0.5


def test_record_many():
    rm = RepositoryMathematics()
    rm.record_many({"a": 1.0, "b": 2.0})
    assert rm.get("a").current == 1.0
    assert rm.get("b").current == 2.0


def test_predefined_metrics():
    rm = RepositoryMathematics()
    assert rm.get("architecture_entropy") is not None
    assert rm.get("dependency_entropy") is not None
    assert rm.get("technical_debt_tensor") is not None
    assert rm.get("evolution_velocity") is not None
    assert rm.get("repository_momentum") is not None
    assert rm.get("engineering_productivity") is not None


def test_compute_entropy_uniform():
    rm = RepositoryMathematics()
    e = rm.compute_entropy([1, 1, 1, 1])
    assert abs(e - 2.0) < 0.001


def test_compute_entropy_concentrated():
    rm = RepositoryMathematics()
    e = rm.compute_entropy([1, 0, 0, 0])
    assert e == 0.0


def test_compute_entropy_empty():
    rm = RepositoryMathematics()
    assert rm.compute_entropy([]) == 0.0


def test_trend_increasing():
    rm = RepositoryMathematics()
    for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
        rm.record("test_metric", v)
    h = rm.get("test_metric")
    assert h.trend == "increasing"


def test_trend_decreasing():
    rm = RepositoryMathematics()
    for v in [0.5, 0.4, 0.3, 0.2, 0.1]:
        rm.record("test_metric2", v)
    h = rm.get("test_metric2")
    assert h.trend == "decreasing"


def test_trend_stable():
    rm = RepositoryMathematics()
    for _ in range(5):
        rm.record("test_metric3", 0.5)
    h = rm.get("test_metric3")
    assert h.trend == "stable"


def test_trend_insufficient_data():
    rm = RepositoryMathematics()
    rm.record("new_metric", 1.0)
    assert rm.get("new_metric").trend == "stable"


def test_confidence():
    rm = RepositoryMathematics()
    rm.record("c_test", 1.0)
    assert rm.get("c_test").confidence < 1.0
    for i in range(20):
        rm.record("c_test", float(i))
    assert rm.get("c_test").confidence == 1.0


def test_compute_trends():
    rm = RepositoryMathematics()
    rm.record("a", 1.0)
    rm.record("a", 2.0)
    trends = rm.compute_trends()
    assert "a" in trends
    assert "current" in trends["a"]
    assert "trend" in trends["a"]
    assert "confidence" in trends["a"]


def test_generate_report():
    rm = RepositoryMathematics()
    rm.record("architecture_entropy", 0.5)
    rm.record("dependency_entropy", 0.3)
    report = rm.generate_report()
    assert report.timestamp > 0
    assert len(report.metrics) > 0
    assert "architecture_entropy" in report.metrics
    assert report.summary


def test_summary():
    rm = RepositoryMathematics()
    rm.record("a", 1.0)
    rm.record("b", 2.0)
    s = rm.summary()
    assert s["metrics_tracked"] >= 2
    assert s["total_samples"] >= 2
    assert "trends" in s


def test_metric_history_defaults():
    h = MetricHistory(name="test")
    assert h.current == 0.0
    assert h.trend == "stable"
    assert h.confidence == 0.0


def test_percent_change():
    rm = RepositoryMathematics()
    rm.record("pct", 100.0)
    rm.record("pct", 110.0)
    trends = rm.compute_trends()
    assert abs(trends["pct"]["percent_change"] - 10.0) < 0.1
