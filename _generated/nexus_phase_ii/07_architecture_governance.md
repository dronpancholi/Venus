# PROJECT NEXUS PHASE II — Mission 7: Architecture Governance

**Date**: 2026-06-30

---

## 1. Problem Statement

The root cause of 30+ duplicate modules across Genesis is the absence of governance:

1. **No canonical registry**: Engineers create new abstractions without checking if one exists
2. **No deprecation lifecycle**: Old abstractions persist indefinitely alongside new ones
3. **No architecture review**: Changes affecting multiple files proceed without review
4. **No ownership tracking**: No one is responsible for canonical capabilities

## 2. Governance Rules

### Rule 1: Canonical Registry Check (Before any new abstraction)

```python
# MUST be called before creating any new capability-level abstraction
def check_canonical(name: str, domain: str) -> CanonicalCheckResult:
    """
    Returns matching canonical capabilities if they exist.
    If match found, engineer MUST reuse or formally reject with EDR.
    """
```

- Violation: Creating a new graph implementation without checking graph_v2, graph/, knowledge_graph.py, etc.
- Enforcement: Code review gate + automated pre-commit check

### Rule 2: Deprecation Lifecycle

```
ACTIVE ──→ DEPRECATED ──→ LEGACY ──→ REMOVED
  │            │              │           │
  │        warnings         no imports   deleted
  │        still usable     source kept
  │        new code         no new
  │        discouraged      consumers

  ─── 2 cycles minimum ─── 1 cycle min ──
```

- ACTIVE: Default state for all new code
- DEPRECATED: Add DeprecationWarning, document replacement
- LEGACY: Move to _legacy/ directory, no imports from non-legacy code
- REMOVED: Delete from repository

### Rule 3: Engineering Decision Record (EDR) Threshold

An EDR is REQUIRED when:
- Creating a module > 200 lines (new file)
- Creating an abstraction that duplicates existing capability
- Changing an API consumed by 3+ modules
- Removing/changing a public function exported from __init__.py
- Any change affecting the boot sequence (platform.py, omega_loop.py)

### Rule 4: Architecture Review Threshold

Architecture review (by AutonomousReviewer or peer) REQUIRED when:
- Change affects 5+ files
- Change creates new dependency between packages
- Change modifies layer boundaries (L1/L2/L3/L4)
- Change adds new external dependency

## 3. CanonicalRegistry

```python
class CanonicalRegistry:
    """Single source of truth for canonical capabilities."""

    def __init__(self):
        self._capabilities: dict[str, CanonicalCapability] = {}

    def register(self, name: str, module_path: str, domain: str,
                 description: str, owner: str = "unowned"):
        self._capabilities[name] = CanonicalCapability(
            name=name, module_path=module_path, domain=domain,
            description=description, owner=owner,
            status=CapabilityStatus.ACTIVE, registered_at=timestamp(),
        )

    def find(self, domain: str | None = None,
             name: str | None = None) -> list[CanonicalCapability]:
        """Search for existing capabilities."""

    def deprecate(self, name: str, replacement: str, reason: str):
        cap = self._capabilities[name]
        cap.status = CapabilityStatus.DEPRECATED
        cap.replacement = replacement
        cap.deprecated_at = timestamp()

    def summary(self) -> dict:
        """Count by status, domain, owner."""
```

### Initial Registration

```python
registry = CanonicalRegistry()
registry.register("Scientist", "genesis.repository_scientist", "scientific_method",
                  "Repository experimentation and scientific method automation")
registry.register("Civilization", "genesis.digital_civilization", "civilization",
                  "Digital civilization with institutes, contracts, reputation")
registry.register("Evolution", "genesis.evolution_v4", "evolution",
                  "Self-evolution with Monte Carlo simulation")
registry.register("Simulation", "genesis.simulator_v2", "simulation",
                  "Multi-domain simulation engine")
registry.register("Ontology", "genesis.ontology", "ontology",
                  "Universal entity model and relationship engine")
registry.register("Reasoning", "genesis.reasoning", "reasoning",
                  "Engineering reasoning and query engine")
registry.register("MetaModel", "genesis.meta_model", "metamodel",
                  "Meta-model engine and type registration")
registry.register("PluginRegistry", "genesis.plugin.registry", "plugin",
                  "ModulePluginRegistry for engine discovery")
```

## 4. DeprecationManager

```python
class DeprecationManager:
    """Manages lifecycle transitions and migration tracking."""

    def __init__(self, registry: CanonicalRegistry):
        self._registry = registry
        self._migrations: dict[str, MigrationRecord] = {}

    def mark_deprecated(self, name: str, replacement: str, reason: str):
        self._registry.deprecate(name, replacement, reason)
        self._migrations[name] = MigrationRecord(
            from_module=name, to_module=replacement,
            status=MigrationStatus.PLANNED, reason=reason,
        )

    def track_import(self, module: str, importer: str):
        """Track who imports deprecated modules."""
        ...

    def get_migration_report(self) -> str:
        """Generate migration status report."""
```

## 5. Enforcement Mechanisms

### Pre-commit Hook (future)
```
1. Check changed files against CanonicalRegistry
2. If new file > 200 lines and no EDR → WARNING
3. If file imports deprecated module → WARNING with replacement suggestion
4. If layer violation detected → ERROR
```

### CI Pipeline (future)
```
1. Run `python -W error::DeprecationWarning` to turn warnings into errors
2. Fail build if any test imports deprecated module directly
3. Generate governance report artifact
```

### Autonomous Reviewer (existing)
The AutonomousReviewer in civilization/review/ already performs architecture reviews. Extend to check these rules.

## 6. Effort

| Component | Effort | Risk |
|-----------|--------|------|
| CanonicalRegistry + initial registration | 1d | None |
| DeprecationManager | 1d | Low |
| Pre-commit hook | 1d | Low |
| CI integration | 0.5d | None |
| Migrate existing EDRs to registry | 0.5d | None |
| **Total** | **4d** | |
