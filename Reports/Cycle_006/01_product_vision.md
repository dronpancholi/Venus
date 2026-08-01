# Cycle 006 — Product Vision

## From Engineering Kernel to Engineering Product

Genesis has spent five cycles building the engineering kernel — an operating system for
understanding, analyzing, simulating, and evolving software repositories. The kernel is
architecturally sound: 3,100+ tests pass, the governance layer enforces layering, the
graph system converges toward a unified model, and the autonomous engineering pipeline
can analyze, plan, and generate patches.

This cycle marks the transition.

Genesis must simultaneously remain a rigorous engineering kernel AND become a product
that developers choose to use every day. The two goals are not in tension — every
product improvement must also improve the kernel, and every kernel improvement must
also improve the product.

## Product Principles

1. **The interface disappears** — the engineering becomes the focus
2. **Calm intelligence** — surfaces what matters, hides what doesn't
3. **Speed as a feature** — every interaction under 100ms or show progress
4. **Predictable** — consistent patterns, no surprises
5. **Premium feel** — every pixel intentional, every animation meaningful

## Product Surfaces

| Surface | Priority | Description |
|---------|----------|-------------|
| **Genesis CLI** | P0 | Existing argparse CLI; needs upgrade to modern UX (rich, progress bars, colors) |
| **Genesis MCP Server** | P0 | Expose all capabilities as MCP tools for IDE integration |
| **Genesis API** | P0 | REST + WebSocket API for external consumers |
| **Genesis Desktop** | P1 | Native desktop app (Electron/Tauri) |
| **Genesis Web** | P1 | Web app for the same experience |
| **Genesis SDK (Python)** | P1 | Python client library wrapping the API |
| **Genesis SDK (TypeScript)** | P2 | TypeScript client library |

All surfaces share one engineering kernel. No duplicated logic.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Product Surfaces                       │
│  CLI  │  MCP  │  API  │  Desktop  │  Web  │  SDK        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               Genesis Kernel (genesis/)                  │
│  Platform Orchestrator  │  ServiceKernel                │
│  Governance             │  EngineeringMemory            │
│  Graphs                 │  Mathematics                  │
│  Simulation             │  Proof Engine                 │
│  Autonomous Agents      │  AI Provider Platform         │
└─────────────────────────────────────────────────────────┘
```

## User Journey (First Run)

1. Install: `pip install genesis` or `brew install genesis` or download desktop app
2. Open Genesis → **Home** screen appears
3. Connect a repository → Genesis scans, indexes, builds knowledge graph
4. Connect an AI provider → Genesis tests capabilities, measures latency, sets defaults
5. Genesis begins autonomous observation → detects issues, generates recommendations
6. User explores architecture, memory, agents, governance through the interface
7. User approves changes → Genesis applies, tests, benchmarks, updates knowledge

## Experience Principles

- **Every screen answers**: What is happening? What is important? What needs attention?
- **Zero-config onboarding**: Connect repo + AI provider = full experience
- **Progressive disclosure**: Simple by default, powerful when needed
- **Live by default**: All data updates in real-time
- **Agent-first**: Agents work continuously; user reviews and approves
- **Keyboard-native**: Every action has a shortcut; command palette is primary interface
