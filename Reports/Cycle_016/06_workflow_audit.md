# Cycle 016 — Workflow Audit

## Core Workflows

### Workflow 1: "Check what's happening"
```
User opens genesis desktop
→ Sees blank screen for up to 30s
→ Eventually sees Command Center with stats
→ Stats are 30-120s stale
→ Wants to know if anything needs attention
→ AttentionWidget shows "All systems normal" or error counts
→ No actionable items displayed
→ No recommendations shown (subtitle promises them)
```
**Friction**: Blank first render, stale data, no actionable intelligence.

### Workflow 2: "Explore agents"
```
User presses 2 (or ctrl+k → "Agents")
→ Sees agent list
→ Clicks an agent → detail panel shows
→ Wants to see agent conversations
→ Presses C → text-based conversation list
→ Cannot read actual messages
→ Wants to see agent graph
→ Sees text tree, not a graph
```
**Friction**: Conversations are read-only, "graph" is a text tree.

### Workflow 3: "Search for something"
```
User presses ctrl+p
→ SearchEverywhere opens
→ Types a query
→ Results appear from 10 sources
→ Wants to search files → clicks "File" button
→ Nothing happens (button is non-functional)
→ Wants to search knowledge → clicks "Know" button
→ Nothing happens
→ Presses Tab to filter (as footer suggests)
→ Nothing happens (Tab is not bound)
```
**Friction**: 2 non-functional source buttons, incorrect keyboard hint.

### Workflow 4: "Check settings"
```
User presses ctrl+s or navigates to Settings
→ Sees General, Kernel, Persistence, AI Providers panels
→ Wants to change the workspace name
→ Cannot — it's read-only
→ Wants to configure AI providers
→ Panel says "check AI Command Center"
→ Goes to AI Command Center
→ Provider list doesn't respond to clicks
→ No configuration options anywhere
```
**Friction**: Settings is a misnomer, zero configuration possible.

### Workflow 5: "Explore knowledge graph"
```
User navigates to Knowledge Graph 2.0
→ Expects a visual graph of entities and relationships
→ Sees statistics: "Events: 42", "Services: 3"
→ Sees hardcoded text about node types
→ Sees task dependencies (the only real relational data)
→ Cannot interact with any "graph"
```
**Friction**: Most misleading screen name. Zero visualization.

### Workflow 6: "Read reports"
```
User navigates to Reports
→ Sees cycle directories: Cycle_015/, Cycle_014/, etc.
→ Clicks a report
→ Sees first 5 lines, truncated at 120 chars
→ Cannot scroll or expand
→ Cannot search across reports
→ Cannot filter by content
```
**Friction**: Reports truncated to 5 lines, no full-text view.

### Workflow 7: "Monitor continuous engineering"
```
User navigates to CE screen
→ Presses S to start watchers
→ Watchers start (good!)
→ Presses W for "Watch Mode"
→ Text changes to "[bold green]Watch Mode ACTIVE[/]"
→ Nothing else happens — it's cosmetic
```
**Friction**: "Watch Mode" is a placebo.

### Workflow 8: "API development"
```
User starts genesis server
→ No banner, no port notification
→ Sends curl request -> gets response
→ Gets 200 with {"error": "not found"} for missing service
→ Wants to explore API → no Swagger UI (CORS not enabled)
→ Wants WebSocket → no auth check, double-delivered events
```
**Friction**: No startup feedback, 200 with error body, no docs, double delivery.

## Workflow Score: 3/10

| Workflow | Score | Key Issues |
|----------|-------|------------|
| Check Status | 2/10 | Blank first render, stale data, no actionable items |
| Explore Agents | 4/10 | No message reading, text "graph" |
| Search | 3/10 | Non-functional sources, wrong keyboard hint |
| Configure Settings | 1/10 | Entirely read-only, dead-end panel |
| Knowledge Graph | 1/10 | No graph, misleading screen name |
| Read Reports | 2/10 | Truncated to 5 lines, no full view |
| CE Monitoring | 4/10 | Works but placebo button |
| API Development | 3/10 | No feedback, no docs, double delivery |
