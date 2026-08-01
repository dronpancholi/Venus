# Health Subsystem API Audit

**Goal:** Ensure server code cannot drift from the Health subsystem API again.

---

## Two `ServiceHealth` Classes (Do Not Confuse)

The codebase has two distinct `ServiceHealth` dataclasses serving different purposes:

### 1. `fabric.discovery.ServiceHealth`

**Purpose:** System-level health snapshot — a single summary of the entire kernel.

**File:** `genesis/fabric/discovery.py:12`

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | Kernel state (running/booting/degraded/shutdown) |
| `uptime_seconds` | `float` | Seconds since kernel started |
| `services_count` | `int` | Number of registered services |
| `messages_sent` | `int` | Total messages sent on the bus |
| `active_sessions` | `int` | Active engineering sessions |
| `threads` | `int` | Active kernel threads |
| `last_heartbeat` | `float` | Timestamp of last heartbeat |
| `errors` | `list[str]` | Recent errors |
| `services` (compat) | `int` | Alias for `services_count` |
| `messages` (compat) | `int` | Alias for `messages_sent` |

**Returned by:** `FabricKernel.health()`

### 2. `service_kernel.ServiceHealth`

**Purpose:** Per-service health — tracks health of one individual service.

**File:** `genesis/service_kernel.py:72`

| Field | Type | Description |
|-------|------|-------------|
| `service_id` | `str` | ID of the service |
| `healthy` | `bool` | Whether the service is healthy |
| `last_check` | `float` | Last health check timestamp |
| `last_latency_ms` | `float` | Last check latency |
| `consecutive_failures` | `int` | Consecutive health check failures |
| `error` | `str | None` | Last error message |

**Used by:** `HealthManager`, `ServiceKernel` (internal to service_kernel.py)

---

## API Surface Map

```
Consumer               → Calls                → Returns           → Fields Accessed
───────────────────────────────────────────────────────────────────────────────────
__main__.py              kernel.health()         ServiceHealth       status, services_count, messages_sent
server.py                kernel.health()         ServiceHealth       status, uptime_seconds, services_count, messages_sent, active_sessions
desktop/screens.py       kernel.health()         ServiceHealth       status, uptime_seconds, services_count, messages_sent, active_sessions, threads, events_delivered
desktop/widgets.py       kernel.stats()          KernelStats         services, events_delivered, uptime_seconds, threads
desktop/experiences.py   kernel.stats()          KernelStats         services, state, uptime_seconds, events_delivered
terminal/__init__.py     kernel.health()         ServiceHealth       status, uptime_seconds, services_count, active_sessions, threads
engineering/copilot.py   kernel.health()         ServiceHealth       status, uptime_seconds
```

---

## Drift Prevention Rules

1. **Always call `kernel.health()` once, not multiple times** — captures a consistent snapshot
2. **Use `services_count` not `services`** on `ServiceHealth` objects (backward compat exists but is deprecated)
3. **Use `messages_sent` not `messages`** on `ServiceHealth` objects (backward compat exists but is deprecated)
4. **Use `kernel.stats().services`** on `KernelStats` objects — this is the correct field name
5. **Never compare by field name between `ServiceHealth` and `KernelStats`** — they have different naming conventions
6. **Always run `test_server.py::TestGenesisAPI`** before merging server-related changes

---

## Verification

A `__getattr__` hook on `ServiceHealth` provides backward compatibility while emitting the correct attribute:

```python
def __getattr__(self, name: str) -> Any:
    mapping = {"services": self.services_count, "messages": self.messages_sent}
    if name in mapping:
        return mapping[name]
    raise AttributeError(...)
```

The regression test `test_startup_path_no_attribute_error` validates both the correct fields and the backward-compat aliases.
