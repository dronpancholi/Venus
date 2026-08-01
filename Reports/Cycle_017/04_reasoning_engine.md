# M123: Engineering Reasoning Engine

> Status: **Implemented**
> Files: `genesis/engineering/reasoning.py`
> Integration: `genesis/fabric/kernel.py` (lazy `reasoning` property)

---

## Summary

Evidence-based engineering analysis using real repository state — not an LLM. Every finding cites specific evidence from the EngineeringRegistry, event system, and knowledge base.

## Analyzers

| Analyzer | What It Detects | Evidence Source |
|----------|----------------|-----------------|
| `fragility` | Empty service registry, failed tasks, executing in degraded state | EngineeringRegistry by_type counts, task statuses |
| `architecture_decay` | Singleton patterns, underutilized types | Object type distribution |
| `coupling` | Objects with excessive cross-links | EngineeringObject link counts |
| `duplication` | Duplicated names across objects | Name frequency analysis |
| `debt` | Missing descriptions, missing tags | Object metadata completeness |
| `comprehensive` | All analyzers combined, severity-sorted | Cross-registry analysis |

## Example Output

```
[critical] fragility: No registered services
  evidence: EngineeringRegistry by_type=service count=0
[warning] duplication: 53 potentially duplicated names
  evidence: 'architecture delta': 4 occurrences
  evidence: 'entity: agentexecutionengine': 17 occurrences
[low] debt: 124 objects lack descriptions
  evidence: Cycle 004 Complete (report)
```

## Performance

- Comprehensive analysis: ~0.3ms (sub-millisecond — data already in memory)
- Each analysis is a bounded scan of the EngineeringRegistry
- No LLM calls, no external dependencies

## Integration

- Accessible via `FabricKernel.instance().reasoning`
- Findings structured as `Finding` dataclasses with severity, evidence, object_ids, recommendations
- (M129 Autonomous Review will run these analyzers on a schedule)
