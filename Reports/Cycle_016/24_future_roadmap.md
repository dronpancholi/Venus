# Cycle 016 — Future Roadmap

## Cycle 017: "Production Confidence"
1. **Auth Hardening** — HMAC tokens, WS auth, credential validation
2. **Error Handling Overhaul** — Replace 30+ `except: pass` with structured errors, error screen
3. **Event-Driven Primary** — Make EventRouter the primary update path; timer is fallback only
4. **Desktop Tests** — Textual pilot tests for all 11 screens
5. **AI Pipeline MVP** — Planner, Model Router, Verifier, Critic stages
6. **Multi-Agent Desktop** — Wire brain module agents into desktop agent screen
7. **Professional Polish** — Loading indicators, scroll preservation, last-updated timestamps

## Cycle 018: "Platform Maturity"
1. **AI Pipeline Complete** — All 14 stages implemented and observable
2. **Multi-Agent System** — 10 specialized agents with goals, permissions, tools
3. **Genesis SDK** — `genesis-sdk` PyPI package, plugin CLI, templates
4. **Storage Migration** — Schema versioning, backup/restore, commit consistency
5. **AI Workspaces** — Persistent conversations with context, memory, repository state
6. **API Versioning** — All APIs at `agentos/v1/*`

## Cycle 019: "AgentOS Foundations"
1. **Stable API Surface** — All interfaces extracted to `genesis/interfaces/`
2. **OpenAPI Documentation** — Auto-generated API docs with Swagger UI
3. **Plugin Marketplace** — Plugin discovery, installation, version management
4. **Performance Budgets** — Startup <1s, navigation <50ms, event delivery <1ms
5. **Cross-Platform** — Windows terminal support, CI/CD pipeline

## Cycle 020: "AgentOS Runtime"
1. **AgentOS Alpha** — First version of AgentOS running on Genesis
2. **Self-Hosting** — Genesis manages its own development workflow
3. **Enterprise Features** — SSO, audit trails, team workspaces, RBAC UI
