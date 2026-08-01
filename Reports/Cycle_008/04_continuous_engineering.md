# CYCLE 008 — CONTINUOUS ENGINEERING REPORT

## Watchers on the Fabric

**Files:** `genesis/watch/__init__.py`, `genesis/tests/test_watch.py`

⸻

## Purpose

Continuous Engineering watches the real workspace and feeds observations back into the
Genesis Fabric. Every file change, git commit, or provider status transition becomes
an EngineeringEvent that agents, memory, and the UI can react to.

## Components

### FilesystemWatcher

Polls a directory tree (configurable interval, default 5s). Computes SHA-256 truncated
to 16 hex chars per file. Emits events when checksums change.

- `EventType.CHANGE` — file modified
- `EventType.CREATE` — file appeared
- `EventType.DELETE` — file disappeared
- Ignores `.git/`, `__pycache__/`, `.DS_Store`, `node_modules/`

### GitWatcher

Watches a git repository by polling `HEAD` commit hash. Emits:

- `EventType.COMMIT` — new commit
- `EventType.BRANCH_CHANGE` — `git diff --stat` between old/new HEAD

### ProviderWatcher

Checks AI provider health via `ProviderRegistry.check_health()`. Emits:

- `EventType.STATUS_CHANGE` — provider up/down/unhealthy

### ContinuousEngineering

Compositor that starts/stops all watchers on a FabricKernel. Manages lifecycle:

```python
ce = ContinuousEngineering(kernel)
ce.start()  # starts all watchers
ce.stop()   # stops all watchers
ce.status()  # returns watcher states
```

## Architecture

```
ContinuousEngineering
├── FilesystemWatcher ──→ fabric.kernel.emit(CHANGE)
├── GitWatcher ──────────→ fabric.kernel.emit(COMMIT)
└── ProviderWatcher ─────→ fabric.kernel.emit(STATUS_CHANGE)
```

All events carry `source="watcher"` and appropriate tags for filtering.

## Tests (8)

- `test_filesystem_watcher_detect_change`
- `test_filesystem_watcher_ignore_patterns`
- `test_git_watcher_detect_commit`
- `test_git_watcher_no_change`
- `test_provider_watcher_status_change`
- `test_provider_watcher_no_change`
- `test_continuous_engineering_start_stop`
- `test_continuous_engineering_status`

## Future

- **Watch expression DSL** — watch specific files/patterns
- **Reactive actions** — trigger agents on file change
- **Dependency watcher** — detect outdated deps in real-time
- **Build watcher** — watch compilation/test results
