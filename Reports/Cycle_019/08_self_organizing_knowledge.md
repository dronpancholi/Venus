# M152 — Self-Organizing Knowledge

## File
`genesis/knowledge_v2/engine.py`, `genesis/knowledge_v2/__init__.py`

## Purpose
Knowledge that reorganizes itself. Clusters emerge automatically, topics merge, duplicate concepts merge, relationships strengthen over time, frequently accessed concepts move closer together, rare concepts archive automatically, knowledge develops a hierarchy, knowledge evolves continuously.

## Key Components

### KnowledgeCluster
- `id`, `name`, `topics`, `concepts`, `items`, `access_count`, `strength`, `last_accessed`

### SelfOrganizingKnowledge
- `add_concept(concept, topic, content, source)` — add to cluster, auto-create if needed
- `access(concept)` — record access, strengthen cluster
- `search(query, limit)` — cross-cluster search ranked by strength
- `consolidate()` — merge overlapping clusters, archive inactive ones
- `stats()` — clusters, concepts, total items, strongest cluster

### Consolidation Algorithm
- Iterates cluster pairs; if overlap > 30%, merge smaller into larger
- Archives clusters with strength < 0.3 and no access in 24h
- Auto-triggers every 50 new concepts

## Integration
- **kernel.knowledge_organizer** — lazy-loaded, auto-booted
- **EngineeringState** — stores cluster/concept counts
- **EngineeringRegistry** — registered as KNOWLEDGE_NODE object
- **KnowledgeEngine** — seeded from existing knowledge
