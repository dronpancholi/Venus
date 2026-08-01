# Production Hardening (M188)

**File:** `genesis/hardening/__init__.py`
**Tests:** 16

Platform-wide quality improvements: typed errors, structured logging, safe/retry patterns.

### Error Hierarchy
```
GenesisError → LifecycleError
            → ResourceError
            → ContractError
            → QueryError
            → DataError
```

### Logger
```python
from genesis.hardening import Logger, get_logger

logger = get_logger(kernel=kernel)
logger.info("Platform booted", subsystem="lifecycle")
logger.warning("High memory usage", subsystem="resources")
logger.error("Provider unavailable", subsystem="ai")

logger.recent(limit=20)  # last N entries
logger.export()          # all entries as dicts
```

### Decorators
```python
from genesis.hardening import safe, retry

@safe("risky_operation", logger=logger)
def might_fail(): ...

@retry(max_attempts=3, delay=1.0, logger=logger)
def flaky_operation(): ...
```
