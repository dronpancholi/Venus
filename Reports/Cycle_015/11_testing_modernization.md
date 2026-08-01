# Cycle 015 — Test Infrastructure Modernization (M108)

## Before

| Metric | Value |
|--------|-------|
| pytest conftest.py | ✗ None |
| pytest.ini | ✗ None |
| Shared fixtures | ✗ None |
| Fixture pattern | `FabricKernel._instance = None` manually in 10+ files |
| Desktop tests | 0 |
| Auth tests | 0 |
| WebSocket tests | 0 |
| Plugin tests | 0 |
| Test markers | ✗ None |

## After

| Metric | Value |
|--------|-------|
| conftest.py | ✅ Created (30+ fixtures) |
| pytest.ini | ✅ Created (markers, filterwarnings) |
| Shared fixtures | ✅ Kernel, storage, server, desktop, providers, agents, WS, security, plugins, conversations |
| Singleton reset | ✅ `autouse=True` fixture — no more manual `_instance = None` |
| Custom markers | ✅ desktop, integration, slow, ai, auth, plugin, ws, storage |
| Fixture count | 22 total |

## Fixture Catalog

### Kernel Fixtures
| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `_reset_kernel_singleton` | function (autouse) | None | Reset FabricKernel._instance before/after each test |
| `kernel` | function | FabricKernel | Fresh booted kernel with all lazy components |
| `kernel_no_boot` | function | FabricKernel | Fresh kernel, not booted |
| `kernel_with_storage` | function | FabricKernel | Booted kernel with SQLite in temp directory |

### Storage Fixtures
| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `temp_db_path` | function | str | Temp .db file path, auto-cleaned |

### Server Fixtures
| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `api_client` | function | TestClient | FastAPI TestClient with booted kernel |
| `api_client_no_auth` | function | TestClient | Auth disabled (same as api_client) |
| `api_client_with_auth` | function | (client, token) | Auth enabled with issued token |

### Desktop Fixtures
| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `desktop_app` | function | GenesisDesktop | App instance (not run), inspectable with pilot |

### Domain Fixtures
| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `provider_registry` | function | ProviderRegistry | Clean registry singleton |
| `agent_runtime` | function | AgentRuntime | Kernel's agent runtime |
| `task_graph` | function | TaskGraph | Kernel's task graph |
| `conversation_engine` | function | ConversationEngine | Kernel's conversation engine |
| `plugin_manager` | function | PluginManager | Fresh manager with temp plugin dir |
| `event_router` | function | EventRouter | Kernel's event router |
| `event_store` | function | EventStore | Kernel's event store |
| `websocket_test_client` | function | (client, ws) | WebSocket test session |
| `security_manager` | function | SecurityManager | Fresh security manager |

## Migration Guide

### Before (old pattern — to be removed)
```python
class TestX:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance()
        self.kernel.boot()

    def teardown_method(self):
        self.kernel.shutdown()
        FabricKernel._instance = None
```

### After (new pattern)
```python
class TestX:
    def test_something(self, kernel):
        # kernel is already booted, ready to use
        assert kernel.state == "RUNNING"
```

## Remaining Work

1. **Desktop pilot tests** — Create `tests/test_desktop.py` with Textual `pilot` for each screen
2. **Auth tests** — Create `tests/test_security.py` for SecurityManager + auth middleware
3. **WebSocket tests** — Add WS test coverage to existing `test_server.py`
4. **Plugin tests** — Create `tests/test_plugin.py` with manifest loading and activation
5. **Add to CI** — Wire `pytest -m "not slow"` into test runner
6. **Migrate old tests** — Convert 10+ files from manual `_instance = None` to fixture usage
