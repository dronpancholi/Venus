# M136 — Engineering Search V2

## File
`genesis/fabric/kernel.py` (kernel.search()), `genesis/server.py` (GET /v1/search)

## Purpose
Unified multi-source engineering search across registry, knowledge, events, audit, timeline, and AI providers. Semantic ranking with relevance scores.

## API

### `kernel.search(query, sources="all", limit=20)`
Searches across:
- **registry/engineering**: EngineeringObject name/type matches (relevance 0.9)
- **knowledge**: KnowledgeEngine structured items (relevance 0.85)
- **events**: Fabric events type/origin/payload (relevance 0.7)
- **audit**: Audit log action/actor (relevance 0.6)
- **timeline**: UniversalTimeline entries (relevance 0.75)
- **providers/ai**: AI provider IDs (relevance 0.8)

### `GET /v1/search?query=...&sources=...&limit=...`
Same functionality exposed as REST API endpoint.

## Integration
- **SearchEverywhere** desktop palette uses KnowledgeEngine
- **Server** exposes search endpoint for external consumers
- **Error handling**: all sources are optional, gracefully degrades if subsystem unavailable
