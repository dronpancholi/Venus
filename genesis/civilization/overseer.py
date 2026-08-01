"""
CivilizationOverseer — orchestrates the multi-agent research civilization.

Manages lifecycle: register agents, execute research cycles, publish findings,
facilitate debates, maintain world model, and trigger autonomous learning.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id
from genesis.civilization.agents.base import ResearchAgent, ResearchFinding


@dataclass
class CivilizationState:
    """Persistent state of the civilization."""
    cycle_count: int = 0
    total_findings: int = 0
    total_publications: int = 0
    total_debates: int = 0
    last_cycle_time: float = 0.0
    created_at: float = 0.0
    metrics: dict[str, float] = field(default_factory=dict)


class CivilizationOverseer:
    """
    Oversees the entire research civilization.

    Responsibilities:
      - Register and manage research agents
      - Execute research cycles across all agents
      - Facilitate multi-agent debates
      - Publish accepted findings
      - Maintain world model
      - Trigger autonomous learning cycles
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "civilization"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.agents: dict[str, ResearchAgent] = {}
        self.state = CivilizationState(created_at=time.time())

        self._load_state()

    # ── Agent Management ──

    def register_agent(self, agent: ResearchAgent):
        """Register a research agent."""
        self.agents[agent.agent_id] = agent
        self._save_state()

    def register_agents(self, *agents: ResearchAgent):
        for a in agents:
            self.register_agent(a)

    def get_agent(self, agent_id: str) -> ResearchAgent | None:
        return self.agents.get(agent_id)

    def list_agents(self) -> dict[str, str]:
        return {aid: a.name for aid, a in self.agents.items()}

    # ── Research Cycle ──

    def run_research_cycle(self, context: dict[str, Any]) -> dict[str, list[ResearchFinding]]:
        """Run one research cycle across all agents."""
        results: dict[str, list[ResearchFinding]] = {}
        total_findings = 0

        for aid, agent in self.agents.items():
            findings = agent.research_cycle(context)
            results[aid] = findings
            total_findings += len(findings)

        self.state.cycle_count += 1
        self.state.total_findings += total_findings
        self.state.last_cycle_time = time.time()
        self._save_state()

        return results

    # ── Debates ──

    def facilitate_debate(self, topic: str, agents: list[str] | None = None) -> dict[str, Any]:
        """Facilitate a multi-agent debate on a topic."""
        participants = agents or list(self.agents.keys())
        from genesis.civilization.research import DebateTranscript, DebateStatement
        transcript = DebateTranscript(
            id=generate_id("debate", 10),
            topic=topic,
            participants=participants,
            timestamp=time.time(),
        )

        for pid in participants:
            agent = self.agents.get(pid)
            if not agent:
                continue
            answers = agent.get_answers_for(topic)
            if answers:
                best = max(answers, key=lambda f: f.confidence)
                transcript.add_statement(
                    agent_id=pid, agent_name=agent.name,
                    statement=f"Based on finding: {best.title} ({best.description[:100]})",
                    position="for" if best.impact >= 0 else "against",
                    evidence=best.evidence[:200],
                )
            else:
                transcript.add_statement(
                    agent_id=pid, agent_name=agent.name,
                    statement=f"No findings yet on '{topic}'. Generating research questions.",
                    position="neutral",
                )

        transcript.consensus = self._compute_consensus(transcript)
        transcript.duration = time.time() - transcript.timestamp
        self.state.total_debates += 1

        # Store in research library if available
        try:
            from genesis.civilization.research import ResearchLibrary
            lib = ResearchLibrary()
            lib.record_debate(transcript)
        except Exception:
            pass

        self._save_state()
        return transcript.to_dict()

    def _compute_consensus(self, transcript) -> float:
        if not transcript.statements:
            return 0.0
        positions = [s.position for s in transcript.statements]
        for_count = positions.count("for")
        against_count = positions.count("against")
        total = len(positions)
        if total == 0:
            return 0.0
        majority = max(for_count, against_count)
        return majority / total

    # ── Publication ──

    def publish_findings(self, min_confidence: float = 0.7) -> int:
        """Publish high-confidence findings as research papers."""
        count = 0
        try:
            from genesis.civilization.research import ResearchPaper, ResearchLibrary
            lib = ResearchLibrary()

            for agent in self.agents.values():
                for finding in agent.memory.findings.values():
                    if finding.confidence >= min_confidence and not finding.peer_reviewed:
                        paper = ResearchPaper(
                            id=generate_id("paper", 12),
                            title=finding.title,
                            authors=[agent.name],
                            abstract=finding.description[:300],
                            body=finding.evidence,
                            domain=agent.research_domain(),
                            findings=[finding.id],
                            confidence=finding.confidence,
                            status="submitted",
                        )
                        lib.submit_paper(paper)
                        finding.peer_reviewed = True
                        agent.memory.publications.append(paper.id)
                        count += 1

            agent._save_memory()  # type: ignore
        except Exception:
            pass

        self.state.total_publications += count
        self._save_state()
        return count

    # ── Summary ──

    def summary(self) -> dict[str, Any]:
        return {
            "cycle_count": self.state.cycle_count,
            "total_findings": self.state.total_findings,
            "total_publications": self.state.total_publications,
            "total_debates": self.state.total_debates,
            "agent_count": len(self.agents),
            "agents": self.list_agents(),
            "last_cycle": self.state.last_cycle_time,
            "uptime_hours": round((time.time() - self.state.created_at) / 3600, 2),
        }

    # ── Persistence ──

    def _state_path(self) -> Path:
        return self.storage_path / "state.json"

    def _save_state(self):
        data = {
            "state": {
                "cycle_count": self.state.cycle_count,
                "total_findings": self.state.total_findings,
                "total_publications": self.state.total_publications,
                "total_debates": self.state.total_debates,
                "last_cycle_time": self.state.last_cycle_time,
                "created_at": self.state.created_at,
            },
            "agents": {aid: a.agent_id for aid, a in self.agents.items()},
        }
        (self._state_path()).write_text(json.dumps(data, indent=2))

    def _load_state(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                s = data.get("state", {})
                self.state.cycle_count = s.get("cycle_count", 0)
                self.state.total_findings = s.get("total_findings", 0)
                self.state.total_publications = s.get("total_publications", 0)
                self.state.total_debates = s.get("total_debates", 0)
                self.state.last_cycle_time = s.get("last_cycle_time", 0)
                self.state.created_at = s.get("created_at", time.time())
            except Exception:
                pass
