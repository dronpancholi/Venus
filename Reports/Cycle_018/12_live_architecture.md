# M140 — Live Architecture Engine

## File
`genesis/architecture/engine.py`, `genesis/architecture/__init__.py`

## Purpose
Executable architecture model derived from source code analysis. Parses Python AST to extract classes, functions, and their dependencies as a live graph.

## Key Components

### LiveArchitectureEngine
- `scan(root)` — walks directory tree, parses all `.py` files with AST
  - Extracts classes (with method counts)
  - Extracts functions (top-level)
  - Extracts call dependencies (function calls, attribute accesses)
- `get_dependents(node_name)` — what depends on this node
- `get_dependencies(node_name)` — what this node depends on
- `summary()` — node/edge counts by type

### ArchitectureNode
- `name`, `type` (class/function), `filepath`, `depends_on`, `provided_by`, `metrics`

### ArchitectureEdge
- `source`, `target`, `relationship`, `weight`

## Performance
Scanned the entire Genesis codebase (487 Python files) in under 2 seconds. Extracted 2,541 architecture nodes.

## Integration
- **FabricKernel.live_architecture** — lazy-loaded, auto-booted
- **EngineeringRegistry** — registered as SERVICE object
- **DigitalTwin** — provides file discovery for scanning
