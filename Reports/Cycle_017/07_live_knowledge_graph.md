# M127: Live Knowledge Graph

> Status: **Designed** (foundation built)
> Enablers: M121 (EngineeringObject types + relationships), M122 (KnowledgeEngine nodes), M125 (Timeline)

---

## Architecture

Every EngineeringObject is a graph node. Every link and relationship is an edge. The graph is always live — adding an object or relationship immediately updates the navigable structure.

```
Knowledge Graph Node (EngineeringObject)
├── id, type, name
├── relationships → typed edges to other nodes
├── links → knowledge/memory/conversations/tasks/events/graph
├── health/quality/risk → live scores
└── timeline entries → chronological history
```

## Implementation Path

1. `KnowledgeGraphEngine` wraps EngineeringRegistry as a graph:
   - Objects → nodes
   - Relationships → edges
   - Timeline entries → node history
2. Desktop `KnowledgeGraphScreen` (currently Tree-based) becomes a live graph viewer
3. Clicking any node opens: history, relationships, timeline, reports, memory, AI summary, tasks, conversations, files, dependencies, architecture, health, recommendations
4. GraphV2 analytics (centrality, path analysis) can be wired into node display

## Existing Foundation

- EngineeringRegistry has all objects + relationships + links
- KnowledgeEngine has 916 knowledge nodes with entity relationships
- KnowledgeGraphScreen already uses Tree widget for entity browsing
- GraphV2 has traversal, analytics, federation ready (1,765 lines, test-verified)
