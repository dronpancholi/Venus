# PROJECT NEXUS PHASE II — Mission 4: Platform Reconstruction

**Date**: 2026-06-30 | **Current**: ~747 lines, 50+ imports, ~44 active service attributes

---

## 1. Current Architecture Anti-Patterns

### Problem 1: God Constructor
platform.py __init__ declares ~49 service attributes. Impossible to distinguish mandatory vs optional infrastructure.

### Problem 2: Import Typhoon
50+ import lines at module level. Every import loads at import-time, even services unused in a given run.

### Problem 3: No Lazy Loading
~44 services eagerly instantiated during boot(). Most are never called after initialization. boot() is slow and tightly coupled.

### Problem 4: Mixed Generations
Services from GENESIS-VIII through GENESIS-XIII all initialized sequentially. No lifecycle tiers.

### Problem 5: Self Import
platform.py imports OmegaLoop, which imports other things. Platform and OmegaLoop are mutually dependent but not obviously so.

## 2. Proposed Architecture: Lazy Service Registry

### Core Registry

```python
@dataclass
class ServiceSpec:
    name: str
    factory: Callable[[], Service]
    lazy: bool = True          # False = created at boot()
    singleton: bool = True      # Only one instance
    dependencies: list[str] = field(default_factory=list)
    _instance: Any = None       # Created on first get()

class ServiceRegistry:
    """Central registry with lazy loading and dependency ordering."""

    def __init__(self):
        self._specs: dict[str, ServiceSpec] = {}
        self._booted = False

    def register(self, name: str, factory: Callable, *, lazy=True, deps=None):
        self._specs[name] = ServiceSpec(name=name, factory=factory, lazy=lazy, dependencies=deps or [])

    def get(self, name: str) -> Any:
        spec = self._specs[name]
        if spec._instance is None:
            for dep in spec.dependencies:
                self.get(dep)  # ensure dependencies are loaded
            spec._instance = spec.factory()
        return spec._instance

    def initialize(self):
        """Eager-init all non-lazy services in dependency order."""
        for name, spec in self._specs.items():
            if not spec.lazy:
                self.get(name)
        self._booted = True

    @property
    def services(self) -> dict[str, bool]:
        return {n: s._instance is not None for n, s in self._specs.items()}
```

### Platform Class

```python
class VenusPlatform:
    """Unified platform with lazy service discovery."""

    def __init__(self, config: PlatformConfig | None = None):
        self.config = config or global_config
        self.registry = ServiceRegistry()
        self._booted = False
        self._register_all()

    def _register_all(self):
        # Tier 1: Infrastructure (non-lazy, created at boot)
        self.registry.register("event_bus", lambda: EventBus(), lazy=False)
        self.registry.register("metadata_store", lambda: MetadataStore(...), lazy=False)
        self.registry.register("knowledge_store", lambda: KnowledgeStore(...), lazy=False)
        # ... other infrastructure stores

        # Tier 2: Domain services (lazy, created on first access)
        self.registry.register("brain", lambda: EngineeringBrain(...), deps=["event_bus"])
        self.registry.register("reasoning", lambda: ReasoningEngine(...), deps=["event_bus", "brain"])
        self.registry.register("planner", lambda: EngineeringPlanner(...), deps=["reasoning"])

    def boot(self) -> VenusPlatform:
        self.registry.initialize()
        self._booted = True
        return self

    def get(self, name: str) -> Any:
        """Public accessor — preferred over direct attribute access."""
        return self.registry.get(name)

    def summary(self) -> dict:
        return {
            "booted": self._booted,
            "services": self.registry.services,
        }
```

## 3. Migration Strategy

### Phase 1: Side-by-Side (1-2 days)
- Create genesis/platform/registry.py with ServiceRegistry
- platform.py creates both old attributes AND new registry
- No behavior change, assertion: same services created

### Phase 2: Registry Primary (1-2 days)
- boot() populates registry instead of self.*
- self.* attributes become property accessors delegating to registry
- Backward-compat maintained for all existing consumers

### Phase 3: True Lazy Loading (2-3 days)
- Most domain services marked lazy=True
- Only infrastructure services created at boot
- Measurable boot time improvement

### Phase 4: Deprecate Direct Attribute Access (1-2 days)
- Add DeprecationWarning on self.* properties in platform.py
- Consumers migrate to platform.get("name")
- Eventual goal: remove properties entirely

## 4. Effort & Risk

| Phase | Lines Changed | Risk | Value |
|-------|-------------|------|-------|
| 1 | +200 | None | Architectural clarity |
| 2 | +100 / -50 | Low | Cleaner API |
| 3 | +50 / -100 | Medium | Faster boot |
| 4 | +30 / -300 | Medium | Clean public API |

## 5. Compatibility

- `platform.service_name` still works (properties delegate to registry)
- `platform.get("service_name")` also works (preferred)
- All existing tests pass without changes
- Migration can proceed incrementally
