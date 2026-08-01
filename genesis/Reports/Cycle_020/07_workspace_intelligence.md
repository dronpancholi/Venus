# M165: Workspace Intelligence

**Status:** Implemented
**Files:** `genesis/desktop/memory.py`
**Integration:** WorkspaceMemory, SessionSnapshot

## Changes

WorkspaceMemory now supports full session auto-restore:

- **SessionSnapshot** — captures complete workspace state (screen, panels, projects, search, workflow, reports, AI session, context)
- **save_session()** — persists snapshots with environment context
- **restore_latest_session()** — returns the most recent snapshot
- **restore_context()** — returns structured context dict for desktop to restore
- **list_sessions()** — browse recent sessions
- **set/get_current_task()** — track what the engineer was working on
- **add_open_report/conversation** — track open artifacts

## Usage

```python
# Save session on shutdown
snap = SessionSnapshot(
    screen_id="home",
    open_panels=["health", "boot", "architecture"],
    context_summary="Working on Cycle 020 boot sequence",
    current_workflow_id="wf_123",
)
WorkspaceMemory.instance().save_session(snap)

# Restore on startup
ctx = WorkspaceMemory.instance().restore_context()
# → {"restored": True, "screen_id": "home", "open_panels": [...], ...}
```
