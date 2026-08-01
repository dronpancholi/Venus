# Subsystem Migration to Canonical Graph API

**Theme:** Migrating consumers from tight coupling to framework-agnostic graph injection.

---

## Migration Pattern

Two types of consumers were migrated:

### 1. Files Using `UnifiedGraph` Directly (metamodel/datalake)

These files accept a `UnifiedGraph` in their constructor. The migration adds a `_resolve_graph()` helper that accepts either `UnifiedGraph` or `CanonicalGraphAPI`:

```python
def _resolve_graph(graph: Any) -> UnifiedGraph:
    if isinstance(graph, UnifiedGraph):
        return graph
    if hasattr(graph, 'unified_graph'):
        return graph.unified_graph
    raise TypeError(...)
```

### 2. Files Using `KnowledgeGraphEngine` (CLI/diagnostics/studio/integration)

These files use KnowledgeGraphEngine-specific APIs (export_cypher, export_graphml, detect_circular_dependencies, etc.) not available on CanonicalGraphAPI. Migration deferred — these continue to work with their existing engine.

---

## Migrated Files

| File | Change | Line |
|------|--------|------|
| `genesis/metamodel/query.py` | EntityQuery.__init__ accepts CanonicalGraphAPI | 36 |
| `genesis/datalake/__init__.py` | VersionedStore.set_graph + DataLakeManager accept CanonicalGraphAPI | 180, 459 |

---

## Migration Pattern Reference

For NEW code:
```python
# Preferred — get canonical graph from kernel
from genesis.fabric.kernel import FabricKernel
graph = FabricKernel.instance().graph.primary

# Accept either type in constructor
class MyConsumer:
    def __init__(self, graph):
        self._graph = _resolve_graph(graph)  # handles both types
```

For existing KnowledgeGraphEngine consumers — add optional graph injection:
```python
def __init__(self, graph=None):
    self.graph = graph or KnowledgeGraphEngine()
```

---

## Files Awaiting Migration

| File | Import | Reason Deferred |
|------|--------|-----------------|
| `cli/commands.py` | KnowledgeGraphEngine | Uses export_cypher/export_graphml |
| `diagnostics/diagnostics.py` | KnowledgeGraphEngine | Uses .graph.edges/.graph.nodes directly |
| `studio/backend.py` | KnowledgeGraphEngine | Uses summary/find_nodes — easy target |
| `integration/project31a.py` | KnowledgeGraphEngine | Uses detect_circular_dependencies, .graph.edges |
| `intelligence/metrics.py` | intelligence.kgraph.KnowledgeGraph | Different API entirely |
| `platform.py` | Multiple graphs | Strategic migration deferred to Cycle 022 |
