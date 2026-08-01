# CYCLE 008 — ARCHITECTURE REPORT

## One Kernel, Many Faces

⸻

## Before / After

```
Before:                   After:
CLI ←→ Kernel             API Server ←→ Kernel
                            Desktop TUI ←→ API Server
                            Watchers ──→ Fabric Events ──→ Kernel
                            CLI ←→ Kernel (unchanged)
                            MCP ←→ Kernel (unchanged)
```

## Architecture Principles Applied

1. **Infrastructure before consumers** — Watchers built first, then API, then TUI
2. **Contracts before implementations** — Fabric events are the contract
3. **Persistence before distribution** — EventStore (50K ring buffer) exists before WebSocket push
4. **Verification before optimization** — 18 tests across new modules
5. **Correctness before performance** — API server is synchronous; async optimization is future
6. **Architecture before convenience** — Every layer boundary is explicit and tested

## Layer Assignments

| Module | Layer | Justification |
|--------|-------|---------------|
| `genesis.watch` | L4 (Infrastructure) | Monitors filesystem, git, provider health — foundational service |
| `genesis.server` | L5 (Application) | FastAPI server — user-facing API surface |
| `genesis.desktop` | L5 (Application) | Textual TUI — user-facing application |

## Coupling

- `genesis.watch` → `genesis.fabric` (emits events)
- `genesis.server` → `genesis.fabric` (queries kernel), `genesis.watch` (watcher status), `genesis.ai` (providers), `genesis.mcp`
- `genesis.desktop` → `genesis.server` (HTTP + WebSocket client), `genesis.fabric` (direct kernel in embedded mode)

## Architectural Risks

| Risk | Mitigation |
|------|------------|
| Textual runs sync — blocks on event queries | Use `run_async` in Textual screens |
| FastAPI server runs in-process with kernel | Thread safety in FabricKernel; use `@sync` decorators |
| Watchers create hot loops | Checksum dedup in FilesystemWatcher; poll interval configurable |
| Desktop + Server = two apps to maintain | Shared contracts (Fabric events); lib splits planned for Cycle 009 |
