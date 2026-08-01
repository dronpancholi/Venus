# Graph Unification Phase 2 — 3 New Adapters

**Theme:** Closing the final gaps in graph unification by wrapping 3 remaining graph systems.

---

## KnowledgeGraphAdapter

Wraps `genesis.knowledge_graph.PlanetaryKnowledgeGraph` — a planetary-scale knowledge graph with 6 sub-graphs (global, semantic, temporal, lineage, causal, evolution).

**Maps to:** PlanetaryKnowledgeGraph.global_graph for read/write operations.

**API coverage:** add_node, get_node, find_nodes, neighbors, node_count, edge_count, summary

**Limitations:** 
- Does not support `remove_node` / `remove_edge` (PKG is append-only)
- Uses only the global sub-graph for canonical operations

**Source:** `genesis/graph_core/engine.py:KnowledgeGraphAdapter`

---

## ExecutionGraphAdapter

Wraps `genesis.execution_graph.ExecutionGraph` — a DAG of runtime execution nodes and edges.

**Maps to:** ExecutionGraph nodes/edges directly.

**API coverage:** add_node, get_node, add_edge, get_edge, find_nodes, neighbors (successors/predecessors), node_count, edge_count, summary

**Limitations:**
- Does not support `remove_node` / `remove_edge` (ExecutionGraph is append-only)
- Node IDs are the ExecutionNode.name

**Source:** `genesis/graph_core/engine.py:ExecutionGraphAdapter`

---

## MetaGraphAdapter

Wraps `genesis.meta.graph.WorkspaceDependencyGraph` — a read-only dependency analysis graph derived from workspace repository data.

**API coverage:** edge_count, summary (read-only)

**Limitations:**
- **Fully read-only** — add_node, remove_node, add_edge, remove_edge all raise NotImplementedError
- Provides structural analysis (cycles, fan-in, fan-out, topological order) through summary

**Source:** `genesis/graph_core/engine.py:MetaGraphAdapter`

---

## Adapter Registration

All 3 adapters are registered in `FabricKernel._init_graph_registry()` at `genesis/fabric/kernel.py:402`:

```python
try:
    from genesis.knowledge_graph import PlanetaryKnowledgeGraph
    pkg = PlanetaryKnowledgeGraph()
    self._graph_registry.register_adapter(KnowledgeGraphAdapter(pkg))
except Exception:
    pass
try:
    from genesis.execution_graph import build_default_execution_graph
    exg = build_default_execution_graph()
    self._graph_registry.register_adapter(ExecutionGraphAdapter(exg))
except Exception:
    pass
try:
    from genesis.meta.workspace import Workspace
    from genesis.meta.graph import WorkspaceDependencyGraph
    ws = Workspace()
    wdg = WorkspaceDependencyGraph(ws)
    self._graph_registry.register_adapter(MetaGraphAdapter(wdg))
except Exception:
    pass
```

Each registration is wrapped in try/except for graceful degradation.
