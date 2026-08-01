# Cycle 016 — Production Hardening Design (M119)

## Current State

### Error Handling
- 30+ `except Exception: pass` locations — systemic silent failure
- 5 bare `except:` — catches KeyboardInterrupt and SystemExit
- Service not-found returns HTTP 200 with error body (not 404)
- 7 API endpoints silently degrade on ImportError
- No loading indicators anywhere
- No crash recovery

### Auth
- Unsigned SHA256 tokens (no HMAC, no signing key)
- No auth on WebSocket
- `issue_token` accepts any identity string — no credential validation
- Auth disabled by default
- RBAC/policy engine exists but never called from API

### Shutdown
- Ctrl+Q quits immediately — no confirmation, watchers abandoned
- No `on_unmount` handler on App — kernel shutdown never called
- No graceful teardown

## Implementation Plan

### Phase 1: Critical (Cycle 017)
| Item | Description | Effort |
|------|-------------|--------|
| Structured error handling | Replace bare except:pass with logged errors | 3d |
| HMAC-signed tokens | Replace SHA256 with HMAC-SHA256 | 1d |
| WebSocket auth | Require token for WS connections | 1d |
| Proper HTTP status codes | Return 404 for not-found, 503 for degraded | 1d |
| Graceful shutdown | on_unmount handler, kernel shutdown | 1d |
| Ctrl+Q confirmation | Confirm dialog before exit | 0.5d |

### Phase 2: Enhanced (Cycle 018)
| Item | Description | Effort |
|------|-------------|--------|
| Credential validation | API key or password for token issuance | 2d |
| RBAC enforcement | Check permissions on all endpoints | 3d |
| Loading indicators | Spinner widgets during data fetch | 2d |
| Error screen | Dedicated error/panic screen | 1d |
| Crash recovery | Session state persistence + restore | 3d |
| Rate limiting | Token bucket per endpoint | 1d |
| Persistence backup | SQLite backup + restore | 2d |
