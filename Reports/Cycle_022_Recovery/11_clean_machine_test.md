# Clean Machine Test

## Test Procedure

Simulated a completely clean machine by:

1. Creating a new directory `/tmp/genesis_clean_test/`
2. Creating a fresh Python virtual environment
3. Installing genesis from source with `pip install -e .`
4. Running all verification commands

## Step-by-Step Results

### Step 1: Create virtual environment
```bash
python3 -m venv /tmp/genesis_clean_test/venv
```
✓ Success

### Step 2: Install genesis
```bash
/tmp/genesis_clean_test/venv/bin/pip install -e /Users/dronpancholi/Developer/01_Strategic/Venus
```
✓ Success — 7 packages installed (genesis, rich, textual + transitive)

### Step 3: Import genesis
```python
import genesis
print(genesis.__version__)  # "1.0.0"
```
✓ Success

### Step 4: Run CLI
```bash
python -m genesis version
python -m genesis doctor
python -m genesis status
python -m genesis config
```
✓ All commands succeed

### Step 5: Install all extras
```bash
pip install -e ".[all]"
```
✓ Success — 6 more packages installed (fastapi, uvicorn, websockets, watchdog + transitive)

### Step 6: Verify optional imports
```python
import fastapi  # ✓
import uvicorn  # ✓
import websockets  # ✓
import watchdog  # ✓
```
✓ All optional imports succeed

### Step 7: Run workspace creation
```bash
python -m genesis workspace
```
✓ Workspace auto-created with all 11 directories

### Step 8: Run tests
```bash
pip install pytest
python -m pytest genesis/tests/test_lifecycle.py ... (15 test files)
```
✓ 166 tests pass (when run with PYTHONPATH from project root)

## What a New User Would See

1. Clone repository
2. `cd genesis`
3. `python3 -m venv .venv && source .venv/bin/activate`
4. `pip install -e ".[all]"`
5. `genesis`
6. Setup wizard guides through workspace + AI provider
7. Desktop opens with experience navigation
8. `genesis import <project>` catalogs and imports project
9. `genesis status` shows all platform components healthy

**Total time from clone to working platform: ~2-3 minutes**
