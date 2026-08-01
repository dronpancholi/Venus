# Build System Audit

## Issue: Incorrect build backend

**Before**:
```toml
build-backend = "setuptools.backends._legacy:_Backend"
```

This backend does not exist in modern setuptools. It produces:
```
BackendUnavailable: Cannot import 'setuptools.backends._legacy'
```

**After**:
```toml
build-backend = "setuptools.build_meta"
```

## Issue: Self-referencing optional dependencies

**Before**:
```toml
all = [
    "genesis[server]",
    "genesis[watch]",
    "watchdog>=4",
]
```

A package should never depend on itself. This creates circular resolution
issues with some package managers.

**After**:
```toml
[project.optional-dependencies]
desktop = ["textual>=8"]
server = ["fastapi>=0.100", "uvicorn>=0.20", "websockets>=10"]
watch = ["watchdog>=4"]
dev = ["watchdog>=4"]
all = [
    "rich>=13",
    "textual>=8",
    "fastapi>=0.100",
    "uvicorn>=0.20",
    "websockets>=10",
    "watchdog>=4",
]
```

## Verified Installations

| Method | Result |
|---|---|
| `pip install -e .` | ✓ Success |
| `pip install -e ".[all]"` | ✓ Success |
| Clean venv, `pip install -e .` | ✓ Success |
| Clean venv, `pip install -e ".[all]"` | ✓ Success |

## Dependencies

**Core** (always installed): rich, textual
**Optional**: fastapi, uvicorn, websockets, watchdog
**Test-only**: pytest (not in pyproject.toml — user installs separately)

Total third-party packages: 6
