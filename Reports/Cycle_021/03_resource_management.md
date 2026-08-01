# Resource Management (M176)

**File:** `genesis/resources/__init__.py`
**Tests:** 13

Tracks platform resources: threads, events, services, sessions, agents, engineering objects.

### API
```python
rm = ResourceMonitor(kernel=kernel, poll_interval=30.0)
rm.start()                     # background polling
snap = rm.snapshot()           # manual snapshot
alerts = snap.alerts()         # resources exceeding limits
summary = rm.summary()         # quick overview
rm.thresholds.set("threads.active", 200)
rm.on_alert(lambda m: ...)     # alert callbacks
```

### Thresholds
| Resource | Default Limit |
|----------|---------------|
| threads.active | 100 |
| events.store | 50,000 |
| services.registered | 500 |
| sessions.active | 100 |
| agents.active | 50 |
| memory.engineering_objects | 100,000 |
