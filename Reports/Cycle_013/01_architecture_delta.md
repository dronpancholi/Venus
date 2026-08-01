# CYCLE 013 — ARCHITECTURE DELTA

---

## DATA FLOW: BEFORE (Cycle 012)

```
Timer (1-10s) → Widget/Screen → FabricKernel.instance().stats/events/agents → poll data
```

Every widget had a `set_interval` timer that fired continuously regardless of whether data had changed. 20 concurrent timers, many reading the same kernel properties.

## DATA FLOW: AFTER (Cycle 013)

```
kernel.emit() → EventRouter → subscribers (widgets/screens) → call_from_thread → UI refresh
                                ↓
                          WebSocket clients (broadcast)
```

Events flow from the source to all consumers in real time. Polling timers exist only as 30s safety nets.

---

## EVENT-TO-UI TIMING

| Step | Thread | Time |
|------|--------|------|
| `kernel.emit(event_type, payload)` | Emitter thread | - |
| `EventRouter.emit()` → subscriber handlers | Same thread | ~0ms |
| `call_from_thread(refresh_method)` | Same thread | ~0ms (queues) |
| `refresh_method()` on Textual thread | Textual thread | Next frame |

Total latency: typically < 16ms (one Textual frame).

---

## NEW PUBLIC API

### `genesis/desktop/widgets.py`

```python
DRIVEN_INTERVAL = 30  # seconds

def _subscribe_events(widget, refresh_method, event_type="*") -> callable
    """Subscribe a widget to EventRouter events. Returns handler for unsubscribe."""

def _unsubscribe_events(handler) -> None
    """Unsubscribe a handler from the EventRouter. Safe to call even if not subscribed."""
```

### `genesis/server.py`

```python
class GenesisAPI:
    def __init__(self, kernel=None, require_auth=False):
        ...

    # Internal:
    def _connect_ws_broadcast(self): ...
    def _register_auth(self, app): ...
```

---

## REMOVED

- 17 `set_interval` calls across widgets and screens
- ~200 lines of polling boilerplate
- No polling overhead when desktop is idle (no data changes → no refreshes)
