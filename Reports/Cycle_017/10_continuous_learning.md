# M130: Continuous Learning

> Status: **Designed** (foundation built)
> Enablers: M121 (EngineeringObject updates), M122 (Knowledge extraction), M123 (Reasoning findings)

---

## Architecture

Every user action enriches Genesis knowledge:

| Action | Learning Effect | Current State |
|--------|----------------|---------------|
| Accept recommendation | Increases confidence, promotes to pattern | Needs wiring |
| Reject recommendation | Decreases confidence, documents rejection | Needs wiring |
| Edit generated code | Stores delta as lesson | Needs wiring |
| Change architecture | Updates architecture patterns | Needs wiring |
| Rename objects | Updates name aliases in registry | Registry supports rename |
| Delete reports | Removes stale knowledge | Needs wiring |
| Approve decisions | Promotes to canonical | Partially wired (extract_decisions) |
| Merge branches | Records architectural evolution | Needs wiring |

## Existing Foundation

- EngineeringRegistry supports `register()`/`unregister()` for objects
- KnowledgeEngine re-indexes on `index_reports(force=True)`
- Brain integration stubs (2 of 7 handlers) exist but are empty
- Event system captures every action as an EngineeringEvent
- Timeline can replay engineering history for enrichment
