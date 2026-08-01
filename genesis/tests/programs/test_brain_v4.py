"""
Tests for GENESIS-IX Phase 2: Engineering Brain V4.
"""

import pytest
from genesis.brain_v4 import (
    EngineeringBrainV4, Goal, GoalLevel, GoalStatus, Plan,
    ExecutivePlanner, StrategicPlanner, TacticalPlanner, TaskPlanner,
    ConstraintSolver, UtilityOptimizer, Belief, BeliefRevision,
    UncertaintyReasoning, ProbabilisticPlanner, CausalLink, CausalInference,
    AnalogicalReasoning, Reflection, ReflectionEngine, AttentionFocus,
    AttentionSystem, ExecutiveMemory, WorldModelSync,
)


class TestGoal:
    def test_create_minimal(self):
        g = Goal()
        assert g.id
        assert g.level == GoalLevel.TASK
        assert g.status == GoalStatus.PROPOSED

    def test_create_with_fields(self):
        g = Goal(name="Reduce latency", level=GoalLevel.EXECUTIVE, priority=0.9)
        assert g.name == "Reduce latency"
        assert g.level == GoalLevel.EXECUTIVE
        assert g.priority == 0.9


class TestPlanners:
    def test_executive_formulate(self):
        brain = EngineeringBrainV4()
        ep = ExecutivePlanner(brain)
        goals = ep.formulate_goals(["High latency detected", "Memory leak"])
        assert len(goals) == 2
        assert all(g.level == GoalLevel.EXECUTIVE for g in goals)

    def test_executive_prioritize(self):
        brain = EngineeringBrainV4()
        ep = ExecutivePlanner(brain)
        goals = [Goal(name="Low", priority=0.3), Goal(name="High", priority=0.9)]
        sorted_goals = ep.prioritize_goals(goals)
        assert sorted_goals[0].name == "High"

    def test_strategic_plan(self):
        g = Goal(name="Test goal", level=GoalLevel.EXECUTIVE)
        sp = StrategicPlanner()
        plan = sp.plan(g)
        assert plan.goal_id == g.id
        assert len(plan.steps) >= 1

    def test_tactical_decompose(self):
        plan = Plan(steps=[{"action": "analyze", "target": "test"},
                           {"action": "build", "target": "test"}])
        tp = TacticalPlanner()
        steps = tp.decompose(plan)
        assert len(steps) >= 2

    def test_task_create(self):
        tp = TaskPlanner()
        steps = [{"action": "execute", "target": "x", "estimated_effort": 1.0}]
        tasks = tp.create_tasks(steps)
        assert len(tasks) == 1
        assert tasks[0]["status"] == "pending"


class TestConstraintSolver:
    def setup_method(self):
        self.cs = ConstraintSolver()

    def test_solve_empty(self):
        assert self.cs.solve() == []

    def test_solve_basic(self):
        self.cs.add_constraint("x", [1, 2, 3])
        solution = self.cs.solve()
        assert solution is not None
        assert solution[0]["x"] == 1

    def test_solve_with_condition(self):
        self.cs.add_constraint("x", [1, 2, 3, 4], condition=lambda v: v > 2)
        solution = self.cs.solve()
        assert solution[0]["x"] == 3


class TestUtilityOptimizer:
    def test_expected_utility(self):
        eu = UtilityOptimizer.expected_utility([(0.5, 100), (0.5, 0)])
        assert eu == 50.0

    def test_max_expected_utility(self):
        options = [
            {"id": "a", "outcomes": [(1.0, 50)]},
            {"id": "b", "outcomes": [(1.0, 100)]},
        ]
        best = UtilityOptimizer.max_expected_utility(options)
        assert best == "b"

    def test_max_no_options(self):
        assert UtilityOptimizer.max_expected_utility([]) is None

    def test_regret(self):
        alts = {"a": [(1.0, 50)], "b": [(1.0, 100)]}
        regret = UtilityOptimizer.regret(alts)
        assert regret["a"] == 50.0
        assert regret["b"] == 0.0


class TestBelief:
    def test_create_minimal(self):
        b = Belief()
        assert b.id
        assert b.confidence == 0.5
        assert b.evidence_ratio == 0.5

    def test_evidence_ratio(self):
        b = Belief(supporting=["e1", "e2"], contradicting=["e3"])
        assert b.evidence_ratio == 2 / 3


class TestBeliefRevision:
    def setup_method(self):
        self.br = BeliefRevision()

    def test_adopt_and_contract(self):
        b = Belief(statement="The sky is blue", confidence=0.9)
        self.br.adopt(b)
        assert self.br.contract(b.id) is True
        assert self.br.contract(b.id) is False

    def test_revise(self):
        b = Belief(statement="test", confidence=0.5)
        self.br.adopt(b)
        self.br.revise(b.id, 0.9)
        assert b.confidence == 0.9

    def test_expand(self):
        new_bs = [Belief(statement="a"), Belief(statement="b")]
        self.br.expand(new_bs)
        assert len(self.br._beliefs) == 2

    def test_add_entailment_and_propagate(self):
        b1 = Belief(statement="a", confidence=0.9)
        b2 = Belief(statement="b", confidence=0.5)
        self.br.adopt(b1)
        self.br.adopt(b2)
        self.br.add_entailment(b1.id, b2.id)
        self.br.propagate(b1.id)
        assert b2.confidence >= 0.5

    def test_contradictions(self):
        self.br.adopt(Belief(statement="same", confidence=0.9))
        self.br.adopt(Belief(statement="same", confidence=0.2))
        contradictions = self.br.contradictions()
        assert len(contradictions) >= 1


class TestUncertaintyReasoning:
    def test_bayesian_update(self):
        posterior = UncertaintyReasoning.bayesian_update(0.5, 0.8, 0.6)
        assert 0 < posterior < 1

    def test_bayesian_update_edge(self):
        posterior = UncertaintyReasoning.bayesian_update(0.5, 0.8, 0.001)
        assert posterior <= 1.0

    def test_dempster_shafer(self):
        bpa = {"a": 0.3, "b": 0.7}
        result = UncertaintyReasoning.dempster_shafer(bpa)
        assert abs(result["a"] - 0.3) < 0.01
        assert abs(result["b"] - 0.7) < 0.01

    def test_kl_divergence(self):
        kl = UncertaintyReasoning.kullback_leibler([0.5, 0.5], [0.5, 0.5])
        assert abs(kl) < 0.001
        kl2 = UncertaintyReasoning.kullback_leibler([0.9, 0.1], [0.5, 0.5])
        assert kl2 > 0


class TestProbabilisticPlanner:
    def setup_method(self):
        self.pp = ProbabilisticPlanner()

    def test_add_outcome_model(self):
        self.pp.add_outcome_model("deploy", [("success", 0.8), ("failure", 0.2)])
        assert "deploy" in self.pp._outcome_models

    def test_expected_value(self):
        self.pp.add_outcome_model("deploy", [("success", 0.8), ("failure", 0.2)])

        def util(state):
            return 100 if state == "success" else -10

        ev = self.pp.expected_value("deploy", util)
        assert abs(ev - 78) < 1


class TestCausalInference:
    def setup_method(self):
        self.ci = CausalInference()

    def test_add_link(self):
        self.ci.add_link(CausalLink(cause="latency", effect="satisfaction", strength=0.8))
        assert len(self.ci._links) == 1

    def test_do_intervention(self):
        self.ci.add_link(CausalLink(cause="latency", effect="satisfaction", strength=0.8))
        effects = self.ci.do_intervention("latency", 0.5)
        assert "satisfaction" in effects
        assert effects["satisfaction"] == 0.5 * 0.8

    def test_counterfactual(self):
        self.ci.add_link(CausalLink(cause="latency", effect="satisfaction", strength=0.8))
        cf = self.ci.counterfactual({"latency": 100, "satisfaction": 50},
                                      {"latency": 50})
        assert cf["latency"] == 50
        assert "satisfaction" in cf

    def test_causal_chain(self):
        self.ci.add_link(CausalLink(cause="a", effect="b", strength=0.5))
        self.ci.add_link(CausalLink(cause="b", effect="c", strength=0.5))
        chains = self.ci.causal_chain("a")
        assert len(chains) >= 1
        assert chains[0] == ["a", "b", "c"]


class TestAnalogicalReasoning:
    def setup_method(self):
        self.ar = AnalogicalReasoning()

    def test_add_case(self):
        self.ar.add_case("case1", {"lang": "python", "type": "web"})
        assert len(self.ar._cases) == 1

    def test_find_analogies(self):
        self.ar.add_case("case1", {"lang": "python", "type": "web"}, outcome="success")
        self.ar.add_case("case2", {"lang": "rust", "type": "cli"}, outcome="success")
        analogies = self.ar.find_analogies({"lang": "python", "type": "web"})
        assert len(analogies) == 2
        assert analogies[0][0]["id"] == "case1"

    def test_transfer_solution(self):
        self.ar.add_case("case1", {"lang": "python"}, outcome="use_fastapi")
        result = self.ar.transfer_solution({"lang": "python"})
        assert result == "use_fastapi"

    def test_transfer_no_match(self):
        assert self.ar.transfer_solution({"lang": "unknown"}) is None


class TestReflectionEngine:
    def setup_method(self):
        self.re = ReflectionEngine()

    def test_analyze_outcome_success(self):
        ref = self.re.analyze_outcome("deploy", 100, 100)
        assert len(ref.findings) == 1
        assert "succeeded" in ref.findings[0]

    def test_analyze_outcome_failure(self):
        ref = self.re.analyze_outcome("deploy", 100, 50)
        assert "deviated" in ref.findings[0]
        assert len(ref.recommendations) > 0

    def test_self_criticize(self):
        actions = [
            {"name": "deploy", "outcome": "failure", "error": "timeout"},
            {"name": "retry", "retries": 5},
        ]
        criticisms = self.re.self_criticize(actions)
        assert len(criticisms) == 2

    def test_generate_recommendations(self):
        self.re.analyze_outcome("test", "expected", "unexpected")
        recs = self.re.generate_recommendations()
        assert len(recs) > 0


class TestAttentionSystem:
    def setup_method(self):
        self.at = AttentionSystem(focus_capacity=3, salience_decay=0.1)

    def test_focus(self):
        f = self.at.focus("goal:1", "goal", "Reduce latency", salience=0.9)
        assert f.target_id == "goal:1"
        assert self.at.primary is not None

    def test_focus_capacity(self):
        for i in range(5):
            self.at.focus(f"t:{i}", "task", f"Task {i}", salience=0.5)
        assert len(self.at._foci) == 3

    def test_primary_returns_highest_salience(self):
        self.at.focus("low", "task", "Low", salience=0.3)
        self.at.focus("high", "task", "High", salience=0.9)
        assert self.at.primary.description == "High"

    def test_tick_removes_low_salience(self):
        self.at.focus("old", "task", "Old", salience=0.05)
        self.at.tick()
        assert len(self.at._foci) == 0

    def test_summary(self):
        self.at.focus("g:1", "goal", "Primary goal", salience=0.9)
        s = self.at.summary()
        assert s["active_foci"] == 1


class TestExecutiveMemory:
    def setup_method(self):
        self.em = ExecutiveMemory(capacity=3)

    def test_remember_and_recall(self):
        self.em.remember("key1", "value1", importance=0.8)
        assert self.em.recall("key1") == "value1"

    def test_recall_nonexistent(self):
        assert self.em.recall("nonexistent") is None

    def test_capacity(self):
        for i in range(5):
            self.em.remember(f"k{i}", f"v{i}", importance=0.5)
        assert len(self.em._entries) == 3

    def test_recent(self):
        self.em.remember("a", 1, importance=0.5)
        self.em.remember("b", 2, importance=0.8)
        recent = self.em.recent(1)
        assert len(recent) == 1


class TestEngineeringBrainV4:
    def setup_method(self):
        self.brain = EngineeringBrainV4()

    def test_create_goal(self):
        g = self.brain.create_goal("Test goal", GoalLevel.EXECUTIVE, priority=0.9)
        assert self.brain.get_goal(g.id) is g
        assert g.level == GoalLevel.EXECUTIVE

    def test_create_goal_with_parent(self):
        parent = self.brain.create_goal("Parent", GoalLevel.EXECUTIVE)
        child = self.brain.create_goal("Child", GoalLevel.STRATEGIC, parent_id=parent.id)
        assert child.parent_id == parent.id
        assert parent.child_ids == [child.id]

    def test_goals_by_level(self):
        self.brain.create_goal("E1", GoalLevel.EXECUTIVE)
        self.brain.create_goal("E2", GoalLevel.EXECUTIVE)
        self.brain.create_goal("S1", GoalLevel.STRATEGIC)
        assert len(self.brain.goals_by_level(GoalLevel.EXECUTIVE)) == 2
        assert len(self.brain.goals_by_level(GoalLevel.STRATEGIC)) == 1

    def test_goal_tree(self):
        p = self.brain.create_goal("Parent", GoalLevel.EXECUTIVE)
        self.brain.create_goal("Child", GoalLevel.STRATEGIC, parent_id=p.id)
        tree = self.brain.goal_tree(p.id)
        assert tree["name"] == "Parent"
        assert len(tree["children"]) == 1

    def test_goal_tree_nonexistent(self):
        assert self.brain.goal_tree("nonexistent") == {}

    def test_update_goal_progress(self):
        g = self.brain.create_goal("Test")
        self.brain.update_goal_progress(g.id, 0.5)
        assert self.brain.get_goal(g.id).progress == 0.5

    def test_update_goal_completion(self):
        g = self.brain.create_goal("Test")
        self.brain.update_goal_progress(g.id, 1.0)
        assert self.brain.get_goal(g.id).status == GoalStatus.ACHIEVED
        assert self.brain.get_goal(g.id).completed_at > 0

    def test_formulate_plan(self):
        g = self.brain.create_goal("Test plan", GoalLevel.STRATEGIC)
        plan = self.brain.formulate_plan(g.id)
        assert plan is not None
        assert len(plan.steps) > 0

    def test_formulate_plan_nonexistent(self):
        assert self.brain.formulate_plan("nonexistent") is None

    def test_reason(self):
        results = self.brain.reason("High latency in production")
        assert len(results) >= 1

    def test_reflect(self):
        actions = [{"name": "deploy", "outcome": "failure", "error": "timeout"}]
        criticisms = self.brain.reflect(actions)
        assert len(criticisms) >= 1

    def test_summary(self):
        self.brain.create_goal("G1", GoalLevel.EXECUTIVE)
        s = self.brain.summary()
        assert s["total_goals"] >= 1
        assert s["hypergraph_nodes"] >= 0
        assert "uptime" in s
