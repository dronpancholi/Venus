# Desktop Runtime Validation

## Issues Found and Fixed

### Issue 1: `TaskSummary` — missing `update()` method

**Error**: `AttributeError: 'TaskSummary' object has no attribute 'update'`
**File**: `genesis/desktop/widgets.py:184`
**Root Cause**: `TaskSummary` extended `Widget` (which has no `update()` in Textual v8) but called `self.update()`. The `update()` method exists on `Static`, `Label`, and other text-rendering widgets.

**Fix**: Changed base class from `Widget` to `Static` (line 164).

### Issue 2: `StatusBar` — missing `update()` method

**Error**: Same pattern — `StatusBar` extended `Widget` but called `self.update()`
**File**: `genesis/desktop/widgets.py:71`
**Fix**: Changed base class from `Widget` to `Static` (line 71).

### Issue 3: `FabricTrafficLight` — missing `update()` method

**Error**: Same pattern — `FabricTrafficLight` extended `Widget` but called `self.update()`
**File**: `genesis/desktop/widgets.py:387`
**Fix**: Changed base class from `Widget` to `Static` (line 358).

### Issue 4: `TaskSummary` — `refresh()` conflicts with `Static.refresh()`

**Error**: `TypeError: TaskSummary.refresh() got an unexpected keyword argument 'layout'`
**File**: `genesis/desktop/widgets.py:184`
**Root Cause**: `Static.update()` calls `self.refresh(layout=True)` internally. But `TaskSummary` overrode `refresh()` without accepting `layout`, causing a `TypeError`. Additionally, the overridden `refresh()` called `self.update()` which would cause infinite recursion with the parent's refresh cycle.

**Fix**: Renamed `TaskSummary.refresh()` to `TaskSummary._update_display()`. Updated all callers (`on_mount`, `_subscribe_events`, `set_interval`, `screens.py`).

### Issue 5: `AttentionWidget` — `refresh()` conflicts with `Widget.refresh()`

**Error**: `TypeError: AttentionWidget.refresh() got an unexpected keyword argument 'layout'`
**File**: `genesis/desktop/widgets.py:284`
**Root Cause**: Same pattern — overrode `refresh()` without accepting kwargs. Called during mount process by Textual framework.

**Fix**: Renamed `AttentionWidget.refresh()` to `AttentionWidget._refresh_content()`. Updated callers in `widgets.py` and `screens.py`.

### Issue 6: `SessionTimeline` — `refresh()` conflicts with `Widget.refresh()`

**Error**: `TypeError: SessionTimeline.refresh() got an unexpected keyword argument 'layout'`
**File**: `genesis/desktop/widgets.py:501`
**Root Cause**: Same pattern — overrode `refresh()` without accepting kwargs.

**Fix**: Renamed `SessionTimeline.refresh()` to `SessionTimeline._refresh_content()`. Updated all callers.

### Issue 7: `CopilotSuggestions` — `refresh()` conflicts with `Widget.refresh()`

**Error**: Same pattern as above (preemptively fixed before runtime occurrence).
**File**: `genesis/desktop/widgets.py:534`
**Fix**: Renamed `CopilotSuggestions.refresh()` to `CopilotSuggestions._refresh_content()`.

### Issue 8: `AgentCollaborationGraph` — `refresh()` conflicts with `Widget.refresh()`

**Error**: Same pattern as above (preemptively fixed).
**File**: `genesis/desktop/widgets.py:407`
**Fix**: Added `*, repaint=True, layout=False` kwargs to `refresh()` signature.

### Issue 9: `MetricsTimeline` — `refresh()` conflicts with `Widget.refresh()`

**Error**: Same pattern as above (preemptively fixed).
**File**: `genesis/desktop/widgets.py:466`
**Fix**: Added `*, repaint=True, layout=False` kwargs to `refresh()` signature.

## Correction Strategy

In Textual v8, `Widget.refresh()` accepts keyword arguments `repaint` (default True) and `layout` (default False). The framework calls `refresh(layout=True)` on widgets during the mount process to trigger layout recalculation. Any widget that overrides `refresh()` must:

1. Accept `**kwargs` or match the parent's signature
2. Or (better) use a differently-named method for custom refresh logic

The fix applied two approaches depending on the widget's purpose:

- **Self-rendering widgets** (`StatusBar`, `TaskSummary`, `FabricTrafficLight`): Changed base from `Widget` to `Static` (which has `update()`), and renamed `refresh()` to avoid conflicting with `Static.refresh()`.
- **Container widgets** (`AttentionWidget`, `SessionTimeline`, `CopilotSuggestions`): Renamed `refresh()` to `_refresh_content()` since they manage child widgets via `query_one`.
- **Widgets that don't call self.update()** (`AgentCollaborationGraph`, `MetricsTimeline`): Added `*, repaint=True, layout=False` to accept the framework's refresh kwargs.

## Verification

- Headless desktop runs for **10 seconds without any exceptions**.
- All **11 screen classes** instantiate successfully.
- All **20 module imports** succeed.
- **18 keyboard bindings** registered.
- **166 tests pass** (zero regressions).
