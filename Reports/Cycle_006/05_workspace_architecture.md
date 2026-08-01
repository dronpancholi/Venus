# Cycle 006 — Workspace Architecture

## Navigation Structure

The Genesis workspace is organized into interconnected sections. Any section can be
reached from anywhere through the command palette, keyboard shortcut, or navigation.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Dock (left)                     │  Main Content Area                    │
│                                   │                                       │
│  ┌─────────────────────┐         │  ┌─────────────────────────────────┐  │
│  │ ● Genesis            │         │  │ Header: Breadcrumb + Search    │  │
│  │                     │         │  ├─────────────────────────────────┤  │
│  │  Home               │         │  │                                 │  │
│  │  Repositories       │         │  │    Content Area                 │  │
│  │  Architecture       │         │  │                                 │  │
│  │  Knowledge          │         │  │    (section-specific content)   │  │
│  │  Memory             │         │  │                                 │  │
│  │  Agents             │         │  │                                 │  │
│  │  Tasks              │         │  │                                 │  │
│  │  Conversations      │         │  ├─────────────────────────────────┤  │
│  │  Runtime            │         │  │ Footer: Status, Progress, Info  │  │
│  │  Services           │         │  └─────────────────────────────────┘  │
│  │  Graphs             │         │                                       │
│  │  Reports            │         │                                       │
│  │  Benchmarks         │         │                                       │
│  │  Governance         │         │                                       │
│  │  Simulations        │         │                                       │
│  │  Plugins            │         │                                       │
│  │  Settings           │         │                                       │
│  └─────────────────────┘         │                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

## Section Descriptions

| Section | Purpose | Key Actions |
|---------|---------|-------------|
| **Home** | Dashboard — what's happening, what needs attention | Overview, jump to action |
| **Repositories** | Connected repos, scan status, analysis | Connect, scan, analyze, remove |
| **Architecture** | Module layering, dependencies, health | Explore layers, inspect deps, run governance |
| **Knowledge** | Knowledge graph browser | Search, filter, zoom, inspect nodes |
| **Engineering Memory** | Session context, recall, history | Query, browse timeline, search |
| **Agents** | Agent list, status, conversations | View agents, chat, assign tasks |
| **Tasks** | Task board, status, detail | Create, assign, track, review |
| **Conversations** | Chat threads with agents | Chat, review history |
| **Runtime** | Services, health, logs | View services, check health, inspect logs |
| **Services** | Service dependency graph | View topology, inspect service |
| **Graphs** | All graph views | Select graph type, explore |
| **Reports** | Generated reports | Browse, read, export |
| **Benchmarks** | Performance benchmarks | View results, compare, run |
| **Governance** | Policies, audits, compliance | View rules, check compliance, view audit log |
| **Simulations** | What-if analysis | Create simulation, view results |
| **Plugins** | Installed plugins | Browse, install, remove, configure |
| **Settings** | All configuration | Provider setup, preferences, themes |

## Keyboard Navigation

| Shortcut | Action |
|----------|--------|
| `Cmd+K` | Command palette |
| `Cmd+1-9` | Navigate to dock sections |
| `Cmd+,` | Settings |
| `Cmd+N` | New (context-dependent) |
| `Cmd+F` | Search current section |
| `Cmd+Shift+F` | Global search |
| `Esc` | Close panel / go back |
| `Cmd+W` | Close tab |
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |

## Information Architecture

Every screen follows a consistent pattern:
1. **Header** — title, breadcrumb, actions
2. **Content** — primary content area with data
3. **Side panel** (optional) — context, details, related items
4. **Footer** (optional) — status, metadata

## Data Flow

```
User Action → Router → Section → ViewModel → API/Kernel → Response → Update
```

All data flows through a central event bus. Components subscribe to relevant events.
UI updates are batched and debounced.
