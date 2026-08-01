# M131: Genesis Public API

> Status: **Designed** (foundation built)
> Enablers: M121 (EngineeringObject), M122 (KnowledgeEngine), M124 (Copilot), M125 (Timeline)

---

## Architecture

Stable, versioned, documented API surface for all Genesis subsystems.

## Proposed Endpoints (21 existing + new)

| Existing Endpoint | Status | M131 Action |
|-------------------|--------|-------------|
| `GET /v1/health` | Tested, no consumer | Stabilize, document |
| `GET /v1/kernel/stats` | Tested, no consumer | Stabilize |
| `GET /v1/events` | Tested | Add timeline integration |
| `GET /v1/services` | Tested | Return EngineeringObject format |
| `GET /v1/agents` | Tested | Return EngineeringObject format |
| `GET /v1/tasks` | Tested | Return EngineeringObject format |
| `GET /v1/conversations` | Tested | Return EngineeringObject format |
| `POST /v1/auth/token` | Tested | Wire SecurityManager properly |
| `WS /v1/ws` | Partially broken | Fix queue drain, add auth |

**New endpoints needed:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/engineering/objects` | GET | List/search EngineeringObjects |
| `/v1/engineering/objects/{id}` | GET | Get EngineeringObject by ID |
| `/v1/engineering/objects/{id}/relationships` | GET | Get relationships |
| `/v1/knowledge/search` | GET | Search knowledge items |
| `/v1/knowledge/decisions` | GET | Get engineering decisions |
| `/v1/knowledge/recommendations` | GET | Get recommendations |
| `/v1/timeline` | GET | Query timeline |
| `/v1/reasoning/analyze` | POST | Run engineering analysis |
| `/v1/copilot/ask` | POST | Ask copilot (context-aware) |

## Existing Foundation

- FastAPI server already has 21 endpoints with correct structure
- EngineeringRegistry supports lookup/search by type/tag
- KnowledgeEngine supports search, decisions, recommendations
- CopilotEngine supports contextual Q&A
- UniversalTimeline supports time-range queries
- Auth system exists but needs proper wiring (SecurityManager)
