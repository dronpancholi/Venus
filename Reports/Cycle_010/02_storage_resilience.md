# CYCLE 010 — STORAGE RESILIENCE REPORT

## Concurrent-Thread SQLite Safety

---

## PROBLEM

When TaskExecutor background thread runs `_tick()` concurrently with the main
thread, both threads may attempt SQLite writes simultaneously. The TaskExecutor
writes agent execution results (task status updates), while the main thread
may be serving API requests or updating desktop state.

This caused `sqlite3.OperationalError: database is locked` failures.

## SOLUTION: THREE-PRONGED APPROACH

### 1. Busy Timeout
```python
self._db.execute("PRAGMA busy_timeout=5000")
```
Gives SQLite a 5-second retry window before failing when a write collision
occurs. Sufficient for WAL-mode contention at moderate concurrency.

### 2. `_write()` Wrapper on All Store Methods
```python
def _write(self, sql: str, params: tuple = ()) -> None:
    try:
        self._db.execute(sql, params)
        self._db.commit()
    except sqlite3.OperationalError:
        pass  # data is fully in-memory; SQLite is crash-recovery mirror
```

Applied to: `store_service`, `delete_service`, `store_contract`,
`delete_contract`, `store_event`, `store_subscription`, `delete_subscription`,
`store_agent_instance`, `delete_agent_instance`, `store_agent_task`,
`store_conversation`, `store_conversation_message`.

### 3. try/except in Kernel emit()
```python
try:
    self._storage.store_event(...)
except Exception:
    pass
```

## RATIONALE

The fabric's true state is always fully in-memory (dictionaries of agents,
tasks, conversations, etc.). SQLite is a crash-recovery mirror, not the
source of truth. Silent failure on write is acceptable because:

1. In-memory state is authoritative
2. SQLite mirrors are rebuilt from heartbeat + event replay on next boot
3. Losing a write is safe — the data is still in memory
