# PROJECT NEXUS PHASE II — Mission 3: OmegaLoop Decomposition

**Date**: 2026-06-30 | **Current Size**: 6,575 lines | **Books**: 18

---

## 1. Current Architecture

OmegaLoop is a single-file class with 18 `_phase_N` methods plus helpers:

```
OmegaLoop (6,575 lines)
├── __init__ + _register_plugins (110 lines)
├── run() — orchestrator (80 lines)
├── _read_atlas_findings() — Atlas feedback (40 lines)
├── Book I:   _phase_01 (220 lines)
├── Book II:  _phase_02 (300 lines)
├── Book III: _phase_03 (350 lines)
├── Book IV:  _phase_04 (280 lines)
├── Book V:   _phase_05 (260 lines)
├── Book VI:  _phase_06 (320 lines)
├── Book VII: _phase_07 (290 lines)
├── Book VIII:_phase_08 (340 lines)
├── Book IX:  _phase_09 (380 lines)
├── Book X:   _phase_10 (310 lines)
├── Book XI:  _phase_11 (290 lines)
├── Book XII: _phase_12 (420 lines)
├── Book XIII:_phase_13 (270 lines)
├── Book XIV: _phase_14 (260 lines)
├── Book XV:  _phase_15 (300 lines)
├── Book XVI: _phase_16 (280 lines)
├── Book XVII:_phase_17 (250 lines)
├── Book XVIII:_phase_18 (240 lines)
├── Helpers: _gather_*, _save_*, _load_*, _report_* (~800 lines)
├── Data: PhaseDeliverable, OmegaMetrics, OmegaReport (~200 lines)
└── Module-level: imports, constants, config (~100 lines)
```

## 2. Responsibility Analysis

### Category A: Core Execution Loop (should be KERNEL)
- `__init__`, `run()`, phase sequencing/dispatch
- Currently ~200 lines

### Category B: Book Implementations (should be BOOKS/)
- Each `_phase_N` method: 240-420 lines
- Mixed concerns: analysis + reporting + filesystem

### Category C: Reporting & Serialization (should be REPORTING/)
- All `_save_phase_N()` calls embedded in book methods
- PhaseDeliverable class
- Report generation logic: ~600 lines across all books

### Category D: Metrics (should be METRICS/)
- OmegaMetrics dataclass
- All metric collection (`_gather_metrics()`, `_compute_*()`)
- ~400 lines

### Category E: Filesystem (should be IO/)
- Path management, directory creation
- JSON read/write, Atlas data loading
- ~200 lines

### Category F: Atlas Integration (should be ATLAS_BRIDGE/)
- `_read_atlas_findings()`
- Atlas to OmegaLoop data flow
- ~40 lines (small but architecturally important)

## 3. Proposed Package Structure

```
genesis/omega_loop/
├── __init__.py              # Re-exports OmegaLoop for backward compat
├── kernel.py                # OmegaLoopKernel — core execution, phase sequencing, shared state
├── books/
│   ├── __init__.py          # Book registry, book_discovery()
│   ├── book_01_09.py        # Books I-IX (digital universe through economics)
│   ├── book_10_18.py        # Books X-XVIII (marketplace through recursive future)
│   └── common.py            # Shared helpers for books
├── reporting.py             # PhaseDeliverable, report generation, aggregation
├── metrics.py               # OmegaMetrics, metric collectors, gauge definitions
├── io.py                    # Filesystem operations, path management, serialization
└── atlas_bridge.py          # Atlas feedback reading, data transformation
```

### Key Design Decisions

**Single-file legacy maintained**: `genesis/omega_loop.py` becomes thin wrapper:
```python
from genesis.omega_loop.kernel import OmegaLoopKernel

class OmegaLoop:
    """Same public API. Delegates to decomposed internals."""
    def __init__(self, *args, **kwargs):
        self._kernel = OmegaLoopKernel(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self._kernel.run(*args, **kwargs)

    @property
    def books(self):
        return self._kernel.books
    # ... etc for each public method/property
```

**Shared state via explicit context object**:
```python
@dataclass
class OmegaContext:
    """Shared mutable state across Books. Replaces self.* pollution."""
    deliverables: dict[int, PhaseDeliverable] = field(default_factory=dict)
    metrics: OmegaMetrics = field(default_factory=OmegaMetrics)
    errors: list[str] = field(default_factory=list)
    atlas_findings: dict | None = None
    plugin_registry: ModulePluginRegistry | None = None
    relationship_engine: RelationshipEngine | None = None
```

**Book abstraction**:
```python
class Book(ABC):
    """Single Book in the OmegaLoop constitution."""
    number: int
    name: str

    @abstractmethod
    def execute(self, ctx: OmegaContext) -> list[PhaseDeliverable]: ...
```

## 4. Migration Plan

| Phase | Change | Effort | Risk |
|-------|--------|--------|------|
| 1 | Extract OmegaMetrics to omega_loop/metrics.py | 0.5d | None |
| 2 | Extract PhaseDeliverable + report logic to omega_loop/reporting.py | 0.5d | None |
| 3 | Extract filesystem helpers to omega_loop/io.py | 0.5d | None |
| 4 | Extract atlas_bridge to omega_loop/atlas_bridge.py | 0.5d | None |
| 5 | Create OmegaContext, extract kernel.py | 1d | Low |
| 6 | Extract Book I-IX to books/book_01_09.py | 2d | Medium (verify each Book) |
| 7 | Extract Book X-XVIII to books/book_10_18.py | 2d | Medium (verify each Book) |
| 8 | Create omega_loop/__init__.py with backward-compat OmegaLoop | 0.5d | None |
| 9 | Full test pass | 0.5d | None |

**Total**: 7.5-8 days | **Risk**: Medium

## 5. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Books reference self.* internal state | HIGH | Books should only access OmegaContext |
| Cross-Book method calls exist | MEDIUM | Audit all cross-Book calls before extraction |
| Platform.py imports OmegaLoop | LOW | Backward-compat wrapper preserves API |
| Lazy imports in omega_loop.py need attention | LOW | Keep lazy imports in kernel, not books |
