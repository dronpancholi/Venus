# Cycle 015 — User Guide

## Quick Start

```bash
genesis desktop
```

Launches the Genesis Engineering Platform in your terminal. Press `?` to see all keybindings.

## Desktop Overview

11 screens organized into 3 zones:

### Zone 1: Intelligence (Screens 1-4)
| Screen | Opens Via | What You See |
|--------|-----------|--------------|
| Workspace | Default | Agent collaboration, task timeline, knowledge graph |
| Agents | `1` | All registered agents with status + resource usage |
| Agent Detail | Click agent | Agent-specific conversations, tasks, memory |
| Engineering Brain | `3` | Reasoning, planning, cognition state |

### Zone 2: Operations (Screens 5-8)
| Screen | Opens Via | What You See |
|--------|-----------|--------------|
| Engineering Memory | `4` | Memory entries, knowledge objects, search |
| Continuous Engineering | `5` | Watcher states, file changes, auto-retry stats |
| Knowledge Graph | `6` | Entity/relationship browser, degree centrality |
| AI Orchestration | `7` | Provider status, model availability, routing |

### Zone 3: Analysis (Screens 9-11)
| Screen | Opens Via | What You See |
|--------|-----------|--------------|
| Timeline | `8` | All events, filtered by type/agent/severity |
| Fabric Inspector | `9` | Kernel internals: sessions, events, services |
| Engineering Command Center | `0` | Dashboard, metrics panel, health monitoring |

## Keyboard Reference

| Key | Action |
|-----|--------|
| `1-0` | Switch to screen |
| `ctrl+k` | Command palette |
| `ctrl+p` | Search everywhere |
| `ctrl+c` | Quit |
| `ctrl+d` | Dashboard |
| `ctrl+r` | Reports |
| `ctrl+b` | Activity bar toggle |
| `ctrl+i` | Inspect selected |
| `ctrl+/` | Keyboard shortcuts |
| `ctrl+s` | Settings |

## Command Palette (ctrl+k)

22 commands available: navigate to any screen, refresh data, inspect kernel, audit log, service list, status, etc.

## Search (ctrl+p)

Search 10+ sources: Events, Agents, Tasks, Services, Audit, Conversations, Commands, Reports, Files, Knowledge.

## Server Mode

```bash
genesis server
```
REST API + WebSocket on `127.0.0.1:8377`. Use `curl` or your browser:
```bash
curl http://127.0.0.1:8377/v1/health
```
