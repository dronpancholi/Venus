# Future Cycles — Roadmap

## Cycle 021: Graph Migration & Desktop Evolution

| Priority | Item | Description |
|----------|------|-------------|
| P0 | Migrate subsystems to canonical graph | Move all 8+ direct graph users to CanonicalGraphAPI |
| P0 | Add remaining graph adapters | graphdb, hypergraph, knowledge_graph, execution_graph, etc. |
| P1 | Split screens.py (1,431 lines) | Per-screen files with `.tcss` styles |
| P1 | Add desktop tests | Textual pilot tests for all 20 screens |
| P2 | Workspace command center | Full project-aware dashboard |

## Cycle 022: Enterprise & Quality

| Priority | Item | Description |
|----------|------|-------------|
| P0 | Decompose omega_loop.py (6,575 lines) | Break into focused modules |
| P1 | Add loading indicators | Skeleton screens during data fetch |
| P1 | Replace silent except: pass | Proper error logging everywhere |
| P2 | Secrets management | Encrypted key-value store |
| P2 | Role-based access control | Restrict actions per role |

## Cycle 023: Platform & Ecosystem

| Priority | Item | Description |
|----------|------|-------------|
| P0 | App marketplace | Installable Genesis applications |
| P1 | Multi-tenant isolation | Separate state per org/project |
| P1 | Persistence for health/session | SQLite-backed health history, session persistence |
| P2 | AgentOS MCP server | Genesis as MCP server for external agents |

## Cycle 024: Performance & Scale

| Priority | Item | Description |
|----------|------|-------------|
| P0 | Lazy booting | Defer phases until first access |
| P1 | Parallel phase execution | Non-dependent phases boot in parallel |
| P1 | Graph query optimization | Indexed lookups, caching |
| P2 | Event persistence | Durable event storage with replay |
