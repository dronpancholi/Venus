"""
Intelligence Service — VRIP intelligence with Engineering Brain sync.

Wraps RepositoryIntelligence and automatically registers all intelligence
findings (issues, gaps, capabilities, planning initiatives) as BrainEntities.
Syncs the VRIP KnowledgeGraph to the brain after each run_all().

Usage:
    service = IntelligenceService(brain=brain)
    results = service.run_all()
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from genesis.brain import EngineeringBrain, BrainEntity
from genesis.intelligence.engine import RepositoryIntelligence
from genesis.intelligence.kgraph import KnowledgeGraph
from genesis.intelligence.gaps import GapDetector
from genesis.intelligence.metrics import MetricsCollector
from genesis.intelligence.planning import StrategicPlanner
from genesis.persistence import CheckpointStore

__all__ = [
    "IntelligenceService",
    "RepositoryIntelligence",
    "KnowledgeGraph",
    "MetricsCollector",
    "GapDetector",
    "StrategicPlanner",
]


ROOT = Path(__file__).resolve().parent.parent


class IntelligenceService:
    """VRIP intelligence with automatic Engineering Brain synchronization.

    Every intelligence finding (issue, gap, capability, planning initiative)
    is registered as a BrainEntity. The VRIP KnowledgeGraph is synced to
    the brain after each run_all().
    """

    def __init__(
        self,
        brain: EngineeringBrain | None = None,
        root: Path | str | None = None,
        checkpoint_store: CheckpointStore | None = None,
        quiet: bool = False,
    ):
        self._brain = brain
        self._engine = RepositoryIntelligence(
            root=Path(root) if root else ROOT,
            checkpoint_store=checkpoint_store,
            quiet=quiet,
        )
        self._sync_count = 0

    @property
    def brain(self) -> EngineeringBrain | None:
        return self._brain

    @property
    def engine(self) -> RepositoryIntelligence:
        return self._engine

    @property
    def kg(self) -> KnowledgeGraph:
        return self._engine.kg

    def run_all(self) -> dict[str, Any]:
        """Run all VRIP phases and sync results to the brain."""
        results = self._engine.run_all()
        if self._brain is not None:
            self._sync_results(results)
        return results

    def _sync_results(self, results: dict[str, Any]):
        """Register all intelligence findings as BrainEntities."""
        # Sync KnowledgeGraph nodes via existing VRIP adapter
        self._brain.sync_vrip_kg(self._engine.kg)

        # Phase 5: Issues
        for issue in results.get("phase_5_analysis", []):
            entity = self._brain.entity(
                label=issue.get("message", "")[:100],
                entity_type="intelligence_issue",
                description=issue.get("message", ""),
                source_system="vrip_intelligence",
            )
            entity.attributes["severity"] = issue.get("severity", "")
            entity.attributes["kind"] = issue.get("kind", "")
            entity.attributes["location"] = issue.get("location", "")
            self._brain.register(entity)
            self._sync_count += 1

        # Phase 6: Capabilities
        for cap in results.get("phase_6_capabilities", []):
            entity = self._brain.entity(
                label=cap.get("name", ""),
                entity_type="intelligence_capability",
                description=cap.get("description", ""),
                source_system="vrip_intelligence",
            )
            entity.attributes["version"] = cap.get("version", "")
            entity.attributes["dependencies"] = str(cap.get("dependencies", []))
            entity.attributes["consumers"] = str(cap.get("consumers", []))
            entity.attributes["spec_references"] = cap.get("spec_references", 0)
            self._brain.register(entity)
            self._sync_count += 1

        # Phase 8: Gaps
        for gap in results.get("phase_8_gaps", []):
            entity = self._brain.entity(
                label=gap.get("title", "")[:100],
                entity_type="intelligence_gap",
                description=gap.get("description", ""),
                source_system="vrip_intelligence",
            )
            entity.attributes["priority"] = gap.get("priority", "")
            entity.attributes["kind"] = gap.get("kind", "")
            entity.attributes["effort"] = gap.get("effort", "")
            entity.attributes["leverage"] = gap.get("leverage", "")
            entity.attributes["risk"] = gap.get("risk", "")
            self._brain.register(entity)
            self._sync_count += 1

        # Phase 9: Planning initiatives
        for plan in results.get("phase_9_planning", []):
            entity = self._brain.entity(
                label=plan.get("title", "")[:100],
                entity_type="intelligence_initiative",
                description=plan.get("rationale", ""),
                source_system="vrip_intelligence",
            )
            entity.attributes["priority"] = plan.get("priority", "")
            entity.attributes["effort"] = plan.get("effort", "")
            entity.attributes["specs"] = str(plan.get("specs", []))
            entity.attributes["modules"] = str(plan.get("modules", []))
            entity.attributes["risk"] = plan.get("risk", "")
            entity.attributes["maturity_increase"] = plan.get("maturity_increase", "")
            self._brain.register(entity)
            self._sync_count += 1

    def summary(self) -> dict[str, Any]:
        """Return service status summary."""
        kg_summary = self._engine.kg.summary() if hasattr(self._engine, "kg") else {}
        return {
            "brain_connected": self._brain is not None,
            "brain_synced": self._sync_count,
            "has_results": bool(self._engine.last_results),
            "knowledge_graph": kg_summary,
        }

    def report(self) -> str:
        """Generate standardized report text."""
        return self._engine.report()
