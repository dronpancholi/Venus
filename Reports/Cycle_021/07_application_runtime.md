# Application Runtime (M180)

**File:** `genesis/runtime/__init__.py`
**Tests:** 11

Production-grade application lifecycle with permissions, settings, notifications, dependency checks.

### API
```python
from genesis.runtime import AppRuntime

r = AppRuntime(kernel=kernel)
app = r.install("my_app", version="2.0.0",
                dependencies=["fabric", "ai"],
                permissions=["read:events", "write:engineering"])

r.start("my_app")     # checks deps first
r.set_setting("my_app", "theme", "dark")
r.notify("my_app", "Update", "New version available", severity="info")
r.stop("my_app")
r.uninstall("my_app")

# Check compatibility
issues = r.check_compatibility("my_app", "3.0.0")
```
