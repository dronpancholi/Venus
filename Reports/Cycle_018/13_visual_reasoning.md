# M144 — Visual Reasoning Engine

## File
`genesis/visual_reasoning/engine.py`, `genesis/visual_reasoning/__init__.py`

## Purpose
Explainable recommendations with evidence graphs. Bridges the gap between raw analysis findings and actionable recommendations by constructing directed evidence graphs.

## Key Components

### VisualReasoningEngine
- `build_evidence_graph(recommendation, reasoning)` — constructs an evidence graph from:
  - **Recommendation node**: the actionable suggestion
  - **Observation nodes**: evidence from reasoning/analysis with confidence scores
  - **Dependency nodes**: code elements that contribute to the observation
- `list_graphs(limit)` — recent evidence graphs
- `summary()` — total graphs, nodes, edges

### EvidenceGraph
- `nodes: list[EvidenceNode]` — recommendation, observations, dependencies
- `edges: list[EvidenceEdge]` — supports/depends_on relationships with weights

## Integration
- **FabricKernel.visual_reasoning** — lazy-loaded, auto-booted
- **EngineeringRegistry** — each recommendation registered as RECOMMENDATION object with graph metadata
- **ReasoningEngine** — source of observations and risk scores
