# M133 — Engineering Digital Twin

## File
`genesis/twin/digital_twin.py`, `genesis/twin/__init__.py`

## Purpose
Creates a live, continuously synchronized model of the repository. Every module, package, class, and function is auto-discovered and registered as an EngineeringObject. The twin watches for file changes and emits events on every scan.

## Key Components

### DigitalTwin
- `scan()` — walks all `*.py` files (excluding `.venv`, `__pycache__`, `.git`), parses AST for classes/functions/imports, registers as EngineeringObjects
- `start(interval)` — background thread that polls for file changes every N seconds
- `get_changed_files()` — MD5 hash comparison to detect file modifications
- `query()` — filtered search by module name, package, class, function, line count
- `summary()` — total modules, packages, lines, classes, functions, scan stats

### RepositoryModel
- `modules: dict[str, ModuleInfo]` — scanned module metadata
- `packages: list[str]` — discovered packages
- Aggregate counters (lines, files, classes, functions)

## Integration
- **FabricKernel.twin** — lazy-loaded property
- **EngineeringRegistry** — twin + each module registered as EngineeringObject
- **Events** — emits `twin.scan.completed` and `twin.files.changed`
- **AutomationEngine** — triggers knowledge refresh on file change

## Test Results
- Scanned 487 modules, 87 packages, ~120K lines, 1,651 classes, 8,725 functions
- Registry stats: 488 objects (1 repository + 487 modules)
- Query: `has_class=DigitalTwin` returns 2 modules
- All 259 tests pass
