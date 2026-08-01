# PROJECT NEXUS PHASE II — Mission 6: Universal Engineering Knowledge & Memory

**Date**: 2026-06-30

---

## 1. Current State

Engineering artifacts are stored as unstructured files:

```
_generated/
├── reports/
│   ├── srec_cycle_001.md
│   ├── nexus_capability_discovery.md
│   └── ... (7 nexus reports)
├── atlas/
│   └── (15 JSON files per run)
└── nexus_phase_ii/
    └── (emerging structure)

genesis/decisions/
├── EDR-001-plugin-registry-pattern.md
└── EDR-002-atlas-omegaloop-feedback-loop.md
```

**Problems**:
- No standard metadata attached to artifacts
- No cross-linking between related artifacts
- No query capability ("find all reports mentioning 'duplication'")
- No versioning of engineering knowledge
- No programmatic access to past findings

## 2. Proposed: EngineeringKnowledgeStore

### Schema

```python
@dataclass
class KnowledgeArtifact:
    """Standard metadata for every engineering artifact."""
    id: str                         # generate_id("knowledge")
    type: KnowledgeType             # REPORT, DECISION, BENCHMARK, etc.
    title: str
    author: str                     # "EngineeringIntelligence" or user name
    created_at: str                 # ISO timestamp
    tags: list[str]                 # ["duplication", "consolidation", "platform"]
    source: str                     # File path or "inline"
    content_hash: str               # SHA256 of content
    summary: str                    # 1-3 sentence summary
    content: str                    # Full content
    related_ids: list[str]          # Cross-links to other artifacts
    metrics: dict[str, float]       # Key metrics at time of creation
    confidence: float               # 0.0-1.0 (for AI-generated)
```

### KnowledgeType Enum

```python
class KnowledgeType(Enum):
    REPORT = "report"           # Generated analysis report
    DECISION = "decision"       # Engineering Decision Record
    BENCHMARK = "benchmark"     # Performance/correctness benchmark
    EXPERIMENT = "experiment"   # Scientific experiment record
    MIGRATION = "migration"     # Migration tracking record
    ROADMAP = "roadmap"         # Future work plan
    HYPOTHESIS = "hypothesis"   # Engineering hypothesis
    OBSERVATION = "observation" # Raw observation
    REVIEW = "review"           # Architecture/design review
    METRIC = "metric"           # Metric measurement
```

### Store API

```python
class EngineeringKnowledgeStore:
    """Persistent store for all engineering knowledge artifacts."""

    def save(self, artifact: KnowledgeArtifact) -> str:
        """Persist artifact. Returns its ID."""

    def get(self, artifact_id: str) -> KnowledgeArtifact | None:
        """Retrieve by ID."""

    def find(self, *, types: list[KnowledgeType] | None = None,
             tags: list[str] | None = None,
             author: str | None = None,
             time_range: tuple[str, str] | None = None) -> list[KnowledgeArtifact]:
        """Query artifacts by various criteria."""

    def search(self, query: str) -> list[KnowledgeArtifact]:
        """Full-text search across all artifacts."""

    def get_related(self, artifact_id: str) -> list[KnowledgeArtifact]:
        """Get all artifacts linked to the given one."""

    def get_latest(self, type: KnowledgeType, n: int = 5) -> list[KnowledgeArtifact]:
        """Get N most recent artifacts of a given type."""

    def export(self, path: str) -> None:
        """Export all knowledge to JSON for external consumption."""

    def summary(self) -> dict:
        """Count by type, total artifacts, date range."""
```

## 3. Integration with Existing Systems

### Atlas Integration
Atlas Stage 14 (Reporting) should save results to EngineeringKnowledgeStore:
```python
# In Atlas Stage 14
knowledge = EngineeringKnowledgeStore()
artifact = KnowledgeArtifact(
    id=generate_id("knowledge"),
    type=KnowledgeType.REPORT,
    title=f"Atlas Run {run_id}",
    author="AtlasEngine",
    created_at=datetime.now(timezone.utc).isoformat(),
    tags=["atlas", "analysis"],
    content_hash=hashlib.sha256(json.dumps(results).encode()).hexdigest(),
    summary=f"Atlas analyzed {results['file_count']} files, found {results['problem_count']} problems",
    content=json.dumps(results, indent=2),
    related_ids=[],
    metrics={"files": results["file_count"], "problems": results["problem_count"]},
    confidence=1.0,
)
knowledge.save(artifact)
```

### OmegaLoop Integration
Book XII (Self Evolution) queries past knowledge to generate roadmap:
```python
# In Book XII
knowledge = EngineeringKnowledgeStore()
past_reports = knowledge.find(tags=["duplication"], types=[KnowledgeType.REPORT])
problems = knowledge.find(types=[KnowledgeType.OBSERVATION], tags=["high-severity"])
```

### Report Generation
Every generated report should also be saved to the store:
```python
# In report generation
knowledge.save(KnowledgeArtifact(
    type=KnowledgeType.REPORT,
    title=title,
    author="EngineeringIntelligence",
    tags=[...],
    content=report_content,
    ...
))
```

## 4. Implementation Plan

| Phase | Change | Effort | Risk |
|-------|--------|--------|------|
| 1 | Create genesis/engineering/knowledge.py with store | 1d | None |
| 2 | Integrate with Atlas Stage 14 | 0.5d | Low |
| 3 | Integrate with OmegaLoop Book XII | 0.5d | Low |
| 4 | Add CLI commands for querying | 0.5d | None |
| 5 | Migrate existing reports to store | 1d | Low |

## 5. Effort

**Total**: 3.5 days | **Dependencies**: None (standalone module, uses existing persistence)
