# Cycle 015 — Universal Object Model (M100)

## Problem Statement

Genesis has ~192 dataclasses, 9 ABCs, 17 Protocols, and countless plain dict returns. Every subsystem defines its own identity, metadata, lifecycle, and serialization patterns. There is no consistency.

## Target Interface

```python
class EngineeringObject:
    """Base for EVERY major concept in Genesis."""

    # ── Identity ──────────────────────────────────────────────────
    id: str                          # Unique identifier
    name: str                        # Human-readable name
    type: str                        # Object type discriminator

    # ── Metadata ──────────────────────────────────────────────────
    created_at: float                # Unix timestamp
    updated_at: float                # Last modification
    tags: list[str]                  # Free-form tags
    metadata: dict[str, Any]         # Extensible key-value store

    # ── Relationships ─────────────────────────────────────────────
    def relationships(self) -> list[Relationship]: ...
    def link(self, target: EngineeringObject, type: str): ...
    def unlink(self, target: EngineeringObject): ...

    # ── Lifecycle ─────────────────────────────────────────────────
    def save(self): ...
    def delete(self): ...
    def archive(self): ...

    # ── Persistence ───────────────────────────────────────────────
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> EngineeringObject: ...

    # ── Validation ────────────────────────────────────────────────
    def validate(self) -> list[str]: ...  # Returns list of errors

    # ── History ───────────────────────────────────────────────────
    def history(self) -> list[ChangeRecord]: ...

    # ── Version ───────────────────────────────────────────────────
    version: int                     # Monotonic version counter

    # ── Health ────────────────────────────────────────────────────
    def health(self) -> ObjectHealth: ...

    # ── Diagnostics ───────────────────────────────────────────────
    def diagnostics(self) -> dict: ...

    # ── Inspection ────────────────────────────────────────────────
    def inspect(self) -> InspectionResult: ...

    # ── Export ────────────────────────────────────────────────────
    def export_json(self) -> str: ...
    def export_markdown(self) -> str: ...
```

## Objects to Unify

| Current Concept | Current Representation | Target Superclass |
|----------------|----------------------|-------------------|
| Agent | `AgentSpec` / `AgentInstance` | `EngineeringObject` |
| Task | `TaskNode` / `AgentTask` | `EngineeringObject` |
| Conversation | `Conversation` | `EngineeringObject` |
| Message | `ConversationMessage` / `AgentMessage` | `EngineeringObject` |
| Event | `EngineeringEvent` | `EngineeringObject` |
| Session | `EngineeringSession` / `Context` | `EngineeringObject` |
| Memory | `MemoryEntry` / `KnowledgeObject` | `EngineeringObject` |
| Graph Node | `GraphNode` / `USIRNode` / `KEntity` | `EngineeringObject` |
| Report | Cycle Markdown files | `EngineeringObject` |
| Decision | ADR markdown files | `EngineeringObject` |
| Plugin | `PluginManifest` | `EngineeringObject` |
| Provider | `AIProvider` | `EngineeringObject` |
| Service | `ServiceInstance` | `EngineeringObject` |
| Workspace | `WorkspaceManifest` | `EngineeringObject` |
| Project | Repository/project metadata | `EngineeringObject` |

## Implementation Plan

1. Create `genesis/core/object.py` with `EngineeringObject` base class
2. Create `Relationship`, `ChangeRecord`, `ObjectHealth`, `InspectionResult` supporting types
3. Create `ObjectRegistry` — central registry of all EngineeringObject instances
4. Add migration mixin: `def __engineering_object__(self) -> EngineeringObject`
5. Migrate one concept per mission cycle (Agent → Task → Conversation → ...)
