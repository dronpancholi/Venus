# CYCLE 007 — REPORT 07: VISUAL ENGINEERING PLATFORM

## Architecture & Design for the Genesis Interface

⸻

## VISION

The Genesis Visual Platform is a calm, premium, intelligent desktop and web
application that makes engineering visible, understandable, and actionable.
It follows the Genesis Design Language — inspired by Apple (clarity), Claude
(calm intelligence), Linear (speed), Raycast (efficiency), Arc (fluidity),
and Notion (structured information) — without copying any of them.

## APPLICATION ARCHITECTURE

```
┌────────────────────────────────────────────────────────────┐
│                    Genesis Desktop/Web                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  UI Layer (React/Svelte/Vue)                         │  │
│  │  ┌──────┐ ┌─────────┐ ┌───────┐ ┌───────────────┐  │  │
│  │  │ Home │ │ Repo    │ │Arch. │ │   ...         │  │  │
│  │  └──────┘ └─────────┘ └───────┘ └───────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI/WebSocket)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Genesis Engineering Kernel                          │  │
│  │  ┌──────────┐ ┌──────┐ ┌────────┐ ┌──────────────┐  │  │
│  │  │ Fabric   │ │ AI   │ │ Agents │ │ Task Graph   │  │  │
│  │  │ Events   │ │ Prov.│ │ Runtime│ │ Conversations│  │  │
│  │  └──────────┘ └──────┘ └────────┘ └──────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

## KEY PAGES

| Page | Purpose | Key Data Sources |
|------|---------|-----------------|
| Home | Mission control, widget dashboard | Fabric events, agent status, task graph |
| Repository | File tree, analysis, metadata | Indexer, graph, scanner |
| Architecture | Layer graph, dependency view, health | TaskGraph, Governance |
| Memory | Engineering memory, timeline, search | EngineeringMemory |
| Knowledge | Knowledge graph browser | KnowledgeGraph |
| Agents | Agent list, status, conversation | AgentRuntime |
| Tasks | Task graph, kanban, detail | TaskGraph |
| Runtime | Service health, logs, metrics | FabricKernel |
| Governance | Policies, audit log, compliance | Governance, Audit |
| Settings | Providers, preferences, themes | AI Router, Fabric |

## LIVE UPDATES

Every page subscribes to relevant Fabric events:
- Agent status change → Agent list re-renders
- Task progress update → Task graph re-renders
- New event → Home activity feed updates
- Architecture change → Architecture health re-calculates
- Provider health change → Provider status updates

All through WebSocket → Fabric event subscription.

## IMPLEMENTATION APPROACH

Phase 1: Python-first prototype using Textual or Rich-based TUI
Phase 2: Web UI using FastAPI + React/Svelte
Phase 3: Desktop using Tauri (Rust shell + web frontend)
