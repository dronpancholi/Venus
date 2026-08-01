# Mission 22 — Graph Convergence Inventory & Plan

## All Graph Implementations (30 identified)

### Tier 1: Core Canonical (Accept No Adaptations)
| # | Location | Classes | Type | Status |
|---|---|---|---|---|
| 1 | `genesis/graph_v2/core.py` | `GraphNode`, `GraphEdge`, `GraphSnapshot`, `GraphEntity`, `GraphLayer`, `UnifiedGraph` | Universal | **CANONICAL** |
| 2 | `genesis/graph_v2/traversal.py` | `GraphTraversal`, `GraphSearch`, `GraphTransform` | Traversal | **CANONICAL** |
| 3 | `genesis/graph_v2/layers.py` | 12 layer types (Structural, Semantic, Capability, Architecture, Runtime, Dependency, Knowledge, Memory, Evolution, Experiment, Research, Organization) | Layers | **CANONICAL** |
| 4 | `genesis/graph_v2/analytics.py` | `GraphAnalytics` | Analytics | **CANONICAL** |
| 5 | `genesis/graph_v2/index.py` | `GraphIndex` | Index | **CANONICAL** |
| 6 | `genesis/graph_v2/partition.py` | `GraphPartition` | Partition | **CANONICAL** |
| 7 | `genesis/graph_v2/federation.py` | `GraphFederation` | Federation | **CANONICAL** |
| 8 | `genesis/graph_v2/compression.py` | `GraphCompression` | Compression | **CANONICAL** |
| 9 | `genesis/graph_v2/versioning.py` | `GraphDiff`, `GraphMerge`, `GraphVersioning` | Versioning | **CANONICAL** |

### Tier 2: Legacy — Has Direct Canonical Replacement Via Adapter
| # | Location | Classes | Canonical Adapter Target |
|---|---|---|---|
| 10 | `genesis/graph/engine.py` | `KnowledgeGraphEngine` | → `UnifiedGraph` + `GraphLayer(KNOWLEDGE)` |
| 11 | `genesis/knowledge_graph.py` | `KnowledgeGraph`, `PlanetaryKnowledgeGraph` | → `UnifiedGraph` + `GraphLayer(KNOWLEDGE)` |
| 12 | `genesis/hypergraph.py` | `HypergraphKnowledgeCore` | → `UnifiedGraph` with hyperedge capability |
| 13 | `genesis/execution_graph.py` | `ExecutionGraph`, `ExecutionGraphMonitor` | → `UnifiedGraph` + `GraphLayer(RUNTIME)` |
| 14 | `genesis/repository_graph.py` | `EngineeringKnowledgeGraph` | → `UnifiedGraph` + `GraphLayer(STRUCTURAL)` |
| 15 | `genesis/brain/graph.py` | `BrainGraph` | → `UnifiedGraph` + `GraphLayer(KNOWLEDGE)` |
| 16 | `genesis/core/uir.py` | `UIRGraph`, `DependencyGraph`, `CapabilityGraph`, `ValidationGraph` | → `UnifiedGraph` layers |
| 17 | `genesis/usir/__init__.py` | `USIRGraph` | → `UnifiedGraph` + `GraphLayer(STRUCTURAL)` |

### Tier 3: Specialized — Needs Custom Adapter
| # | Location | Classes | Strategy |
|---|---|---|---|
| 18 | `genesis/graphdb/__init__.py` | `PersistentGraphDB`, `GraphQueryBuilder` | Persistence adapter on `UnifiedGraph` |
| 19 | `genesis/ued/graph.py` | `GraphNode`, `GraphEdge`, `GraphStore` | UED persistence adapter |
| 20 | `genesis/meta/graph.py` | `WorkspaceDependencyGraph`, `WorkspaceGraph` | Meta-model adapter |
| 21 | `genesis/meta/build_graph.py` | `BuildGraph` | Build system adapter |
| 22 | `genesis/ucos/graph.py` | `CapabilityDependencyGraph` | Capability graph adapter |
| 23 | `genesis/metamodel/graph.py` | `UnifiedGraph` (⚠ duplicate name) | Rename conflict → MetaModelGraph |
| 24 | `genesis/os/task_graph.py` | `PersistentTaskGraph` | Task graph adapter |
| 25 | `genesis/laboratory/world_graph.py` | `WorldGraph` | Lab adapter |
| 26 | `genesis/observatory/graph.py` | `ObservatoryGraph` | Observatory adapter |
| 27 | `genesis/intelligence/kgraph.py` | `KnowledgeGraph` | VRIP/KGraph adapter |

### Tier 4: Domain Models — Lightweight wrappers
| # | Location | Classes | Strategy |
|---|---|---|---|
| 28 | `genesis/civilization/knowledge/__init__.py` | `LineageGraph` | Domain model |
| 29 | `genesis/civilization/research/__init__.py` | `CitationGraph` | Domain model |
| 30 | `genesis/memory/types.py` | `GraphMemory` | Memory-backed graph |
| 31 | `genesis/mathematics.py` | `GraphCalculus` | Math operations on graphs |
| 32 | `genesis/utils/graph_algorithms.py` | (utility functions) | Algorithm library |

## Convergence Plan

### Step 1: Create UnifiedGraph Adapter
A wrapper that makes any graph implementation look like a UnifiedGraph sub-graph.

### Step 2: Create persistent GraphStore
Unified graph persistence backed by UED or GraphDB.

### Step 3: Implement per-graph adapters
Starting with the most-depended-upon graphs.

### Step 4: Measure convergence
Duplicate algorithms, duplicate node models, duplicate edge models removed.
