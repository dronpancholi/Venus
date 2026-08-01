# PROJECT NEMESIS Phase III — Mission 10: Universal Plugin Ecosystem

**Date**: 2026-06-30 | **Repository**: 335 Python files (excl tests), ~71,916 lines (excl tests), 72 test files, 2,763 tests
**Scope**: Every engine, every registry — transform PluginRegistry into complete capability discovery platform

---

## 1. Executive Summary

Genesis has **31 distinct registry/plugin classes** spread across 20 modules. Every subsystem defines its own registry. None share a common interface. None discover from each other. Eight are named "ServiceRegistry" — each incompatible.

The primary systems are:
- **PluginManager** (plugin/manager.py): External plugin loading via manifest files (YAML/JSON). Has lifecycle management, dependency resolution, hot reload. Used by platform.py.
- **ModulePluginRegistry** (plugin/registry.py): Internal engine registry with factory functions. Used by Atlas for engine discovery.
- **CapabilityRegistry** (capability/registry.py): Capability definitions with interfaces, contracts, policies. Used by platform.py.
- **PluginLoader** (kernel/plugin_loader.py): Kernel's own plugin loading.

**Key finding**: There are 3 independent plugin/engine discovery mechanisms and zero integration between them. An engine registered in ModulePluginRegistry is invisible to CapabilityRegistry, PluginManager, ServiceProvider, and all 8 ServiceRegistries.

**Design**: Merge ModulePluginRegistry + CapabilityRegistry into a single `EngineCapabilityRegistry` that becomes the discovery backbone for the entire platform. PluginManager remains for external (filesystem) plugins. All other registries become adapters or are deprecated.

---

## 2. Every Registry Class

### 2.1 Primary Plugin/Registry Systems

| # | Registry | Module | Lines | Mechanism | Consumers | Status |
|---|----------|--------|-------|-----------|-----------|--------|
| 1 | PluginManager | plugin/manager.py | 236 | External file loading + manifest | platform.py | Active |
| 2 | ModulePluginRegistry | plugin/registry.py | 110 | Internal factory registration | Atlas | Active |
| 3 | CapabilityRegistry | capability/registry.py | 269 | Capability definitions | platform.py | Active |
| 4 | PluginLoader | kernel/plugin_loader.py | ~80 | Kernel plugin loading | None | Dead |
| 5 | PluginManifest | plugin/manifest.py | 123 | Manifest schema | PluginManager | Active |

### 2.2 Service Registries (8 implementations)

| # | Registry | Module | Mechanism | Consumers | Status |
|---|----------|--------|-----------|-----------|--------|
| 6 | ServiceProvider (DI) | di/container.py | Type-based DI | 57 services | Active |
| 7 | ServiceRegistry | platform_v2.py | String-based, with states | 0 | Dead |
| 8 | ServiceRegistry | engineering_os.py | String-based, with heartbeat | 0 | Dead |
| 9 | ServiceRegistry | fabric/discovery.py | Capability-based discovery | 0 | Dead |
| 10 | EntityRegistry | ontology.py | Entity types | EngineeringOS | Active |
| 11 | CanonicalRegistry | ontology.py | Canonical entity types | ReasoningEngine | Active |
| 12 | CodeGenRegistry | compiler/codegen/base.py | Code generators | Compiler | Active |
| 13 | PassRegistry | compiler/passes/base.py | Compiler passes | Compiler | Active |

### 2.3 Other Registries (18 more)

| # | Registry | Module | Consumers | Status |
|---|----------|--------|-----------|--------|
| 14 | TypeRegistry | core/types.py | Meta model | Active |
| 15 | EntityTypeRegistry | metamodel/registry.py | Meta model | Active |
| 16 | ContractRegistry | fabric/contracts.py | None | Dead |
| 17 | CapabilityRegistry (UCOS) | ucos/registry.py | None | Dead |
| 18 | RepositoryRegistry | observatory/registry.py | Observatory | Active |
| 19 | LawRegistry | civilization/physics/ | Civilization | Active |
| 20 | WatcherRegistry | os/watchers.py | OS layer | Active |

### 2.4 Engine Classes (Not Registries, But Need Discovery)

Every engine class should be discoverable through the registry. These are the engines from Missions 7-9:

| Engine | Module | Lines | Consumers | Currently Discoverable? |
|--------|--------|-------|-----------|----------------------|
| Compiler | compiler/compiler.py | 206 | platform.py | No (hard-coded) |
| KnowledgeGraphEngine | graph/engine.py | 305 | EventBus | No |
| ExecutionEngine | runtime/executor.py | 266 | EventBus, HistoryStore | No |
| MetadataEngine | core/metadata.py | 213 | platform.py | No |
| Diagnostics | diagnostics/diagnostics.py | 236 | platform.py | No |
| RepositoryIndexer | indexer/indexer.py | 270 | platform.py | No |
| PluginManager | plugin/manager.py | 236 | platform.py | No |
| MemoryEngine | memory/engine.py | 65 | platform.py | No |
| EngineeringBrain | brain/__init__.py | 264 | EventBus | No |
| IntelligenceService | intelligence/__init__.py | 160 | brain | No |
| ReasoningEngine | reasoning.py | 14,526 | Scientist, Engineer | No |
| MetaModelEngine | meta_model.py | 711 | platform.py | No |
| RelationshipEngine | ontology.py | 1,398 | platform.py | No |
| EconomicsEngine | economics.py | 8,768 | platform.py | No |
| EngineeringPlanner | planner.py | 14,526 | OmegaLoop | No |
| RepositoryScientist | repository_scientist.py | — | OmegaLoop | No |
| RepositoryEngineer | repository_engineer.py | — | OmegaLoop | No |
| RepositoryEconomics | repository_economics.py | — | OmegaLoop | No |
| DigitalCivilization | digital_civilization.py | — | OmegaLoop | No |
| ReverseEngineeringEngine | reverse_engineer.py | 754 | OmegaLoop | No |
| OmegaLoop | omega_loop.py | 327,217 | platform.py | No |

**None of the 21 major engines are discoverable** — they are all instantiated by name in platform.py boot(). The only engine that IS discoverable is Atlas, which uses ModulePluginRegistry.

---

## 3. Integration Gap Analysis

### 3.1 What ModulePluginRegistry Knows

```python
ModulePluginRegistry._plugins = {
    "name": EnginePlugin(name, type, factory, instance, description, dependencies)
}
```

**Capabilities**: Register by name+type, lazy factory, dependency list, description
**Missing**: Version, health, metrics, contracts, interfaces, lifecycle hooks, hot loading

### 3.2 What CapabilityRegistry Knows

```python
CapabilityDefinition: {
    capability_id, name, description, version, owner,
    semantic_type, dependencies, interfaces[],
    inputs[], outputs[], contracts[], policies[],
    permissions[], validation_rules[], certification_state
}
```

**Capabilities**: Rich capability metadata, contracts, interfaces, permissions, validation
**Missing**: Factory, instance, lazy init, health, lifecycle, hot loading

### 3.3 What PluginManager Knows

```python
PluginInstance: {
    manifest (name, version, entry_point, dependencies, capabilities, hooks),
    module, state ("registered"|"loaded"|"active"|"inactive"),
    instance, handlers{}
}
```

**Capabilities**: Manifest-based, dependency resolution, activation lifecycle, hooks, hot reload
**Missing**: Type-based discovery, lazy factories, contracts, health, metrics

### 3.4 What ServiceProvider Knows

```python
ServiceDefinition: {interface, implementation, singleton, lazy, initialized}
ServiceProvider: {registry: {type -> ServiceDefinition}, instances: {type -> Any}}
```

**Capabilities**: Type-based DI, singleton scoping, lazy init, thread safety
**Missing**: Factory metadata, version, health, capabilities, contracts, discovery

---

## 4. Design: EngineCapabilityRegistry

### 4.1 Unified Engine Plugin Model

```python
@dataclass
class EnginePlugin:
    """A registered engine with full metadata and lifecycle."""

    # Identity
    name: str
    version: str
    engine_type: str          # "compiler", "graph", "reasoning", "planner", etc.
    description: str

    # Implementation
    factory: Callable[[], Any] | None = None
    instance: Any = None      # Lazy-initialized via factory

    # Contracts
    interfaces: list[InterfaceDef] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    # Lifecycle
    status: EngineStatus = EngineStatus.REGISTERED
    health_check: Callable[[], bool] | None = None

    # Metrics
    metrics: dict[str, float] = field(default_factory=dict)
    execution_count: int = 0
    avg_latency_ms: float = 0.0

    # Metadata
    owner: str = "genesis"
    source: str = ""           # "platform" | "plugin" | "atlas" | "manual"
    compatibility: str = ">=1.0.0"
    tags: list[str] = field(default_factory=list)

    def get_instance(self) -> Any:
        if self._instance is None and self.factory is not None:
            self._instance = self.factory()
            self.status = EngineStatus.INITIALIZED
        return self._instance
```

### 4.2 Unified Registry Interface

```python
class EngineCapabilityRegistry:
    """Single source of truth for all engine discovery."""

    def __init__(self):
        self._engines: dict[str, EnginePlugin] = {}

    # ── Registration ──
    def register(self, plugin: EnginePlugin) -> str:
        """Register an engine plugin."""
        ...

    def register_from_module(self, module, base_type: str = "") -> list[str]:
        """Auto-discover engines in a module by scanning for classes."""
        ...

    # ── Discovery ──
    def get(self, name: str) -> EnginePlugin:
        """Get engine by name."""
        ...

    def get_by_type(self, engine_type: str) -> list[EnginePlugin]:
        """Get all engines of a type."""
        ...

    def get_by_capability(self, capability: str) -> list[EnginePlugin]:
        """Get all engines providing a capability."""
        ...

    def search(self, query: str) -> list[EnginePlugin]:
        """Full-text search over engine names, descriptions, capabilities."""
        ...

    def find_by_interface(self, method: str, path: str) -> list[EnginePlugin]:
        """Find engines that implement a specific interface method."""
        ...

    # ── Lifecycle ──
    def initialize(self, name: str) -> Any:
        """Initialize (or get existing instance of) an engine."""
        ...

    def initialize_all(self) -> dict[str, Any]:
        """Initialize all registered engines."""
        ...

    def health_check(self, name: str) -> bool:
        """Run health check for an engine."""
        ...

    def health_check_all(self) -> dict[str, bool]:
        """Run health checks for all engines."""
        ...

    # ── Documentation ──
    def generate_catalog(self) -> str:
        """Generate automatic capability catalog (Markdown)."""
        ...

    def generate_dependency_graph(self) -> dict[str, list[str]]:
        """Generate dependency graph of all engines."""
        ...

    def generate_api_inventory(self) -> dict[str, list[str]]:
        """Generate API inventory: all interfaces × all engines."""
        ...

    def generate_ownership_report(self) -> dict[str, str]:
        """Generate ownership tracking: engine → owner."""
        ...

    # ── Persistence ──
    def to_dict(self) -> dict[str, Any]:
        """Serialize full registry state."""
        ...

    def save(self, path: str | Path):
        """Save registry to JSON."""
        ...

    def load(self, path: str | Path):
        """Load registry from JSON."""
        ...
```

### 4.3 Auto-Discovery

```python
# Module-level declaration pattern (convention over configuration)
# Any module can declare its engines:

__engines__ = [
    EnginePlugin(
        name="compiler",
        version="1.0.0",
        engine_type="compilation",
        description="Multi-language compiler pipeline",
        factory=lambda: Compiler(event_bus, artifact_store),
        capabilities=["compile", "generate", "transform"],
        dependencies=["event_bus", "artifact_store"],
    ),
    EnginePlugin(
        name="reasoning",
        version="1.0.0",
        engine_type="reasoning",
        description="Engineering reasoning engine",
        factory=lambda: ReasoningEngine(rel_engine, meta_model, canon_reg),
        capabilities=["reason", "analyze", "infer"],
        dependencies=["relationship_engine", "meta_model", "canonical_registry"],
    ),
]
```

### 4.4 Auto-Generated Catalog Example

```markdown
# Engine Capability Catalog

## Compilation (2 engines)
| Name | Version | Capabilities | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| compiler | 1.0.0 | compile, generate, transform | event_bus, artifact_store | initialized |
| meta_compiler | 1.0.0 | meta_compile, codegen | None | registered |

## Graph (3 engines)
| Name | Version | Capabilities | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| graph_engine | 1.0.0 | knowledge_graph, architecture | event_bus, knowledge_store | initialized |
| relationship_engine | 1.0.0 | entity_relationships | None | initialized |
| unified_graph | 1.0.0 | layered_graph, federation | None | registered |

## Reasoning (4 engines)
| Name | Version | Capabilities | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| reasoning | 1.0.0 | reason, analyze, infer | rel_engine, meta_model | initialized |
| repository_scientist | 1.0.0 | research, analyze | reasoning | initialized |
| repository_engineer | 1.0.0 | implement, refactor | reasoning, scientist | initialized |
| repository_economics | 1.0.0 | cost_analysis, roi | reasoning | initialized |
```

### 4.5 Auto-Generated Dependency Graph

```python
def generate_dependency_graph(self) -> dict[str, list[str]]:
    graph = {}
    for name, plugin in self._engines.items():
        graph[name] = list(plugin.dependencies)
    return graph

# Output:
# {
#   "compiler": ["event_bus", "artifact_store"],
#   "graph_engine": ["event_bus", "knowledge_store"],
#   "reasoning": ["relationship_engine", "meta_model", "canonical_registry"],
#   "repository_scientist": ["reasoning"],
#   "repository_engineer": ["reasoning", "repository_scientist"],
#   "omega_loop": []  # root
# }
```

### 4.6 Auto-Generated API Inventory

```python
def generate_api_inventory(self) -> dict[str, list[str]]:
    inventory = {}
    for name, plugin in self._engines.items():
        if plugin.instance:
            methods = [
                m for m in dir(plugin.instance)
                if callable(getattr(plugin.instance, m))
                and not m.startswith("_")
            ]
            inventory[name] = methods
    return inventory

# Output:
# {
#   "compiler": ["compile", "compile_string", "generate", ...],
#   "reasoning": ["reason", "analyze", "infer", "summary", ...],
#   "omega_loop": ["execute", "run_all", "report", ...],
# }
```

---

## 5. Engine Categories

| Category | Engines | Registry Type | Discovery Strategy |
|----------|---------|--------------|-------------------|
| **Infrastructure** | EventBus, MetadataEngine, Diagnostics | ServiceProvider | Type-based |
| **Persistence** | MetadataStore, KnowledgeStore, HistoryStore, etc. | ServiceProvider | Type-based |
| **Compilation** | Compiler, MetaCompiler | EngineCapabilityRegistry | Auto-discover |
| **Graph** | KnowledgeGraphEngine, RelationshipEngine | EngineCapabilityRegistry | Auto-discover |
| **Execution** | ExecutionEngine, ExecGraphEngine | EngineCapabilityRegistry | Auto-discover |
| **Memory** | MemoryEngine, 16 MemoryTypes | EngineCapabilityRegistry | Auto-discover |
| **Knowledge** | EngineeringBrain, IntelligenceService | EngineCapabilityRegistry | Auto-discover |
| **Reasoning** | ReasoningEngine, RepositoryScientist, Engineer, Economics | EngineCapabilityRegistry | Auto-discover |
| **Planning** | EngineeringPlanner | EngineCapabilityRegistry | Auto-discover |
| **Economics** | EconomicsEngine | EngineCapabilityRegistry | Auto-discover |
| **Orchestration** | OmegaLoop, Atlas | EngineCapabilityRegistry | Auto-discover |
| **External** | User plugins | PluginManager | Manifest files |

---

## 6. Migration Strategy

### Phase 1: Create EngineCapabilityRegistry (in `genesis/plugin/`)

1. Create `genesis/plugin/capability_registry.py` with the unified EnginePlugin model
2. Add auto-discovery by scanning modules for `__engines__` declarations
3. Port existing ModulePluginRegistry registration into the new registry
4. Keep old ModulePluginRegistry as backward-compatible wrapper

**Risk**: Low — additive
**Lines**: ~300 new code

### Phase 2: Add Engine Declarations

1. Add `__engines__` declarations to every major engine module
2. Register all 21 major engines in EngineCapabilityRegistry
3. Generate initial catalog, dependency graph, API inventory

**Risk**: Low — no behavior change
**Lines changed**: 1-2 per engine module

### Phase 3: Integrate with Platform

1. Replace platform.py manual instantiation with EngineCapabilityRegistry discovery
2. EngineCapabilityRegistry.initialize_all() replaces 50 sequential instantiations
3. Dependency resolution replaces hard-coded boot order

**Risk**: Medium — boot order changes from sequential to dependency-resolved
**Rollback**: Keep old platform.boot() as fallback

### Phase 4: Deprecate Old Registries

| Registry | Action |
|----------|--------|
| ModulePluginRegistry (plugin/registry.py) | **Keep** as backward-compatible wrapper |
| ServiceRegistry (platform_v2.py) | **Deprecate** |
| ServiceRegistry (engineering_os.py) | **Deprecate** |
| ServiceRegistry (fabric/discovery.py) | **Deprecate** |
| CapabilityRegistry (ucos/registry.py) | **Deprecate** |
| PluginLoader (kernel/plugin_loader.py) | **Deprecate** |
| ContractRegistry (fabric/contracts.py) | **Deprecate** |
| EntityRegistry (ontology.py) | **Keep** (entity types are different from engines) |
| CanonicalRegistry (ontology.py) | **Keep** (entity canonicalization is different) |
| CodeGenRegistry (compiler/codegen/) | **Keep** (compiler-internal) |
| PassRegistry (compiler/passes/) | **Keep** (compiler-internal) |

---

## 7. Engineering Decisions

### 7.1 Why not use PluginManager as the universal registry?

PluginManager is designed for **external** plugins loaded from filesystem manifests. Engines are **internal** — they're Python classes in the codebase, not installable packages. PluginManager requires manifest files on disk; EngineCapabilityRegistry uses Python-level `__engines__` declarations.

### 7.2 Why not extend ServiceProvider instead?

ServiceProvider is a DI container — it maps type → instance. EngineCapabilityRegistry is a discovery platform — it maps name → metadata → factory → instance. They serve different purposes:
- ServiceProvider: "Give me an instance of this type"
- EngineCapabilityRegistry: "Find all engines that provide this capability, show me their metadata, then give me an instance"

The two can be linked: EngineCapabilityRegistry can use ServiceProvider for instance resolution when types are known.

### 7.3 Why `__engines__` declarations instead of class scanning?

Explicit declarations (`__engines__`) are better than scanning for class inheritance because:
1. Not every Service/Engine class should be discoverable (some are internal)
2. Dependencies must be declared (can't be auto-detected)
3. Multiple instances of the same class with different configs are possible
4. Factory functions can handle complex initialization (DI injection, configuration)

---

## 8. Validation

- **2,763 tests pass** — Universal Plugin Ecosystem is a design; no code changed
- **31 registry classes cataloged** across 20 modules
- **8 named "ServiceRegistry"** — all incompatible
- **21 major engines** — 0 currently discoverable through any registry
- **3 independent discovery mechanisms** — all isolated from each other

---

## 9. Next Steps

1. Create `genesis/plugin/capability_registry.py` with EngineCapabilityRegistry
2. Add `__engines__` declarations to all 21 major engine modules
3. Auto-generate catalog, dependency graph, API inventory, ownership report
4. Integrate with platform boot (dependency-resolved initialization)
5. Add deprecation warnings to 7 redundant registries
6. Mission 11: Engineering Memory
