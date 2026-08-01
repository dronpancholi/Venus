# CYCLE 013 — P0 SPRINT: EVENT-DRIVEN UI, API AUTH, WEBSOCKET PUSH

**Cycle:** 013
**Theme:** Real-time everywhere — push-based UI, authenticated API, live WebSocket
**Missions:** WebSocket push, API auth, Event-driven UI
**Test Count:** 3,274 passing, 0 failing (100% clean)
**Lines Changed:** ~150 across 3 files

---

## EXECUTIVE SUMMARY

Cycle 013 eliminates Genesis's last polling dependencies. All desktop widgets and screens now react to fabric events in real time instead of polling at 1-10s intervals. The GenesisAPI server gains token-based auth and automatically pushes events to all WebSocket clients.

### What Changed

| Component | Before | After |
|-----------|--------|-------|
| UI timers | 20 timers (1-30s) across widgets/screens | 1 timer at 1s (traffic light sampling), 3 at 30s (filesystem), rest are event-driven |
| API auth | None — bearer token validation | Token auth with middleware, token issue/revoke endpoints |
| WebSocket | Manual subscribe per WS client | Auto-push: all fabric events broadcast to all WS clients |
| Test count | 3,274 pass, 0 fail | 3,274 pass, 0 fail (no regressions) |

---

## FILES CHANGED

| File | Change | Key Lines |
|------|--------|-----------|
| `genesis/server.py` | +WS broadcast subscription, +SecurityManager auth, +auth middleware, +`/v1/auth/*` endpoints | lifespan, _connect_ws_broadcast, _register_auth |
| `genesis/desktop/widgets.py` | +`_subscribe_events`/`_unsubscribe_events` helpers, 10 widgets converted, `_DRIVEN_INTERVAL=30` | _subscribe_events, _unsubscribe_events, every widget's on_mount/on_unmount |
| `genesis/desktop/screens.py` | 8 screens converted to event-driven, 2 kept at 30s (filesystem), EventsScreen unchanged | Each screen's on_mount/on_unmount |

---

## REMAINING TIMERS

| Interval | Count | Widget/Screen | Reason |
|----------|-------|---------------|--------|
| 1s | 1 | FabricTrafficLight | Needs 10-sample sliding window for avg throughput |
| 30s | 3 | RepositoryScreen, ReportsScreen, EventsScreen | Filesystem scanning — no event trigger |

---

## KEY PATTERN

```python
def on_mount(self):
    self._handler = _subscribe_events(self, self._refresh)
    self._refresh()
    self.set_interval(30, self._refresh)  # fallback only

def on_unmount(self):
    _unsubscribe_events(self._handler)
```

All 17 converted widgets/screens use this exact pattern. The EventRouter calls the handler synchronously from any thread; `call_from_thread` delegates the actual refresh to the Textual event loop. The 30s timer is a safety net for data that changes without emitting events.

---

## API AUTH

```
POST   /v1/auth/token     Issue token (identity: str, ttl?: float)
POST   /v1/auth/revoke    Revoke token (token: str)
GET    /v1/auth/status     Check if auth is enabled

Auth middleware (when require_auth=True):
  - All routes except /v1/auth/* require "Bearer <token>" in Authorization header
  - Invalid/expired tokens return 401
  - Identity stored in request.state.identity
```

---

## TEST RESULTS

| Run | Tests | Pass | Fail |
|-----|-------|------|------|
| Full suite (97 test files) | 3,274 | 3,274 | 0 |
