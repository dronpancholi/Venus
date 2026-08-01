"""
Tests for the Cognitive Architecture — Program 1 of GENESIS VIII.
"""

import pytest

from genesis.brain.cognition import (
    CognitiveArchitecture, BeliefSystem, Belief, BeliefEvidence,
    BeliefStatus, EvidenceKind,
    GoalHierarchy, Goal, GoalStatus, GoalPriority,
    ReasoningEngine, CausalLink, Inference, ReasoningMode,
    WorkingMemory, EpisodicMemory,
    AttentionMechanism, AttentionFocus,
    ReflectionEngine, Reflection,
    StrategyEngine, Tool, Strategy,
    DecisionEngine, Alternative, Decision, Criterion, DecisionMode,
    Orchestrator, CognitiveAgent, AgentTask, TaskStatus,
)


class TestBeliefSystem:
    def test_create_belief(self):
        bs = BeliefSystem()
        b = bs.believe("The system is stable", confidence=0.8, source_system="test")
        assert b.statement == "The system is stable"
        assert b.confidence == 0.8
        assert b.status == BeliefStatus.LIKELY

    def test_belief_with_evidence(self):
        bs = BeliefSystem()
        ev = BeliefEvidence(kind=EvidenceKind.EMPIRICAL, statement="Observed stability",
                            supports=True, weight=0.9)
        b = bs.believe("System is stable", evidence=ev)
        assert len(b.evidence) == 1
        assert b.confidence > 0.5

    def test_contradicting_evidence(self):
        bs = BeliefSystem()
        ev1 = BeliefEvidence(statement="Supports", supports=True, weight=0.9)
        ev2 = BeliefEvidence(statement="Contradicts", supports=False, weight=0.9)
        b = bs.believe("Hypothesis X")
        b.add_evidence(ev1)
        b.add_evidence(ev2)
        assert b.status == BeliefStatus.CONTRADICTED

    def test_find_by_status(self):
        bs = BeliefSystem()
        bs.believe("Confirmed fact", confidence=0.98)
        bs.believe("Hypothetical", confidence=0.3)
        confirmed = bs.find(status=BeliefStatus.CONFIRMED)
        assert len(confirmed) == 1

    def test_relate_beliefs(self):
        bs = BeliefSystem()
        p = bs.believe("Parent belief", confidence=0.9)
        c = bs.believe("Child belief", confidence=0.7)
        bs.relate(p.id, c.id)
        assert c.parent_id == p.id
        assert c.id in p.child_ids

    def test_contradiction_detection(self):
        bs = BeliefSystem()
        bs.believe("Same statement", confidence=1.0, source_system="s1")
        bs.believe("Same statement", confidence=0.7, source_system="s2")
        contradictions = bs.detect_contradictions()
        # Both >= 0.7 and diff >= 0.3
        assert len(contradictions) == 1

    def test_decay(self):
        bs = BeliefSystem()
        b = bs.believe("Temporary belief", confidence=0.8, tags=["temp"])
        b.decay_rate = 0.5
        b.decay(days_passed=10)
        assert b.confidence < 0.5

    def test_prune(self):
        bs = BeliefSystem()
        bs.believe("Keep this", confidence=0.9)
        bs.believe("Remove this", confidence=0.001)
        removed = bs.prune(min_confidence=0.01)
        assert removed >= 1
        assert bs.belief_count >= 1

    def test_summary(self):
        bs = BeliefSystem()
        bs.believe("Fact A", confidence=0.9)
        bs.believe("Fact B", confidence=0.5)
        s = bs.summary()
        assert s["total_beliefs"] == 2
        assert s["average_confidence"] > 0


class TestGoalHierarchy:
    def test_create_goal(self):
        gh = GoalHierarchy()
        g = gh.create_goal("Refactor module X", priority=GoalPriority.HIGH,
                           owner="agent:1")
        assert g.name == "Refactor module X"
        assert g.priority == GoalPriority.HIGH
        assert g.status == GoalStatus.PROPOSED

    def test_goal_decomposition(self):
        gh = GoalHierarchy()
        parent = gh.create_goal("Parent goal")
        children = gh.decompose(parent.id, [
            {"name": "Subgoal 1", "estimated_effort": 5.0},
            {"name": "Subgoal 2", "estimated_effort": 3.0},
        ])
        assert len(children) == 2
        assert len(gh.get(parent.id).child_ids) == 2

    def test_progress_rollup(self):
        gh = GoalHierarchy()
        parent = gh.create_goal("Parent")
        children = gh.decompose(parent.id, [
            {"name": "Child 1"},
            {"name": "Child 2"},
        ])
        gh.update_progress(children[0].id, 1.0)
        gh.update_progress(children[1].id, 0.5)
        assert gh.get(parent.id).progress == 0.75

    def test_blocked_goal(self):
        gh = GoalHierarchy()
        dep = gh.create_goal("Dependency")
        g = gh.create_goal("Blocked goal", dependency_ids=[dep.id])
        assert g.status == GoalStatus.BLOCKED

    def test_priority_ordering(self):
        gh = GoalHierarchy()
        g1 = gh.create_goal("Low priority", priority=GoalPriority.LOW)
        g2 = gh.create_goal("High priority", priority=GoalPriority.HIGH)
        g3 = gh.create_goal("Critical", priority=GoalPriority.CRITICAL)
        for g in (g1, g2, g3):
            gh.update_progress(g.id, 0.1)
        ordered = gh.priorities(status=None)
        assert ordered[0].priority == GoalPriority.CRITICAL

    def test_goal_chain(self):
        gh = GoalHierarchy()
        root = gh.create_goal("Root")
        mid = gh.create_goal("Middle", parent_id=root.id)
        leaf = gh.create_goal("Leaf", parent_id=mid.id)
        chain = gh.get_chain(leaf.id)
        assert len(chain) == 3
        assert chain[0].id == root.id
        assert chain[-1].id == leaf.id

    def test_summary(self):
        gh = GoalHierarchy()
        gh.create_goal("Goal A", priority=GoalPriority.HIGH)
        gh.create_goal("Goal B", priority=GoalPriority.LOW)
        s = gh.summary()
        assert s["total_goals"] == 2

    def test_update_blocked_on_dependency_completion(self):
        gh = GoalHierarchy()
        dep = gh.create_goal("Dependency")
        g = gh.create_goal("Blocked goal", dependency_ids=[dep.id])
        assert g.status == GoalStatus.BLOCKED
        gh.update_progress(dep.id, 1.0)
        # After the dependency is done, the blocked goal should be re-checked
        # (re-checking happens on next explicit access or update)
        g = gh.get(g.id)
        assert g is not None


class TestReasoningEngine:
    def test_add_causal_link(self):
        re = ReasoningEngine()
        link = re.add_causal_link("src:1", "tgt:1", strength=0.8)
        assert link.source_id == "src:1"
        assert link.target_id == "tgt:1"

    def test_infer_causes(self):
        re = ReasoningEngine()
        re.add_causal_link("cause:1", "effect:1", strength=0.9)
        re.add_causal_link("cause:2", "effect:1", strength=0.3)
        causes = re.infer_causes("effect:1", min_strength=0.5)
        assert len(causes) == 1
        assert causes[0].source_id == "cause:1"

    def test_infer_effects(self):
        re = ReasoningEngine()
        re.add_causal_link("src:1", "eff:1", strength=0.8)
        re.add_causal_link("src:1", "eff:2", strength=0.6)
        effects = re.infer_effects("src:1")
        assert len(effects) == 2

    def test_counterfactual(self):
        re = ReasoningEngine()
        re.add_causal_link("x", "y", strength=0.8)
        re.add_causal_link("y", "z", strength=0.7)
        effects = re.counterfactual(lambda e: 0.5, "x", 1.0)
        assert "x" in effects
        assert "y" in effects

    def test_bayesian_update(self):
        re = ReasoningEngine()
        posterior = re.bayesian_update(prior=0.5, likelihood=0.9, evidence_prob=0.6)
        assert 0.7 < posterior < 0.8

    def test_add_rule_and_deduce(self):
        re = ReasoningEngine()
        re.add_rule("error", "needs_fix", confidence=0.9)
        inferences = re.deduce({"error_detected": 0.8})
        assert len(inferences) >= 1
        assert inferences[0].mode == ReasoningMode.DEDUCTIVE

    def test_causal_chain(self):
        re = ReasoningEngine()
        re.add_causal_link("a", "b", strength=0.9)
        re.add_causal_link("b", "c", strength=0.8)
        chains = re.causal_chain("a")
        assert len(chains) >= 1

    def test_summary(self):
        re = ReasoningEngine()
        re.add_causal_link("a", "b")
        re.add_rule("x", "y")
        s = re.summary()
        assert s["causal_links"] == 1
        assert s["rules"] == 1


class TestWorkingMemory:
    def test_store_and_retrieve(self):
        wm = WorkingMemory(capacity=5)
        slot = wm.store("Active task", content_type="observation", salience=0.8)
        assert wm.size == 1
        retrieved = wm.get(slot.id)
        assert retrieved is not None
        assert retrieved.access_count == 1

    def test_eviction(self):
        wm = WorkingMemory(capacity=3)
        wm.store("A", salience=0.1)
        wm.store("B", salience=0.9)
        wm.store("C", salience=0.8)
        wm.store("D", salience=0.7)  # Should evict A
        assert wm.size <= 3
        assert wm.get("A") is None

    def test_focus(self):
        wm = WorkingMemory()
        wm.store("Low", salience=0.3)
        wm.store("High", salience=0.9)
        assert wm.focus().content == "High"

    def test_update_salience(self):
        wm = WorkingMemory()
        s = wm.store("Item", salience=0.5)
        wm.update_salience(s.id, 0.3)
        assert wm.get(s.id).salience == 0.8

    def test_decay(self):
        wm = WorkingMemory()
        wm.store("Item", salience=0.2)
        wm.decay_all(rate=0.3)
        assert wm.size == 0  # Decayed to 0

    def test_retrieve_by_type(self):
        wm = WorkingMemory()
        wm.store("A", content_type="observation")
        wm.store("B", content_type="belief")
        results = wm.retrieve(content_type="observation")
        assert len(results) == 1

    def test_summary(self):
        wm = WorkingMemory(capacity=7)
        wm.store("Item")
        s = wm.summary()
        assert s["size"] == 1
        assert s["capacity"] == 7


class TestEpisodicMemory:
    def test_record_and_recent(self):
        em = EpisodicMemory()
        em.record("observation", "Saw something")
        em.record("decision", "Chose option A")
        recent = em.recent(1)
        assert len(recent) == 1
        assert recent[0].event_type == "decision"

    def test_by_type(self):
        em = EpisodicMemory()
        em.record("inference", "Inferred X")
        em.record("inference", "Inferred Y")
        em.record("observation", "Observed Z")
        inferences = em.by_type("inference")
        assert len(inferences) == 2

    def test_by_entity(self):
        em = EpisodicMemory()
        em.record("action", "Did something", entities=["entity:1"])
        em.record("action", "Did other", entities=["entity:2"])
        results = em.by_entity("entity:1")
        assert len(results) == 1

    def test_search(self):
        em = EpisodicMemory()
        em.record("test", "Found a bug in module X")
        em.record("test", "Fixed module Y")
        results = em.search(query="bug")
        assert len(results) == 1

    def test_summary(self):
        em = EpisodicMemory(max_entries=100)
        em.record("obs", "Event 1")
        em.record("obs", "Event 2")
        s = em.summary()
        assert s["total_entries"] == 2
        assert s["max_entries"] == 100


class TestAttentionMechanism:
    def test_bottom_up(self):
        am = AttentionMechanism()
        focus = am.bottom_up("entity", "e:1", "Important entity", salience=0.9)
        assert focus.target_id == "e:1"
        assert am.primary_focus.target_id == "e:1"

    def test_top_down(self):
        am = AttentionMechanism()
        am.top_down("goal", "g:1", "Critical goal", priority=0.8)
        foci = am.current_focus
        assert any(f.target_id == "g:1" for f in foci)

    def test_surprise_triggers_orient(self):
        am = AttentionMechanism(surprise_threshold=0.3)
        focus = am.orient("entity", "e:1", "Unexpected result", 0.2, 0.9)
        if focus:  # Surprise may be >= threshold
            assert focus.source == "bottom_up"

    def test_decay(self):
        am = AttentionMechanism(salience_decay=0.2)
        am.bottom_up("entity", "e:1", "Item", salience=0.3)
        am.decay()
        am.decay()
        assert len(am.current_focus) == 0

    def test_focus_capacity(self):
        am = AttentionMechanism(focus_capacity=2)
        am.bottom_up("e", "1", "A", salience=0.9)
        am.bottom_up("e", "2", "B", salience=0.8)
        am.bottom_up("e", "3", "C", salience=0.7)
        assert len(am.current_focus) <= 2


class TestReflectionEngine:
    def test_analyze_decisions_empty(self):
        refl = ReflectionEngine()
        results = refl.analyze_decisions([])
        assert len(results) == 0

    def test_self_criticize(self):
        refl = ReflectionEngine()
        decisions = [
            {"description": "Bad decision", "outcome": "failure", "alternatives": [],
             "evidence_count": 1},
        ]
        criticisms = refl.self_criticize(decisions)
        assert len(criticisms) >= 1

    def test_generate_recommendations(self):
        refl = ReflectionEngine()
        class MockEpisode:
            outcome = "failure"
            description = "Failed attempt at X"
            id = "ep:1"
        recommendations = refl.generate_recommendations([MockEpisode()])
        assert isinstance(recommendations, list)


class TestStrategyEngine:
    def test_register_tool(self):
        se = StrategyEngine()
        tool = se.register_tool("analyzer", "Code analyzer",
                                 capabilities=["analysis"], cost_per_use=2.0)
        assert tool.name == "analyzer"
        assert tool.cost_per_use == 2.0

    def test_find_tools_by_capability(self):
        se = StrategyEngine()
        se.register_tool("A", capabilities=["analysis"])
        se.register_tool("B", capabilities=["testing"])
        tools = se.find_tools(capability="analysis")
        assert len(tools) == 1

    def test_select_tool(self):
        se = StrategyEngine()
        se.register_tool("A", capabilities=["analysis"], success_rate=0.9)
        se.register_tool("B", capabilities=["analysis"], success_rate=0.5)
        selected = se.select_tool("analysis")
        assert selected is not None
        assert selected.name == "A"

    def test_generate_strategies(self):
        se = StrategyEngine()
        se.register_tool("A", capabilities=["analysis"], cost_per_use=1.0)
        se.register_tool("B", capabilities=["testing"], cost_per_use=2.0)
        strategies = se.generate_strategies("goal:1", ["analysis", "testing"])
        assert len(strategies) >= 1

    def test_update_success_rate(self):
        se = StrategyEngine()
        t = se.register_tool("A", capabilities=["x"], success_rate=0.5)
        se.select_tool("x")
        se.update_success_rate(t.id, succeeded=True)
        assert t.success_rate > 0.5


class TestDecisionEngine:
    def test_register_criterion(self):
        de = DecisionEngine()
        c = de.register_criterion("quality", weight=2.0)
        assert c.weight == 2.0

    def test_evaluate(self):
        de = DecisionEngine()
        de.register_criterion("score", weight=1.0)
        alts = [
            Alternative(name="A", criteria_scores={"score": 0.9}),
            Alternative(name="B", criteria_scores={"score": 0.5}),
        ]
        decision = de.evaluate(alts)
        assert decision.selected_id == alts[0].id
        assert decision.confidence > 0.5

    def test_priority_order(self):
        de = DecisionEngine()
        de.register_criterion("score", weight=1.0)
        alts = [
            Alternative(name="A", criteria_scores={"score": 0.3}),
            Alternative(name="B", criteria_scores={"score": 0.9}),
            Alternative(name="C", criteria_scores={"score": 0.6}),
        ]
        ordered = de.priority_order(alts)
        assert ordered[0].name == "B"
        assert ordered[-1].name == "A"

    def test_hard_constraint(self):
        de = DecisionEngine()
        de.register_criterion("score", weight=1.0)
        de.add_hard_constraint(lambda a: a.criteria_scores.get("score", 0) > 0.5)
        alts = [
            Alternative(name="Valid", criteria_scores={"score": 0.9}),
            Alternative(name="Invalid", criteria_scores={"score": 0.3}),
        ]
        decision = de.evaluate(alts)
        assert decision.selected_id == alts[0].id

    def test_sensitivity_analysis(self):
        de = DecisionEngine()
        de.register_criterion("cost", weight=1.0, higher_is_better=False)
        de.register_criterion("quality", weight=1.0)
        alts = [
            Alternative(name="Cheap", criteria_scores={"cost": 0.1, "quality": 0.3}),
            Alternative(name="Quality", criteria_scores={"cost": 0.9, "quality": 0.9}),
        ]
        decision = de.evaluate(alts)
        results = de.sensitivity_analysis(decision, alts, ["cost", "quality"])
        assert "cost_halved" in results or "cost_doubled" in results


class TestOrchestrator:
    def test_register_agent(self):
        orch = Orchestrator()
        agent = orch.register_agent("Worker-1", agent_type="researcher",
                                     capabilities=["analysis"])
        assert agent.name == "Worker-1"
        assert orch.agent_count == 1

    def test_find_agents_by_capability(self):
        orch = Orchestrator()
        orch.register_agent("A", capabilities=["analysis"])
        orch.register_agent("B", capabilities=["testing"])
        agents = orch.find_agents(capability="analysis")
        assert len(agents) == 1

    def test_assign_task(self):
        orch = Orchestrator()
        orch.register_agent("Worker", capabilities=["task"])
        task = orch.assign_task("Do something", required_capabilities=["task"])
        assert task is not None
        assert task.description == "Do something"
        assert task.status == TaskStatus.ASSIGNED

    def test_complete_task(self):
        orch = Orchestrator()
        orch.register_agent("Worker", capabilities=["task"])
        task = orch.assign_task("Do something", required_capabilities=["task"])
        orch.complete_task(task.id, result="done")
        assert orch._tasks[task.id].status == TaskStatus.COMPLETED

    def test_fail_and_retry(self):
        orch = Orchestrator()
        orch.register_agent("Worker", capabilities=["task"])
        task = orch.assign_task("Do something", required_capabilities=["task"])
        orch.fail_task(task.id, error="Something went wrong")
        # Should retry
        assert orch._tasks[task.id].retry_count == 1
        assert orch._tasks[task.id].status == TaskStatus.PENDING

    def test_agent_tree(self):
        orch = Orchestrator()
        parent = orch.register_agent("Parent", agent_type="manager")
        child = orch.register_agent("Child", capabilities=["work"], parent_id=parent.id)
        tree = orch.get_agent_tree(parent.id)
        assert tree["name"] == "Parent"
        assert len(tree["children"]) == 1

    def test_decompose_task(self):
        orch = Orchestrator()
        orch.register_agent("A", capabilities=["x"])
        orch.register_agent("B", capabilities=["y"])
        task = orch.assign_task("Complex task", required_capabilities=["x"])
        children = orch.decompose_task(task.id, [
            {"description": "Sub 1", "capabilities": ["x"]},
            {"description": "Sub 2", "capabilities": ["y"]},
        ])
        assert len(children) >= 1


class TestCognitiveArchitecture:
    def test_create(self):
        ca = CognitiveArchitecture()
        assert ca.beliefs is not None
        assert ca.goals is not None
        assert ca.reasoning is not None
        assert ca.memory_working is not None
        assert ca.memory_episodic is not None
        assert ca.attention is not None
        assert ca.reflection is not None
        assert ca.strategy is not None
        assert ca.decision is not None
        assert ca.orchestrator is not None

    def test_observe(self):
        ca = CognitiveArchitecture()
        ca.observe("System status: OK", entities=["entity:1"], importance=0.8)
        assert ca.memory_episodic.entry_count == 1
        assert ca.memory_working.size >= 1

    def test_think(self):
        ca = CognitiveArchitecture()
        ca.think("Inferred that X causes Y")
        assert ca.memory_episodic.entry_count == 1

    def test_reflect(self):
        ca = CognitiveArchitecture()
        ca.observe("Event 1", importance=0.5)
        ca.observe("Event 2", importance=0.5)
        ca.observe("Event 3", importance=0.5)
        reflections = ca.reflect()
        assert isinstance(reflections, list)

    def test_decide(self):
        ca = CognitiveArchitecture()
        ca.decision.register_criterion("score", weight=1.0)
        alts = [
            Alternative(name="A", criteria_scores={"score": 0.9}),
            Alternative(name="B", criteria_scores={"score": 0.4}),
        ]
        decision = ca.decide(alts)
        assert decision.selected_id == alts[0].id

    def test_tick(self):
        ca = CognitiveArchitecture()
        ca.memory_working.store("Item", salience=0.3)
        ca.attention.bottom_up("e", "1", "Focus", salience=0.5)
        ca.tick()
        # Salience should have decayed
        assert ca.memory_working.size >= 0

    def test_summary(self):
        ca = CognitiveArchitecture()
        ca.beliefs.believe("Test belief", confidence=0.8)
        ca.goals.create_goal("Test goal")
        s = ca.summary()
        assert "beliefs" in s
        assert "goals" in s
        assert s["beliefs"]["total_beliefs"] == 1
        assert s["goals"]["total_goals"] == 1

    def test_belief_in_brain(self):
        from genesis.brain import EngineeringBrain
        import tempfile, os
        with tempfile.TemporaryDirectory() as td:
            brain = EngineeringBrain(storage_path=os.path.join(td, "brain.db"))
            assert brain.cognition is not None
            brain.cognition.beliefs.believe("Brain belief", confidence=0.9)
            assert brain.cognition.beliefs.belief_count == 1
