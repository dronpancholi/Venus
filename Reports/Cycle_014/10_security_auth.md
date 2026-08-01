# Phase 0 Delta: Security & Authentication

**Files:** `genesis/kernel/security_manager.py` (123 lines), `genesis/server.py` auth middleware  
**Tests:** 0 (auth-specific)

## SecurityManager Capabilities

### RBAC
| Method | Purpose |
|--------|---------|
| `create_role(role, permissions)` | Define role with permission set |
| `assign_role(identity, role)` | Assign role to identity |
| `remove_role(identity, role)` | Remove role assignment |
| `has_permission(identity, permission)` | Check identity permission |
| `roles_of(identity)` | List roles for identity |

### Policy-Based Authorization
| Method | Purpose |
|--------|---------|
| `add_policy(resource, action, effect, conditions)` | Define allow/deny policy |
| `check_policy(identity, resource, action, context)` | Evaluate policies |

### Token Management
| Method | Purpose |
|--------|---------|
| `issue_token(identity, ttl_seconds)` | Issue SHA-256 token with expiry |
| `validate_token(token)` | Return identity or None |
| `revoke_token(token)` | Revoke single token |
| `revoke_all_for(identity)` | Revoke all identity tokens |

## Server Auth Integration

- **Default:** `require_auth=False` — all routes open, only `/v1/auth/status` returns `{"auth": false}`
- **Enabled:** Bearer token middleware on all routes except `/v1/auth/*`
- Token endpoints: POST `/v1/auth/token`, POST `/v1/auth/revoke`

## Findings

1. **No test coverage** — 0 tests for SecurityManager, token lifecycle, or auth middleware
2. **No password/credential storage** — tokens can be issued with any identity string, no authentication required
3. **SHA-256 tokens are stored in plain dict** — no hashing, no encryption, no secure store
4. **No token expiry enforcement in EventRouter** — token validated on HTTP request but not bound to event/session identity
5. **No permission granularity on routes** — Bearer token middleware only checks token validity, not route-level permissions
6. **`SecurityManager` part of UniversalKernel** — not accessible from FabricKernel (which is what the server wraps)

## Recommendations

1. Add comprehensive tests for SecurityManager: token lifecycle, RBAC, policy evaluation
2. Add API key/credential store with hashed secrets
3. Hash tokens at rest using SHA-256 of SHA-256
4. Link token identity to event `origin` for audit tracking
5. Add route-level permission checking in auth middleware using `check_policy()`
6. Add `SecurityManager` reference to FabricKernel so server can access it without UniversalKernel
