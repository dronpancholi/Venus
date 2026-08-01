# CYCLE 012 — USER EXPERIENCE AND SCREEN GUIDE

---

## SCREEN REFERENCE

### 1. Engineering Command Center (Ctrl+H)
```
┌──────────────────────────────────────────────────────────────────┐
│ Engineering Command Center                                       │
│ What changed? | Attention | Activity | Agents | Tasks            │
├────────────┬──────────────┬──────────────────────────────────────┤
│ ATTENTION  │ ACTIVE AGENTS │ LIVE EVENTS                         │
│ ✗ Agent X  │ ● alpha idle │ [kernel.booted] fabric              │
│   blocked  │ ▶ beta run   │ [service.reg] fabric               │
│ ◐ 3 tasks  │ ● gamma idle │ [session.begun] fabric             │
│   ready    │              │                                     │
├────────────┼──────────────┼──────────────────────────────────────┤
│ ACTIVITY   │ TASK GRAPH   │ SESSIONS                            │
│ ⊡ ev type  │ 12 nodes     │ sess_abc eng (120s)                │
│ ⊡ ev type  │ 3 ready      │ sess_def res (45s)                 │
├────────────┴──────────────┴──────────────────────────────────────┤
│ Metrics: Events 142 | Uptime 340s | Services 3 | Sessions 1     │
├──────────────────────────────────────────────────────────────────┤
│ Genesis │ running │ 142 events │ 340s │ DB │ Ctrl+K              │
└──────────────────────────────────────────────────────────────────┘
```

### 2. Fabric Inspector (Ctrl+Shift+F)
See events flowing through Genesis. Traffic light shows throughput.
Metrics view: histogram details, executor stats, event type breakdown.
Sessions view: active engineering sessions, scheduled tasks.

### 3. Agent Collaboration (Ctrl+Shift+A)
Agent hierarchy with chief/deputy visualization. Click any agent for full detail (role, model, provider, tasks, completion rate). D key shows delegation graph (TaskGraph summary). C key shows conversations.

### 4. Engineering Memory Explorer (Ctrl+Shift+M)
Browse 6 memory types: Events, Audit, Conversations, Tasks, Reports, Decisions. Left panel shows navigation list, right panel shows detail. Filter with / key.

### 5. Knowledge Graph 2.0 (Ctrl+G)
5 views: Nodes (entity counts), Edges (connection map), Types (type catalog), Dependencies (task DAG), Agents (agent overlay). Searchable with / key.

### 6. AI Orchestration Center (Ctrl+1)
Provider registry with health indicators, capabilities, models. Routing and fallback chain information. System metrics integration.

### 7. Continuous Engineering V3 (Ctrl+2)
Watcher status with active/inactive indicators. Start/stop watchers. Watch mode toggle for auto-detection. Real-time event stream.

---

## NAVIGATION PATTERNS

Every screen follows the same layout template:
1. Title bar: `[bold white]Screen Name[/]`
2. Subtitle: `[dim]actions | keybindings[/]`
3. Content: 2-3 column horizontal split
4. Status bar: `dock: bottom`

Every modal follows the same template:
1. Container with blue border (`#5E9EFF`)
2. Input at top
3. ListView with results
4. Hint bar at bottom
