# PROJECT NEXUS PHASE II — Mission 8: Engineering Quality Metrics

**Date**: 2026-06-30

---

## 1. Principles

1. **Real metrics, not synthetic**: Every metric must measure something that affects engineering outcomes
2. **Trendable**: Metrics must persist across runs to show improvement/regression
3. **Actionable**: A metric must suggest what to do next
4. **Minimal**: Prefer 10 meaningful metrics over 100 meaningless ones

## 2. Metric Catalog

### 2.1 Duplication Metrics

| Metric | Formula | Target | Current Baseline |
|--------|---------|--------|------------------|
| duplicate_modules | Count of modules with same capability | 0 | 12 clusters |
| duplicate_lines | Total lines in deprecated modules | 0 | ~2,675 |
| consolidation_progress | Canonical lines / (canonical + deprecated) lines | 1.0 | ~0.80 |
| deprecation_coverage | Modules with DeprecationWarning / total deprecated | 1.0 | 0.7 (7/10) |

### 2.2 Coupling Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| module_instability | efferent / (afferent + efferent) | 0.3-0.7 |
| module_abstractness | abstract classes / total classes | 0.3-0.5 |
| import_fan_in | Count of modules importing this module | < 20 |
| platform_import_count | Number of module-level imports in platform.py | < 20 (currently ~50) |
| circular_dependencies | Count of circular import chains | 0 |

### 2.3 Architecture Health

| Metric | Formula | Target |
|--------|---------|--------|
| layer_violations | Count of layer rule violations | 0 (currently 0) |
| duplicate_abstraction_count | New duplicates created per cycle | 0 |
| edr_coverage | Modules >200 lines with EDR / total >200 line modules | 1.0 |
| canonical_coverage | Modules in CanonicalRegistry / total capabilities | 1.0 |

### 2.4 Test Quality

| Metric | Formula | Target | Baseline |
|--------|---------|--------|----------|
| test_count | Total test functions | > 2,763 | 2,763 |
| test_pass_rate | Passed / (passed + failed) | 1.0 | 1.0 |
| test_to_source_ratio | Test lines / source lines | > 0.3 | ~0.25 |
| untested_modules | Modules without any test | 0 | ~20 |

### 2.5 Documentation

| Metric | Formula | Target |
|--------|---------|--------|
| docstring_coverage | Functions with docstrings / total functions | > 0.5 |
| edr_count | Total Engineering Decision Records | > 10 |
| report_coverage | Capabilities with reports / total capabilities | 1.0 |

### 2.6 Evolution

| Metric | Formula | Target |
|--------|---------|--------|
| consolidation_rate | Lines removed per cycle | > 500 |
| migration_velocity | Modules migrated per cycle | > 2 |
| new_module_quality | New modules with deprecation risk score | < 0.2 |

## 3. Architecture

### MetricCollector

```python
class MetricCollector(ABC):
    """Base class for metric collectors."""

    @abstractmethod
    def collect(self, repo_path: Path) -> dict[str, Any]:
        """Collect metrics. Returns dict of metric_name -> value."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Collector name."""

class DuplicationCollector(MetricCollector):
    name = "duplication"

    def collect(self, repo_path: Path) -> dict[str, Any]:
        warnings_on_import = ... # scan for DeprecationWarning in module files
        deprecated_modules = ... # list of modules with warnings
        return {
            "duplicate_modules": len(deprecated_modules),
            "duplicate_lines": sum(lines(m) for m in deprecated_modules),
            "deprecation_coverage": ...,
        }

class CouplingCollector(MetricCollector):
    name = "coupling"

    def collect(self, repo_path: Path) -> dict[str, Any]:
        # Parse import graph, compute fan-in/fan-out
        return {...}

class ArchitectureCollector(MetricCollector):
    name = "architecture"

    def collect(self, repo_path: Path) -> dict[str, Any]:
        # Check layer violations, circular deps
        return {...}
```

### MetricStore

```python
class MetricStore:
    """Persists metrics across runs for trend analysis."""

    def save_snapshot(self, metrics: dict[str, Any], run_id: str):
        """Save complete metric snapshot."""

    def get_trend(self, metric_name: str, window: int = 10) -> list[tuple[str, float]]:
        """Get last N values of a metric with run IDs."""

    def get_latest(self) -> dict[str, Any]:
        """Get most recent snapshot."""

    def get_delta(self) -> dict[str, tuple[float, float, float]]:
        """Get (current, previous, change) for all metrics."""
```

### Dashboard Generator

```python
class MetricDashboard:
    """Generates HTML dashboard from metric data."""

    def generate(self, store: MetricStore) -> str:
        """Returns HTML string."""
        latest = store.get_latest()
        trends = {m: store.get_trend(m) for m in latest}

        html = "<html><body>"
        html += "<h1>Genesis Engineering Dashboard</h1>"
        html += f"<p>Run ID: {latest['run_id']}</p>"

        for category, metrics in self._categorize(latest).items():
            html += f"<h2>{category}</h2><table>"
            for name, value in metrics.items():
                delta = store.get_delta(name)
                color = "green" if delta[2] >= 0 else "red"
                html += f"<tr><td>{name}</td><td>{value}</td>"
                html += f"<td style='color:{color}'>{delta[2]:+.1f}</td></tr>"
            html += "</table>"

        html += "</body></html>"
        return html
```

## 4. Integration

### Atlas Stage 11 (Benchmarking)
Stage 11 should use MetricCollectors:
```python
# In Atlas Stage 11
collectors = [DuplicationCollector(), CouplingCollector(), ...]
metrics = {}
for c in collectors:
    metrics[c.name] = c.collect(repo_path)
store.save_snapshot(metrics, run_id)
dashboard = MetricDashboard().generate(store)
with open(f"_generated/dashboard_{run_id}.html", "w") as f:
    f.write(dashboard)
```

## 5. Effort

| Component | Effort | Risk |
|-----------|--------|------|
| MetricCollector base + 3 collectors | 1d | None |
| MetricStore (persistence + trends) | 1d | None |
| Dashboard generator | 1d | None |
| Atlas integration | 0.5d | Low |
| CI integration | 0.5d | None |
| **Total** | **4d** | |
