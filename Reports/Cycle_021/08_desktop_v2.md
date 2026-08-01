# Desktop 2.0 / Workspace Manager (M181)

**File:** `genesis/workspace/__init__.py`
**Tests:** 8

Adds workspace templates, layout management, pinned projects, and recent work tracking to the Genesis Desktop.

### Built-in Templates
| Template | Screens | Use Case |
|----------|---------|----------|
| engineering | home, agents, events, knowledge | Full workspace |
| review | events, knowledge | Architecture review |
| minimal | home | Quick access |

### API
```python
from genesis.workspace import WorkspaceManager

wm = WorkspaceManager()
wm.apply_template("engineering")
wm.pin_project("/path/to/project")
wm.add_recent("Reviewed architecture decisions")
```
