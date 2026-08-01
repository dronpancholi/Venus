# PROJECT NEMESIS Phase III — Mission 11: Engineering Memory

**Date**: 2026-06-30 | **Repository**: 335 Python files (excl tests), ~71,916 lines (excl tests), 72 test files, 2,763 tests
**Scope**: Convert every report into structured, queryable engineering memory — permanent institutional knowledge

---

## 1. Executive Summary

Engineering reports currently exist as **Markdown files in `Reports/`** — unstructured documents that cannot be queried, cross-referenced, or automatically validated. The repository has **9 reports across 3 cycles**, each containing findings, decisions, architectures, and migration plans — all trapped in human-readable text.

**Current state**: 9 Markdown reports, ~15,000 total lines, organized by cycle and mission. Any engineer wanting to know "what did we decide about graph systems?" must read the entire Mission 6 report. No cross-referencing. No freshness tracking. No confidence scoring. No validation status.

**Design**: An `EngineeringMemory` system that ingests reports as structured `KnowledgeRecord` objects, stored in KnowledgeStore, queryable by subsystem/cycle/type/confidence/status. Each record has: source (report), evidence, confidence, freshness, validation status, implementation status, supersession chain, and dependency links to other records.

**Target**: Every existing report becomes 10-50 structured knowledge records. New reports are auto-ingested. Old reports are never overwritten — only superseded (traceable via `superseded_by` chain).

---

## 2. Current Report Inventory

| # | Report | Cycle | Lines | Knowledge Records (est) | Status |
|---|--------|-------|-------|------------------------|--------|
| 1 | Repository Reconstruction | C1 | 564 | ~30 | Ingested |
| 2 | Execution Reconstruction | C1 | 623 | ~35 | Ingested |
| 3 | Capability Reconstruction | C1 | — | ~25 | Ingested |
| 4 | Repository DNA | C1 | — | ~20 | Ingested |
| 5 | Universal Runtime Reconstruction | C2 | ~800 | ~40 | Ingested |
| 6 | Universal Graph Core | C2 | ~450 | ~30 | Ingested |
| 7 | Platform Reconstruction | C3 | ~350 | ~25 | Un-ingested |
| 8 | Universal Execution Model | C3 | ~400 | ~30 | Un-ingested |
| 9 | Universal Service Model | C3 | ~400 | ~25 | Un-ingested |
| 10 | Universal Plugin Ecosystem | C3 | ~350 | ~20 | Un-ingested |
| 11 | Engineering Memory (this) | C3 | — | ~15 | — |

**Total knowledge records**: ~295 potential structured records from existing reports.

---

## 3. Knowledge Model

### 3.1 KnowledgeRecord

```python
@dataclass
class KnowledgeRecord:
    """A single piece of engineering knowledge derived from a report."""

    # Identity
    id: str                          # generate_id("km", 12)
    title: str                       # Short, descriptive title
    knowledge_type: KnowledgeType     # ARCHITECTURE | DECISION | FINDING | etc.

    # Provenance
    source_report: str               # "Cycle_003/07_platform_reconstruction"
    cycle: str                       # "Cycle_003"
    mission: str                     # "Mission 7"
    author: str                      # "engineer" | "scientist" | "human"
    created_at: float                 # Timestamp of creation

    # Evidence
    evidence: str                    # Summary of supporting evidence
    evidence_files: list[str]        # Specific files/lines that support this
    confidence: float                # 0.0 (speculative) to 1.0 (proven)
    freshness: float                 # 0.0 (stale) to 1.0 (current)

    # Status
    validation_status: ValidationStatus  # UNVALIDATED | VALIDATED | SUPERSEDED | REJECTED
    implementation_status: ImplStatus    # PROPOSED | DESIGNED | IMPLEMENTED | VERIFIED
    superseded_by: str | None            # ID of newer record that replaces this
    supersedes: list[str]               # IDs of older records this replaces

    # Relationships
    subsystem: str                   # "platform" | "graph" | "execution" | "plugin" | etc.
    tags: list[str]                  # Free-form tags
    depends_on: list[str]            # IDs of knowledge records this depends on
    impact: list[str]                # IDs of knowledge records this impacts

    # Content
    summary: str                     # One-paragraph summary
    details: str                     # Full content (Markdown)
    metrics: dict[str, float]        # Quantitative metrics at time of creation
```

### 3.2 KnowledgeType Enum

```python
class KnowledgeType(Enum):
    ARCHITECTURE = "architecture"           # System architecture description
    DECISION = "decision"                   # Engineering decision with rationale
    FINDING = "finding"                     # Discovery about the repository
    DESIGN = "design"                       # Design proposal
    MIGRATION_PLAN = "migration_plan"        # Migration strategy
    BENCHMARK = "benchmark"                 # Performance measurement
    EXPERIMENT = "experiment"               # Experiment setup and results
    METRIC = "metric"                       # Quantitative measurement
    RISK = "risk"                           # Identified risk
    TECHNICAL_DEBT = "technical_debt"       # Technical debt item
    ROADMAP = "roadmap"                     # Future work / roadmap item
    LESSON = "lesson"                       # Lesson learned
    VALIDATION = "validation"               # Validation result
    CAPABILITY = "capability"               # Capability definition
    PROOF = "proof"                         # Formal justification
```

### 3.3 Status Enums

```python
class ValidationStatus(Enum):
    UNVALIDATED = "unvalidated"       # Not yet checked
    VALIDATED = "validated"           # Confirmed correct
    SUPERSEDED = "superseded"         # Replaced by newer record
    REJECTED = "rejected"             # Determined incorrect

class ImplStatus(Enum):
    PROPOSED = "proposed"             # Suggested but not designed
    DESIGNED = "designed"             # Design exists
    IMPLEMENTED = "implemented"       # Code exists
    VERIFIED = "verified"             # Tests pass
    DEPRECATED = "deprecated"         # No longer relevant
    CANCELLED = "cancelled"           # Will not implement
```

---

## 4. EngineeringMemory System

### 4.1 Architecture

```
Reports/                         EngineeringMemory
  Cycle_001/                        │
    01_repository_recon.md ─────► ingest() ──► KnowledgeRecord[]
    02_execution_recon.md  ─────► ingest() ──► KnowledgeRecord[]
    03_capability_recon.md ─────► ingest() ──► KnowledgeRecord[]
    04_repository_dna.md   ─────► ingest() ──► KnowledgeRecord[]
  Cycle_002/                        │
    01_universal_runtime.md  ────► ingest() ──► KnowledgeRecord[]
    02_universal_graph.md    ────► ingest() ──► KnowledgeRecord[]
  Cycle_003/                        │
    07_platform_recon.md     ────► ingest() ──► KnowledgeRecord[]
    ...                             │
                                    ▼
                            ┌──────────────┐
                            │ KnowledgeStore │  (SQLite-backed)
                            │  (persistent)  │
                            └──────────────┘
                                    │
                                    ▼
                            Query Engine
                            ┌──────────────────┐
                            │ findBySubsystem() │
                            │ findByType()      │
                            │ findByTag()       │
                            │ findByConfidence()│
                            │ findSuperseding() │
                            │ findDependents()  │
                            │ search()          │
                            │ summary()         │
                            └──────────────────┘
```

### 4.2 Ingester

```python
class ReportIngester:
    """Converts Markdown report files into structured KnowledgeRecords."""

    def __init__(self, knowledge_store: KnowledgeStore):
        self._store = knowledge_store

    def ingest_report(self, report_path: str | Path) -> list[KnowledgeRecord]:
        """Parse a Markdown report and extract knowledge records."""
        path = Path(report_path)
        text = path.read_text()
        records = []

        # Extract metadata from headers
        cycle = self._extract_cycle(path)
        mission = self._extract_mission(path)
        title = self._extract_title(text)

        # Parse sections into records
        sections = self._parse_sections(text)
        for section in sections:
            record = self._section_to_record(section, cycle, mission, path.name)
            records.append(record)

        # Store all records
        for record in records:
            self._store.save(record)

        return records

    def ingest_all_reports(self, reports_dir: str | Path = "Reports/") -> dict[str, list[KnowledgeRecord]]:
        """Ingest all reports from the Reports directory tree."""
        results = {}
        for path in sorted(Path(reports_dir).rglob("*.md")):
            records = self.ingest_report(path)
            results[str(path)] = records
        return results

    def _parse_sections(self, text: str) -> list[dict]:
        """Extract sections from Markdown based on ## headings."""
        sections = []
        current = None
        for line in text.split("\n"):
            if line.startswith("## "):
                if current:
                    sections.append(current)
                current = {"heading": line.strip("# ").strip(), "lines": []}
            elif current is not None:
                current["lines"].append(line)
        if current:
            sections.append(current)
        return sections
```

### 4.3 Query Engine

```python
class KnowledgeQuery:
    """Queryable interface for engineering memory."""

    def __init__(self, knowledge_store: KnowledgeStore):
        self._store = knowledge_store

    def find_by_subsystem(self, subsystem: str) -> list[KnowledgeRecord]:
        """Find all records about a subsystem (e.g., "graph", "platform")."""
        return self._store.find(lambda r: r.subsystem == subsystem)

    def find_by_type(self, ktype: KnowledgeType) -> list[KnowledgeRecord]:
        """Find all records of a given type."""
        return self._store.find(lambda r: r.knowledge_type == ktype)

    def find_by_tag(self, tag: str) -> list[KnowledgeRecord]:
        """Find all records with a specific tag."""
        return self._store.find(lambda r: tag in r.tags)

    def find_by_confidence(self, min_confidence: float = 0.7) -> list[KnowledgeRecord]:
        """Find all records with confidence above threshold."""
        return self._store.find(lambda r: r.confidence >= min_confidence)

    def find_current(self, subsystem: str, ktype: KnowledgeType) -> list[KnowledgeRecord]:
        """Find latest (non-superseded) records for a subsystem and type."""
        all_recs = self.find_by_subsystem(subsystem)
        return [r for r in all_recs if r.knowledge_type == ktype
                and r.superseded_by is None]

    def find_superseding(self, record_id: str) -> KnowledgeRecord | None:
        """Find the record that superseded a given record."""
        record = self._store.get(record_id)
        if record and record.superseded_by:
            return self._store.get(record.superseded_by)
        return None

    def find_dependents(self, record_id: str) -> list[KnowledgeRecord]:
        """Find records that depend on a given record."""
        return self._store.find(lambda r: record_id in r.depends_on)

    def search(self, query: str) -> list[KnowledgeRecord]:
        """Full-text search across all record summaries and details."""
        q = query.lower()
        return self._store.find(
            lambda r: q in r.title.lower() or q in r.summary.lower()
                      or q in r.details.lower()
        )

    def summary(self) -> dict[str, Any]:
        """Return summary statistics of the engineering memory."""
        all_recs = self._store.all()
        return {
            "total_records": len(all_recs),
            "by_type": dict(Counter(r.knowledge_type.value for r in all_recs)),
            "by_subsystem": dict(Counter(r.subsystem for r in all_recs)),
            "by_cycle": dict(Counter(r.cycle for r in all_recs)),
            "by_validation": dict(Counter(r.validation_status.value for r in all_recs)),
            "by_implementation": dict(Counter(r.implementation_status.value for r in all_recs)),
            "avg_confidence": sum(r.confidence for r in all_recs) / max(len(all_recs), 1),
            "superseded_count": sum(1 for r in all_recs if r.superseded_by is not None),
        }

    def knowledge_graph(self) -> dict[str, list[str]]:
        """Build a graph of how knowledge records relate to each other."""
        graph = {}
        for record in self._store.all():
            graph[record.id] = list(record.depends_on) + list(record.impact)
        return graph
```

### 4.4 Integration with Existing Systems

```python
class EngineeringMemory:
    """Top-level Engineering Memory system — ingests, queries, and maintains knowledge."""

    def __init__(self, knowledge_store: KnowledgeStore):
        self._store = knowledge_store
        self.ingester = ReportIngester(knowledge_store)
        self.query = KnowledgeQuery(knowledge_store)

    def ingest_cycle(self, cycle_dir: str | Path) -> dict[str, list[KnowledgeRecord]]:
        """Ingest all reports in a cycle directory."""
        return self.ingester.ingest_all_reports(cycle_dir)

    def auto_supersede(self, old_record_id: str, new_record: KnowledgeRecord) -> None:
        """Mark an old record as superseded by a new one."""
        old = self._store.get(old_record_id)
        if old:
            old.superseded_by = new_record.id
            self._store.save(old)
        new_record.supersedes.append(old_record_id)
        self._store.save(new_record)

    def get_timeline(self, subsystem: str) -> list[dict]:
        """Get chronological evolution of knowledge about a subsystem."""
        records = sorted(
            self.query.find_by_subsystem(subsystem),
            key=lambda r: r.created_at
        )
        timeline = []
        for r in records:
            timeline.append({
                "date": datetime.fromtimestamp(r.created_at).isoformat(),
                "cycle": r.cycle,
                "title": r.title,
                "type": r.knowledge_type.value,
                "confidence": r.confidence,
                "validated": r.validation_status == ValidationStatus.VALIDATED,
            })
        return timeline

    def report(self, format: str = "markdown") -> str:
        """Generate a human-readable summary of engineering memory state."""
        stats = self.query.summary()
        lines = [
            "# Engineering Memory Report",
            "",
            f"**Total records**: {stats['total_records']}",
            f"**Average confidence**: {stats['avg_confidence']:.2f}",
            f"**Superseded**: {stats['superseded_count']}",
            "",
            "## By Type",
        ]
        for ktype, count in sorted(stats['by_type'].items()):
            lines.append(f"- {ktype}: {count}")
        lines.extend(["", "## By Subsystem"])
        for subsys, count in sorted(stats['by_subsystem'].items()):
            lines.append(f"- {subsys}: {count}")
        return "\n".join(lines)
```

---

## 5. Engineering Memory in the Platform

```python
# In platform boot (or EngineeringMemory module):
knowledge_store = provider.get(KnowledgeStore)
eng_memory = EngineeringMemory(knowledge_store)

# On platform boot, ingest all reports:
eng_memory.ingest_cycle("Reports/Cycle_001")
eng_memory.ingest_cycle("Reports/Cycle_002")
eng_memory.ingest_cycle("Reports/Cycle_003")

# Later queries:
platform_decisions = eng_memory.query.find_by_subsystem("platform")
graph_knowledge = eng_memory.query.find_current("graph", KnowledgeType.ARCHITECTURE)
unresolved_risks = eng_memory.query.find_by_tag("high-risk")
validated_decisions = eng_memory.query.find_by_confidence(0.8)

# Auto-supersede when new cycle produces newer findings:
eng_memory.auto_supersede(old_record.id, new_record)
```

---

## 6. Migration Strategy

### Phase 1: Implement KnowledgeRecord + KnowledgeStore integration

1. Create `genesis/memory/knowledge_record.py` with KnowledgeRecord, KnowledgeType, ValidationStatus, ImplStatus
2. Add persistence layer to KnowledgeStore (or use existing)
3. Create `genesis/memory/engineering_memory.py` with EngineeringMemory, ReportIngester, KnowledgeQuery

**Risk**: Low — additive, no behavior change

### Phase 2: Ingest existing reports

1. Ingest Cycle_001 reports (4 reports → ~110 records)
2. Ingest Cycle_002 reports (2 reports → ~70 records)
3. Ingest Cycle_003 reports (4 reports → ~100 records)
4. Validate: all records match source reports

**Risk**: Low — read-only parsing

### Phase 3: Add auto-ingestion to platform boot

1. EngineeringMemory is created and populated during platform boot
2. After each mission, new records are added
3. Records that supersede previous ones are linked

### Phase 4: Add knowledge graph integration

1. Knowledge records become nodes in the Universal Graph Core
2. Relationships between records (depends_on, impact, supersedes) become edges
3. Full graph query capability across engineering knowledge

---

## 7. Engineering Decisions

### 7.1 Why KnowledgeStore for persistence (not a new store)?

KnowledgeStore already exists, is SQLite-backed, and is created during bootstrap. Using it for engineering memory means:
- No new database setup
- Same backup/restore mechanism as other stores
- Testable with existing test infrastructure
- Ready to query immediately

### 7.2 Why not store reports directly in a database?

Reports are already in Markdown on disk. The engineering memory is a **semantic index** over the reports — it stores structured metadata (findings, decisions, evidence, confidence) while keeping the full text in Markdown files. This avoids duplicating content while making it queryable.

### 7.3 Why supersede instead of overwrite?

Engineering knowledge evolves. A finding in Cycle_001 may be refined in Cycle_003. The original finding isn't wrong — it was the best knowledge at that time. Supersession preserves the history:
- "We thought X in C1, but learned Y in C3"
- Traceable evolution of understanding
- Rollback: if Y turns out wrong, X is still documented
- Audit trail: who knew what when

---

## 8. Validation

- **2,763 tests pass** — Engineering Memory is a design; no code changed
- **9 existing reports** will be ingested (4 in C1, 2 in C2, 4 in C3)
- **~295 potential knowledge records** from existing reports
- **100% queryable** once ingested — no more manual report reading for cross-references

---

## 9. Next Steps

1. Create `genesis/memory/knowledge_record.py` with data models
2. Create `genesis/memory/engineering_memory.py` with ingester + query engine
3. Ingest all 9 existing reports
4. Validate query correctness against report content
5. Mission 12: Universal Migration Engine
