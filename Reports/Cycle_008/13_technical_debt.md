# CYCLE 008 — TECHNICAL DEBT REPORT

## Areas for Improvement

⸻

## Debt Items

| Item | Severity | Affects | Cost |
|------|----------|---------|------|
| Server stubs for metrics/registry/audit | Low | API | ~20 min |
| Textual TUI hardcoded tokens | Low | Desktop | ~30 min |
| No WebSocket reconnection in desktop | Medium | Desktop | ~1h |
| FilesystemWatcher polling (not watchdog observer) | Low | Watch | ~2h |
| No API authentication | Medium | Server | ~4h |
| No error handling in watchers for missing paths | Low | Watch | ~30 min |
| Desktop doesn't use FastAPI when started with server | Medium | Desktop | ~1h |
| No async caching in Textual screens | Low | Desktop | ~2h |

## Mitigation

| Item | Priority | Plan |
|------|----------|------|
| WebSocket reconnection | High | Add `on_disconnect` reconnect loop in GenesisClient |
| API authentication | High | Add `--api-key` flag + header validation |
| Server stubs | Low | Filled as-needed (no actual regression) |
| Hardcoded tokens | Low | Extract to `genesis/ui/styles.py` for Textual |
| Watcher error handling | Low | Wrap in try/except with log |
| Desktop-Server integration | Medium | Single process mode: `genesis desktop --server` |
| Async caching | Low | After initial user testing, add `lru_cache` on event queries |
