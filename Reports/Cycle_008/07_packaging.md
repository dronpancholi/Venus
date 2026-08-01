# CYCLE 008 — PACKAGING REPORT

## Genesis pip-installable

**File:** `pyproject.toml`

⸻

## Purpose

Make Genesis installable with a single command: `pip install genesis`

## Configuration

| Field | Value |
|-------|-------|
| Build system | setuptools |
| Python | ≥3.12 |
| Core deps | rich, textual |
| Server deps | fastapi, uvicorn, websockets |
| Watch deps | watchdog |
| All deps | core + server + watch |

## Install Options

```bash
# Core (desktop TUI only)
pip install genesis

# With API server
pip install genesis[server]

# With watchers
pip install genesis[watch]

# Everything
pip install genesis[all]
```

## Entry Points

| Command | Entry | Description |
|---------|-------|-------------|
| `genesis` | `genesis.__main__:main` | CLI entry (no args shows help) |
| `genesis-desktop` | `genesis.desktop:main` | Desktop TUI |
| `genesis-server` | `genesis.server:main` | API server |

## CLI Commands

```bash
python -m genesis               # CLI help
python -m genesis desktop       # Start Textual TUI
python -m genesis server        # Start FastAPI server
python -m genesis watch         # Start Continuous Engineering
python -m genesis --help        # Show help
```

## Running from Source

```bash
PYTHONPATH=/path/to/genesis:$PYTHONPATH /venv/bin/python -m genesis desktop
```

## Versioning

- First release: `0.1.0` (alpha)
- Follows SemVer
- Version in `pyproject.toml` (single source of truth)
- Future: `genesis --version` shows package version
