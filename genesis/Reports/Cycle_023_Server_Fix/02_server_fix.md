# Server Startup Fix — Details

---

## Before

`genesis/__main__.py:192-193`:

```python
k = FK.instance()
rprint(f"  [dim]Status: {k.health().status} | "
       f"{k.health().services} services | {k.health().messages} messages[/dim]")
```

Three problems:
1. `.services` does not exist on `ServiceHealth` (field is `services_count`)
2. `.messages` does not exist on `ServiceHealth` (field is `messages_sent`)
3. `k.health()` called 3 times instead of once (wasteful, potentially racy)

---

## After

`genesis/__main__.py:192-194`:

```python
k = FK.instance()
h = k.health()
rprint(f"  [dim]Status: {h.status} | "
       f"{h.services_count} services | {h.messages_sent} messages[/dim]")
```

Fixes:
1. `.services_count` — correct field name
2. `.messages_sent` — correct field name
3. Single `health()` call with cached result

---

## Backward Compatibility

Added `__getattr__` to `ServiceHealth` in `genesis/fabric/discovery.py`:

```python
def __getattr__(self, name: str) -> Any:
    mapping = {"services": self.services_count, "messages": self.messages_sent}
    if name in mapping:
        return mapping[name]
    raise AttributeError(...)
```

This ensures any other callers using `.services` or `.messages` continue working until they can be updated.

---

## Server Startup Sequence (Fixed)

```
cmd_serve([])
  ├── _banner()                    # Print "Genesis — Engineering Computing Platform"
  ├── _ensure_config()             # Load config (no-op if exists)
  ├── _auto_setup_if_needed()      # Silent default setup if first run
  ├── kernel.boot()                # Boot all subsystems
  ├── Print banner message         # "Genesis started."
  ├── h = kernel.health()          # ← FIXED: single call, correct fields
  ├── rprint status line           # "running | 0 services | 0 messages"
  └── run_server()                 # ← now reached without AttributeError
        ├── GenesisAPI()           # Wrap kernel in FastAPI
        ├── api.create_app()       # Register routes, lifespan
        └── uvicorn.run(app)       # Bind to 127.0.0.1:8080
```

---

## What Changed

| File | Lines | Δ |
|------|-------|---|
| `genesis/__main__.py` | 192-194 | Fixed field names, single health() call |
| `genesis/fabric/discovery.py` | 22-26 | Added __getattr__ backward compat |
| `genesis/tests/test_server.py` | 103-142 | Added 4 new regression tests |
