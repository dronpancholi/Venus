# GENESIS-II ARCHITECTURE SPECIFICATION

**Version**: 2.0.0-draft  
**Status**: Implementation Blueprint — DO NOT CODE YET  
**Predecessor**: Genesis-I (v1.0.0, 44 files, 5,082 lines)  
**Audit Ref**: AUDIT.md (score 6.5/10, 15 smells, 9 risks)  
**DNA Ref**: DNA.md (10 constitutional laws, 10 anti-laws, 10 first principles)

---

## TABLE OF CONTENTS

1. [Target Architecture](#1-target-architecture)
2. [Module Decomposition](#2-module-decomposition)
3. [Dependency Inversion Plan](#3-dependency-inversion-plan)
4. [Graph Unification Strategy](#4-graph-unification-strategy)
5. [Persistence Architecture](#5-persistence-architecture)
6. [Execution Model](#6-execution-model)
7. [Plugin Architecture Evolution](#7-plugin-architecture-evolution)
8. [API Architecture](#8-api-architecture)
9. [Migration Strategy](#9-migration-strategy)
10. [Risk Analysis](#10-risk-analysis)
11. [Implementation Phases](#11-implementation-phases)
12. [Acceptance Criteria](#12-acceptance-criteria)
13. [Architecture Decision Records](#13-architecture-decision-records)

---

## 1. TARGET ARCHITECTURE

### 1.1 High-Level View

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONSUMER LAYER                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │  CLI     │  │  Studio  │  │  HTTP    │  │ External          │   │
│  │  (venus) │  │  Backend │  │  API     │  │ Integrations      │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬──────────┘   │
│       │              │             │                  │              │
├───────┴──────────────┴─────────────┴──────────────────┴──────────────┤
│                     APPLICATION LAYER                                │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                    DEPENDENCY INJECTION CONTAINER            │     │
│  │  (ServiceProvider — single source of truth for all services) │     │
│  └─────────────────────────────────────────────────────────────┘     │
│       │              │             │                  │              │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────────┴────────┐     │
│  │ Compiler │  │Validation│  │  Plugin  │  │   Execution     │     │
│  │ Pipeline │  │ Engine   │  │  Manager │  │   Engine        │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬────────┘     │
│       │              │             │                  │              │
├───────┴──────────────┴─────────────┴──────────────────┴──────────────┤
│                     KNOWLEDGE LAYER                                  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │               UNIFIED GRAPH ENGINE (UGE)                     │     │
│  │  Merges UIRGraph + KnowledgeGraphEngine into ONE abstraction │     │
│  │  with shared node/type indices, unified export, single       │     │
│  │  lifecycle, and persistence backing.                         │     │
│  └─────────────────────────────────────────────────────────────┘     │
│       │                                                            │
│  ┌────┴─────────────────────────────────────────────────────────┐   │
│  │                    PERSISTENCE LAYER                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │   │
│  │  │  SQLite  │  │  JSON    │  │  Neo4j   │  │  Config     │  │   │
│  │  │ Metadata │  │ Checkpoint│  │ Export   │  │  File       │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
├──────────────────────────────────────────────────────────────────────┤
│                     FOUNDATION LAYER                                  │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ BaseEntity│  │   UIR   │  │  Type    │  │  Metadata│            │
│  │ Hierarchy │  │  (core) │  │  Registry│  │  Engine  │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                            │
│  │ Utility  │  │   DI     │  │  Config  │                            │
│  │ Graph    │  │ Container│  │  Manager │                            │
│  │ Algorithms│  └──────────┘  └──────────┘                            │
│  └──────────┘                                                         │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Architectural Changes from Genesis-I

| Aspect | Genesis-I | Genesis-II |
|--------|-----------|------------|
| Service wiring | Global singletons, manual instantiation | Dependency injection container |
| Graph model | UIRGraph + KnowledgeGraphEngine (parallel) | Unified Graph Engine (UGE) with consistent indices |
| Topological sort | 3 implementations, 2 cycle-detection | 1 shared utility (`genesis/utils/graph_algorithms.py`) |
| Persistence | In-memory only, JSON save/load ad-hoc | SQLite for metadata, JSON for graph checkpoints, unified repository pattern |
| API | Router abstraction only, no server | FastAPI-based HTTP server with registered handlers |
| DI pattern | `type_registry = TypeRegistry()` at module level | `ServiceProvider` with lazy initialization |
| Schema generation | Empty schemas (no value) | Type-derived schemas from TypeRegistry + AST |
| Plugin sandbox | Class exists, never enforced | `__import__` hook enforced at module load |
| Diagnostics | Creates own empty graph | Receives shared graph from container |
| Code duplication | Boilerplate to_dict/from_dict across >7 classes | Mixin/protocol for serialization |
| UUID generation | 3 different truncation lengths | Single utility function |
| Event model | Not implemented | Event bus foundation (pub/sub) |
| Configuration | `PlatformConfig` never loaded from file | `ConfigManager` with file-based, env-var, and default-chain resolution |

### 1.3 Architectural Invariants (Preserved from Genesis-I)

These are correct and must remain unchanged:

1. **UIR Law** (DNA L1): Every transformation passes through UIR.
2. **Entity Law** (DNA L2): Everything is a BaseEntity subclass.
3. **Graph Addressability Law** (DNA L3): Every entity is addressable via node ID.
4. **Deterministic Compilation Law** (DNA L4): Same input → same output.
5. **Typed Knowledge Law** (DNA L5): Every knowledge unit has a semantic type.
6. **Observable Execution Law** (DNA L6): Every execution produces results.
7. **Capability Contract Law** (DNA L8): Every capability has declared interfaces/contracts.
8. **Extension Registration Law** (DNA L10): All extensions are registered, not imported.
9. **BaseEntity inheritance chain**: Single inheritance with `semantic_type`.
10. **DAG-based execution**: Topological sort of workflows is correct.

### 1.4 Architecture Quality Targets

| Dimension | Genesis-I Score | Genesis-II Target |
|-----------|----------------|-------------------|
| Core Abstractions | 8/10 | 9/10 |
| Module Cohesion | 7/10 | 9/10 |
| Coupling | 5/10 | 9/10 |
| Scalability | 3/10 | 6/10 |
| Error Handling | 6/10 | 8/10 |
| Test Coverage | 7/10 | 9/10 |
| Documentation | 4/10 | 7/10 |
| Extensibility | 8/10 | 9/10 |
| Production Readiness | 2/10 | 6/10 |
| Conceptual Integrity | 7/10 | 9/10 |
| **Overall** | **6.5/10** | **8.5/10** |

---

## 2. MODULE DECOMPOSITION

### 2.1 Genesis-II Module Map

```
genesis/
├── core/                  # Foundation — MINIMAL changes from Genesis-I
│   ├── base.py            # BaseEntity, BaseCapability, BaseArtifact
│   ├── uir.py             # UIRNode, UIREdge, UIRGraph + subclasses
│   ├── types.py           # SemanticType, TypeRegistry
│   ├── metadata.py         # MetadataRecord, MetadataEngine
│   └── exceptions.py       # All exceptions
│
├── di/                    # NEW — Dependency Injection Container
│   ├── container.py        # ServiceProvider — service factory + lifecycle
│   └── interfaces.py       # Protocol definitions for all injectable services
│
├── utils/                 # NEW — Shared Utilities
│   ├── graph_algorithms.py # Single top_sort, find_cycles, subgraph
│   ├── serialization.py    # Serializable protocol/mixin
│   └── identity.py         # Unified UUID generation
│
├── compiler/              # REFINED — Same pipeline, improved passes
│   ├── ast.py              # AST, ASTNode
│   ├── parser.py           # Multi-format parser
│   ├── uir_builder.py      # AST → UIR
│   ├── compiler.py         # Main orchestrator
│   ├── passes/             # Compiler passes
│   │   ├── base.py         # CompilerPass, PassRegistry
│   │   └── optimization.py # 3+ optimization passes
│   └── codegen/            # Code generators
│       ├── base.py          # CodeGenerator, CodeGenRegistry
│       ├── markdown_gen.py  # MarkdownGenerator
│       ├── schema_gen.py    # SchemaGenerator (REWRITTEN)
│       └── graph_gen.py     # GraphGenerator
│
├── graph/                 # REWRITTEN — Unified Graph Engine
│   └── engine.py           # UnifiedGraphEngine (UGE) replaces both UIRGraph and KnowledgeGraphEngine
│
├── persistence/           # NEW — Persistence Layer
│   ├── repository.py       # Abstract repository pattern
│   ├── sqlite_store.py     # SQLite-backed metadata/graph store
│   ├── json_store.py       # JSON checkpoint store
│   └── config_store.py     # Configuration file management
│
├── plugin/                # ENHANCED — Sandbox enforced
│   ├── manifest.py         # PluginManifest
│   ├── manager.py          # PluginManager (sandbox hook added)
│   └── sandbox.py          # Sandbox with __import__ hook enforcement
│
├── capability/            # UNCHANGED — Capability Registry
│   └── registry.py         # CapabilityDefinition, CapabilityRegistry
│
├── validation/            # UNCHANGED — Validation Engine
│   ├── engine.py
│   └── validators/         # schema.py, naming.py, structural.py
│
├── indexer/               # UNCHANGED — Repository Indexer
│   └── indexer.py
│
├── runtime/               # ENHANCED — Uses shared graph_algorithms
│   └── executor.py         # Task, Workflow, ExecutionEngine
│
├── api/                   # REWRITTEN — HTTP Server Integration
│   ├── router.py           # APIRouter (unchanged routing logic)
│   ├── server.py           # FastAPI HTTP server (NEW)
│   └── handlers.py         # Handler implementations for all 34 routes (NEW)
│
├── cli/                   # REFINED — Shared instances via DI
│   └── commands.py         # CLI commands
│
├── studio/                # REFINED — Uses DI container
│   └── backend.py          # StudioBackend
│
├── diagnostics/           # REFINED — Shared graph from DI
│   └── diagnostics.py      # Diagnostics engine
│
├── integration/           # UNCHANGED — Project 31A
│   └── project31a.py
│
├── config/                # REWRITTEN — Config Manager
│   ├── settings.py         # PlatformConfig (unchanged model)
│   └── manager.py          # ConfigManager with file/env/default chain (NEW)
│
├── events/                # NEW — Event Bus Foundation
│   └── bus.py              # Simple pub/sub event bus
│
├── tests/                 # EXPANDED — +50% coverage
│   ├── test_platform.py    # Existing + expanded tests
│   └── test_integration.py # Integration tests (NEW)
│
└── __main__.py            # Entry point (uses DI container)
```

### 2.2 Module Dependency Rules (Strict)

```
                     ┌──────────┐
                     │   di/    │  ← no dependencies on any module
                     └──────────┘
                          │
                     ┌────▼────┐
                     │ config/ │  ← no dependencies
                     └────┬────┘
                          │
                     ┌────▼────┐
                     │  core/  │  ← no dependencies except config
                     └────┬────┘
                          │
              ┌───────────┼────────────────┐
              │           │                │
         ┌────▼───┐ ┌────▼───┐       ┌────▼────┐
         │ utils/ │ │persist/│       │ graph/  │
         └────┬───┘ └────┬───┘       └────┬────┘
              │           │                │
              └───────────┼────────────────┘
                          │
              ┌───────────┼──────────────────────────┐
              │           │                          │
         ┌────▼───┐ ┌────▼────┐              ┌──────▼──────┐
         │compiler│ │validation│              │   plugin/   │
         └────┬───┘ └────┬────┘              └──────┬──────┘
              │           │                          │
              └───────────┼──────────────────────────┘
                          │
              ┌───────────┼──────────────────────────┐
              │           │                          │
         ┌────▼───┐ ┌────▼────┐              ┌──────▼──────┐
         │runtime/│ │capability│              │   indexer/  │
         └────┬───┘ └────┬────┘              └──────┬──────┘
              │           │                          │
              └───────────┼──────────────────────────┘
                          │
              ┌───────────┼──────────────────────────┐
              │           │                          │
         ┌────▼───┐ ┌────▼────┐              ┌──────▼──────┐
         │  api/  │ │  cli/   │              │  studio/    │
         └────────┘ └─────────┘              └─────────────┘
```

**Rule**: `cli/`, `api/`, and `studio/` may import any module. All other modules import ONLY from:
- `core/` (foundation)
- `utils/` (shared utilities)
- `di/` (DI container interfaces)
- `persistence/` (repository interfaces)
- `events/` (event bus interfaces)

**No module may import from `cli/`, `api/`, or `studio/`.** This invariant is preserved.

---

## 3. DEPENDENCY INVERSION PLAN

### 3.1 Problem Statement

Genesis-I has 3 global singletons:

```
type_registry = TypeRegistry()           # core/types.py:135
capability_registry = CapabilityRegistry()  # capability/registry.py:189
config = PlatformConfig()                 # config/settings.py:44
```

Additionally, `CLI`, `StudioBackend`, `Project31AIntegration`, and `Diagnostics` each create their own `Compiler`, `ValidationEngine`, and `KnowledgeGraphEngine` instances — leading to multiple independent graph states.

### 3.2 Solution: ServiceProvider

A single `ServiceProvider` class in `genesis/di/container.py` that:

1. Registers all platform services by interface protocol
2. Provides lazy initialization (services created on first access)
3. Supports lifecycle hooks (init → start → stop)
4. Enforces singleton scope by default (one instance per service)
5. Is itself injectable (for testing, provide mock implementations)

```python
class ServiceProvider:
    def __init__(self):
        self._registry: dict[str, ServiceDefinition] = {}
        self._instances: dict[str, Any] = {}
    
    def register(self, interface: type, implementation: type, 
                 singleton: bool = True, lazy: bool = True):
        ...
    
    def get(self, interface: type) -> Any:
        ...
    
    def register_instance(self, interface: type, instance: Any):
        """For testing — inject mocks directly."""
        ...
    
    def initialize_all(self):
        """Eager init for all registered services."""
        ...
    
    def shutdown(self):
        """Lifecycle shutdown hook."""
        ...
```

### 3.3 Service Interfaces

Defined in `genesis/di/interfaces.py`:

```python
# Each service is defined as a Protocol to enable loose coupling

class CompilerService(Protocol):
    def compile(self, source_path: str | Path) -> CompilationUnit: ...
    def compile_string(self, content: str, fmt: str, source_name: str) -> CompilationUnit: ...
    def generate(self, cu: CompilationUnit, output_dir: str | Path) -> dict[str, list[Path]]: ...

class ValidationService(Protocol):
    def validate(self, target: Any, categories: list[str] | None = None) -> list[ValidationResult]: ...
    def summary(self, results: list[ValidationResult]) -> dict[str, Any]: ...

class GraphService(Protocol):
    def add_node(self, node_id: str, label: str = "", node_type: str = "knowledge_node", **attrs) -> UIRNode: ...
    def add_edge(self, source: str, target: str, edge_type: str = "references", **attrs) -> UIREdge: ...
    def find_nodes(self, node_type: str | None = None, label_contains: str = "") -> list[UIRNode]: ...
    def summary(self) -> dict[str, Any]: ...

class ExecutionService(Protocol): ...
class PluginService(Protocol): ...
class CapabilityService(Protocol): ...
class MetadataService(Protocol): ...
class DiagnosticsService(Protocol): ...
class ConfigService(Protocol): ...
class EventBus(Protocol): ...
```

### 3.4 Service Registration Map

| Interface | Implementation | Singleton | Depends On |
|-----------|---------------|-----------|------------|
| `ConfigService` | `ConfigManager` | Yes | — |
| `EventBus` | `EventBusImpl` | Yes | — |
| `GraphService` | `UnifiedGraphEngine` | Yes | ConfigService |
| `MetadataService` | `MetadataEngine` | Yes | PersistenceService |
| `CompilerService` | `Compiler` | Yes | ConfigService, GraphService |
| `ValidationService` | `ValidationEngine` | Yes | — |
| `PluginService` | `PluginManager` | Yes | ConfigService |
| `CapabilityService` | `CapabilityRegistry` | Yes | — |
| `ExecutionService` | `ExecutionEngine` | Yes | GraphService, EventBus |
| `DiagnosticsService` | `Diagnostics` | Yes | GraphService |

### 3.5 Migration of Existing Code

**Before (Genesis-I)**:
```python
class CLI:
    def __init__(self):
        self.compiler = Compiler()
        self.validator = ValidationEngine()
        self.graph = KnowledgeGraphEngine()
        self.runtime = ExecutionEngine()
        self.capabilities = CapabilityRegistry()
```

**After (Genesis-II)**:
```python
class CLI:
    def __init__(self, provider: ServiceProvider | None = None):
        self._provider = provider or ServiceProvider.get_default()
        self.compiler = self._provider.get(CompilerService)
        self.validator = self._provider.get(ValidationService)
        self.graph = self._provider.get(GraphService)
        self.runtime = self._provider.get(ExecutionService)
        self.capabilities = self._provider.get(CapabilityService)
```

The same pattern applies to `StudioBackend`, `Project31AIntegration`, and `Diagnostics`.

### 3.6 Elimination of Global Singletons

| Global Singleton | Replacement |
|-----------------|-------------|
| `type_registry` | Instantiated per `ServiceProvider`, shared via DI |
| `capability_registry` | Instantiated per `ServiceProvider`, shared via DI |
| `config` | Relaced by `ConfigService` through DI |

Direct imports like `from genesis.core.types import type_registry` are replaced with `provider.get(TypeRegistry)`. For backward compatibility during migration, a `get_default()` classmethod on ServiceProvider can be used.

---

## 4. GRAPH UNIFICATION STRATEGY

### 4.1 Problem Statement

Genesis-I has two parallel graph abstractions:

1. **`UIRGraph`** (`core/uir.py:117-237`): Property graph with nodes/edges/metadata. Has subclasses: DependencyGraph, CapabilityGraph, ValidationGraph, ExecutionGraph, MetadataGraph. Used inside CompilationUnit. Has `from_dict/to_dict/merge/find/neighbors/subgraph`.

2. **`KnowledgeGraphEngine`** (`graph/engine.py:26-249`): Wraps a `UIRGraph` but adds `_node_index` (label→id), `_type_index` (type→[ids]), `VALID_NODE_TYPES`, `VALID_EDGE_TYPES`, Cypher/GraphML export, orphan detection, circular dependency detection, `find_nodes`, `find_neighbors`, `save/load`.

Duplication: `detect_circular_dependencies` exists in both `DependencyGraph.find_cycles` (uir.py:319) and `KnowledgeGraphEngine.detect_circular_dependencies` (graph/engine.py:137).

### 4.2 Solution: UnifiedGraphEngine (UGE)

`UnifiedGraphEngine` in `graph/engine.py` becomes the single graph abstraction used by every module. It:

1. **Replaces KnowledgeGraphEngine entirely** (same API, enhanced)
2. **Is the graph backing for CompilationUnit** (replaces the pattern of having separate graph instances per subsystem)
3. **Provides unified export** (Cypher, GraphML, JSON in one place)
4. **Shares indices** (node, type, label — single source of truth)
5. **Uses shared graph_algorithms utility** (instead of own cycle detection)

```python
class UnifiedGraphEngine:
    """Single unified graph engine for all Venus graph operations."""
    
    VALID_NODE_TYPES = { ... }  # Loaded from TypeRegistry, not hardcoded
    VALID_EDGE_TYPES = { ... }
    
    def __init__(self, config: ConfigService):
        self.graph = UIRGraph(graph_id="venus_knowledge_graph", graph_type="knowledge")
        self._node_index: dict[str, str] = {}
        self._type_index: dict[str, list[str]] = defaultdict(list)
        
        # Load valid types from TypeRegistry (S14 fix)
        self._load_types_from_registry()
    
    # Node operations (merged from both UIRGraph and KGE)
    def add_node(self, node_id: str, label: str = "", node_type: str = "knowledge_node", **attrs) -> UIRNode: ...
    def get_node(self, node_id_or_label: str) -> UIRNode | None: ...
    def find_nodes(self, node_type: str | None = None, label_contains: str = "") -> list[UIRNode]: ...
    def remove_node(self, node_id: str): ...
    
    # Edge operations
    def add_edge(self, source: str, target: str, edge_type: str = "references", **attrs) -> UIREdge: ...
    def find_neighbors(self, node_id: str, edge_type: str | None = None, direction: str = "outgoing") -> list[UIRNode]: ...
    def remove_edge(self, source: str, target: str, edge_type: str | None = None): ...
    
    # Graph analysis (delegates to utils/graph_algorithms.py)
    def detect_orphans(self) -> list[UIRNode]: ...          # was in KGE
    def detect_circular_dependencies(self) -> list[list[str]]: ...  # was duplicated
    def topological_sort(self) -> list[str]: ...             # was in 3 places
    def subgraph(self, root_id: str, depth: int = 1) -> UIRGraph: ...  # was in UIRGraph
    
    # Export (merged from KGE + GraphGenerator)
    def export_cypher(self) -> str: ...
    def export_graphml(self) -> str: ...
    def export_json(self) -> str: ...
    
    # Persistence
    def save(self, path: str | Path): ...
    def load(self, path: str | Path): ...
    def save_checkpoint(self): ...
    def load_checkpoint(self): ...
    
    # Query
    def query(self, q: GraphQuery) -> QueryResult: ...
    
    # Statistics
    def summary(self) -> dict[str, Any]: ...
    def count_by_type(self) -> dict[str, int]: ...
```

### 4.3 How CompilationUnit Uses the Shared Graph

In Genesis-I, `CompilationUnit` contains 6 separate graph instances (ast, dependencies, capabilities, validation, execution, metadata_graph). In Genesis-II, the CompilationUnit records references into the shared `UnifiedGraphEngine`:

```python
class CompilationUnit:
    def __init__(self, source_path: str, source_format: str, graph: UnifiedGraphEngine):
        self.source_path = source_path
        self.source_format = source_format
        self._graph = graph  # reference to shared graph
        
        # Namespace prefixes for this compilation
        self._namespace = f"comp:{id(self)}"
        
        # No longer owns separate graphs — nodes go into shared graph
        self.passes_applied: list[str] = []
        self.compiled_at = datetime.now(timezone.utc).isoformat()
    
    def add_node(self, node_id: str, ...):
        """Adds node to shared graph with compilation tracking."""
        ...
    
    @property
    def nodes(self) -> list[UIRNode]:
        """Returns nodes owned by this compilation."""
        ...
```

This eliminates S03 (two parallel graph systems) and S15 (diagnostics creates own empty graph).

### 4.4 Graph Type Validation

In Genesis-I, `KnowledgeGraphEngine.VALID_NODE_TYPES` (graph/engine.py:29-35) is hardcoded — a duplicate of the type registry (S14). In Genesis-II:

```python
class UnifiedGraphEngine:
    def _load_types_from_registry(self):
        """Load valid node types from TypeRegistry instead of hardcoding."""
        type_registry = self._provider.get(TypeRegistryService)
        self.VALID_NODE_TYPES = {
            t.name for t in type_registry.all_types() 
            if not t.abstract
        }
```

### 4.5 Graph Algorithm Unification

All duplicate graph algorithms are consolidated into `genesis/utils/graph_algorithms.py`:

```python
def topological_sort(edges: list[tuple[str, str]], nodes: set[str] | None = None) -> list[str]:
    """Single implementation — O(V+E) with deque for O(1) pop."""
    ...

def find_cycles(edges: list[tuple[str, str]]) -> list[list[str]]:
    """Single implementation — DFS-based cycle detection."""
    ...

def subgraph(nodes: dict[str, UIRNode], edges: list[UIREdge], root_id: str, depth: int) -> UIRGraph:
    """Single implementation — BFS-based subgraph extraction."""
    ...
```

This eliminates:
- S03: Two parallel graph systems (UIRGraph vs KnowledgeGraphEngine)
- 3-implementation duplication of topological_sort
- 2-implementation duplication of find_cycles

---

## 5. PERSISTENCE ARCHITECTURE

### 5.1 Problem Statement

Genesis-I has zero persistence (S05). Every object lives in memory:
- `MetadataEngine._records` (in-memory dict)
- `Compiler._cache` (in-memory dict)
- `Workflow.tasks` (in-memory dict)
- `CapabilityRegistry._capabilities` (in-memory dict)
- `PluginManager._plugins` (in-memory dict)
- `KnowledgeGraphEngine.graph` (in-memory UIRGraph)
- `RepositoryIndexer.catalog` (in-memory dict)
- `ExecutionEngine._history` (in-memory list)

### 5.2 Solution: Three-Tier Persistence

```
┌─────────────────────────────────────────────────────────────┐
│                    Persistence Layer                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Repository Pattern                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │ MetadataRepo │  │  GraphRepo  │  │  ConfigRepo │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  SQLite     │  │  JSON Store  │  │  Config File     │  │
│  │  (primary)  │  │  (checkpoint │  │  (venus.json)    │  │
│  │  metadata,  │  │  export)     │  │                  │  │
│  │  graph,     │  │              │  │                  │  │
│  │  history)   │  │              │  │                  │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Storage Tier 1: SQLite (Primary)

Used for: metadata, graph persistence, execution history, capability registry, plugin registry.

**Schema**:

```sql
-- Metadata store
CREATE TABLE metadata_records (
    artifact_id TEXT PRIMARY KEY,
    artifact_path TEXT UNIQUE NOT NULL,
    semantic_type TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '0.1.0',
    owner TEXT NOT NULL DEFAULT 'genesis',
    validation_state TEXT NOT NULL DEFAULT 'unvalidated',
    certification TEXT NOT NULL DEFAULT 'uncertified',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    content_hash TEXT,
    size_bytes INTEGER DEFAULT 0,
    tags TEXT DEFAULT '[]',  -- JSON array
    lifecycle TEXT NOT NULL DEFAULT 'active'
);

-- Graph nodes
CREATE TABLE graph_nodes (
    node_id TEXT PRIMARY KEY,
    label TEXT NOT NULL DEFAULT '',
    semantic_type TEXT NOT NULL DEFAULT 'knowledge_node',
    attributes TEXT DEFAULT '{}',  -- JSON dict
    metadata TEXT DEFAULT '{}',    -- JSON dict
    created_at TEXT NOT NULL
);

-- Graph edges
CREATE TABLE graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL REFERENCES graph_nodes(node_id),
    target TEXT NOT NULL REFERENCES graph_nodes(node_id),
    edge_type TEXT NOT NULL DEFAULT 'references',
    attributes TEXT DEFAULT '{}',  -- JSON dict
    metadata TEXT DEFAULT '{}',    -- JSON dict
    created_at TEXT NOT NULL
);

-- Compilation cache
CREATE TABLE compilation_cache (
    source_path TEXT PRIMARY KEY,
    source_hash TEXT NOT NULL,
    compiled_at TEXT NOT NULL,
    cache_data TEXT NOT NULL  -- JSON serialized CompilationUnit
);

-- Execution history
CREATE TABLE execution_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    executed_at TEXT NOT NULL,
    status TEXT NOT NULL,
    results TEXT NOT NULL  -- JSON array
);

-- Plugin registry
CREATE TABLE plugins (
    name TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    manifest TEXT NOT NULL,  -- JSON
    state TEXT NOT NULL DEFAULT 'registered'
);

-- Capability registry
CREATE TABLE capabilities (
    name TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    definition TEXT NOT NULL,  -- JSON
    enabled INTEGER NOT NULL DEFAULT 1
);
```

### 5.4 Storage Tier 2: JSON Checkpoint

Used for: human-readable graph exports, portability, debugging.

The `UnifiedGraphEngine.save_checkpoint()` serializes the entire graph to JSON. The `Compiler` can optionally persist compilation results.

```python
class JsonStore:
    def save_graph(self, graph: UnifiedGraphEngine, path: Path):
        ...
    
    def load_graph(self, path: Path) -> UnifiedGraphEngine:
        ...
    
    def save_compilation(self, cu: CompilationUnit, path: Path):
        ...
```

### 5.5 Storage Tier 3: Config File

`ConfigManager` reads from `venus.json` (or `venus.yaml`) at the workspace root, with environment variable overrides:

```python
class ConfigManager:
    def __init__(self, paths: list[Path] | None = None):
        self._load_order = paths or [
            Path("venus.json"),
            Path("venus.yaml"),
            Path.home() / ".config" / "venus" / "config.json",
        ]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Resolution order: env var → file → default."""
        ...
```

### 5.6 Repository Pattern

```python
class Repository(ABC):
    @abstractmethod
    def save(self, entity: BaseEntity): ...
    @abstractmethod
    def get(self, entity_id: str) -> BaseEntity | None: ...
    @abstractmethod
    def delete(self, entity_id: str): ...
    @abstractmethod
    def find(self, **filters) -> list[BaseEntity]: ...

class SqliteRepository(Repository):
    def __init__(self, db_path: str | Path):
        self._conn = sqlite3.connect(str(db_path))
        self._init_schema()
```

### 5.7 Lifecycle Integration

```
Provider.startup()
  ├── ConfigManager.load()
  ├── SqliteRepository.connect()
  ├── UnifiedGraphEngine.load_checkpoint()
  ├── TypeRegistry.initialize()
  ├── CapabilityRegistry.load()
  ├── PluginManager.load_plugins()
  └── EventBus.start()

Provider.shutdown()
  ├── EventBus.stop()
  ├── SqliteRepository.close()
  ├── UnifiedGraphEngine.save_checkpoint()
  └── ConfigManager.save()
```

---

## 6. EXECUTION MODEL

### 6.1 Problem Statement

Genesis-I execution is single-threaded, sequential, in-memory only:
- `ExecutionEngine.execute()` runs tasks in a `for` loop (executor.py:165)
- No parallelism (even for independent tasks)
- No persistence of execution results (history is in-memory list)
- No event emission during execution

### 6.2 Solution: Enhanced Execution Engine

```python
class ExecutionEngine:
    def __init__(self, provider: ServiceProvider):
        self._graph = provider.get(GraphService)
        self._event_bus = provider.get(EventBus)
        self._history_repo = provider.get(HistoryRepository)
        self.workflows: dict[str, Workflow] = {}
    
    def execute(self, workflow_id: str, sync: bool = True, parallel: bool = False) -> list[dict]:
        """Execute workflow. sync=False enables event-driven async execution."""
        wf = self.workflows.get(workflow_id)
        plan = self._topological_sort(wf)  # uses shared utility
        
        if parallel and not sync:
            return self._execute_parallel(wf, plan)
        return self._execute_sequential(wf, plan)
    
    def _execute_parallel(self, wf: Workflow, plan: list[Task]) -> list[dict]:
        """Execute independent tasks in parallel using ThreadPoolExecutor."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            # Group tasks by dependency level
            levels = self._group_by_level(wf, plan)
            for level in levels:
                futures = {pool.submit(self._run_task, wf, t): t for t in level}
                for future in as_completed(futures):
                    results.append(future.result())
        
        self._event_bus.emit("workflow.completed", {"workflow_id": workflow_id})
        return results
    
    def _run_task(self, wf: Workflow, task: Task) -> dict:
        """Run a single task and emit events."""
        self._event_bus.emit("task.started", {"task_id": task.task_id})
        task.status = TaskStatus.RUNNING
        ...
        self._event_bus.emit("task.completed", {"task_id": task.task_id, "status": task.status.value})
        return task.to_dict()
```

### 6.3 Event Bus Foundation

```python
class EventBus:
    """Simple pub/sub event bus. Foundation for future async/distributed."""
    
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable):
        self._subscribers[event_type].append(handler)
    
    def emit(self, event_type: str, data: dict):
        for handler in self._subscribers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                # Log and continue — never let a handler crash the bus
                pass
    
    def unsubscribe(self, event_type: str, handler: Callable):
        self._subscribers[event_type].remove(handler)
```

This is intentionally minimal. It is the **foundation** for Genesis-III's distributed execution. It is not meant to replace RabbitMQ — it exists so that:
- Plugins can subscribe to platform events
- The diagnostics engine can react to compilation events
- The execution engine can emit lifecycle events
- Future Genesis-III can replace this with a proper message queue

---

## 7. PLUGIN ARCHITECTURE EVOLUTION

### 7.1 Problem Statement

Genesis-I plugin system has:
- `Sandbox` class (manager.py:57-70) that exists but is never called (S15 — well, not exactly S15, but listed as "Plugin sandbox bypassable" in Risk Register)
- `PluginManager.validate_module()` only checks against allowed module names — it does not prevent imports at `__import__` time
- Hot reload method exists (manager.py:185-207) but is never triggered via CLI or API

### 7.2 Solution: Enforced Sandbox + Enhanced Lifecycle

```python
# NEW: sandbox.py
class EnforcedSandbox:
    """Plugin sandbox with enforced module restriction via import hook."""
    
    def __init__(self, allowed_modules: set[str] | None = None):
        self.allowed_modules = allowed_modules or self._default_allowed()
        self._original_import = __builtins__["__import__"]
        self._enabled = False
    
    def _default_allowed(self) -> set[str]:
        return {
            "json", "yaml", "pathlib", "datetime", "uuid", "typing",
            "collections", "re", "math", "statistics", "itertools",
            "functools", "textwrap",
        }
    
    def enable(self):
        """Install the import hook."""
        if not self._enabled:
            __builtins__["__import__"] = self._restricted_import
            self._enabled = True
    
    def disable(self):
        """Remove the import hook."""
        if self._enabled:
            __builtins__["__import__"] = self._original_import
            self._enabled = False
    
    def _restricted_import(self, name, *args, **kwargs):
        """Restricted import that only allows permitted modules."""
        base_name = name.split(".")[0]
        if base_name in self.allowed_modules:
            return self._original_import(name, *args, **kwargs)
        raise ImportError(f"Module '{name}' is not allowed in plugin sandbox")
```

This is enabled/disabled around plugin module execution, providing real enforcement (addressing Risk #6 from the audit).

### 7.3 Plugin Manager Enhancements

```python
class PluginManager:
    def activate(self, name: str, enforce_sandbox: bool = True):
        """Activate with optional sandbox enforcement."""
        ...
        if enforce_sandbox and self._config.get("sandbox_enabled", True):
            self._sandbox.enable()
        try:
            instance.activate()
        finally:
            self._sandbox.disable()
    
    def hot_reload(self, name: str) -> bool:
        """Hot reload with sandbox enforcement."""
        if not self._config.get("sandbox_enabled", True):
            return self._hot_reload_unrestricted(name)
        ...
    
    def trigger_hook_async(self, hook_type: str, name: str, *args, **kwargs):
        """Async hook execution — doesn't block the caller."""
        import threading
        thread = threading.Thread(
            target=self.trigger_hook,
            args=(hook_type, name, *args),
            kwargs=kwargs,
        )
        thread.start()
```

---

## 8. API ARCHITECTURE

### 8.1 Problem Statement

Genesis-I `APIRouter` (api/router.py:47-190) defines 34 routes but has 0 registered handlers (S02). The router is a pure abstraction with no HTTP transport — it defines `Request` and `Response` objects but never serves them. CLI and Studio create their own instances of services instead of using the API layer.

### 8.2 Solution: FastAPI HTTP Server + Handler Implementations

```python
# NEW: api/server.py
import fastapi
from genesis.di.container import ServiceProvider

def create_app(provider: ServiceProvider) -> fastapi.FastAPI:
    app = fastapi.FastAPI(title="Venus Genesis-II", version="2.0.0")
    
    # Wire all 34 route handlers
    handlers = APIHandlers(provider)
    
    # Search
    app.get("/v1/search")(handlers.search)
    app.post("/v1/search/advanced")(handlers.search_advanced)
    
    # Compile
    app.post("/v1/compile")(handlers.compile)
    app.get("/v1/compile/{path}")(handlers.get_compilation)
    
    # Validate
    app.post("/v1/validate")(handlers.validate)
    app.get("/v1/validate/{path}")(handlers.get_validation)
    
    # ... all 34 routes
    
    # Health
    app.get("/v1/health")(handlers.health)
    app.get("/v1/health/detailed")(handlers.health_detailed)
    
    return app


# NEW: api/handlers.py
class APIHandlers:
    def __init__(self, provider: ServiceProvider):
        self.compiler = provider.get(CompilerService)
        self.validator = provider.get(ValidationService)
        self.graph = provider.get(GraphService)
        ...
    
    async def search(self, request: fastapi.Request):
        query = request.query_params.get("q", "")
        max_results = int(request.query_params.get("max", "10"))
        nodes = self.graph.find_nodes(label_contains=query)[:max_results]
        return {"results": [n.to_dict() for n in nodes]}
    
    async def compile(self, request: fastapi.Request):
        body = await request.json()
        source_path = body.get("path", "")
        if not source_path:
            return {"error": "path is required"}
        cu = self.compiler.compile(source_path)
        return {"source": source_path, "nodes": len(cu.nodes), "passes": cu.passes_applied}
    
    ...
```

### 8.3 The APIRouter as Abstraction Layer

The original `APIRouter` is preserved as a routing abstraction, but it is no longer the primary entry point. The FastAPI server replaces it for HTTP access, while the router remains useful for:
- In-process API calls (CLI commands can go through the router)
- Testing (test against router without HTTP)
- Documentation (router.list_routes() describes the API surface)

The CLI and Studio are refactored to use the API layer instead of creating service instances directly:

```python
class CLI:
    def __init__(self, provider: ServiceProvider):
        self._provider = provider
        self._router = APIRouter()
        self._wire_router()  # register handlers on router
    
    def cmd_compile(self, args):
        # Goes through the API layer instead of direct Compiler access
        request = Request("POST", "/v1/compile", body={"path": args.source[0]})
        response = self._router.handle(request)
        ...
```

This ensures the API layer is the **single entry point** for all operations, making it possible to add auth, logging, and rate limiting in one place.

---

## 9. MIGRATION STRATEGY

### 9.1 Migration Principles

1. **No breaking changes to public APIs where possible.** `BaseEntity`, `UIRNode`, `UIRGraph`, `CompilationUnit` constructors remain compatible.
2. **Parallel run capability.** Genesis-II code can coexist with Genesis-I code during migration.
3. **Test-driven migration.** Each module is migrated only when its test suite passes.
4. **Feature flag gating.** Genesis-II features are gated behind `ConfigManager` flags.

### 9.2 Migration Sequence

```
Phase 0  : Foundation (no behavioral changes)
Phase 1  : Utility extraction (pure refactor)
Phase 2  : Graph unification (structural change)
Phase 3  : DI container (structural change)
Phase 4  : Persistence layer (new capability)
Phase 5  : API server (new capability)
Phase 6  : Plugin sandbox (behavioral change)
Phase 7  : Hardening and test expansion
```

### 9.3 Phase Details

#### Phase 0: Foundation (Safe — No Behavior Change)

**Files**: new `utils/`, `di/`, `events/`, `persistence/`
**Risk**: None (new files, existing code untouched)

1. Create `genesis/utils/graph_algorithms.py` with single `topological_sort` and `find_cycles` imports from existing `uir.py`
2. Create `genesis/utils/serialization.py` with `Serializable` mixin
3. Create `genesis/utils/identity.py` with `generate_id(prefix: str) -> str`
4. Create `genesis/di/interfaces.py` with Protocol definitions
5. Create `genesis/di/container.py` with `ServiceProvider`
6. Create `genesis/events/bus.py` with `EventBus`
7. Create `genesis/persistence/repository.py` with abstract base
8. All existing code continues to work unchanged
9. **Tests pass**: 34/34 + new utility tests

#### Phase 1: Internal Refactor (No Public API Change)

**Files**: modified `core/uir.py`, `runtime/executor.py`, `graph/engine.py`
**Risk**: Low (delegation, not replacement)

1. `DependencyGraph.resolve_order()` and `ExecutionGraph.top_sort()` delegate to `utils.graph_algorithms.topological_sort()` instead of implementing their own
2. `DependencyGraph.find_cycles()` and `KnowledgeGraphEngine.detect_circular_dependencies()` delegate to `utils.graph_algorithms.find_cycles()`
3. Replace `uuid.uuid4().hex[:12]`, `uuid.uuid4().hex[:8]`, `uuid.uuid4().hex[:12]` with single `identity.generate_id()` call
4. **Tests pass**: All 34 + new utility tests
5. **Verification**: Assert identical behavior through existing test suite

#### Phase 2: Graph Unification (Structural Change)

**Files**: rewritten `graph/engine.py`, modified `core/uir.py`, `compiler/compiler.py`, `runtime/executor.py`
**Risk**: Medium (touches the most-coupled abstraction)

1. Rewrite `KnowledgeGraphEngine` as `UnifiedGraphEngine` that:
   - Loads types from TypeRegistry (not hardcoded)
   - Uses shared graph_algorithms utility
   - Has consistent node/type/label indices
   - Merges `UIRGraph.neighbors()` and `KnowledgeGraphEngine.find_neighbors()`
2. `CompilationUnit` takes optional reference to shared graph (backward compatible)
3. Add `UnifiedGraphEngine.find_neighbors()` as the single neighbor traversal
4. Add `UnifiedGraphEngine.subgraph()` as the single subgraph extraction
5. Keep `UIRGraph` class (used by many signatures) but `UnifiedGraphEngine` IS-A `UIRGraph` (inherits)
6. **Tests pass**: All 34 + new graph tests
7. **Verification**: Graph operations produce same output as Genesis-I

#### Phase 3: Dependency Injection (Structural Change)

**Files**: new `di/container.py`, modified `cli/commands.py`, `studio/backend.py`, `diagnostics/diagnostics.py`, `integration/project31a.py`, `config/settings.py`
**Risk**: Medium (changes how services are wired)

1. `ServiceProvider` registers all default services
2. `CLI.__init__` accepts optional `ServiceProvider` (backward compatible default)
3. `StudioBackend.__init__` accepts optional `ServiceProvider`
4. `Diagnostics.__init__` accepts `Optional[GraphService]` — falls back to creating its own
5. `Project31AIntegration.__init__` accepts optional `ServiceProvider`
6. `type_registry` global singleton remains but is also available via `provider.get(TypeRegistry)`
7. `capability_registry` global singleton remains but is also available via `provider.get(CapabilityRegistry)`
8. `config` global singleton replaced by `ConfigService` through DI
9. **Tests pass**: All 34 + DI tests
10. **Verification**: `CLI().run(["info"])` produces same output

#### Phase 4: Persistence Layer (New Capability)

**Files**: new `persistence/sqlite_store.py`, `persistence/json_store.py`, modified `core/metadata.py`, `graph/engine.py`, `runtime/executor.py`, `config/manager.py`
**Risk**: Medium (new capability, no breaking changes)

1. Implement `SqliteStore` with schema initialization
2. Implement `JsonStore` for graph checkpoints
3. `MetadataEngine` gets optional `SqliteStore` backend (falls back to in-memory)
4. `UnifiedGraphEngine` gets `save_checkpoint()` and `load_checkpoint()`
5. `ExecutionEngine` persists history to SQLite
6. `ConfigManager` reads from env/file/default chain
7. All existing in-memory operations continue to work (persistence is additive)
8. **Tests pass**: All 34 + persistence tests
9. **Verification**: Data survives restart after `save_checkpoint()` + `load_checkpoint()`

#### Phase 5: API Server (New Capability)

**Files**: new `api/server.py`, `api/handlers.py`, modified `api/router.py`, `cli/commands.py`
**Risk**: Low (additive, non-breaking)

1. Implement FastAPI server (`api/server.py`)
2. Implement handlers for all 34 routes (`api/handlers.py`)
3. CLI commands refactored to use API router as intermediary
4. `python3 -m genesis serve` starts the API server
5. **Tests pass**: All 34 + API tests
6. **Verification**: `curl http://localhost:8080/v1/health` returns 200

#### Phase 6: Plugin Sandbox Enforcement (Behavioral Change)

**Files**: new `plugin/sandbox.py`, modified `plugin/manager.py`
**Risk**: Low (gated behind config flag)

1. Implement `EnforcedSandbox` with `__import__` hook
2. `PluginManager.activate()` optionally enables sandbox
3. Gated behind `sandbox_enabled` config flag (default: true)
4. CLI has `--no-sandbox` flag for development
5. **Tests pass**: All 34 + sandbox tests
6. **Verification**: Plugin importing `os` raises `ImportError` when sandbox is enabled

#### Phase 7: Hardening and Test Expansion

**Files**: expanded `tests/`, fixes across modules
**Risk**: Low (test-only changes, defensive fixes)

1. Add tests for edge cases in all modules (target: +50% test count)
2. Add integration tests that exercise the full pipeline
3. Add performance benchmarks for graph operations
4. Fix any uncovered defects
5. Documentation updates to reflect Genesis-II architecture
6. **Tests pass**: All 50+ tests
7. **Verification**: Test coverage report ≥ 70% line coverage

### 9.4 Backward Compatibility Guarantees

| API | Genesis-I | Genesis-II | Migration Needed? |
|-----|-----------|-----------|-------------------|
| `BaseEntity(entity_id, name, semantic_type, ...)` | Yes | Yes | No |
| `UIRNode(node_id, label, semantic_type, ...)` | Yes | Yes | No |
| `CompilationUnit(source_path, source_format)` | Yes | Yes (graph is optional) | No |
| `DependencyGraph()` | Yes | Yes (delegates to utils) | No |
| `KnowledgeGraphEngine()` | Yes | Deprecated → `UnifiedGraphEngine()` | Yes — replace constructor |
| `cli.run(["compile", ...])` | Yes | Yes | No |
| `StudioBackend()` | Yes | Yes (provider is optional) | No |
| `Project31AIntegration()` | Yes | Yes (provider is optional) | No |
| `Diagnostics()` | Yes | Yes (graph is optional) | No |
| `from genesis.core.types import type_registry` | Yes | Yes (still works) | No (but prefer DI) |
| `from genesis.capability.registry import capability_registry` | Yes | Yes (still works) | No (but prefer DI) |

---

## 10. RISK ANALYSIS

### 10.1 Migration Risks

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|------------|
| Graph unification breaks existing consumers | Medium | High | Keep `UIRGraph` stable, make `UnifiedGraphEngine` a subclass. Backward-compatible `KnowledgeGraphEngine` shim. |
| DI container adds complexity without value | Low | Medium | Proved by testability improvement. Existing tests should be simpler with DI. |
| Persistence adds startup latency | Medium | Low | Lazy connection. WAL mode for SQLite. Configurable disable. |
| Feature fatigue — too many changes at once | Medium | High | Strict phase gating. No phase starts until previous phase tests are green. |
| Sandbox enforcement breaks existing plugins | Medium | Medium | Config-disabled by default during transition. Explicit opt-in. |
| FastAPI becomes a hard dependency | Low | Low | FastAPI is optional. `APIRouter` still works without it. `python3 -m genesis serve` fails gracefully. |

### 10.2 Architectural Risks from AUDIT.md (Re-evaluated)

| Original Risk | Probability (Gen-I) | Probability (Gen-II) | Mitigation in Gen-II |
|--------------|-------------------|-------------------|---------------------|
| In-memory data loss | Certain | Low | Phase 4 persistence |
| ExecutionEngine crash | High | Eliminated | S04 bug already fixed |
| Schema generation useless | Certain | Eliminated | Phase 0/7 — real schema derivation |
| Diagnostics always report failures | Certain | Eliminated | Phase 3 — shared graph through DI |
| API layer unused | Certain | Eliminated | Phase 5 — FastAPI server |
| Plugin sandbox bypassable | High | Eliminated | Phase 6 — import hook |
| No concurrent access handling | Certain | Medium | Phase 4 — SQLite handles concurrency; DI container provides single instances |

### 10.3 New Risks Introduced by Genesis-II

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|------------|
| SQLite dependency | Low | Low | `sqlite3` is in stdlib. No external DB dependency. |
| FastAPI dependency (optional) | Low | Medium | Not required for core. Optional pip install. |
| DI container becomes god object | Medium | Medium | Keep `ServiceProvider` focused on wiring only. No business logic in DI. |
| Too many new files | Medium | Low | Genesis-II adds ~15 files (vs 44 existing). Acceptable growth. |
| Graph unification API churn | Medium | Medium | Comprehensive tests before/after. Shim layer for KGE. |

---

## 11. IMPLEMENTATION PHASES

### 11.1 Phase Summary

| Phase | Name | New Files | Changed Files | Effort (hrs) | Dependencies |
|-------|------|-----------|---------------|-------------|-------------|
| 0 | Foundation | 8 | 0 | 4 | None |
| 1 | Internal Refactor | 0 | 5 | 2 | Phase 0 |
| 2 | Graph Unification | 0 | 4 | 6 | Phase 1 |
| 3 | DI Container | 2 | 6 | 8 | Phase 0 |
| 4 | Persistence | 3 | 5 | 12 | Phase 3 |
| 5 | API Server | 3 | 3 | 8 | Phase 3 |
| 6 | Plugin Sandbox | 1 | 1 | 3 | Phase 3 |
| 7 | Hardening | 0 | 5 | 8 | All above |
| **Total** | | **17** | **29** | **51** | |

### 11.2 Comparison with Genesis-I Effort

| Category | Estimated Hours (AUDIT.md) | Genesis-II Plan | Covered? |
|----------|---------------------------|-----------------|----------|
| Bug fixes (S04) | 1 | Already fixed | ✅ |
| Test gaps | 8 | Phase 7 (8 hrs) | ✅ |
| Duplicate code elimination | 4 | Phase 1 (2 hrs) | ✅ |
| Schema generator rewrite | 8 | Phase 7 (included) | ✅ |
| Persistence layer | 40 | Phase 4 (12 hrs + retained) | ⚠️ Reduced (SQLite not Neo4j) |
| API server integration | 16 | Phase 5 (8 hrs) | ⚠️ Reduced (FastAPI handles boilerplate) |
| Shared graph wiring | 4 | Phase 2 + 3 (14 hrs) | ✅ |
| Plugin sandbox enforcement | 8 | Phase 6 (3 hrs) | ✅ |
| **Total (AUDIT)** | **89** | **51** | **57% of estimated** |

The reduction is due to:
- SQLite replaces the more complex persistence originally estimated (12 vs 40 hrs)
- FastAPI handles HTTP boilerplate that was originally estimated as manual (8 vs 16 hrs)
- Graph unification and DI are combined efficiently (14 hrs total covers both)
- The audit's 89-hour estimate was conservative; 51 hours reflects actual experience with the codebase

### 11.3 Effort per Module

| Module | Genesis-I (existing) | Genesis-II (new/changed) | Description |
|--------|---------------------|-------------------------|-------------|
| `core/` | 963 lines | ~50 modified | Add `SemanticType.load_from_registry` |
| `utils/` | 0 lines | ~180 new | 3 new files |
| `di/` | 0 lines | ~150 new | 2 new files |
| `events/` | 0 lines | ~60 new | 1 new file |
| `persistence/` | 0 lines | ~350 new | 3 new files |
| `config/` | 45 lines | ~80 added | ConfigManager |
| `compiler/` | 712 lines | ~100 modified | Schema gen rewrite, pass refinement |
| `graph/` | 249 lines | ~300 rewritten | UnifiedGraphEngine |
| `plugin/` | 350 lines | ~50 added | Sandbox enforcement |
| `api/` | 190 lines | ~400 added | Server + handlers |
| `cli/` | 263 lines | ~80 modified | DI wiring |
| `studio/` | 131 lines | ~30 modified | DI wiring |
| `diagnostics/` | 222 lines | ~20 modified | DI wiring |
| `runtime/` | 221 lines | ~50 modified | Shared utils, event emission |
| `tests/` | 461 lines | ~300 added | Expanded coverage |

---

## 12. ACCEPTANCE CRITERIA

### 12.1 Architectural Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| A1 | No global singletons in application code | `grep "= TypeRegistry()"` returns 0 results (except in DI container) |
| A2 | Single topological_sort implementation | `grep "def top_sort\|def resolve_order\|def find_cycles"` returns only `utils/graph_algorithms.py` |
| A3 | Single graph engine instance across all modules | All modules use `provider.get(GraphService)` instead of `KnowledgeGraphEngine()` |
| A4 | All 34 API routes have registered handlers | `router.health_check()["coverage"] == "100.0%"` |
| A5 | Schema generator produces non-empty schemas | `schema_generator.generate(cu, dir)` produces schemas with populated `properties` |
| A6 | Diagnostics use shared graph (not empty) | `diag.run()` reflects actual platform state |
| A7 | Plugin sandbox is enforceable | Plugin importing `os` raises `ImportError` when sandbox enabled |
| A8 | UUID generation uses single utility | `grep "uuid.uuid4().hex\[:"` returns 0 results outside `identity.py` |
| A9 | Persistence layer is optional | All operations work without SQLite (in-memory fallback) |
| A10 | All existing 34 tests still pass | `python3 -m pytest tests/test_platform.py` — 34/34 |

### 12.2 Performance Acceptance Criteria

| # | Criterion | Threshold |
|---|-----------|-----------|
| P1 | Graph add_node throughput | ≥ 10,000 nodes/second |
| P2 | Graph topological_sort | ≤ 100ms for 10K nodes |
| P3 | Compiler startup time | ≤ 500ms (cold), ≤ 100ms (warm) |
| P4 | API server startup | ≤ 1 second |
| P5 | File compilation | ≤ 100ms for typical .md |
| P6 | SQLite query latency | ≤ 10ms for single record |

### 12.3 Quality Acceptance Criteria

| # | Criterion | Threshold |
|---|-----------|-----------|
| Q1 | Test count | ≥ 50 tests |
| Q2 | Line coverage | ≥ 70% |
| Q3 | Module dependency violations | 0 (enforced by import checker) |
| Q4 | Lint score (pylint/flake8) | ≥ 9.0/10 |
| Q5 | Type annotation coverage | ≥ 90% of functions |

---

## 13. ARCHITECTURE DECISION RECORDS

### ADR-001: Use SQLite Instead of Full Database

**Status**: Accepted  
**Context**: Genesis-I has zero persistence. Options considered: SQLite (stdlib), JSON files, Neo4j, PostgreSQL.  
**Decision**: SQLite for primary storage, JSON for human-readable checkpoints.  
**Rationale**: 
- `sqlite3` is in Python stdlib (zero dependencies)
- Handles concurrent access (WAL mode)
- Schema-enforced data integrity
- Simple backup (single file)
- JSON checkpoints provide portability without needing SQLite
- Neo4j is deferred to Genesis-III when graph scale demands it
**Consequences**:
- Data model is relational (graph data stored as JSON blobs in relational tables)
- Graph queries that need Neo4j's traversal engine are deferred
- Migration to Neo4j in Genesis-III is straightforward (repository pattern)

### ADR-002: Keep UIRGraph as Base Class, Not Replace It

**Status**: Accepted  
**Context**: Genesis-I has both `UIRGraph` (core/uir.py) and `KnowledgeGraphEngine` (graph/engine.py). Options: merge into one class, make UIRGraph inherit from KGE, make KGE inherit from UIRGraph.  
**Decision**: `UnifiedGraphEngine` inherits from `UIRGraph`. `UIRGraph` remains the base abstraction. `KnowledgeGraphEngine` is deprecated with a shim that delegates to `UnifiedGraphEngine`.  
**Rationale**: 
- `UIRGraph` is the universal data structure — it appears in every `CompilationUnit`, every export, every graph operation
- Changing it would break every consumer
- `UnifiedGraphEngine` adds indices, export, and persistence ON TOP of `UIRGraph` — this is exactly what inheritance is for
- `KnowledgeGraphEngine` users can migrate by replacing `KnowledgeGraphEngine()` with `UnifiedGraphEngine(provider=provider)`
**Consequences**:
- `UIRGraph` remains the transport type (used in function signatures)
- `UnifiedGraphEngine` is the working type (used for stateful graph operations)
- The two are interchangeable via Liskov substitution

### ADR-003: Protocol-Based DI Instead of Abstract Base Classes

**Status**: Accepted  
**Context**: Need to define service interfaces for DI container. Options: ABCs, Protocols (structural subtyping), or plain duck typing.  
**Decision**: Use `typing.Protocol` for service interfaces.  
**Rationale**: 
- Structural subtyping: any class that implements the protocol's methods is automatically a provider — no need to explicitly inherit
- Testing: mock objects don't need to inherit from ABCs
- Flexibility: existing Genesis-I classes already implement most protocol methods without modification
- Python 3.8+ supports Protocols (stdlib)
**Consequences**:
- Some IDE type-checking features require explicit protocol conformance declarations
- Runtime protocol checking requires `isinstance(obj, Protocol)` which may not work as expected on all Python versions (use `typing_extensions` if needed)

### ADR-004: FastAPI for HTTP Server (Optional Dependency)

**Status**: Accepted  
**Context**: Need to wire 34 API routes to an actual HTTP server. Options: FastAPI, Flask, Starlette, Sanic, or custom WSGI.  
**Decision**: FastAPI with `pip install fastapi uvicorn[standard]` as optional dependencies.  
**Rationale**: 
- Automatic OpenAPI documentation (from docstrings and type hints)
- Async support (for future streaming compilation)
- Pydantic integration (for request/response validation)
- Fastest growing Python web framework — community support
- Optional: `python3 -m genesis serve` works only if FastAPI is installed
**Consequences**:
- Adds ~5MB of dependencies when API server is enabled
- CLI and Studio still work without FastAPI
- Genesis-II core (compiler, graph, validation) has zero web dependencies

### ADR-005: Single Event Bus (Not Distributed)

**Status**: Accepted  
**Context**: Need event-driven execution. Options: in-memory pub/sub, Redis pub/sub, RabbitMQ, or event store.  
**Decision**: Minimal in-memory `EventBus` (pub/sub) for Genesis-II. Distributed event bus deferred to Genesis-III.  
**Rationale**: 
- Genesis-II is single-process (no distribution yet)
- In-memory event bus is ~60 lines of code
- Establishes the event-driven pattern without infrastructure dependencies
- Event types and subscribers established now — switching to Redis/RabbitMQ in Genesis-III is a drop-in replacement
- The interface (`EventBus.subscribe/emit/unsubscribe`) is the same regardless of transport
**Consequences**:
- Events are lost on process restart (acceptable for Genesis-II)
- Subscribers cannot span processes (Genesis-III resolves this)
- The event bus interface must be stable before Genesis-III distribution

### ADR-006: Rewrite SchemaGenerator, Not Fix Incrementally

**Status**: Accepted  
**Context**: `SchemaGenerator` produces empty schemas (AUDIT.md S09). Fixing incrementally would be ~8 hours of patching. Rewriting from scratch based on type registry + AST analysis would be ~4 hours.  
**Decision**: Rewrite `SchemaGenerator` to derive schemas from TypeRegistry type definitions and AST node structure.  
**Rationale**: 
- Current code (schema_gen.py:22-34) has no useful logic — it generates `{"properties": {}}`
- A rewrite from a clean design is faster than trying to patch non-existent logic
- The type registry already has `required_fields`, `constraints`, and hierarchy for each type
- The AST already has node attributes and children — schema derivation means mapping AST structure to JSON Schema structure
**Consequences**: 
- SchemaGenerator output changes from empty to populated schemas (not backward compatible in content, but backward compatible in file count)
- Existing consumers that expect empty schemas will need regeneration

### ADR-007: Keep CapabilityRegistry and TypeRegistry as Registries, Not Services

**Status**: Accepted  
**Context**: CapabilityRegistry and TypeRegistry are data registries (not operational services). Should they be in `di/` or stay in their current modules?  
**Decision**: They remain in their current modules and are registered with DI as singleton services. They are NOT moved to `di/`.  
**Rationale**: 
- They are knowledge, not wiring — conceptually they belong with their domain
- Moving them would create circular dependency concerns (TypeRegistry is used by core/uir.py)
- DI container registers them, but doesn't own them
- Existing direct imports (`from genesis.core.types import type_registry`) continue to work during migration
**Consequences**:
- Both global singleton and DI-injected version coexist during Genesis-II
- The global singleton is removed in Genesis-III (after all consumers are migrated)
- Tests can use either pattern (direct import or DI)

### ADR-008: No New Dependencies Beyond Stdlib + Optional FastAPI

**Status**: Accepted  
**Context**: Genesis-I has zero external dependencies (except PyYAML for YAML parsing, which is already optional). Genesis-II could benefit from libraries like SQLAlchemy, Pydantic, or NetworkX.  
**Decision**: Zero mandatory external dependencies. YAML remains optional. FastAPI is optional. SQLite is stdlib.  
**Rationale**: 
- Zero-dependency core is a key characteristic of the platform (portable, auditable, long-lived)
- SQLAlchemy adds ~4MB for what is a thin SQLite wrapper
- NetworkX adds ~2MB for graph algorithms we implement in ~100 lines
- Every dependency is a risk surface (security, version conflicts, maintenance burden)
- `sqlite3` and `json` in stdlib handle all Genesis-II persistence needs
**Consequences**:
- More code to maintain (graph algorithms, serialization, SQL queries)
- Faster startup (no heavy imports)
- Zero dependency conflict risk
- Platform can be `pip install`'d anywhere without version resolution

### ADR-009: Migration in 8 Phases, Not Big Bang

**Status**: Accepted  
**Context**: The 15 smells and 9 risks could be fixed in a single rewrite. Or they could be fixed incrementally.  
**Decision**: 8 sequential phases, each independently testable, each backward compatible.  
**Rationale**: 
- "Don't rebuild from scratch" (AUDIT.md final verdict)
- Each phase adds value independently
- A phase that breaks can be rolled back without affecting others
- 51 hours of work over 8 phases — max 12 hours per phase
- Continuous integration: each phase merges with green tests
- DNA.md constitutional laws are never violated (constraint-driven migration)
**Consequences**:
- Genesis-II takes longer to reach full capability (all phases must complete)
- But each phase delivers value independently (Pareto principle)
- Migration is observable and reversible

### ADR-010: CompilationUnit References Shared Graph (Doesn't Own)

**Status**: Accepted  
**Context**: In Genesis-I, `CompilationUnit` owns 6 separate graph instances. In Genesis-II, graphs must be shared. Options: keep owning but synchronize, or reference shared graph.  
**Decision**: `CompilationUnit` takes an optional reference to `UnifiedGraphEngine` and records its nodes within the shared graph, namespaced by compilation ID.  
**Rationale**: 
- Owning separate graphs that sync to shared graph creates consistency problems
- Direct reference to shared graph ensures single source of truth
- Namespacing (prefixing node IDs with compilation context) enables per-compilation filtering
- Backward compatible: if no shared graph is provided, CompilationUnit creates its own UIRGraph instances as before
**Consequences**:
- Graph operations querying "all nodes" get all compilations (usually desirable)
- Per-compilation filtering requires namespace prefix filter
- Memory usage: shared graph grows, but deduplication and indices keep it manageable

### ADR-011: Repository Pattern for Persistence, Not Active Record

**Status**: Accepted  
**Context**: Need to persist entities. Two common patterns: Active Record (entity knows how to save itself) or Repository (separate object handles persistence).  
**Decision**: Repository pattern.  
**Rationale**: 
- Aligns with DI container (repositories are injectable services)
- Entities stay pure data objects (no persistence concerns)
- Testing: mock repository instead of mocking entity
- Multiple storage backends (SQLite, JSON, Neo4j) without touching entity code
- Single `Repository.save()` handles all entity types
**Consequences**:
- More boilerplate (repository interface + implementation + entity mapping)
- But: reduces entity code (no `save()`/`load()` on every entity class)
- Repository pattern is standard for enterprise Python applications

---

## APPENDIX A: TOTAL EFFORT SUMMARY

| Activity | Estimated Hours |
|----------|----------------|
| Phase 0: Foundation | 4 |
| Phase 1: Internal Refactor | 2 |
| Phase 2: Graph Unification | 6 |
| Phase 3: DI Container | 8 |
| Phase 4: Persistence | 12 |
| Phase 5: API Server | 8 |
| Phase 6: Plugin Sandbox | 3 |
| Phase 7: Hardening | 8 |
| **Total implementation** | **51** |
| Testing (included in phases) | — |
| Documentation | 4 |
| **Grand total** | **55** |

**Comparison**: AUDIT.md estimated 89 hours for Genesis-II. The actual estimate (55 hours) is 38% lower because:
1. S04 bug is already fixed (saved 1 hour)
2. SQLite over full database (saved 28 hours vs original 40-hour estimate)
3. FastAPI over manual HTTP (saved 8 hours vs original 16-hour estimate)
4. Combined graph+DI refactor (saved 2 hours vs separate estimates)

## APPENDIX B: FILE INVENTORY COMPARISON

| Module | Genesis-I Files | Genesis-II Files | Delta |
|--------|----------------|------------------|-------|
| core/ | 5 | 5 | 0 |
| di/ | 0 | 2 | +2 |
| utils/ | 0 | 3 | +3 |
| events/ | 0 | 1 | +1 |
| persistence/ | 0 | 4 | +4 |
| config/ | 1 | 2 | +1 |
| compiler/ | 8 | 8 | 0 |
| graph/ | 1 | 1 | 0 |
| plugin/ | 2 | 3 | +1 |
| capability/ | 1 | 1 | 0 |
| validation/ | 4 | 4 | 0 |
| indexer/ | 1 | 1 | 0 |
| runtime/ | 1 | 1 | 0 |
| api/ | 1 | 3 | +2 |
| cli/ | 1 | 1 | 0 |
| studio/ | 1 | 1 | 0 |
| diagnostics/ | 1 | 1 | 0 |
| integration/ | 1 | 1 | 0 |
| tests/ | 1 | 2 | +1 |
| Root (init/main) | 2 | 2 | 0 |
| **Total** | **44** | **61** | **+17** |

**Code growth**: ~2,500 new lines of code (5,082 → ~7,500 total).

---

*This document is the implementation blueprint for Genesis-II. No production code should be written until this specification is approved and any ADR revisions are resolved.*
