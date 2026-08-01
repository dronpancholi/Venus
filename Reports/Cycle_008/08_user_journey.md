# CYCLE 008 — USER JOURNEY REPORT

## From Install to Daily Use

⸻

## Journey Map

### 1. Install

```bash
pip install genesis
```

Expected output: `Successfully installed genesis-0.1.0`

### 2. First Run

```bash
genesis desktop
```

Expected output: Textual TUI appears with Home screen showing:
- Header: "Genesis Desktop v0.1"
- Agent list with 0 agents
- Event log with 0 events
- Status bar showing connected state

### 3. Explore

- `Ctrl+K` → type "View Agents" → see agent screen (empty)
- `Ctrl+K` → type "View Events" → see event log (empty)

### 4. Connect to Backend

```bash
# In another terminal:
genesis server
```

Expected: `Genesis API running on http://127.0.0.1:8377`

### 5. Start Watchers

```bash
# In another terminal:
genesis watch --path /path/to/repo
```

Expected: File changes emit events visible in desktop TUI

### 6. Check Health

```bash
curl http://127.0.0.1:8377/v1/health
```

Expected: `{"status": "ok", "uptime_seconds": ..., "event_count": 0, "watcher_count": 0}`

### 7. Daily Workflow

1. Open desktop TUI (`genesis desktop`) at start of day
2. System shows live event stream, agent activity
3. File changes appear as events in real-time
4. Command palette for navigation, search, actions
5. End of day: check event log for summary

## User Personas

| Persona | Use Case |
|---------|----------|
| Solo Developer | Watch code changes, auto-architect, get AI suggestions |
| Engineering Lead | Monitor team activity, detect architectural drift |
| DevOps | Watch CI/CD events, track deployments |
| AI Researcher | Experiment with agent configurations |
