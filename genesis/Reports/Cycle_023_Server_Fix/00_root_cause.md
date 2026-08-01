# Root Cause Analysis — Server Startup Failure

**Date:** 2026-07-06
**Impact:** `genesis serve` reached application initialization but failed before uvicorn started
**Error:** `AttributeError: 'ServiceHealth' object has no attribute 'services'`

---

## The Bug

### Symptom

```
% genesis serve
Genesis — Engineering Computing Platform

Genesis started.

  Web:      http://127.0.0.1:8080/
  Desktop:  http://127.0.0.1:8080/desktop
  API:      http://127.0.0.1:8080/docs
  WebSocket: ws://127.0.0.1:8080/v1/ws

Traceback (most recent call last):
  ...
AttributeError: 'ServiceHealth' object has no attribute 'services'
```

The server banner printed successfully, but the status line at `__main__.py:193` crashed before `run_server()` was called.

### Root Cause

`genesis/__main__.py:192-193` accessed `.services` and `.messages` on a `ServiceHealth` object:

```python
k = FK.instance()
rprint(f"  [dim]Status: {k.health().status} | "
       f"{k.health().services} services | {k.health().messages} messages[/dim]")
```

The `ServiceHealth` dataclass in `genesis/fabric/discovery.py` defines the field as `services_count` (not `.services`) and `messages_sent` (not `.messages`):

```python
@dataclass
class ServiceHealth:
    status: str = "unknown"
    uptime_seconds: float = 0.0
    services_count: int = 0       # was accessed as .services
    messages_sent: int = 0        # was accessed as .messages
    active_sessions: int = 0
    threads: int = 0
    last_heartbeat: float = 0.0
    errors: list[str] = field(default_factory=list)
```

### Why It Was Missed

1. **No backward compatibility** — `ServiceHealth` had no aliases for `.services` or `.messages`
2. **No regression test for `genesis serve`** — the `test_server.py` suite tested individual API endpoints but never exercised the full `cmd_serve()` startup path
3. **API drift** — `KernelStats` (returned by `kernel.stats()`) has `.services` but `ServiceHealth` (returned by `kernel.health()`) uses `.services_count`. The similarity between the two classes caused confusion.

---

## Fix Applied

### 1. Fix the caller (`__main__.py`)

```python
# Before (crashed):
rprint(f"  [dim]Status: {k.health().status} | "
       f"{k.health().services} services | {k.health().messages} messages[/dim]")

# After (fixed):
h = k.health()
rprint(f"  [dim]Status: {h.status} | "
       f"{h.services_count} services | {h.messages_sent} messages[/dim]")
```

### 2. Add backward compatibility (`fabric/discovery.py`)

Added `__getattr__` to `ServiceHealth` so existing `.services` and `.messages` accessors continue working:

```python
def __getattr__(self, name: str) -> Any:
    mapping = {"services": self.services_count, "messages": self.messages_sent}
    if name in mapping:
        return mapping[name]
    raise AttributeError(...)
```

### 3. Add regression tests (`test_server.py`)

- `test_startup_path_no_attribute_error` — validates all attribute names exist and backward compat works
- `test_docs_endpoint_responds` — verifies `/docs` responds
- `test_openapi_json` — verifies OpenAPI schema
- `test_full_serve_cmd_no_exception` — exercises the full `cmd_serve()` path with mocked uvicorn

---

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `genesis/__main__.py` | Fixed `.services` → `.services_count`, `.messages` → `.messages_sent` | 3 |
| `genesis/fabric/discovery.py` | Added `__getattr__` backward compatibility | 5 |
| `genesis/tests/test_server.py` | Added 4 regression tests | 40 |
