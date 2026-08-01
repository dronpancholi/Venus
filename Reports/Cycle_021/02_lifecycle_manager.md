# Platform Lifecycle Manager (M175)

**File:** `genesis/lifecycle/__init__.py`
**Tests:** 14

Replaces scattered lifecycle management with one unified PlatformLifecycle.

### States
UNINITIALIZED → INIT → STARTING → READY ↔ PAUSED → STOPPING → STOPPED → SHUTDOWN
                                                      ↓
                                               RECOVERING → RESTARTING

### API
```python
pl = PlatformLifecycle(kernel=kernel)
pl.register("subsystem_name")
pl.boot()      # init → start → ready
pl.pause()     # ready → paused  
pl.resume()    # paused → ready
pl.stop()      # ready → stopped
pl.shutdown()  # any → shutdown
pl.recover()   # failed → boot
pl.upgrade()   # ready → ready (hooks)
pl.restart()   # shutdown → boot
```

### Signal Handling
Automatically installs SIGINT/SIGTERM handlers that call shutdown() gracefully.
