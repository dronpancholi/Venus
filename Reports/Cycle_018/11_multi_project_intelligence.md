# M139 — Multi-Project Intelligence

## File
`genesis/multi_project/engine.py`, `genesis/multi_project/__init__.py`

## Purpose
Cross-project intelligence platform. Manages multiple registered projects, scans their source code metrics, and provides comparison across projects.

## Key Components

### MultiProjectIntelligence
- `register_project(name, root)` — register a project by name and filesystem path
- `scan_project(name)` — analyze Python source: modules, lines, classes, functions
- `list_projects()` — all registered projects with metrics
- `compare(name_a, name_b)` — side-by-side comparison with differences

### ProjectInfo
- `name`, `root`, `modules`, `lines`, `classes`, `functions`, `last_scanned`

## Integration
- **FabricKernel.multi_project** — lazy-loaded, auto-booted
- **EngineeringRegistry** — each project registered as REPOSITORY object
