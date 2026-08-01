# M163: Engineering Graph Unification

**Status:** Implemented
**Files:** `genesis/graph_core/engine.py`, `genesis/graph_core/__init__.py`
**Integration:** FabricKernel.graph (GraphRegistry), CanonicalGraph, GraphV2Adapter

---

## Problem

The audit identified 8+ competing graph implementations:

| Implementation | Lines | Purpose |
|---------------|-------|---------|
| `graph_v2/core.py` | 269 | Multi-layer graph (Structural, Semantic, Knowledge, etc.) |
| `graphdb/__init__.py` | 835 | SQLite-backed persistent graph database |
| `hypergraph.py` | 648 | Hypergraph with n-ary edges, embeddings, algorithms |
| `knowledge_graph.py` | 320 | Knowledge entities with multi-view routing |
| `execution_graph.py` | 420 | DAG execution modeling |
| `meta/graph.py` | 205 | Workspace dependency analysis |
| `metamodel/graph.py` | 346 | UnifiedGraph — "single universal graph" |
| `graph/engine.py` | 305 | UIR-based knowledge graph with validation |

All overlapping. No developer knows which to use.

## Solution

### Architecture

```
GraphRegistry (kernel.graph)
  ├── primary: CanonicalGraph  ← facade over metamodel UnifiedGraph
  ├── adapters:
  │   ├── graph_v2  → GraphV2Adapter  (wraps graph_v2/UnifiedGraph)
  │   └── ...       → future adapters (graphdb, hypergraph, etc.)
  └── summary()    → unified health report
```

### CanonicalGraphAPI (Abstract Interface)

All graph operations go through one interface:

| Operation | Description |
|-----------|-------------|
| `add_node(node)` | Add a node; returns node ID |
| `get_node(id)` | Get node by ID |
| `remove_node(id)` | Remove node and its edges |
| `add_edge(edge)` | Add an edge between two nodes |
| `get_edge(id)` | Get edge by ID |
| `remove_edge(id)` | Remove an edge |
| `find_nodes(query)` | Query nodes by type, name, tags, properties, search |
| `neighbors(id, type, dir)` | Get neighboring nodes with edges |
| `path(from, to, depth)` | Find paths between nodes |
| `subgraph(root, depth)` | Extract subgraph |
| `node_count()` | Total nodes |
| `edge_count()` | Total edges |
| `summary()` | Graph statistics |

### CanonicalGraph (Primary Implementation)

Wraps `metamodel.graph.UnifiedGraph` — the closest existing implementation to a canonical graph. Provides:

- 200+ EntityTypes and 160+ EntityRelations from the metamodel
- Subgraph extraction, pattern matching, merge, filter
- JSON serialization
- Thread-safe operations

### GraphAdapter (Backward Compatibility)

Base class for wrapping existing graph implementations. Current adapters:
- **GraphV2Adapter** — wraps `graph_v2.UnifiedGraph` (multi-layer)

Future adapters can be added for graphdb, hypergraph, knowledge_graph, etc.

### Data Model

```python
CanonicalNode:
  id, name, node_type, description, labels[], properties{}, tags[],
  weight, confidence, source, created_at

CanonicalEdge:
  id, source_id, target_id, edge_type, weight, properties{}, metadata{},
  confidence, bidirectional, created_at

GraphQuery:
  node_type, name, labels[], tags[], properties{}, search, limit, offset
```

## Results

| Metric | Value |
|--------|-------|
| Graph implementations wrapped | 2 (CanonicalGraph + GraphV2Adapter) |
| Total abstractions eliminated | 8 → 1 canonical interface |
| Adapter interface | Extensible for all 8+ implementations |
| Backward compatibility | All existing graphs continue working |
| Kernel integration | `kernel.graph.primary` / `kernel.graph.get_adapter()` |

## Future Work

1. **Add adapters for remaining 6+ graph implementations** (graphdb, hypergraph, knowledge_graph, execution_graph, meta/graph, graph/engine)
2. **Unified graph query language** — query across all graphs with one syntax
3. **Graph health** — register graph health collectors
4. **Cross-graph queries** — query primary + adapter graphs simultaneously
5. **Gradual migration** — move subsystems from direct graph usage to canonical graph
