# M122: Engineering Knowledge Engine

> Status: **Implemented**
> Files: `genesis/knowledge/parser.py`, `genesis/knowledge/engine.py`, `genesis/knowledge/__init__.py`
> Integration: `genesis/fabric/kernel.py` (lazy `knowledge` property)

---

## Summary

Reports are no longer static markdown files. The Knowledge Engine automatically parses every report into structured knowledge: entities, decisions, recommendations, risks, architecture patterns — stored as EngineeringObjects.

Architecture knowledge, decisions, and lessons are now machine-readable, searchable, and cross-referenced through the EngineeringRegistry.

## Architecture

```
KnowledgeEngine
├── index_reports() → parses Reports/ directory
│   └── parse_reports_directory()
│       └── parse_report(filepath) → ParsedReport
│           ├── extract_entities() → ["FabricKernel", "M110", "TDR-001", ...]
│           ├── extract_decisions() → ["Decision: ..."]
│           ├── extract_recommendations() → ["Recommendation: ..."]
│           ├── extract_risks() → ["Risk: ..."]
│           ├── extract_patterns() → ["Architecture: ..."]
│           └── extract_tags() → ["audit", "performance", ...]
├── search(query, kind, tag) → EngineeringObject[]
├── search_reports(query, cycle) → ParsedReport[]
├── get_decisions() → KnowledgeItem[]
└── get_recommendations() → KnowledgeItem[]
```

## Extraction Results

| Metric | Count |
|--------|-------|
| Reports indexed | 149 (across 16 cycles) |
| Knowledge items total | 916 |
| Entities discovered | 793 |
| Decisions extracted | 39 |
| Recommendations | 27 |
| Risks identified | 14 |
| Architecture patterns | 43 |

## Integration

- Accessible via `FabricKernel.instance().knowledge`
- All knowledge items stored as `EngineeringObject` with type `KNOWLEDGE_NODE`
- Reports stored as EngineeringObjects with relationships to extracted knowledge
- SearchEngine can query both reports and knowledge items
- (M124 Copilot and M127 Knowledge Graph will consume these objects)
