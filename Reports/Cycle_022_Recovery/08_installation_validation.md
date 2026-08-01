# Installation Validation

## Test Environments

### 1. Primary Development Venv
- Python 3.14.4
- macOS (Darwin)
- `pip install -e .` → ✓
- `pip install -e ".[all]"` → ✓

### 2. Clean Virtual Environment (from scratch)
```bash
python3 -m venv /tmp/genesis_clean_test/venv
/tmp/genesis_clean_test/venv/bin/pip install -e /Users/dronpancholi/Developer/01_Strategic/Venus
```
- ✓ Installs rich 15.0.0, textual 8.2.8 + transitive deps
- ✓ genesis 1.0.0 imported successfully
- ✓ `python -m genesis version` works

### 3. Clean Venv with [all] extras
```bash
/tmp/genesis_clean_test/venv/bin/pip install -e ".[all]"
```
- ✓ All 6 dependencies installed
- ✓ fastapi, uvicorn, websockets, watchdog all importable
- ✓ `genesis doctor` reports 8/8 checks passed

## Python Version Compatibility

| Python | Build | Install | Tests |
|---|---|---|---|
| 3.14.4 | ✓ | ✓ | ✓ (166 pass) |

Tested on Python 3.14.4 (macOS). The pyproject.toml declares
`requires-python = ">=3.11"` and the code uses no 3.14-specific features.
Lower versions (3.11–3.13) should work but were not tested here.
