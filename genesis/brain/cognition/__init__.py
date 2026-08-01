"""
Cognitive Architecture — unified cognitive system for the Engineering Brain.

Combines belief systems, goal hierarchy, reasoning, working/episodic memory,
attention, reflection, strategy, decision-making, and multi-agent orchestration
into a single cognitive architecture.

Usage:
    from genesis.brain.cognition import CognitiveArchitecture
    
    arch = CognitiveArchitecture()
    arch.beliefs.believe("The system is stable", confidence=0.8)
    arch.goals.create_goal("Refactor module X", priority=GoalPriority.HIGH)
    arch.reasoning.add_causal_link("entity:1", "entity:2", strength=0.9)
    arch.memory_working.store("Processing task Y", content_type="observation")
    arch.attention.bottom_up("entity", "entity:1", "Critical entity", salience=0.9)
"""

from genesis.brain.cognition.belief import BeliefSystem, Belief, BeliefEvidence, BeliefStatus, EvidenceKind
from genesis.brain.cognition.goals import GoalHierarchy, Goal, GoalStatus, GoalPriority
from genesis.brain.cognition.reasoning import ReasoningEngine, CausalLink, Inference, ReasoningMode
from genesis.brain.cognition.memory import WorkingMemory, EpisodicMemory, WorkingMemorySlot, EpisodicMemoryEntry
from genesis.brain.cognition.attention import AttentionMechanism, AttentionFocus
from genesis.brain.cognition.reflection import ReflectionEngine, Reflection
from genesis.brain.cognition.strategy import StrategyEngine, Tool, Strategy
from genesis.brain.cognition.decision import DecisionEngine, Alternative, Decision, Criterion, DecisionMode
from genesis.brain.cognition.orchestration import Orchestrator, CognitiveAgent, AgentTask, AgentStatus, TaskStatus

__all__ = [
    "CognitiveArchitecture",
    "BeliefSystem", "Belief", "BeliefEvidence", "BeliefStatus", "EvidenceKind",
    "GoalHierarchy", "Goal", "GoalStatus", "GoalPriority",
    "ReasoningEngine", "CausalLink", "Inference", "ReasoningMode",
    "WorkingMemory", "EpisodicMemory", "WorkingMemorySlot", "EpisodicMemoryEntry",
    "AttentionMechanism", "AttentionFocus",
    "ReflectionEngine", "Reflection",
    "StrategyEngine", "Tool", "Strategy",
    "DecisionEngine", "Alternative", "Decision", "Criterion", "DecisionMode",
    "Orchestrator", "CognitiveAgent", "AgentTask", "AgentStatus", "TaskStatus",
]


class CognitiveArchitecture:
    """Unified cognitive architecture for the Engineering Brain.

    Integrates all cognitive subsystems:
    - Belief system for knowledge representation with uncertainty
    - Goal hierarchy for intentional behavior
    - Reasoning engine for causal/counterfactual/Bayesian inference
    - Working memory for active information
    - Episodic memory for experience tracking
    - Attention mechanism for focus management
    - Reflection engine for self-improvement
    - Strategy engine for tool selection and planning
    - Decision engine for multi-criteria decisions
    - Orchestrator for multi-agent coordination
    """

    def __init__(self):
        self._beliefs = BeliefSystem()
        self._goals = GoalHierarchy()
        self._reasoning = ReasoningEngine()
        self._memory_working = WorkingMemory()
        self._memory_episodic = EpisodicMemory()
        self._attention = AttentionMechanism()
        self._reflection = ReflectionEngine()
        self._strategy = StrategyEngine()
        self._decision = DecisionEngine()
        self._orchestrator = Orchestrator()
        self._started_at = __import__('time').time()

    @property
    def beliefs(self) -> BeliefSystem:
        return self._beliefs

    @property
    def goals(self) -> GoalHierarchy:
        return self._goals

    @property
    def reasoning(self) -> ReasoningEngine:
        return self._reasoning

    @property
    def memory_working(self) -> WorkingMemory:
        return self._memory_working

    @property
    def memory_episodic(self) -> EpisodicMemory:
        return self._memory_episodic

    @property
    def attention(self) -> AttentionMechanism:
        return self._attention

    @property
    def reflection(self) -> ReflectionEngine:
        return self._reflection

    @property
    def strategy(self) -> StrategyEngine:
        return self._strategy

    @property
    def decision(self) -> DecisionEngine:
        return self._decision

    @property
    def orchestrator(self) -> Orchestrator:
        return self._orchestrator

    # ——— Integrated Operations ———

    def observe(self, description: str, entities: list[str] | None = None,
                importance: float = 0.5, tags: list[str] | None = None):
        """Record an observation in episodic memory and working memory."""
        self._memory_episodic.record(
            event_type="observation",
            description=description,
            entities=entities,
            importance=importance,
            tags=tags,
        )
        self._memory_working.store(
            content=description,
            content_type="observation",
            salience=importance,
        )

    def think(self, description: str, beliefs_before: dict[str, float] | None = None,
              beliefs_after: dict[str, float] | None = None):
        """Record a cognitive event (inference, decision) in episodic memory."""
        self._memory_episodic.record(
            event_type="inference",
            description=description,
            beliefs_before=beliefs_before or {},
            beliefs_after=beliefs_after or {},
            importance=0.7,
        )

    def reflect(self) -> list[Reflection]:
        """Run reflection over recent episodic memory."""
        recent = self._memory_episodic.recent(50)
        return self._reflection.analyze_decisions(recent)

    def decide(self, alternatives: list[Alternative],
               criteria: list[str] | None = None) -> Decision:
        """Run decision and record the outcome."""
        decision = self._decision.evaluate(alternatives, criteria)
        self._memory_episodic.record(
            event_type="decision",
            description=f"Decision: {decision.context} → {decision.selected_id}",
            entities=[decision.selected_id],
            outcome="pending",
            importance=0.8,
        )
        return decision

    def tick(self):
        """Run one cognitive cycle: decay attention and working memory salience."""
        self._attention.decay()
        self._memory_working.decay_all(rate=0.05)

    def summary(self) -> dict[str, Any]:
        return {
            "beliefs": self._beliefs.summary(),
            "goals": self._goals.summary(),
            "reasoning": self._reasoning.summary(),
            "working_memory": self._memory_working.summary(),
            "episodic_memory": self._memory_episodic.summary(),
            "attention": self._attention.summary(),
            "reflection": self._reflection.summary(),
            "strategy": self._strategy.summary(),
            "decision": self._decision.summary(),
            "orchestrator": self._orchestrator.summary(),
        }
