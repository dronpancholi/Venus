# CYCLE 009 — API SERVER EXTENSIONS REPORT

---

## New Endpoints

### `GET /v1/storage`

Returns StorageEngine stats and table sizes.

```json
{
  "db_path": "/Users/user/.genesis/fabric.db",
  "connected": true,
  "write_count": 1250,
  "read_count": 3400,
  "table_sizes": {
    "events": 5000,
    "agents": 12,
    "agent_tasks": 150,
    ...
  }
}
```

### `GET /v1/execution`

Returns AgentExecutionEngine statistics.

```json
{
  "execution_count": 42,
  "total_duration_ms": 125000.0,
  "avg_duration_ms": 2976.19
}
```

### `GET /v1/repository`

Returns watcher status and file system state.

```json
{
  "active": true,
  "watchers": {
    "filesystem": {
      "active": true,
      "last_scan": 1700000000.0,
      "scan_count": 500,
      "change_count": 25,
      "error_count": 0
    },
    "git": { ... },
    "provider": { ... }
  }
}
```

### `GET /v1/conversations/{id}/messages`

Returns messages for a specific conversation from persistence.

```json
{
  "messages": [
    {
      "id": "cmsg:abc123",
      "conversation_id": "conv:xyz789",
      "role": "user",
      "content": "Let's review the architecture",
      "timestamp": 1700000000.0
    }
  ],
  "count": 1
}
```

## Enhanced Endpoints

### `GET /v1/services` (enhanced)

Now returns persisted service data instead of empty.

```json
{
  "count": 5,
  "services": [
    {
      "id": "svc:abc",
      "name": "compiler",
      "version": "2.0.0",
      "capabilities": ["compile", "parse"],
      "status": "registered",
      "registered_at": 1700000000.0,
      "last_heartbeat": 1700000500.0
    }
  ]
}
```

### `GET /v1/metrics` (enhanced)

Now returns real metric snapshot with histogram details.

### `GET /v1/audit` (enhanced)

Now returns real audit entries with action/actor filtering and total count.
