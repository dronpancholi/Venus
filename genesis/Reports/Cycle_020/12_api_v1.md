# M170: Genesis API V1

**Status:** API surface defined, 19 REST endpoints + 33 in-memory routes + 5 new Cycle 020 endpoints

## Current API Surface

### REST Endpoints (FastAPI, `server.py`)

| Endpoint | Method | Status |
|----------|--------|--------|
| `/v1/health` | GET | Stable |
| `/v1/kernel/stats` | GET | Stable |
| `/v1/events` | GET | Stable |
| `/v1/events/emit` | POST | Stable |
| `/v1/services` | GET | Stable |
| `/v1/agents` | GET | Stable |
| `/v1/tasks` | GET | Stable |
| `/v1/conversations` | GET | Stable |
| `/v1/metrics` | GET | Stable |
| `/v1/audit` | GET | Stable |
| `/v1/watch` | GET | Stable |
| `/v1/providers` | GET | Stable |
| `/v1/search` | GET | Stable |
| `/v1/auth/*` | GET/POST | Stable |

### New Cycle 020 Endpoints (Recommended)

| Endpoint | Method | Source |
|----------|--------|--------|
| `/v1/health/detailed` | GET | HealthEngine.score() |
| `/v1/observability/actions` | GET | ObservabilityEngine.query() |
| `/v1/observability/export` | GET | ObservabilityEngine.export() |
| `/v1/boot/report` | GET | BootEngine.report() |
| `/v1/graph/query` | POST | CanonicalGraph.find_nodes() |
| `/v1/workspace/session` | GET | WorkspaceMemory.restore_context() |
| `/v1/workspace/session` | POST | WorkspaceMemory.save_session() |

## API Versioning Strategy

- All endpoints under `/v1/` are frozen for Cycle 020
- No breaking changes without a new version prefix (`/v2/`)
- Documented via inline docstrings and auto-generated OpenAPI
