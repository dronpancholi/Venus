"""
GENESIS-IX Phase 2: Engineering Brain V4.

The Brain becomes the orchestration layer for the entire platform.
Implements: hierarchical goals, executive/strategic/tactical/task planning,
constraint solving, utility optimization, belief revision, uncertainty reasoning,
probabilistic planning, causal inference, counterfactual reasoning, analogical
reasoning, reflection engine, attention system, executive memory, world model sync.
"""

from __future__ import annotations

import warnings
warnings.warn(
    f"{__name__} is deprecated. Use genesis.brain.EngineeringBrain instead.",
    DeprecationWarning,
    stacklevel=2,
)

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id
from genesis.hypergraph import Hypergraph, HypergraphNode, HypergraphEdge, EdgeType


# ── Goal Hierarchy ──

class GoalLevel(Enum):
    EXECUTIVE = "executive"         # Highest — what to achieve
    STRATEGIC = "strategic"         # How to achieve
    TACTICAL = "tactical"           # Specific actions
    TASK = "task"                   # Executable operations


class GoalStatus(Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    ACHIEVED = "achieved"
    FAILED = "failed"
    SUPERSEDED = "superseded"


@dataclass
class Goal:
    id: str = ""
    name: str = ""
    level: GoalLevel = GoalLevel.TASK
    description: str = ""
    parent_id: str = ""
    child_ids: list[str] = field(default_factory=list)
    status: GoalStatus = GoalStatus.PROPOSED
    priority: float = 0.5
    utility: float = 0.5
    constraints: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    progress: float = 0.0
    expected_value: float = 0.0
    created_at: float = 0.0
    completed_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("goal", 10)
        if not self.created_at:
            self.created_at = time.time()


# ── Planner Layer ──

@dataclass
class Plan:
    id: str = ""
    goal_id: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    estimated_utility: float = 0.0
    estimated_cost: float = 0.0
    risk: float = 0.0
    status: str = "draft"
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("plan", 10)
        if not self.created_at:
            self.created_at = time.time()


class ExecutivePlanner:
    """Highest-level planning: what to achieve."""

    def __init__(self, brain: EngineeringBrainV4):
        self._brain = brain

    def formulate_goals(self, observations: list[str]) -> list[Goal]:
        goals = []
        for obs in observations:
            g = Goal(name=f"Address: {obs[:50]}", level=GoalLevel.EXECUTIVE,
                      priority=0.8, description=obs)
            goals.append(g)
        return goals

    def prioritize_goals(self, goals: list[Goal]) -> list[Goal]:
        return sorted(goals, key=lambda g: (g.priority, g.utility), reverse=True)


class StrategicPlanner:
    """Strategic planning: how to achieve executive goals."""

    def plan(self, goal: Goal) -> Plan:
        return Plan(
            goal_id=goal.id,
            steps=[{"action": "analyze", "target": goal.name},
                   {"action": "decompose", "target": goal.name},
                   {"action": "execute", "target": goal.name}],
            estimated_utility=goal.utility * 0.8,
            risk=0.2,
        )


class TacticalPlanner:
    """Tactical planning: specific actions for strategic objectives."""

    def decompose(self, plan: Plan) -> list[dict[str, Any]]:
        return [
            {"step": f"tactical_{i}", "action": "execute",
             "target": plan.steps[i]["target"] if i < len(plan.steps) else "unknown",
             "estimated_effort": 1.0}
            for i in range(max(1, len(plan.steps) * 2))
        ]


class TaskPlanner:
    """Task-level planning: executable operations."""

    def create_tasks(self, tactical_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tasks = []
        for step in tactical_steps:
            tasks.append({
                "task_id": generate_id("task", 8),
                "action": step["action"],
                "target": step["target"],
                "estimated_effort": step.get("estimated_effort", 1.0),
                "status": "pending",
            })
        return tasks


# ── Constraint Solver ──

class ConstraintSolver:
    """Solves constraint satisfaction problems for planning."""

    def __init__(self):
        self._constraints: list[dict[str, Any]] = []

    def add_constraint(self, var: str, domain: list[Any],
                        condition: Callable[[Any], bool] | None = None):
        self._constraints.append({"var": var, "domain": domain, "condition": condition})

    def solve(self) -> list[dict[str, Any]] | None:
        if not self._constraints:
            return []
        solution: dict[str, Any] = {}
        for c in self._constraints:
            for val in c["domain"]:
                if not c["condition"] or c["condition"](val):
                    solution[c["var"]] = val
                    break
        return [solution] if solution else None


# ── Utility Optimizer ──

class UtilityOptimizer:
    """Optimizes decisions based on expected utility."""

    @staticmethod
    def expected_utility(outcomes: list[tuple[float, float]]) -> float:
        return sum(p * u for p, u in outcomes)

    @staticmethod
    def max_expected_utility(options: list[dict[str, Any]]) -> str | None:
        best_option = None
        best_value = -float('inf')
        for opt in options:
            eu = UtilityOptimizer.expected_utility(opt.get("outcomes", []))
            if eu > best_value:
                best_value = eu
                best_option = opt.get("id")
        return best_option

    @staticmethod
    def regret(alternatives: dict[str, list[tuple[float, float]]]) -> dict[str, float]:
        expected = {name: UtilityOptimizer.expected_utility(outs)
                    for name, outs in alternatives.items()}
        best = max(expected.values())
        return {name: best - ev for name, ev in expected.items()}


# ── Belief Revision ──

@dataclass
class Belief:
    id: str = ""
    statement: str = ""
    confidence: float = 0.5
    source: str = ""
    evidence: list[str] = field(default_factory=list)
    supporting: list[str] = field(default_factory=list)
    contradicting: list[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("blf", 10)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @property
    def evidence_ratio(self) -> float:
        total = len(self.supporting) + len(self.contradicting)
        if total == 0:
            return 0.5
        return len(self.supporting) / total


class BeliefRevision:
    """AGM-style belief revision with contraction and expansion."""

    def __init__(self):
        self._beliefs: dict[str, Belief] = {}
        self._entailment: dict[str, set[str]] = defaultdict(set)

    def adopt(self, belief: Belief):
        self._beliefs[belief.id] = belief

    def contract(self, belief_id: str) -> bool:
        return self._beliefs.pop(belief_id, None) is not None

    def revise(self, belief_id: str, new_confidence: float):
        belief = self._beliefs.get(belief_id)
        if belief:
            belief.confidence = new_confidence
            belief.updated_at = time.time()

    def expand(self, new_beliefs: list[Belief]):
        for b in new_beliefs:
            if b.id not in self._beliefs:
                self._beliefs[b.id] = b

    def add_entailment(self, from_id: str, to_id: str):
        self._entailment[from_id].add(to_id)

    def propagate(self, belief_id: str):
        belief = self._beliefs.get(belief_id)
        if not belief:
            return
        for entailed in self._entailment.get(belief_id, set()):
            target = self._beliefs.get(entailed)
            if target:
                target.confidence = max(target.confidence, belief.confidence * 0.8)
                target.updated_at = time.time()

    def contradictions(self) -> list[tuple[str, str]]:
        result = []
        beliefs_list = list(self._beliefs.values())
        for i in range(len(beliefs_list)):
            for j in range(i + 1, len(beliefs_list)):
                b1, b2 = beliefs_list[i], beliefs_list[j]
                if (b1.statement.lower() == b2.statement.lower()
                        and abs(b1.confidence - b2.confidence) > 0.5):
                    result.append((b1.id, b2.id))
        return result


# ── Uncertainty Reasoning ──

class UncertaintyReasoning:
    """Probabilistic reasoning under uncertainty."""

    @staticmethod
    def bayesian_update(prior: float, likelihood: float, evidence_p: float) -> float:
        posterior = (likelihood * prior) / max(evidence_p, 0.001)
        return min(max(posterior, 0.0), 1.0)

    @staticmethod
    def dempster_shafer(bpa: dict[str, float]) -> dict[str, float]:
        total = sum(bpa.values())
        return {k: v / total for k, v in bpa.items()}

    @staticmethod
    def kullback_leibler(p: list[float], q: list[float]) -> float:
        return sum(pi * math.log2(pi / max(qi, 0.001))
                   for pi, qi in zip(p, q) if pi > 0)


class ProbabilisticPlanner:
    """Plans under uncertainty using probabilistic outcomes."""

    def __init__(self):
        self._outcome_models: dict[str, list[tuple[str, float]]] = {}

    def add_outcome_model(self, action: str, outcomes: list[tuple[str, float]]):
        self._outcome_models[action] = outcomes

    def expected_value(self, action: str, utility_fn: Callable[[str], float]) -> float:
        outcomes = self._outcome_models.get(action, [])
        return sum(p * utility_fn(state) for state, p in outcomes)


# ── Causal Inference ──

@dataclass
class CausalLink:
    id: str = ""
    cause: str = ""
    effect: str = ""
    strength: float = 0.5
    direction: str = "positive"
    mechanism: str = ""
    confidence: float = 0.5
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("csl", 10)
        if not self.created_at:
            self.created_at = time.time()


class CausalInference:
    """Causal reasoning with do-calculus and counterfactuals."""

    def __init__(self):
        self._links: dict[str, CausalLink] = {}
        self._graph = Hypergraph()

    def add_link(self, link: CausalLink):
        self._links[link.id] = link
        self._graph.relate(link.cause, link.effect, "causes",
                            weight=link.strength)

    def do_intervention(self, variable: str, value: float,
                         value_fn: Callable[[str], float] | None = None) -> dict[str, float]:
        effects: dict[str, float] = {}
        for link in self._links.values():
            if link.cause == variable:
                effect_value = value * link.strength if link.direction == "positive" \
                    else value * (1.0 - link.strength)
                effects[link.effect] = effect_value
        return effects

    def counterfactual(self, actual: dict[str, float],
                        intervention: dict[str, float]) -> dict[str, float]:
        cf = dict(actual)
        for var, val in intervention.items():
            cf[var] = val
            effects = self.do_intervention(var, val)
            for effect, e_val in effects.items():
                if effect in cf:
                    cf[effect] = cf[effect] * 0.5 + e_val * 0.5
        return cf

    def causal_chain(self, start: str, max_depth: int = 10) -> list[list[str]]:
        chains: list[list[str]] = []
        queue: list[tuple[str, list[str]]] = [(start, [start])]
        while queue and len(chains) < 10:
            current, path = queue.pop(0)
            if len(path) >= max_depth:
                chains.append(path)
                continue
            has_next = False
            for link in self._links.values():
                if link.cause == current and link.effect not in path:
                    queue.append((link.effect, path + [link.effect]))
                    has_next = True
            if not has_next:
                chains.append(path)
        return chains


# ── Analogical Reasoning ──

class AnalogicalReasoning:
    """Reasoning by analogy between domains."""

    def __init__(self):
        self._cases: list[dict[str, Any]] = []

    def add_case(self, case_id: str, features: dict[str, Any],
                  outcome: Any = None):
        self._cases.append({"id": case_id, "features": features, "outcome": outcome})

    def find_analogies(self, query: dict[str, Any],
                        top_k: int = 5) -> list[tuple[dict[str, Any], float]]:
        scores: list[tuple[dict[str, Any], float]] = []
        for case in self._cases:
            sim = self._feature_similarity(query, case["features"])
            scores.append((case, sim))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]

    def transfer_solution(self, query: dict[str, Any]) -> Any | None:
        analogies = self.find_analogies(query, top_k=1)
        if analogies:
            return analogies[0][0].get("outcome")
        return None

    @staticmethod
    def _feature_similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
        common = set(a.keys()) & set(b.keys())
        if not common:
            return 0.0
        sim = 0.0
        for key in common:
            if a[key] == b[key]:
                sim += 1.0
        return sim / len(common) if common else 0.0


# ── Reflection Engine ──

@dataclass
class Reflection:
    id: str = ""
    topic: str = ""
    analysis: str = ""
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence: float = 0.5
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("rfl", 10)
        if not self.created_at:
            self.created_at = time.time()


class ReflectionEngine:
    """Self-reflection and self-criticism."""

    def __init__(self):
        self._reflections: list[Reflection] = []

    def analyze_outcome(self, action: str, expected: Any, actual: Any) -> Reflection:
        success = expected == actual or actual > expected if isinstance(actual, (int, float)) else False
        findings = []
        if success:
            findings.append(f"Action '{action}' succeeded as expected")
        else:
            findings.append(f"Action '{action}' deviated from expectation")
        recs = []
        if not success:
            recs.append(f"Investigate root cause of deviation in '{action}'")
        ref = Reflection(topic=f"Outcome: {action}", analysis=self._analyze(expected, actual),
                          findings=findings, recommendations=recs)
        self._reflections.append(ref)
        return ref

    def self_criticize(self, recent_actions: list[dict[str, Any]]) -> list[str]:
        criticisms = []
        for act in recent_actions:
            if act.get("outcome") == "failure":
                criticisms.append(f"Action '{act['name']}' failed: {act.get('error', 'unknown')}")
            if act.get("retries", 0) > 2:
                criticisms.append(f"Action '{act['name']}' retried excessively")
        return criticisms

    def generate_recommendations(self) -> list[str]:
        recs = []
        for ref in self._reflections[-10:]:
            recs.extend(ref.recommendations)
        return list(set(recs))

    @staticmethod
    def _analyze(expected: Any, actual: Any) -> str:
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            delta = actual - expected
            return f"Delta: {delta:+.2f} ({delta / max(abs(expected), 0.01) * 100:+.1f}%)"
        return f"Expected: {expected}, Actual: {actual}"


# ── Attention System ──

@dataclass
class AttentionFocus:
    target_id: str = ""
    target_type: str = ""
    description: str = ""
    salience: float = 0.0
    source: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    @property
    def age(self) -> float:
        return time.time() - self.created_at


class AttentionSystem:
    """Multi-source attention with salience decay and priority focus."""

    def __init__(self, focus_capacity: int = 7, salience_decay: float = 0.1):
        self._foci: list[AttentionFocus] = []
        self._focus_capacity = focus_capacity
        self._salience_decay = salience_decay

    def focus(self, target_id: str, target_type: str, description: str,
               salience: float = 0.5, source: str = "internal") -> AttentionFocus:
        f = AttentionFocus(target_id=target_id, target_type=target_type,
                            description=description, salience=salience, source=source)
        self._foci.append(f)
        self._foci.sort(key=lambda x: x.salience, reverse=True)
        if len(self._foci) > self._focus_capacity:
            self._foci = self._foci[:self._focus_capacity]
        return f

    @property
    def primary(self) -> AttentionFocus | None:
        if not self._foci:
            return None
        return max(self._foci, key=lambda f: f.salience * (1.0 - self._salience_decay * f.age / 10))

    def tick(self):
        self._foci = [f for f in self._foci
                      if f.salience * (1.0 - self._salience_decay * f.age / 10) > 0.1]

    def summary(self) -> dict[str, Any]:
        return {"active_foci": len(self._foci),
                "primary": self.primary.description if self.primary else None}


# ── Executive Memory ──

class ExecutiveMemory:
    """Short-term memory for the executive function."""

    def __init__(self, capacity: int = 20):
        self._entries: list[dict[str, Any]] = []
        self._capacity = capacity

    def remember(self, key: str, value: Any, importance: float = 0.5):
        self._entries.append({"key": key, "value": value, "importance": importance,
                               "timestamp": time.time()})
        self._entries.sort(key=lambda e: e["importance"], reverse=True)
        if len(self._entries) > self._capacity:
            self._entries = self._entries[:self._capacity]

    def recall(self, key: str) -> Any | None:
        for e in reversed(self._entries):
            if e["key"] == key:
                return e["value"]
        return None

    def recent(self, n: int = 5) -> list[dict[str, Any]]:
        return sorted(self._entries, key=lambda e: e["timestamp"], reverse=True)[:n]


# ── World Model Sync ──

class WorldModelSync:
    """Synchronizes the Brain's world model with external systems."""

    def __init__(self, brain: EngineeringBrainV4):
        self._brain = brain
        self._last_sync: dict[str, float] = {}

    def sync_hypergraph(self, hypergraph: Hypergraph) -> int:
        count = 0
        for node in hypergraph._nodes.values():
            hn = HypergraphNode(id=node.id, label=node.label, node_type=node.node_type,
                                 properties=dict(node.properties), tags=list(node.tags))
            self._brain.hypergraph.add_node(hn)
            count += 1
        for edge in hypergraph._edges.values():
            self._brain.hypergraph.relate(
                edge.source_id, edge.target_id, edge.relation,
                weight=edge.weight, edge_type=edge.edge_type,
            )
            count += 1
        self._last_sync["hypergraph"] = time.time()
        return count

    def last_sync_time(self, source: str) -> float:
        return self._last_sync.get(source, 0.0)


# ── EngineeringBrainV4 ──

class EngineeringBrainV4:
    """Brain V4 — Central orchestration layer for the entire platform."""

    def __init__(self):
        # Hypergraph
        self.hypergraph = Hypergraph()

        # Goal hierarchy
        self._goals: dict[str, Goal] = {}
        self._goal_hierarchy: dict[str, list[str]] = defaultdict(list)

        # Planners
        self.executive = ExecutivePlanner(self)
        self.strategic = StrategicPlanner()
        self.tactical = TacticalPlanner()
        self.task = TaskPlanner()

        # Constraint solver
        self.constraints = ConstraintSolver()

        # Utility optimizer
        self.utility = UtilityOptimizer()

        # Belief revision
        self.beliefs = BeliefRevision()

        # Uncertainty reasoning
        self.uncertainty = UncertaintyReasoning()
        self.probabilistic = ProbabilisticPlanner()

        # Causal inference
        self.causal = CausalInference()

        # Analogical reasoning
        self.analogies = AnalogicalReasoning()

        # Reflection
        self.reflection = ReflectionEngine()

        # Attention
        self.attention = AttentionSystem()

        # Executive memory
        self.executive_memory = ExecutiveMemory()

        # World model sync
        self.world_sync = WorldModelSync(self)

        self._started_at = time.time()

    # ── Goal Management ──

    def create_goal(self, name: str, level: GoalLevel = GoalLevel.TASK,
                     parent_id: str = "", priority: float = 0.5) -> Goal:
        g = Goal(name=name, level=level, parent_id=parent_id, priority=priority)
        self._goals[g.id] = g
        if parent_id:
            parent = self._goals.get(parent_id)
            if parent:
                parent.child_ids.append(g.id)
            self._goal_hierarchy[parent_id].append(g.id)
        return g

    def get_goal(self, goal_id: str) -> Goal | None:
        return self._goals.get(goal_id)

    def goals_by_level(self, level: GoalLevel) -> list[Goal]:
        return [g for g in self._goals.values() if g.level == level]

    def goal_tree(self, root_id: str) -> dict[str, Any]:
        root = self._goals.get(root_id)
        if not root:
            return {}
        return {
            "id": root.id, "name": root.name, "level": root.level.value,
            "status": root.status.value, "progress": root.progress,
            "children": [self.goal_tree(cid) for cid in root.child_ids],
        }

    def update_goal_progress(self, goal_id: str, progress: float):
        g = self._goals.get(goal_id)
        if g:
            g.progress = min(1.0, max(0.0, progress))
            if progress >= 1.0:
                g.status = GoalStatus.ACHIEVED
                g.completed_at = time.time()

    # ── Planning ──

    def formulate_plan(self, goal_id: str) -> Plan | None:
        goal = self._goals.get(goal_id)
        if not goal:
            return None
        plan = self.strategic.plan(goal)
        tactical_steps = self.tactical.decompose(plan)
        tasks = self.task.create_tasks(tactical_steps)
        plan.steps = tasks
        return plan

    # ── Reasoning ──

    def reason(self, observation: str) -> list[dict[str, Any]]:
        results = []
        hyps = self.executive.formulate_goals([observation])
        for hyp in hyps:
            analogies = self.analogies.find_analogies({"description": hyp.name})
            results.append({
                "goal": hyp.name,
                "analogies": len(analogies),
                "best_analogy": analogies[0][0].get("id") if analogies else None,
            })
        return results

    def reflect(self, actions: list[dict[str, Any]]) -> list[str]:
        criticisms = self.reflection.self_criticize(actions)
        return criticisms

    # ── Summary ──

    def summary(self) -> dict[str, Any]:
        goal_counts = {level.value: len(self.goals_by_level(level)) for level in GoalLevel}
        return {
            "goals": goal_counts,
            "total_goals": len(self._goals),
            "beliefs": len(self.beliefs._beliefs),
            "causal_links": len(self.causal._links),
            "analogies": len(self.analogies._cases),
            "attention_foci": len(self.attention._foci),
            "reflections": len(self.reflection._reflections),
            "hypergraph_nodes": self.hypergraph.node_count,
            "hypergraph_edges": self.hypergraph.edge_count,
            "uptime": time.time() - self._started_at,
        }
