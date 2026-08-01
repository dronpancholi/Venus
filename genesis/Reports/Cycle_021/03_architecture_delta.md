# Architecture Delta — Cycle 020 → Cycle 021

---

## Files Changed

| File | Lines | Change |
|------|-------|--------|
| `genesis/graph_core/engine.py` | +230 | 3 new adapter classes + _resolve_graph helper |
| `genesis/graph_core/__init__.py` | +3 | Export 3 new adapters |
| `genesis/fabric/kernel.py` | +19 | Import + register 3 new adapters |
| `genesis/metamodel/query.py` | +10 | _resolve_graph helper + type loosen |
| `genesis/datalake/__init__.py` | +14 | _resolve_graph helper + type loosen |
| `genesis/Reports/Cycle_021/` | 7 files | Cycle 021 reports |

---

## Adapter Architecture

```
kernel.graph (GraphRegistry)
├── primary → CanonicalGraph (wraps metamodel.UnifiedGraph)
├── graph_v2 → GraphV2Adapter (wraps graph_v2.UnifiedGraph)
├── hypergraph → HypergraphAdapter (wraps hypergraph.Hypergraph)
├── graphdb → GraphDBAdapter (wraps graphdb.PersistentGraphDB)
├── knowledge_graph → KnowledgeGraphAdapter (wraps PlanetaryKnowledgeGraph)  ← NEW
├── execution_graph → ExecutionGraphAdapter (wraps ExecutionGraph)           ← NEW
└── meta_graph → MetaGraphAdapter (wraps WorkspaceDependencyGraph)           ← NEW
```

---

## Migration Verdict

| Graph System | Has Adapter? | Used by kernel.graph? |
|-------------|-------------|----------------------|
| metamodel.UnifiedGraph | ✓ Primary | ✓ |
| graph_v2.UnifiedGraph | ✓ GraphV2Adapter | ✓ |
| hypergraph.Hypergraph | ✓ HypergraphAdapter | ✓ |
| graphdb.PersistentGraphDB | ✓ GraphDBAdapter | ✓ |
| knowledge_graph.PlanetaryKnowledgeGraph | ✓ KnowledgeGraphAdapter | ✓ |
| execution_graph.ExecutionGraph | ✓ ExecutionGraphAdapter | ✓ |
| meta.graph.WorkspaceDependencyGraph | ✓ MetaGraphAdapter | ✓ |
| graph.engine.KnowledgeGraphEngine | ✗ (standalone) | ✗ (different API) |
| intelligence.kgraph.KnowledgeGraph | ✗ (different lib) | ✗ |

Every graph system with a comparable API now has a canonical adapter.
