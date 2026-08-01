# PROJECT NEMESIS Phase II — Mission 6: Universal Graph Core

**Date**: 2026-06-30 | **Repository**: 335 Python files (excl tests), ~71,916 lines (excl tests), 72 test files, 2,763 tests
**Scope**: Every graph subsystem — node/edge model, storage, query API, analytics, consumers, duplication

---

## 1. Executive Summary

Genesis has **6 independent graph systems** with 7 distinct node models and 7 distinct edge models. Each was built to solve a specific problem; none was designed to be canonical. The result: ~3,250 lines of duplicated graph infrastructure, 6 incompatible APIs, and no shared core.

**The duplication is worst in the repository**: 19.1% of capability groups have 2+ implementations, and graph systems are the most duplicated (6×).

**Core finding**: No single graph system is canonical. Each has unique capability that must be preserved. The design for a Universal Graph Core must unify the node/edge models, query APIs, and analytics while preserving each system's specialized capabilities (hyperedges, persistence, event-driven updates, knowledge sub-graphs, layered partitioning).

---

## 2. Every Graph System: Origin, Purpose, Model, Consumers

### 2.1 `graph/engine.py` — KnowledgeGraphEngine (305 lines)

**Purpose**: Event-driven knowledge graph. Connects to UIR graph for architecture analysis, emits events on mutation, integrates with EventBus and KnowledgeStore.

**Location**: `genesis/graph/engine.py`

**Node model**: `UIRNode` (from `core/uir.py`) — uid, node_type, name, properties, metadata, source_location, complexity, dependencies

**Edge model**: `UIREdge` (from `core/uir.py`) — source, target, edge_type, weight, properties, metadata

**Storage**: In-memory UIR graph (no persistence)

**Query API**: `query_nodes()`, `query_edges()`, `find_path()`, `get_connected_components()`, `get_subgraph()` — all delegate to UIRGraph

**Key APIs**:
```python
class KnowledgeGraphEngine:
    def __init__(self, event_bus, uir_graph, knowledge_store)
    def acquire_knowledge(self, knowledge_item) -> str
    def query_graph(self, query) -> list[dict]
    def get_statistics(self) -> dict
    def build_dependency_graph(self, module_name) -> dict
    def analyze_architecture(self) -> dict
    def export(self, format) -> str
```

**Event hooks**: `on_graph_updated` (fires after mutations)

**Consumers**: `EventBus`, `KnowledgeStore` (via DI injection). Used in platform boot.

**Unique value**: Event-driven architecture analysis with DI wiring. Wraps UIRGraph as the architectural analysis foundation.

**Status**: **Legacy** — wrapped around UIRGraph. Should delegate to Universal Graph Core.

### 2.2 `graph_v2/core.py` + `graph_v2/layers.py` — UnifiedGraph (~800 lines)

**Purpose**: Multi-layer, partitioned, federated graph for repository metadata. Most architecturally complete.

**Location**: `genesis/graph_v2/core.py`, `genesis/graph_v2/layers.py`
**Also**: `genesis/graph_v2/analytics.py` (131 lines), `genesis/graph_v2/federation.py` (104 lines)

**Node model**: `GraphNode` — uid, node_type, name, properties, layer, partition_id, version, timestamp, metadata
```python
@dataclass
class GraphNode:
    uid: str
    node_type: str
    name: str
    properties: dict
    layer: str
    partition_id: int
    version: int = 0
    timestamp: float = 0.0
    metadata: dict = field(default_factory=dict)
```

**Edge model**: `GraphEdge` — source_uid, target_uid, edge_type, properties, layer, partition_id, version, weight, metadata
```python
@dataclass
class GraphEdge:
    uid: str
    source_uid: str
    target_uid: str
    edge_type: str
    properties: dict
    layer: str
    partition_id: int
    version: int = 0
    weight: float = 1.0
    timestamp: float = 0.0
    metadata: dict = field(default_factory=dict)
```

**Storage**: In-memory dictionaries — `nodes: dict[str, GraphNode]`, `edges: dict[str, GraphEdge]`, `layer_nodes: dict[str, set[str]]`, `partition_nodes: dict[int, set[str]]`

**Query API**: Rich query interface:
```python
class GraphQuery:
    def filter(self, **conditions) -> GraphQuery
    def layer(self, layer_name) -> GraphQuery
    def limit(self, n) -> GraphQuery
    def offset(self, n) -> GraphQuery
    def order_by(self, key, desc) -> GraphQuery
    def execute_nodes(self) -> list[GraphNode]
    def execute_edges(self) -> list[GraphEdge]

class UnifiedGraph:
    def add_node(self, node) -> str
    def add_edge(self, edge) -> str
    def get_node(self, uid) -> GraphNode
    def get_edge(self, uid) -> GraphEdge
    def query(self) -> GraphQuery
    def get_all_nodes(self) -> list[GraphNode]
    def get_all_edges(self) -> list[GraphEdge]
    def get_statistics(self) -> dict
```

**Layer types** (from layers.py): `LAYER_TYPES = ["source", "dependency", "runtime", "data", "infrastructure", "domain", "deployment", "network", "storage", "security", "monitoring", "testing"]`

**Analytics**: Centrality, clustering, path-finding, degree distribution, connected components, shortest paths

**Federation**: Node-level and query-level federation across multiple graph instances

**Unique value**: Layered architecture, partitioning, versioned nodes/edges, full GraphQuery builder, analytics engine, federation support. Most complete design.

**Status**: **Should be canonical core** — missing only persistence, typed edges, temporal edges, and event hooks.

### 2.3 `hypergraph.py` — HypergraphKnowledgeCore (648 lines)

**Purpose**: Hypergraph where edges can connect N nodes (not just 2). Weighted, probabilistic, temporal edges with confidence scoring.

**Location**: `genesis/hypergraph.py`

**Node model**: `HyperNode` — uid, label, attributes, node_type, metadata, timestamp

**Edge model**: `HyperEdge` — uid, edge_type, nodes (list of uids), weight, confidence, probability, temporal (start/end time), attributes, metadata

```python
@dataclass
class HyperNode:
    uid: str = ""
    label: str = ""
    attributes: dict = field(default_factory=dict)
    node_type: str = "entity"
    metadata: dict = field(default_factory=dict)
    timestamp: float = 0.0

@dataclass
class HyperEdge:
    uid: str = ""
    edge_type: str = "associates"
    nodes: list[str] = field(default_factory=list)
    weight: float = 1.0
    confidence: float = 1.0
    probability: float = 1.0
    temporal: tuple[float, float] | None = None
    attributes: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
```

**Storage**: In-memory — `nodes: dict[str, HyperNode]`, `edges: dict[str, HyperEdge]`, `incidence: dict[str, set[str]]` (node → edge mapping)

**Query API**:
```python
class HypergraphKnowledgeCore:
    def add_node(self, node) -> str
    def add_edge(self, edge) -> str
    def get_node(self, uid) -> HyperNode
    def get_edge(self, uid) -> HyperEdge
    def get_incident_edges(self, node_uid) -> list[HyperEdge]
    def query_nodes(self, **attrs) -> list[HyperNode]
    def query_edges(self, **attrs) -> list[HyperEdge]
    def get_neighbors(self, node_uid) -> dict[str, set[str]]
    def hyper_path(self, start_uid, end_uid) -> list[list[str]]
    def subgraph(self, node_uids) -> dict
    def merge_nodes(self, target_uid, source_uids) -> str
    def export(self, fmt) -> str
    def statistics(self) -> dict
```

**Export formats**: JSON, GEXF

**Unique value**: N-ary hyperedges (edges with N > 2 endpoints), probabilistic edges, temporal edges (start/end time), confidence scoring, node merging, hyper-path finding, incidence matrix

**Status**: **Legacy** — unique hypergraph capability must be ported. No consumers found in codebase.

### 2.4 `knowledge_graph.py` — PlanetaryKnowledgeGraph (320 lines)

**Purpose**: Domain-typed knowledge graph with 6 sub-graph types. Originally for planetary-scale knowledge modeling.

**Location**: `genesis/knowledge_graph.py`

**Node model**: `KEntity` — uid, name, entity_type, domain, properties, source, confidence, metadata

```python
@dataclass
class KEntity:
    uid: str = ""
    name: str = ""
    entity_type: str = "concept"
    domain: str = "general"
    properties: dict = field(default_factory=dict)
    source: str = ""
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)
```

**Edge model**: `KRelation` — source_uid, target_uid, relation_type, weight, confidence, properties, metadata

```python
@dataclass
class KRelation:
    uid: str = ""
    source_uid: str = ""
    target_uid: str = ""
    relation_type: str = "references"
    weight: float = 1.0
    confidence: float = 1.0
    properties: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
```

**Storage**: In-memory — `entities: dict[str, KEntity]`, `relations: dict[str, KRelation]`, `domain_index: dict[str, set[str]]`, `type_index: dict[str, set[str]]`

**Sub-graphs**: `create_subgraph(graph_type)` — 6 types: `dependencies`, `architecture`, `knowledge`, `evolution`, `metrics`, `capabilities`

**Query API**:
```python
class PlanetaryKnowledgeGraph:
    def add_entity(self, entity) -> str
    def add_relation(self, relation) -> str
    def query_entities(self, domain, entity_type) -> list[KEntity]
    def query_relations(self, relation_type) -> list[KRelation]
    def get_neighbors(self, uid, max_depth) -> dict
    def create_subgraph(self, graph_type) -> PlanetaryKnowledgeGraph
    def get_statistics(self) -> dict
```

**Unique value**: Domain-typed entities, 6 sub-graph types (dependencies, architecture, knowledge, evolution, metrics, capabilities), domain/type-based indexing, sub-graph extraction

**Status**: **Legacy** — domain typing and sub-graph concept are valuable. No DI consumers found.

### 2.5 `brain/graph.py` — BrainGraph (~400 lines)

**Purpose**: Persistent brain graph. Wraps PersistentGraphDB, syncs all subsystems into a unified graph. Reflexively syncs itself.

**Location**: `genesis/brain/graph.py`

**Node model**: Uses `graphdb.Node` — uid, name, node_type, description, attributes, source, confidence, tags, created_at, updated_at

**Edge model**: Uses `graphdb.Edge` — id, source_uid, target_uid, relation, weight, confidence, attributes, metadata, source, created_at

**Storage**: PersistentGraphDB (SQLite-backed with JSON/CSV/GEXF/Cypher export)

**Query API**: Exposes PersistentGraphDB methods plus subsystem sync:
```python
class BrainGraph:
    def __init__(self, db_path="brain_graph.db")
    def sync_memory(self, memory_store) -> None
    def sync_knowledge(self, knowledge_graph) -> None
    def sync_cognition(self, cognition_graph) -> None
    def sync_learning(self, learning_graph) -> None
    def sync_experience(self, experience_graph) -> None
    def sync_all(self) -> dict
    def query(self, query_obj) -> list
    def search(self, text) -> list
    def get_statistics(self) -> dict
```

**Unique value**: SQLite-backed persistence, syncs all brain subsystems (memory, knowledge, cognition, learning, experience), full-text search, graph algorithms (BFS, DFS, centrality, clustering, pathfinding), multiple export formats

**Status**: **Standalone with value** — persistence mechanism is unique and necessary. Sync architecture is valuable.

### 2.6 `graphdb/__init__.py` — PersistentGraphDB (835 lines)

**Purpose**: Full SQLite-backed graph database with query builder, full-text search, graph algorithms, and export.

**Location**: `genesis/graphdb/__init__.py`

**Node model**: `Node` — uid, name, node_type, description, attributes, source, confidence, tags, created_at, updated_at

**Edge model**: `Edge` — id, source_uid, target_uid, relation, weight, confidence, attributes, metadata, source, created_at

```python
@dataclass
class Node:
    uid: str = ""
    name: str = ""
    node_type: str = "entity"
    description: str = ""
    attributes: dict = field(default_factory=dict)
    source: str = ""
    confidence: float = 1.0
    tags: list = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0

@dataclass
class Edge:
    id: str = ""
    source_uid: str = ""
    target_uid: str = ""
    relation: str = "references"
    weight: float = 1.0
    confidence: float = 1.0
    attributes: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    source: str = ""
    created_at: float = 0.0
```

**Storage**: SQLite — tables: `nodes`, `edges`, `graph_metadata`. Full indices on uid, type, name, timestamps, relation, source.

**Query API**: Full query builder:
```python
class Query:
    def where(self, **conditions) -> Query
    def where_edge(self, **conditions) -> Query
    def order_by(self, field, desc) -> Query
    def limit(self, n) -> Query
    def offset(self, n) -> Query
    def execute(self) -> list[Node]

class PersistentGraphDB:
    def add_node(self, node) -> str
    def add_edge(self, node1_uid, node2_uid, relation, **kw) -> str
    def get_node(self, uid) -> Node
    def get_edge(self, id) -> Edge
    def query(self) -> Query
    def text_search(self, text) -> list
    def bfs(self, start_uid, max_depth) -> list
    def dfs(self, start_uid, max_depth) -> list
    def centrality(self) -> dict
    def clustering(self) -> dict
    def connected_components(self) -> list
    def find_path(self, source_uid, target_uid) -> list
    def export_json(self) -> str
    def export_csv(self, path) -> None
    def export_gexf(self) -> str
    def export_cypher(self) -> str
    def get_statistics(self) -> dict
```

**Algorithms**: BFS, DFS, degree centrality, betweenness centrality, clustering coefficient, connected components, shortest path

**Export formats**: JSON, CSV, GEXF, Cypher

**Unique value**: SQLite-backed persistence (only graph with real database storage), full query builder, full-text search, complete graph algorithm suite, 4 export formats, versioned metadata table

**Status**: **Standalone with value** — only persistent graph system. Should remain standalone but adopt the Universal Graph Core node/edge model.

---

## 3. Comparison Matrix

| Dimension | graph/engine | graph_v2/ | hypergraph.py | knowledge_graph.py | brain/graph | graphdb/ |
|-----------|-------------|-----------|---------------|-------------------|-------------|----------|
| **Lines** | 305 | ~1,035 | 648 | 320 | ~400 | 835 |
| **Node model** | UIRNode | GraphNode | HyperNode | KEntity | Node (graphdb) | Node |
| **Edge model** | UIREdge | GraphEdge | HyperEdge (n-ary) | KRelation | Edge (graphdb) | Edge |
| **Storage** | In-memory | In-memory | In-memory | In-memory | SQLite | SQLite |
| **Persistence** | None | None | None | None | SQLite file | SQLite file |
| **Query builder** | No | Yes (GraphQuery) | No | No | No | Yes (Query) |
| **Full-text search** | No | No | No | No | Yes | Yes |
| **Graph algorithms** | components, paths | centrality, clustering, paths, components | hyper-path | No | BFS, DFS, centrality, clustering, components | BFS, DFS, centrality, clustering, components, paths |
| **Event hooks** | Yes (EventBus) | No | No | No | No | No |
| **Layers** | No | Yes (12 types) | No | 6 sub-graphs | No | No |
| **Partitioning** | No | Yes | No | No | No | No |
| **Versioning** | No | Yes (per node/edge) | No | No | No | No |
| **Temporal** | No | Yes (timestamp) | Yes (start/end) | No | No | Yes (created_at) |
| **Confidence** | No | No | Yes | Yes | Yes (attribute) | Yes |
| **Hyperedges** | No | No | Yes | No | No | No |
| **Probabilistic** | No | No | Yes | No | No | No |
| **Federation** | No | Yes | No | No | No | No |
| **Domain typing** | No | No | No | Yes | No | No |
| **Subsystem sync** | No | No | No | No | Yes | No |
| **DI connected** | Yes | No | No | No | No | No |
| **Architecture analysis** | Yes | No | No | No | No | No |
| **Node merging** | No | No | Yes | No | No | No |
| **Export formats** | 1 (from UIR) | No | 2 (JSON, GEXF) | No | 4 (JSON, CSV, GEXF, Cypher) | 4 (JSON, CSV, GEXF, Cypher) |
| **Consumers** | EventBus, KnowledgeStore | None found | None found | None found | Brain subsystems | BrainGraph |
| **Canonical?** | Legacy | **Proposed core** | Legacy | Legacy | Standalone | Standalone |

---

## 4. Duplication Analysis

### 4.1 Duplicate Node Models

Every graph defines its own `Node` or entity class with varying field names for the same concepts:

| Concept | graph/engine | graph_v2/ | hypergraph.py | knowledge_graph.py | graphdb/ |
|---------|-------------|-----------|---------------|-------------------|----------|
| Unique ID | `uid` | `uid` | `uid` | `uid` | `uid` |
| Name | `name` | `name` | `label` | `name` | `name` |
| Type | `node_type` | `node_type` | `node_type` | `entity_type` | `node_type` |
| Properties | `properties` | `properties` | `attributes` | `properties` | `attributes` |
| Metadata | `metadata` | `metadata` | `metadata` | `metadata` | `description` |
| Timestamp | — | `timestamp` | `timestamp` | — | `created_at`/`updated_at` |
| Confidence | — | — | — | `confidence` | `confidence` |
| Source | `source_location` | — | — | `source` | `source` |

**Impact**: Any code switching between graphs must manually translate fields. Type checking across graphs is impossible.

### 4.2 Duplicate Edge Models

| Concept | graph/engine | graph_v2/ | hypergraph.py | knowledge_graph.py | graphdb/ |
|---------|-------------|-----------|---------------|-------------------|----------|
| Unique ID | — | `uid` | `uid` | `uid` | `id` |
| Source | `source` | `source_uid` | in `nodes` list | `source_uid` | `source_uid` |
| Target | `target` | `target_uid` | in `nodes` list | `target_uid` | `target_uid` |
| Type | `edge_type` | `edge_type` | `edge_type` | `relation_type` | `relation` |
| Weight | `weight` | `weight` | `weight` | `weight` | `weight` |
| Confidence | — | — | `confidence` | `confidence` | `confidence` |
| Properties | `properties` | `properties` | `attributes` | `properties` | `attributes` |
| Metadata | `metadata` | `metadata` | `metadata` | `metadata` | `metadata` |

### 4.3 Duplicate Query APIs

| Operation | graph/engine | graph_v2/ | hypergraph.py | knowledge_graph.py | graphdb/ |
|-----------|-------------|-----------|---------------|-------------------|----------|
| Filter nodes | `query_nodes()` | `query().filter()` | `query_nodes(**attrs)` | `query_entities(domain, type)` | `query().where()` |
| Filter edges | `query_edges()` | `query().filter()` | `query_edges(**attrs)` | `query_relations(type)` | `query().where_edge()` |
| Get by ID | — | `get_node()` | `get_node()` | — | `get_node()` |
| Neighbors | `get_connected_components()` | — | `get_neighbors()` | `get_neighbors()` | BFS/DFS |
| Path finding | `find_path()` | shortest paths | `hyper_path()` | — | `find_path()` |
| Statistics | `get_statistics()` | `get_statistics()` | `statistics()` | `get_statistics()` | `get_statistics()` |

**Impact**: 5 different APIs for the same set of graph operations. Code cannot be shared.

### 4.4 Duplicate Graph Algorithms

| Algorithm | graph/engine | graph_v2/ | hypergraph.py | graphdb/ |
|-----------|-------------|-----------|---------------|----------|
| Connected components | Yes | Yes | — | Yes |
| Shortest path | Yes | Yes | — | Yes |
| Centrality | — | Yes | — | Yes |
| Clustering | — | Yes | — | Yes |
| BFS | — | — | — | Yes |
| DFS | — | — | — | Yes |
| Hyper-path | — | — | Yes | — |

**Impact**: Centrality, clustering, connected components, and path finding each have 2-3 implementations with different APIs.

### 4.5 Overlap Score

```
graph/engine   ─────── UIRGraph wrapper ──────  (uses UIRNode/UIREdge)
graph_v2/      ─────── layered architecture ────  (GraphNode/GraphEdge)
hypergraph.py  ─────── hyperedges ─────────────  (HyperNode/HyperEdge)
knowledge_graph.py ─── sub-graphs/domain typing ─  (KEntity/KRelation)
brain/graph    ─────── wraps graphdb ──────────  (Node/Edge)
graphdb/       ─────── SQLite persistence ─────  (Node/Edge)
```

**Total overlap**: ~60% of functionality is duplicated across 2+ graph systems. Only ~40% is unique.

---

## 5. Consumer Analysis

### 5.1 Direct Consumers (imports at runtime)

| Consumer | graph/engine | graph_v2/ | hypergraph.py | knowledge_graph.py | brain/graph | graphdb/ |
|----------|-------------|-----------|---------------|-------------------|-------------|----------|
| `platform.py` | Yes | No | No | No | No | No |
| `brain/graph.py` | No | No | No | No | No | Yes |
| `omega_loop.py` | Yes | No | No | No | No | No |
| `atlas.py` | Yes | No | No | No | No | No |
| Test files | — | — | Yes (test_hypergraph.py) | — | — | Yes (test_graphdb.py) |

### 5.2 Graph Analysis from Projection

Based on ownership, dependency, lifecycle, and consumer analysis:

- **graph/engine.py**: 1 consumer (platform.py boot → KnowledgeGraphEngine → wrapped by KnowledgeGraphService). 1 test file.
- **graph_v2/**: No runtime consumers. 1 test file (test_graph_v2.py). Appears unused in production code.
- **hypergraph.py**: No runtime consumers. 1 test file (test_hypergraph.py ~400 lines).
- **knowledge_graph.py**: No runtime consumers. No test file.
- **brain/graph.py**: No runtime consumers (BrainGraph never instantiated by platform.py). No test file.
- **graphdb/**: 1 consumer (brain/graph.py). 1 test file (test_graphdb.py).

**Finding**: Only `graph/engine.py` has real DI consumers at boot time. `graphdb/` has a potential consumer (brain/graph.py) but brain/graph.py itself is never instantiated. The other 4 graph systems have no runtime consumers — they are library code with no active instantiation.

---

## 6. Design: Universal Graph Core

### 6.1 Design Requirements

Based on archaeology:

1. **Unified node model**: One Node dataclass that subsumes all 5 node models
2. **Unified edge model**: One Edge dataclass that subsumes all 5 edge models, supporting N-ary edges
3. **Multiple storage backends**: In-memory (for ephemeral), SQLite (for persistence), with pluggable backend interface
4. **Rich query API**: Chainable query builder with filtering, ordering, pagination
5. **Graph algorithms**: Centrality, clustering, components, path finding, BFS, DFS, hyper-path
6. **Event hooks**: Mutation callbacks for EventBus integration
7. **Layer/partition support**: From graph_v2/ — layers, partitions, versioning
8. **Temporal edges**: From hypergraph.py — start/end time for time-bounded relationships
9. **Confidence/probability**: From hypergraph.py + knowledge_graph.py
10. **Full-text search**: From graphdb/ — FTS5-based
11. **Export**: Multiple formats (JSON, CSV, GEXF, Cypher, DOT)
12. **Backward compatibility**: Must not break graph/engine.py API (it has consumers)

### 6.2 Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Universal Graph Core                      │
├─────────────────────────────────────────────────────────────┤
│  Node       │  Edge (binary) │  HyperEdge (N-ary)           │
│  ─────────  │  ─────────────  │  ────────────────────        │
│  uid, name  │  source, target │  uid, type, nodes[]          │
│  type, tags │  type, weight   │  weight, confidence           │
│  props, ts  │  props, meta    │  prob, temporal, props        │
├─────────────────────────────────────────────────────────────┤
│  GraphCore (unified interface)                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ QueryBuilder │  │ GraphAlgo    │  │ EventManager     │    │
│  │ .filter()    │  │ .centrality  │  │ .on_mutation()   │    │
│  │ .where()     │  │ .clustering  │  │ .emit_event()    │    │
│  │ .order()     │  │ .components  │  │                  │    │
│  │ .limit()     │  │ .paths       │  │                  │    │
│  │ .paginate()  │  │ .bfs/dfs     │  │                  │    │
│  └─────────────┘  └──────────────┘  └──────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Storage Backends                                            │
│  ┌────────────────┐  ┌──────────────────┐                   │
│  │ MemoryBackend  │  │ SQLiteBackend    │                   │
│  │ (dict-based)   │  │ (persistent)     │                   │
│  └────────────────┘  └──────────────────┘                   │
├─────────────────────────────────────────────────────────────┤
│  Extensions                                                  │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────┐  │
│  │ Layers   │ │Partitions│ │ Federation  │ │ TextSearch  │  │
│  └──────────┘ └──────────┘ └────────────┘ └─────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐              │
│  │ Export   │ │SubGraphs │ │ SubsystemSync  │              │
│  └──────────┘ └──────────┘ └────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Unified Node Model

```python
@dataclass
class GraphNode:
    uid: str
    name: str
    node_type: str
    properties: dict
    metadata: dict
    tags: list[str]
    source: str
    confidence: float
    created_at: float
    updated_at: float
    version: int
    layer: str
    partition_id: int
```

**Field mapping**:
| Universal Field | UIRNode field | GraphNode field | HyperNode field | KEntity field | graphdb.Node field |
|----------------|---------------|-----------------|-----------------|---------------|-------------------|
| `uid` | `uid` | `uid` | `uid` | `uid` | `uid` |
| `name` | `name` | `name` | `label` | `name` | `name` |
| `node_type` | `node_type` | `node_type` | `node_type` | `entity_type` | `node_type` |
| `properties` | `properties` | `properties` | `attributes` | `properties` | `attributes` |
| `metadata` | `metadata` | `metadata` | `metadata` | `metadata` | — |
| `tags` | — | — | — | — | `tags` |
| `source` | `source_location` | — | — | `source` | `source` |
| `confidence` | — | — | — | `confidence` | `confidence` |
| `created_at` | — | `timestamp` | `timestamp` | — | `created_at` |
| `updated_at` | — | — | — | — | `updated_at` |
| `version` | — | `version` | — | — | — |
| `layer` | — | `layer` | — | — | — |
| `partition_id` | — | `partition_id` | — | — | — |

### 6.4 Unified Edge Model

```python
@dataclass
class GraphEdge:
    uid: str
    source_uid: str
    target_uid: str
    edge_type: str
    weight: float
    confidence: float
    probability: float
    temporal: tuple[float, float] | None  # (start_time, end_time)
    properties: dict
    metadata: dict
    source: str
    created_at: float
    version: int
    layer: str
    partition_id: int
```

### 6.5 HyperEdge (specialization of GraphEdge)

```python
@dataclass
class HyperEdge(GraphEdge):
    node_uids: list[str]  # N-ary endpoints (supersedes source_uid/target_uid)
```

Allows edges connecting 1, 2, or N nodes.

### 6.6 GraphCore Interface

```python
class GraphCore:
    def __init__(self, backend: StorageBackend)

    # Node operations
    def add_node(self, node: GraphNode) -> str
    def get_node(self, uid: str) -> GraphNode
    def update_node(self, uid: str, **updates) -> bool
    def delete_node(self, uid: str) -> bool
    def get_all_nodes(self) -> list[GraphNode]
    def count_nodes(self) -> int

    # Edge operations
    def add_edge(self, edge: GraphEdge) -> str
    def add_hyperedge(self, edge: HyperEdge) -> str
    def get_edge(self, uid: str) -> GraphEdge | HyperEdge
    def update_edge(self, uid: str, **updates) -> bool
    def delete_edge(self, uid: str) -> bool
    def get_all_edges(self) -> list[GraphEdge | HyperEdge]
    def count_edges(self) -> int

    # Query
    def query(self) -> QueryBuilder

    # Graph algorithms
    def bfs(self, start_uid: str, max_depth: int = 5) -> list[str]
    def dfs(self, start_uid: str, max_depth: int = 5) -> list[str]
    def find_path(self, source_uid: str, target_uid: str) -> list[str]
    def connected_components(self) -> list[set[str]]
    def centrality(self) -> dict[str, float]
    def clustering_coefficient(self) -> dict[str, float]
    def degree_distribution(self) -> dict[int, int]
    def hyper_path(self, start_uid: str, end_uid: str) -> list[list[str]]

    # Events
    def on_mutation(self, callback: Callable) -> None
    def emit_event(self, event_type: str, data: dict) -> None

    # Extensions
    def with_layer(self, layer: str) -> "GraphCore"
    def with_partition(self, partition_id: int) -> "GraphCore"
    def search(self, text: str) -> list[GraphNode]
    def get_subgraph(self, node_uids: set[str]) -> "GraphCore"
    def export(self, fmt: str) -> str

    # Stats
    def get_statistics(self) -> dict
```

### 6.7 Storage Backend Interface

```python
class StorageBackend(ABC):
    @abstractmethod
    def add_node(self, node: GraphNode) -> str
    @abstractmethod
    def get_node(self, uid: str) -> GraphNode | None
    @abstractmethod
    def update_node(self, uid: str, updates: dict) -> bool
    @abstractmethod
    def delete_node(self, uid: str) -> bool
    @abstractmethod
    def count_nodes(self) -> int

    @abstractmethod
    def add_edge(self, edge: GraphEdge) -> str
    @abstractmethod
    def get_edge(self, uid: str) -> GraphEdge | None
    @abstractmethod
    def update_edge(self, uid: str, updates: dict) -> bool
    @abstractmethod
    def delete_edge(self, uid: str) -> bool
    @abstractmethod
    def count_edges(self) -> int

    @abstractmethod
    def query(self, query: QuerySpec) -> list

    @abstractmethod
    def commit(self) -> None
    @abstractmethod
    def close(self) -> None
```

### 6.8 Migration Strategy

**Phase 1**: Create `genesis/graph_core/` package with GraphCore, unified models, MemoryBackend, and backward-compatible adapters for all 6 existing graph APIs.

**Phase 2**: Add SQLiteBackend (port from graphdb/), QueryBuilder (port from graph_v2/), and GraphAlgo (port from graphdb/ + graph_v2/).

**Phase 3**: Add HyperEdge support, temporal edges, probability (port from hypergraph.py).

**Phase 4**: Add layers, partitions, versioning, federation (port from graph_v2/).

**Phase 5**: Add domain typing, sub-graphs, subsystem sync (port from knowledge_graph.py + brain/graph.py).

**Phase 6**: Replace graph/engine.py internals with GraphCore, add EventBus adapter, deprecate old graph systems.

**Rollback**: Each phase is independently revertible. Old graph systems remain importable during migration.

---

## 7. Engineering Decisions

### 7.1 Why not pick an existing graph system as canonical?

**Rejected alternatives**:

1. **Pick graph_v2/ as canonical**: Most complete API but no persistence, no event hooks, no hyperedges, no text search, no consumers to verify against.

2. **Pick graphdb/ as canonical**: Best storage but no layers, partitions, hyperedges, event hooks. Schema is DDL-constrained — hard to extend.

3. **Pick graph/engine.py as canonical**: Has DI consumers but wraps UIRGraph which serves a different purpose (architecture analysis IR). No persistence, no layered model, limited query.

4. **Keep all 6 separate (status quo)**: ~3,250 lines of semantic duplication. Every new graph feature must be implemented 6 times.

**Decision**: Build Universal Graph Core that subsumes all 6, then make each existing system an adapter over it. This preserves backward compatibility while providing one canonical graph API.

### 7.2 Why not extract into a separate package?

The graph systems are deeply coupled to Genesis concepts (UIR, ontology, brain subsystems, EventBus). Extracting would require decoupling that is premature before the Universal Graph Core exists and is verified.

**Decision**: Keep inside genesis/ as `genesis.graph_core` for now. Extract after Phase 6 when all consumers have migrated.

### 7.3 Should hypergraph be a separate class?

Yes. HyperEdge is structurally different (N-ary endpoints, probability, temporal bounds). Making it a subclass of GraphEdge is cleaner than forcing N-ary into source_uid/target_uid.

**Decision**: HyperEdge as a subclass of GraphEdge with `node_uids: list[str]` field.

---

## 8. Technical Debt Impact

| System | Lines | Unique value | Duplication | Migration cost | Risk |
|--------|-------|-------------|-------------|----------------|------|
| graph/engine.py | 305 | Event hooks, DI, architecture analysis | Node/edge model, query API | Medium — needs adapter | Low (has consumers) |
| graph_v2/* | ~1,035 | Layers, partitions, versioning, federation, analytics | Node/edge model, query API | Medium — no consumers to break | Low |
| hypergraph.py | 648 | HyperEdge, probability, temporal | Node/edge model, query | High — unique hypergraph logic | Medium |
| knowledge_graph.py | 320 | Domain typing, sub-graph types | Node/edge model | Low — no consumers | Low |
| brain/graph.py | ~400 | Subsystem sync | Node/edge model, algorithms | Medium — sync logic is unique | Medium |
| graphdb/* | 835 | SQLite persistence, FTS, export | Node/edge model, algorithms, query | High — SQL schema migration | Medium |

**Total lines**: ~3,543 lines of graph code
**Duplication ratio**: ~60% (~2,125 lines duplicated)
**Migration**: 6 phases, each independently revertible

---

## 9. Validation

- **Existing tests**: All 2,763 tests must continue passing at each phase
- **No new test regressions**: Each phase adds tests alongside implementation
- **Backward compatibility**: Old import paths must work until final deprecation
- **Memory + SQLite consistency**: Both backends must produce identical query results for the same data

---

## 10. Next Steps

1. Phase 1 implementation: `genesis/graph_core/` with GraphNode, GraphEdge, GraphCore (MemoryBackend), backward-compatible adapters
2. Phase 2: SQLiteBackend + QueryBuilder + GraphAlgo
3. Phase 3: HyperEdge + temporal + probability
4. Phase 4: Layers + partitions + versioning + federation
5. Phase 5: Domain typing + sub-graphs + subsystem sync
6. Phase 6: graph/engine.py → GraphCore, deprecate old graph systems
7. Test suite run after each phase
8. Produce migration guide for any downstream code
