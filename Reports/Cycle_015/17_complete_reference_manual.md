# Cycle 015 — Complete Reference Manual

## Architecture Overview

Genesis is a 6-layer engineering platform:

```
PLUGIN    Layer 5: PluginManager → external extensions
PLATFORM  Layer 4: Desktop, Server, CLI, Watch
INTELLECT Layer 3: Brain, Cognition, Planning, Reasoning
DOMAIN    Layer 2: Agents, Execution, Tasks, Conversations, Graph, Memory, Storage
KERNEL    Layer 1: FabricKernel (EventRouter, ServiceRegistry, Metrics, Audit, Scheduler)
FOUNDATION Layer 0: Core types, Utils, DI Container
```

## Kernel Reference

### FabricKernel (`genesis/fabric/kernel.py`)
- Singleton: `FabricKernel.instance(storage_path, enable_persistence)`
- Lifecycle: `boot() → health() → stats() → shutdown()`
- Events: `emit(type, payload)`, `on_event(type, handler)`, `query_events()`
- Sessions: `begin_session(type, metadata)`, `end_session(id)`

### EventRouter (`genesis/fabric/events.py`)
- `subscribe(type, handler, filter_fn)`, `unsubscribe(handler)`
- `emit(event)`, `emit_raw(type, payload, ...)`
- EventStore: bounded 50K, 6 indexes, FIFO eviction

### ServiceRegistry (`genesis/fabric/discovery.py`)
- `register(name, version, capabilities)`, `unregister(instance_id)`
- `get(instance_id)`, `list_services()`

## Desktop Reference

### App (`genesis/desktop/app.py`)
- 11 screens registered in `SCREENS` dict
- 13 keyboard bindings
- Navigation: `navigate_to(target)` → pop + push

### Screens (`genesis/desktop/screens.py`)
- 11 Screen classes, 1,395 lines total
- Common pattern: `on_mount` → set_interval + subscribe events
- Event-driven: `_subscribe_events()` + 30s timer fallback

### Widgets (`genesis/desktop/widgets.py`)
- 14 widgets + 5 shared color maps
- Widgets read from `FabricKernel.instance()` in `on_mount`
- All data access wrapped in try/except

### Palette (`genesis/desktop/palette.py`)
- `CommandPalette`: 22 commands, `ctrl+k`
- `SearchEverywhere`: 10+ sources, `ctrl+p`

## Server Reference

### GenesisAPI (`genesis/server.py`)
- FastAPI + WebSocket on `127.0.0.1:8377`
- 18 REST endpoints under `/v1/`
- WebSocket at `/v1/ws` with event broadcast
- Optional Bearer token auth
- Launch: `run_server(host, port)`

## Storage Reference

### StorageEngine (`genesis/fabric/storage.py`)
- SQLite with WAL mode, 10 tables
- Tables: events, agents, agent_tasks, agent_messages, task_graph_nodes, conversations, conversation_messages, audit_entries, metric_points, services

### SQLiteStore (`genesis/persistence/sqlite_store.py`)
- 6 stores: Metadata, Knowledge, History, Artifact, Checkpoint, Memory
- SQLite with WAL mode

## AI Reference

### Provider Interface (`genesis/ai/__init__.py`)
- `chat()`, `stream_chat()`, `embeddings()`, `tool_call()`
- 3 providers: NVIDIA, Ollama, OpenAI-compat
- Routing: `AIRouter._rank_providers(capability)` → score-based selection

## Test Infrastructure

### Fixtures (`tests/conftest.py`)
- 22 fixtures: kernel, server, desktop, providers, agents, WS, security, plugins, conversations
- Autouse singleton reset
- Markers: desktop, integration, slow, ai, auth, plugin, ws, storage
