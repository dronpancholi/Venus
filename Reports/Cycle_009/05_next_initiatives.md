# CYCLE 009 — NEXT INITIATIVES REPORT

---

## Ranked Backlog

### Critical (Cycle 010)

| # | Initiative | Est. Effort | Unlocks |
|---|-----------|-------------|---------|
| 1 | **WebSocket reconnection** | 2h | Reliable desktop connectivity |
| 2 | **API authentication (API key)** | 4h | Safe network exposure |
| 3 | **Event buffering/rate limiting** | 3h | Stability under high event volume |
| 4 | **Query execution from desktop** | 4h | Interactive KG exploration |

### High (Cycle 010-011)

| # | Initiative | Est. Effort | Unlocks |
|---|-----------|-------------|---------|
| 5 | **Multi-workspace support** | 6h | Multiple repos |
| 6 | **Task executor loop in kernel** | 4h | Autonomous task execution |
| 7 | **Provider health UI in desktop** | 3h | Provider management |
| 8 | **WebSocket per-client filters** | 3h | Scalability |
| 9 | **Migration engine** | 8h | Schema evolution |
| 10 | **Backend-to-Fabric wiring** | 8h | Connect compiler/graph to Fabric |

### Medium (Cycle 011-012)

| # | Initiative | Est. Effort | Unlocks |
|---|-----------|-------------|---------|
| 11 | **Dark/light theme toggle** | 2h | User preference |
| 12 | **Event search in desktop** | 3h | Debugging |
| 13 | **CI/CD integration** | 8h | Pipeline integration |
| 14 | **Plugin system** | 20h | Ecosystem |
| 15 | **Graph visualization in desktop** | 10h | Visual KG |

### Low (Cycle 012+)

| # | Initiative | Est. Effort | Unlocks |
|---|-----------|-------------|---------|
| 16 | **Native desktop (Tauri)** | 40h | Production desktop |
| 17 | **Install wizard** | 8h | First-run experience |
| 18 | **Distributed mode** | 40h | Team collaboration |
| 19 | **Formal verification** | 80h | Correctness proof |
| 20 | **Self-hosting** | 120h | Genesis runs on Genesis |

## Estimated Effort for Cycle 010

- **16-20 engineering hours** (critical + high priority)
- **4-5 focused sessions** (4h each)
- **Target: 3,500+ tests, 100% pass**

## Architectural Debt Remaining

| Debt | Severity | Owner |
|------|----------|-------|
| WebSocket has no reconnection logic | MEDIUM | fabric/transport |
| API has no authentication | MEDIUM | server |
| Events can grow unbounded | MEDIUM | storage/events |
| Desktop has no real KG visualization | MEDIUM | desktop |
| Backend (compiler/graph) not wired to Fabric | LOW | integration |
| No migration engine for schema changes | LOW | storage |
