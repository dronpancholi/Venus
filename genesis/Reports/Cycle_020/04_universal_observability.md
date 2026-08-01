# M162: Universal Observability

**Status:** Implemented
**Files:** `genesis/observability/engine.py`, `genesis/observability/__init__.py`
**Integration:** FabricKernel.observability, records boot events automatically

---

## Design

### Action Types (20)

| Type | Description |
|------|-------------|
| api_call | REST/WebSocket API endpoints |
| desktop_interaction | TUI screen navigation, commands, palettes |
| ai_request | AI chat, stream, embeddings, tool calls |
| workflow | Workflow engine executions |
| event | Event bus emissions |
| engineering_object_mutation | Engineering object CRUD |
| plugin | Plugin operations |
| search | Unified search queries |
| recommendation | Copilot suggestions |
| report_generation | Report generation |
| boot | Startup sequence |
| shutdown | Shutdown sequence |
| health_check | Health assessments |
| knowledge_update | Knowledge engine mutations |
| twin_scan | Digital twin scans |
| sdk_call | SDK capability invocations |
| reasoning | Reasoning engine operations |
| decision | Decision intelligence |
| navigation | Desktop screen navigation |
| command | CLI/desktop commands |

### ActionRecord Schema

```
id           str       # Unique action ID (timestamp + random)
type         ActionType
subsystem    str       # Source subsystem
action       str       # Action name
severity     ActionSeverity  # debug/info/warning/error/critical
timestamp    float     # Unix timestamp
duration     float     # Execution time in seconds
success      bool
actor        str       # Who triggered it
detail       str       # Human-readable description
metadata     dict      # Structured context
error        str       # Error message if failed
trace        str       # Stack trace if failed
parent_id    str       # For nested actions
tags         list[str] # Free-form tags
```

### Architecture

```
ObservabilityEngine
  ├── record(type, subsystem, action, ...)  → ActionRecord
  ├── query(filter)                         → list[ActionRecord]
  ├── query_by_type(type)                   → list[ActionRecord]
  ├── query_by_subsystem(subsystem)         → list[ActionRecord]
  ├── errors(since, limit)                  → list[ActionRecord]  # ERROR + CRITICAL
  ├── stats()                               → dict
  ├── export(format)                        → str (json or csv)
  ├── export_to_file(path, format)          → str (saved path)
  ├── replay(id)                            → ActionRecord
  └── clear()

ObservableMixin          # Mixin for any class to self-record
record_action()          # Decorator for automatic action recording
```

### Export Formats

- **JSON** — full record dump, filterable
- **CSV** — flat table for spreadsheet analysis

### Health Correlation

- Errors automatically trigger a health snapshot
- Error rate feeds into HealthEngine error dimension

### Kernel Integration

```python
kernel.observability                     # ObservabilityEngine
kernel.observability.record(...)         # Record any action
kernel.observability.stats()             # Usage statistics
kernel.observability.export("json")      # Export all records
kernel.observability.errors()            # Recent errors
```

## Results

| Metric | Value |
|--------|-------|
| Action types | 20 |
| Filter dimensions | 10 |
| Export formats | 2 (JSON, CSV) |
| Max records | 100,000 |
| Default collectors | 0 (ad-hoc recording) |
| Boot recording | Automatic |
