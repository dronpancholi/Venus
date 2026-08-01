# M128: Engineering Project Intelligence

> Status: **Designed**
> Enablers: M121 (EngineeringObject), M122 (KnowledgeEngine), M123 (Reasoning)

---

## Architecture

Multiple repositories grouped into intelligent Projects with:

| Metric | Source | Implementation |
|--------|--------|---------------|
| **Health** | ReasoningEngine fragility analysis | Aggregated findings across project objects |
| **Velocity** | TaskGraph critical path + completion rate | Task node completion timestamps |
| **Risk** | KnowledgeEngine risks + failed tasks | Risky findings per project |
| **Knowledge** | KnowledgeEngine coverage | Indexed reports + entities per project |
| **Architecture** | Object type distribution | Registry by-type stats per project |
| **Activity** | Timeline event frequency | Timeline entries per time window |

## Implementation Path

1. `EngineeringProject(EngineeringObject)` with `project_type` = PROJECT
2. Repositories linked via `EngineeringRelationship(relationship_type="belongs_to")`
3. Health/velocity/risk computed on refresh from aggregated child objects
4. Desktop: new screen or tab in RepositoryScreen
