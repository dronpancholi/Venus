# Dependency Audit

## Audit Method
Scanned all `import` and `from ... import` statements across all `.py` files
in `genesis/` and `genesis/tests/`.

## Results

### Core Dependencies (3 packages)
| Package | Version | Used In | Purpose |
|---|---|---|---|
| `rich` | >=13 | setup, doctor, __main__, desktop | Terminal UI (tables, panels, prompts) |
| `textual` | >=8 | desktop/*.py | TUI framework for Desktop app |

### Optional Dependencies (4 packages)
| Package | Version | Extra Group | Used In |
|---|---|---|---|
| `fastapi` | >=0.100 | server | genesis/server.py |
| `uvicorn` | >=0.20 | server | genesis/server.py |
| `websockets` | >=10 | server | Pulled by FastAPI |
| `watchdog` | >=4 | watch, dev | genesis/dev.py |

### Test-Only Dependencies (4 packages)
| Package | Used In |
|---|---|
| `pytest` | All test files |
| `bcrypt` | test_laboratory.py |
| `jwt` (PyJWT) | test_laboratory.py |
| `sqlalchemy` | test_laboratory.py |

### Not Dependencies (false positives in string literals)
The following appear in triple-quoted source-code test strings but are
NOT dependencies of genesis:
- `@angular/core`, `@angular/common/http`
- `react`, `axios`, `rxjs`

### Issues Found and Fixed

**Fixed**: Self-referencing in `all` extras — `genesis[server]` and
`genesis[watch]` were referencing `genesis` itself as a dependency.

**Verified**: No unused packages in dependencies list.
**Verified**: No duplicate packages.
**Verified**: No conflicting version requirements.
**Verified**: All imports are guarded with proper try/except for optionals.

### Package Count
- Total third-party dependencies: **6** (2 core + 4 optional)
- Test-only dependencies: **4**
- Fits in a single `pip install` command
