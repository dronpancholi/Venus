# CYCLE 012 — DESIGN DECISIONS AND ARCHITECTURE DELTA

---

## KEY DESIGN DECISIONS

### 1. Enhanced Widget Architecture

**Decision:** Create specialized real-time widgets (AttentionWidget, LiveActivityFeed, FabricTrafficLight) instead of modifying existing polling widgets.

**Rationale:** Each real-time widget has a unique polling model (traffic needs 1s, attention needs 3s, metrics needs 5s). Mixing intervals in a single widget would be fragile. Each widget owns its `set_interval` and `refresh` method.

### 2. Three-Panel Command Center Layout

**Decision:** EngineeringCommandCenter uses a 3-column layout (left: attention/activity/metrics, center: agents/tasks, right: events/sessions) instead of the old 2-column split.

**Rationale:** Three columns provide natural grouping — left for "what needs attention", center for "what's running", right for "what's happening". The 35/35/30 split keeps all content visible at terminal width 120+.

### 3. View Mode Pattern for Multi-View Screens

**Decision:** Use a `_view` attribute + keyboard-toggled view modes (M81 Memory Explorer has 6 views, M82 Knowledge Graph has 5 views, M69 Repository has 3 views).

**Rationale:** Single screen with multiple views is easier to navigate than multiple screens with similar content. Keyboard shortcuts (E/A/C/T) provide fast switching. The pattern is consistent across screens.

### 4. Filter Bar for High-Content Screens

**Decision:** Add filter `Input` widgets to Memory Explorer, Timeline, and Knowledge Graph (hidden until / is pressed).

**Rationale:** Screens with 30-50 lines of content need filtering to navigate. The filter is case-insensitive and operates on the rendered line text.

### 5. FabricTrafficLight as Throughput Indicator

**Decision:** Events/sec sampling with a 10-sample sliding window, color-coded (green >5/s, yellow >1/s, dim <1/s).

**Rationale:** The traffic light gives an immediate visual sense of fabric activity without requiring the user to read numbers. The 10-sample window smooths out spikes.

### 6. Agent Collaboration via Delegation + Conversation Views

**Decision:** Separate agent hierarchy into delegation view (TaskGraph-based) and conversation view (ConversationEngine-based), accessible via D/C keys.

**Rationale:** Agents collaborate through two channels — task delegation (DAG) and conversation (messages). Showing both in one view would be cluttered. Separate views with keyboard switching keeps each view focused.

---

## ARCHITECTURE DELTA (Cycle 011 → Cycle 012)

| Aspect | Cycle 011 | Cycle 012 |
|--------|-----------|-----------|
| Screens | 10 screens | 14 screens (+FabricInspector, +MemoryExplorer, +AgentCollaboration replaces AgentOps, +AIOrchestration replaces AI) |
| Widgets | 9 widgets | 15 widgets (+6 new: Attention, LiveActivity, TrafficLight, CollabGraph, MetricsTimeline, SessionTimeline) |
| Command Palette | 21 commands | 25 commands (+inspector_metrics, inspector_sessions) |
| Search Sources | 7 sources | 10 sources (+Knowledge, +Reports, +Files) |
| Keyboard Bindings | 12 bindings | 13 bindings (+Ctrl+Shift+F, Ctrl+Shift+A, Ctrl+Shift+M) |
| CSS Classes | ~40 selectors | ~60 selectors (+all new screen/panel IDs) |
| View Pattern | 1-2 views/screen | Up to 6 views/screen with keyboard switching |
| Filtering | Timeline only | Memory Explorer, Knowledge Graph, Timeline |
