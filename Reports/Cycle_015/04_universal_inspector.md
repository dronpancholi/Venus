# Cycle 015 — Universal Inspector (M101)

## Concept

Anything visible in Genesis should be inspectable. Click any object → Inspector opens → shows Overview, Identity, Metadata, Relationships, Timeline, Dependencies, Dependents, Memory, Knowledge, Architecture, Events, Reports, Conversations, Tasks, Benchmarks, Health, Performance, Diagnostics, Recommendations.

## Inspector Architecture

```
User clicks object
  → ObjectRegistry.get(id) → EngineeringObject
    → InspectorScreen.push(object)
      → Panels for each inspection dimension
```

## Inspector Panels

| Panel | Source | Description |
|-------|--------|-------------|
| Overview | `object.to_dict()` | Name, type, status, quick summary |
| Identity | `object.id`, `object.name` | ID, name, type, version, timestamps |
| Metadata | `object.metadata` | Tags, custom metadata |
| Relationships | `object.relationships()` | Linked objects with type labels |
| Timeline | `kernel.query_events(...)` | Events involving this object |
| Dependencies | Graph traversal | Objects this depends on |
| Dependents | Graph traversal | Objects depending on this |
| Memory | `UniversalMemorySystem.query(...)` | Memory entries referencing this |
| Knowledge | `UnifiedGraph.neighbors(...)` | Graph neighborhood |
| Architecture | Component mapping | Architectural role and layer |
| Events | `EventStore.query(...)` | Events by this object |
| Reports | Filesystem scan | Report files mentioning this |
| Conversations | `ConversationEngine.search(...)` | Conversations referencing this |
| Tasks | `TaskGraph.get_by_...()` | Tasks involving this object |
| Benchmarks | Performance data | Historical performance |
| Health | `object.health()` | Status, uptime, errors |
| Performance | Operation timing | Recent operation duration |
| Diagnostics | `object.diagnostics()` | Internal state inspection |
| Recommendations | Rules engine | Suggested next actions |

## Desktop Implementation

Create `InspectorScreen(Screen)` in `genesis/desktop/screens.py`:

- Composes 12 `DataPanel` widgets in a scrollable vertical layout
- Each panel is a `SectionTitle` + `RichLog`
- Panels are lazy-loaded (expand on click)
- Ctrl+I on any selected item opens inspector
- ActivityBar gets an "Inspect" button

## Data Flow

```
Click → app.inspect(object_id)
  → ObjectRegistry.get(object_id) → EngineeringObject
    → InspectorScreen(object)
      → Panel 1: Overview (sync)
      → Panel 2: Events (async from EventStore)
      → Panel 3: Tasks (async from TaskGraph)
      → ...
```
