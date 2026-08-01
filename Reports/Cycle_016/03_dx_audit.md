# Cycle 016 — Developer Experience (DX) Audit

## CLI & Entry Points

### Current State
- `genesis desktop` — launches TUI
- `genesis server` — launches FastAPI on :8377
- `genesis watch` — file watcher + auto-restart
- `genesis --help` — inline help text (hand-written, not argparse)
- `genesis <anything else>` — falls through to `genesis.cli.commands.CLI`

### Problems
1. **Hand-rolled help text** (__main__.py:36-42). No structured argument parsing. No tab completion. No `--version` flag.
2. **`ce` alias undocumented** — `genesis ce` works but is not listed in help.
3. **No console_scripts entry** in pyproject.toml — must use `python -m genesis`.
4. **Server port only configurable via env vars** — `GENESIS_HOST`, `GENESIS_PORT`. No `--port` flag.
5. **Startup produces no output** — no banner, no version, no "listening on port" message.
6. **Crash produces raw traceback** — no "run genesis desktop --help" guidance on error.

## Development Workflow

### Setup
```bash
pip install -e ".[dev,desktop,server]"
```
Works but no devcontainer, no nix flake, no Dockerfile for development.

### Testing
- 3,274 tests across 139 modules (35.6% coverage)
- `conftest.py` with 22 fixtures (Cycle 015)
- `pytest.ini` with markers
- ✅ `pytest -m desktop` works
- ✅ `pytest -m "not slow"` works

### Problems
1. **No hot-reload for desktop development** — must restart after every code change.
2. **No dev server** — `genesis server --reload` doesn't exist (uvicorn --reload not wired).
3. **No type checking in CI** — `mypy --strict genesis/` is not automated.
4. **No linting in CI** — `ruff` not automated.
5. **No pre-commit hooks** in repo.

## Code Quality

### Strengths
- Consistent naming conventions across storage layer (store_/query_/delete_ prefixes)
- Well-typed dataclasses with clear field names
- Thread safety with RLock in EventStore, EventRouter, ProviderRegistry
- Clean separation: AI abc → providers, Plugin manifest → manager → registry

### Weaknesses
1. **30+ `except Exception: pass` locations** — systemic silent failure.
2. **Bare `except:`** in 5 locations — catches KeyboardInterrupt and SystemExit.
3. **Cross-class private attribute access** — 10+ references to `_private` members.
4. **`__import__` for lazy loading** (kernel.py:158-160) — breaks IDE support and static analysis.
5. **`_message_to_dict` in wrong module** — shared utility lives in nvidia.py.
6. **`RuntimeError` name collision** — Genesis defines its own, shadowing Python built-in.
7. **Inconsistent commit strategy** in storage — some methods commit, most don't.
8. **No migration system** — SCHEMA_VERSION is recorded but never used.

### Code Duplication
- TimelineScreen ~80% duplicated from EngineeringMemoryExplorer (~124 lines shared)
- Reports filesystem scanning duplicated in screens.py and palette.py
- Event/Audit/Conversation/Tasks query logic duplicated across screens

## API Developer Experience

### Existing API
- 16 REST endpoints + 1 WebSocket
- Clean `/v1/` prefix, clear route names
- Auth middleware is well-structured

### API DX Problems
1. **No Pydantic models** for request validation — raw `Body(...)` with `dict[str, Any]`.
2. **No response model** — FastAPI auto-generates incorrect OpenAPI schema.
3. **No auto-generated documentation** — no Swagger UI customization.
4. **No CORS middleware** — prevents browser-based API exploration.
5. **No rate limiting** — any endpoint can be flooded.
6. **No request ID tracing** — impossible to correlate log entries across requests.
7. **No pagination metadata** — `total`, `next_page`, `prev_page` absent.
8. **Inconsistent response shapes** — some use `{"count": N, ...}`, others bare dicts.

## Plugin Developer Experience

### Existing
- `PluginManifest` with validation, YAML/JSON serialization
- `PluginManager` with lifecycle (register → load → activate)
- Hook system with event bus integration
- Sandbox for module isolation

### Plugin DX Problems
1. **No plugin template** — developers must write manifests from scratch.
2. **No plugin CLI** — `genesis plugin create my-plugin` doesn't exist.
3. **No documentation** — no developer guide for creating plugins.
4. **No example plugin** in the repository.
5. **Sandbox not enforced** — `validate_module` exists but is never called.
6. **No version resolution** — semver checking absent.
7. **No circular dependency detection** — A→B→A causes infinite loop.
8. **No dependency topological sort** — activation order is insertion order.

## Build & Deploy

| Concern | Status |
|---------|--------|
| pip installable | ✅ `pip install -e .` |
| pyproject.toml | ✅ Exists with extras |
| Version management | ❌ No `--version`, no `__version__` in package |
| Dockerfile | ❌ Missing |
| Docker compose | ❌ Missing |
| CI/CD | ❌ Not present in repo |
| Pre-commit | ❌ Missing |
| Dev container | ❌ Missing |
| Nix flake | ❌ Missing |

## DX Score: 4/10

| Dimension | Score | Key Issues |
|-----------|-------|------------|
| CLI & Entry Points | 3/10 | No argparse, no --version, no console_scripts, raw traceback |
| Dev Workflow | 4/10 | No hot-reload, no --reload, no pre-commit, no CI |
| Code Quality | 5/10 | Silent failures, private access, name collision, duplication |
| API DX | 4/10 | No Pydantic models, no CORS, no pagination, inconsistent shapes |
| Plugin DX | 3/10 | No templates, no CLI, no examples, no docs, sandbox not enforced |
| Build & Deploy | 2/10 | No Docker, no CI/CD, no version flag, no devcontainer |
