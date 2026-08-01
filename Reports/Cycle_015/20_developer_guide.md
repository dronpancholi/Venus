# Cycle 015 — Developer Guide

## Repository Layout

```
genesis/
├── __init__.py              # Package metadata
├── __main__.py              # CLI: genesis [desktop|server|watch]
├── ai/                      # AI providers & routing
├── core/                    # Core types, constants
├── desktop/                 # Textual desktop application (11 screens)
├── di/                      # Dependency injection (ServiceProvider)
├── engine/                  # Execution engine (TaskExecutor)
├── fabric/                  # Kernel, events, storage, discovery, scheduler
├── graph_v2/                # UnifiedGraph architecture
├── kernel/                  # Legacy kernel components
├── memory_system.py         # Universal memory system
├── persistence/             # SQLite storage stores
├── plugin/                  # Plugin management
├── server.py                # FastAPI + WebSocket server
└── services/                # Platform services
```

## Development Workflow

### Setup
```bash
pip install -e ".[dev,desktop,server]"
```

### Run
```bash
genesis desktop          # Textual UI
genesis server           # FastAPI on :8377
genesis watch            # File watcher
```

### Test
```bash
pytest                          # All tests
pytest -m desktop               # Desktop tests only
pytest -m "not slow"            # Skip slow tests
pytest tests/ -n auto           # Parallel (pytest-xdist)
```

### Code Style
- Typed: `mypy --strict genesis/`
- Formatted: `ruff format genesis/`
- 3,274 verified tests, 73 packages, 464 Python files

## Architecture Rules

1. **Dependency Rule**: Layer N may only depend on layers ≤ N
2. **Kernel Singleton**: `FabricKernel.instance()` — never instantiate directly
3. **Event Bus**: Cross-component communication via EventRouter, not direct imports
4. **Error Resilience**: Every data access in screens/widgets wrapped in try/except
5. **Keyboard First**: Every action must have a keyboard shortcut

## Adding a New Screen

1. Create class in `genesis/desktop/screens.py`
2. Add to `SCREENS` dict in `app.py`
3. Add `action_go_<name>()` to `app.py`
4. Add keyboard binding in `app.py` if needed
5. Add palette command in `palette.py`
6. Add `_subscribe_events()` for live updates
7. Add 30s timer fallback in `on_mount`

## Debugging

- `genesis server` then `curl http://127.0.0.1:8377/v1/health`
- Textual dev tools: `genesis desktop --dev`
- Watch mode: `genesis watch` (auto-restarts on file change)
