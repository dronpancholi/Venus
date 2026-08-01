# M121: Engineering Object Model

> Status: **Implemented**
> Files: `genesis/engineering/object.py`, `genesis/engineering/registry.py`, `genesis/engineering/__init__.py`
> Integration: `genesis/fabric/kernel.py`, `genesis/fabric/agents.py`, `genesis/fabric/tasks.py`, `genesis/fabric/conversations.py`

---

## Summary

Every entity in Genesis is now a first-class Engineering Object with universal ID, type, history, relationships, health, quality, risk, activity scores, and links to all subsystems. The EngineeringRegistry maps all objects across the platform by ID.

## Architecture

```
EngineeringObject
├── id (ven:{prefix}:{hex})          # Universal ID across all subsystems
├── object_type (EngineeringObjectType)  # 22 types: event, service, agent, task, conversation, session, report, decision, plugin, etc.
├── name, description, tags, owner, importance, ai_summary
├── history_ids, parent_id           # Historical lineage
├── relationships                    # Typed edges to other objects
├── links                            # Knowledge, Memory, Conversations, Tasks, Events, Graph
├── health, quality, risk, activity  # Live scores
└── created_at, updated_at, metadata

EngineeringRegistry
├── register(obj) → id              # Auto-registers from kernel
├── get(id) → EngineeringObject      # Universal lookup
├── get_by_type(type) → list         # Filter by type
├── get_by_tag(tag) → list           # Filter by tag
├── search(query) → list             # Text search across all fields
└── stats() → dict                   # Count by type/tag
```

## Integration Points

All auto-register as EngineeringObjects when created:

| Subsystem | File | Object Type | Trigger |
|-----------|------|-------------|---------|
| FabricKernel.register_service() | kernel.py:174 | SERVICE | Service registration |
| FabricKernel.begin_session() | kernel.py:248 | SESSION | Session start |
| AgentRuntime.spawn() | agents.py:165 | AGENT | Agent creation |
| TaskGraph.add_node() | tasks.py:119 | TASK | Task node creation |
| ConversationEngine.create() | conversations.py:117 | CONVERSATION | Conversation creation |

## Universal Lookup

`FabricKernel.lookup(object_id)` resolves any ID across:
1. EngineeringRegistry (cached objects)
2. ServiceRegistry (by instance ID)
3. AgentRuntime (by agent ID)
4. TaskGraph (by node ID)
5. EventStore (by event ID)
6. AuditLog (by search match)

## Tests

- 259 existing tests pass with zero regressions
- Verified: registry count, by_type filtering, lookup across systems, session registration
