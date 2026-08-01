# Phase 0 Delta: Test Infrastructure

**Directory:** `tests/` + `tests/programs/` — 98 test files  
**Total tests:** 3,274 (baseline from Cycle 013), ~10,709 (census count including UED)  
**pytest version:** 9.0.3

## Test Organization

```
tests/
  test_kernel.py          — 159 tests, 17 classes (FabricKernel, EventRouter, SecurityManager, etc.)
  test_genesis_xii.py     — 145 tests, 30 classes
  test_meta.py            — 130+ tests, 16 classes
  test_brain.py           — 77 tests, 7 classes
  test_cognition.py       — 81 tests, 11 classes
  test_acquisition.py     — 69 tests, 6 classes
  test_server.py          — 10 tests, 1 class (GenesisAPI REST routes)
  ...

tests/programs/
  test_brain_v4.py        — Higher-level program tests
  test_civilization_v2.py
  test_engineering_os.py
  test_platform_v2.py
  ...
```

## Test Patterns

- **No conftest.py** — zero shared fixtures at any level
- **xunit style** — `setup_method` for per-test initialization
- **Singleton reset pattern** — `FabricKernel._instance = None; kernel = FabricKernel.instance()` repeated in 10+ files
- **FastAPI TestClient** created inline in each test method
- **Value-based assertions** — `assert resp.status_code == 200`, `assert data["status"] == "running"`
- **Network tests exist** — `test_acquisition.py` fetches from GitHub, NPM, PyPI, Cargo

## Coverage Gaps

| Package | Files | Lines | Tests | Maturity |
|---------|-------|-------|-------|----------|
| `genesis.desktop` | 4 | 2,486 | 0 | 0.52 |
| `genesis.plugin` | 3 | 368 | 0 | 0.58 |
| `genesis.api` | 2 | 197 | 0 | 0.52 |
| `genesis.autonomous` | 3 | 330 | 0 | 0.33 |
| `genesis.events` | 2 | 104 | 0 | 0.52 |
| `genesis.di` | 4 | 525 | 0 | 0.58 |
| `genesis.compiler` | 13 | 950 | 0 | 0.58 |

## Findings

1. **No test configuration** — no `pytest.ini`, `pyproject.toml`, or `setup.cfg` with pytest config
2. **No fixtures anywhere** — every test file self-contains setup logic, leading to massive code duplication
3. **Singleton pattern hinders testability** — `FabricKernel._instance = None` pattern is fragile (tests must run sequentially, shared state leaks between tests)
4. **0 desktop tests** — no Textual `pilot` tests, no screen/widget unit tests
5. **0 auth tests** — SecurityManager, token lifecycle, auth middleware untested
6. **0 WebSocket tests** — `test_server.py` tests REST only
7. **Census counts may be inflated** — some census-cataloged "tests" may include non-test code

## Recommendations

1. Add `conftest.py` with shared fixtures: `clean_kernel()`, `api_client()`, `test_provider()`
2. Add `pytest.ini` with test discovery paths and markers (`desktop`, `integration`, `slow`)
3. Replace `_instance = None` pattern with `FabricKernel.reset_test_instance()` classmethod
4. Create `test_desktop.py` using Textual's `pilot` for screen navigation and widget render tests
5. Create `test_security.py` for SecurityManager and auth middleware
6. Add WebSocket test client to `test_server.py`
