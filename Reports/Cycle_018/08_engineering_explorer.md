# M135 — Engineering Explorer

## File
`genesis/explorer/engine.py`, `genesis/explorer/__init__.py`

## Purpose
Relationship-based intelligent navigation across engineering objects. Follows EngineeringObject.relationships to build connected graphs, find paths between objects, and discover object networks.

## Key Components

### EngineeringExplorer
- `explore(object_id, max_depth=2)` — BFS traversal from a starting object, collecting all relationships and connected objects
- `explore_by_type(object_type, limit=20)` — explore all objects of a given type
- `find_path(source_id, target_id, max_depth=5)` — shortest path between two objects via BFS

### ExplorationResult
- `source_id`, `source_name`, `source_type` — starting object info
- `relationships` — list of all relationship edges found
- `connected_objects` — all objects reached during traversal
- `total_connections` — count of connections found

## Integration
- **FabricKernel.explorer** — lazy-loaded, auto-booted
- **EngineeringRegistry** — source of all objects and their relationships
- **Desktop** — can power the Entity Explorer (KnowledgeGraphScreen) with live relationship data
