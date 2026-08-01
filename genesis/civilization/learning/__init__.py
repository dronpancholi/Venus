"""
Autonomous Learning System (Program L) — nightly execution cycle.

The civilization runs autonomously on a schedule:
  1. Observe: scan repository registry for new/changed repositories
  2. Research: run research cycles across all agents
  3. Discover: mine patterns, detect anomalies, generate findings
  4. Debate: hold multi-agent debates on open questions
  5. Publish: submit high-confidence findings as papers
  6. Archive: store all results for future reference
  7. Improve: update world model with new observations
  8. Plan: generate next research agenda based on gaps
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LearningCycleResult:
    """Result of a single autonomous learning cycle."""
    cycle_number: int = 0
    repositories_scanned: int = 0
    findings_produced: int = 0
    papers_published: int = 0
    debates_held: int = 0
    experiments_run: int = 0
    world_model_updated: bool = False
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: float = 0.0


@dataclass
class LearningSchedule:
    """Schedule configuration for autonomous learning."""
    interval_hours: float = 24.0
    max_repositories_per_cycle: int = 10
    min_confidence_for_publish: float = 0.7
    run_experiments: bool = True
    run_debates: bool = True
    update_world_model: bool = True
    archive_results: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


class NightlyLearningCycle:
    """
    Autonomous learning system that runs on a schedule.

    Integrates with:
      - Observatory (repository ingestion)
      - Laboratory (genome analysis, experiments)
      - Civilization (research agents, debates, publications)
      - World Model (Bayesian prediction, risk assessment)
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "learning"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.schedule = LearningSchedule()
        self.cycle_results: list[LearningCycleResult] = []
        self._load()

    def run_cycle(self, overseer=None) -> LearningCycleResult:
        """Execute one autonomous learning cycle."""
        start = time.time()
        result = LearningCycleResult(
            cycle_number=len(self.cycle_results) + 1,
            timestamp=start,
        )

        try:
            result.repositories_scanned = self._observe_phase()
        except Exception as e:
            result.errors.append(f"Observe failed: {e}")

        try:
            result.findings_produced = self._research_phase(overseer)
        except Exception as e:
            result.errors.append(f"Research failed: {e}")

        try:
            result.papers_published = self._publish_phase(overseer)
        except Exception as e:
            result.errors.append(f"Publish failed: {e}")

        if self.schedule.run_debates:
            try:
                result.debates_held = self._debate_phase(overseer)
            except Exception as e:
                result.errors.append(f"Debate failed: {e}")

        if self.schedule.run_experiments:
            try:
                result.experiments_run = self._experiment_phase()
            except Exception as e:
                result.errors.append(f"Experiment failed: {e}")

        if self.schedule.update_world_model:
            try:
                self._update_world_model()
                result.world_model_updated = True
            except Exception as e:
                result.errors.append(f"World model update failed: {e}")

        if self.schedule.archive_results:
            self._archive_cycle(result)

        result.duration_seconds = time.time() - start
        self.cycle_results.append(result)
        self._save()

        return result

    def _observe_phase(self) -> int:
        """Scan repositories for new/changed content."""
        count = 0
        try:
            from genesis.observatory.registry import RepositoryRegistry
            reg = RepositoryRegistry()
            repos = [r for r in reg.list_repos() if r.get("status") == "active"]
            for repo in repos[:self.schedule.max_repositories_per_cycle]:
                count += 1
        except ImportError:
            pass
        return count

    def _research_phase(self, overseer) -> int:
        """Run research cycles."""
        if not overseer:
            return 0
        context = {"cycle": len(self.cycle_results) + 1}
        results = overseer.run_research_cycle(context)
        return sum(len(fs) for fs in results.values())

    def _publish_phase(self, overseer) -> int:
        """Publish high-confidence findings."""
        if not overseer:
            return 0
        return overseer.publish_findings(min_confidence=self.schedule.min_confidence_for_publish)

    def _debate_phase(self, overseer) -> int:
        """Hold debates on top open questions."""
        if not overseer:
            return 0
        topics = [
            "What is the highest-impact improvement for this repository?",
            "What architectural patterns are most prevalent?",
            "What are the most critical security risks?",
            "How can test coverage be improved?",
            "What is the economic value of refactoring?",
        ]
        count = 0
        for topic in topics:
            overseer.facilitate_debate(topic)
            count += 1
        return count

    def _experiment_phase(self) -> int:
        """Run experiments on recent hypotheses."""
        count = 0
        try:
            from genesis.laboratory.experiment import ExperimentPlatform
            ep = ExperimentPlatform()
            recent = ep.list_experiments(limit=5)
            for exp in recent:
                result = ep.run_experiment(exp.get("id", ""))
                if result:
                    count += 1
        except ImportError:
            pass
        return count

    def _update_world_model(self):
        """Update the world model with latest observations."""
        try:
            from genesis.civilization.world_model import WorldModel
            from genesis.observatory.registry import RepositoryRegistry
            from genesis.laboratory.genome.builder import GenomeBuilder

            wm = WorldModel()
            reg = RepositoryRegistry()
            repos = [r for r in reg.list_repos() if r.get("status") == "active"]

            builder = GenomeBuilder()
            for repo in repos[:5]:
                try:
                    from genesis.usir.compiler import MultiLanguageCompiler
                    compiler = MultiLanguageCompiler()
                    usir = compiler.compile(repo.get("path", ""))
                    if usir:
                        genome = builder.build(usir)
                        wm.observe_genome(genome)
                except Exception:
                    pass
        except ImportError:
            pass

    def _archive_cycle(self, result: LearningCycleResult):
        """Archive cycle results for historical analysis."""
        path = self.storage_path / f"cycle_{result.cycle_number}.json"
        path.write_text(json.dumps({
            "cycle_number": result.cycle_number,
            "repositories_scanned": result.repositories_scanned,
            "findings_produced": result.findings_produced,
            "papers_published": result.papers_published,
            "debates_held": result.debates_held,
            "experiments_run": result.experiments_run,
            "world_model_updated": result.world_model_updated,
            "errors": result.errors,
            "duration_seconds": result.duration_seconds,
            "timestamp": result.timestamp,
        }, indent=2))

    def summary(self) -> dict[str, Any]:
        return {
            "total_cycles": len(self.cycle_results),
            "schedule": self.schedule.to_dict(),
            "last_cycle": self.cycle_results[-1].__dict__ if self.cycle_results else None,
            "recent_results": [r.__dict__ for r in self.cycle_results[-5:]],
        }

    def _save(self):
        data = {
            "schedule": self.schedule.to_dict(),
            "results": [r.__dict__ for r in self.cycle_results],
        }
        (self.storage_path / "learning_state.json").write_text(json.dumps(data, indent=2))

    def _load(self):
        path = self.storage_path / "learning_state.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if "schedule" in data:
                    self.schedule = LearningSchedule(**data["schedule"])
                if "results" in data:
                    self.cycle_results = [LearningCycleResult(**r) for r in data["results"]]
            except Exception:
                pass
