"""
Tests for the Autonomous Planning System — Phase 3 of GENESIS IX.
"""

import os
import tempfile

import pytest

from genesis.planning import (
    Plan, PlanStep, Planner, PlanStatus, StepStatus,
    StrategicPlanner, ArchitecturalPlanner, ResearchPlanner,
    ImplementationPlanner, ExecutionPlanner, ValidationPlanner,
    PublicationPlanner, PlanningSystem, PlannerLevel, LEVEL_ORDER,
)
from genesis.brain import EngineeringBrain


class TestPlanPrimitives:
    def test_create_step(self):
        step = PlanStep(action="test_action", description="A test step")
        assert step.id != ""
        assert step.action == "test_action"
        assert step.status == StepStatus.PENDING
        assert step.created_at > 0

    def test_create_step_with_dependencies(self):
        step = PlanStep(
            action="step_b",
            dependencies=["step_a"],
            estimated_effort=2.5,
        )
        assert "step_a" in step.dependencies
        assert step.estimated_effort == 2.5

    def test_create_plan(self):
        plan = Plan(title="Test Plan", goal="Achieve something")
        assert plan.id != ""
        assert plan.level == "strategic"
        assert plan.status == PlanStatus.DRAFT
        assert plan.progress == 0.0
        assert plan.is_terminal is True

    def test_plan_progress(self):
        plan = Plan(level="implementation")
        plan.add_step("step_1")
        plan.add_step("step_2")
        assert plan.progress == 0.0

        plan.steps[0].status = StepStatus.COMPLETED
        assert plan.progress == 0.5

        plan.steps[1].status = StepStatus.COMPLETED
        assert plan.progress == 1.0

    def test_next_steps(self):
        plan = Plan()
        s1 = plan.add_step("step_1")
        s2 = plan.add_step("step_2", dependencies=[s1.id])
        s3 = plan.add_step("step_3")

        next_steps = plan.next_steps()
        assert len(next_steps) == 2  # s1 and s3 have no deps
        assert any(s.id == s1.id for s in next_steps)
        assert any(s.id == s3.id for s in next_steps)

        s1.status = StepStatus.COMPLETED
        next_steps = plan.next_steps()
        assert len(next_steps) == 2  # s2 now ready, s3 still ready

    def test_add_step(self):
        plan = Plan()
        step = plan.add_step("write_code", description="Write the code",
                             estimated_effort=3.0, language="python")
        assert step.action == "write_code"
        assert step.params.get("language") == "python"
        assert len(plan.steps) == 1

    def test_brain_entity_conversion(self):
        plan = Plan(title="Convert Me", goal="Test conversion")
        entity = plan.to_brain_entity()
        assert entity.entity_type == "plan"
        assert entity.label == "Convert Me"
        assert entity.source_id == plan.id
        assert entity.attributes["level"] == "strategic"
        assert entity.attributes["progress"] == 0.0

    def test_step_brain_entity(self):
        step = PlanStep(action="test", description="Test step")
        entity = step.to_brain_entity("plan:1")
        assert entity.entity_type == "plan_step"
        assert entity.attributes["plan_id"] == "plan:1"
        assert entity.attributes["action"] == "test"

    def test_summary(self):
        plan = Plan(level="implementation", title="My Feature")
        plan.add_step("step_1")
        plan.add_step("step_2")
        plan.steps[0].status = StepStatus.COMPLETED
        plan.status = PlanStatus.ACTIVE

        s = plan.summary()
        assert s["level"] == "implementation"
        assert s["status"] == "active"
        assert s["steps_total"] == 2
        assert s["steps_by_status"]["completed"] == 1
        assert s["steps_by_status"]["pending"] == 1
        assert s["progress"] == 0.5

    def test_is_terminal(self):
        plan = Plan(id="parent")
        assert plan.is_terminal is True
        plan.sub_plan_ids.append("child")
        assert plan.is_terminal is False


class TestPlanners:
    @pytest.fixture
    def brain(self):
        with tempfile.TemporaryDirectory() as td:
            yield EngineeringBrain(storage_path=os.path.join(td, "plan_test.db"))

    def test_strategic_planner(self, brain):
        p = StrategicPlanner(brain)
        plan = p.plan_epoch(
            "Become the leading AI platform",
            duration_days=365,
            objectives=["Build core AI", "Add ML support", "Scale to 1M users"],
        )
        assert plan.level == "strategic"
        assert plan.status == PlanStatus.ACTIVE
        assert len(plan.steps) == 3
        assert p.active_plans()[0].id == plan.id

    def test_strategic_planner_empty_objectives(self, brain):
        p = StrategicPlanner(brain)
        plan = p.plan_epoch("Just a vision")
        assert len(plan.steps) == 0
        assert plan.status == PlanStatus.ACTIVE

    def test_architectural_planner(self, brain):
        p = ArchitecturalPlanner(brain)
        plan = p.plan_design(
            "DataPipeline",
            requirements=["Must support streaming", "Must be fault-tolerant"],
            parent_plan_id="strat:1",
        )
        assert plan.level == "architectural"
        assert plan.parent_plan_id == "strat:1"
        assert len(plan.steps) == 2
        assert plan.steps[0].params.get("requirement") == "Must support streaming"

    def test_research_planner(self, brain):
        p = ResearchPlanner(brain)
        plan = p.plan_investigation(
            "Why is latency high?",
            hypotheses=["Network bottleneck", "CPU saturation", "I/O wait"],
        )
        assert plan.level == "research"
        assert len(plan.steps) == 3

    def test_implementation_planner(self, brain):
        p = ImplementationPlanner(brain)
        plan = p.plan_feature(
            "User Authentication",
            tasks=["Add login page", "Implement JWT", "Add tests"],
        )
        assert plan.level == "implementation"
        assert len(plan.steps) == 3
        assert plan.steps[1].dependencies == [plan.steps[0].id]

    def test_execution_planner(self, brain):
        parent = Plan(level="implementation", title="Feature X")
        parent.add_step("step_1")
        parent.add_step("step_2")

        p = ExecutionPlanner(brain)
        plan = p.schedule_plan(parent, available_resources=["dev-1", "dev-2"])
        assert plan.level == "execution"
        assert len(plan.steps) == 2

    def test_validation_planner(self, brain):
        p = ValidationPlanner(brain)
        plan = p.plan_validation(
            "Auth Module",
            checks=["Unit tests pass", "Integration tests pass", "Security review"],
        )
        assert plan.level == "validation"
        assert len(plan.steps) == 3

    def test_publication_planner(self, brain):
        p = PublicationPlanner(brain)
        plan = p.plan_publication(
            "v2.0 Release",
            audiences=["developers", "enterprise-customers"],
        )
        assert plan.level == "publication"
        assert len(plan.steps) >= 4

    def test_planner_create_plan(self, brain):
        p = StrategicPlanner(brain)
        plan = p.create_plan("A new goal", priority=0.8)
        assert plan.goal == "A new goal"
        assert plan.priority == 0.8
        assert plan.status == PlanStatus.DRAFT
        assert plan.id in p.plans

    def test_planner_get_plan(self):
        p = StrategicPlanner()
        plan = p.create_plan("Find me")
        assert p.get_plan(plan.id) is plan
        assert p.get_plan("nonexistent") is None

    def test_planner_update_status(self):
        p = StrategicPlanner()
        plan = p.create_plan("Status test")
        result = p.update_status(plan.id, PlanStatus.ACTIVE)
        assert result is True
        assert plan.status == PlanStatus.ACTIVE

        result = p.update_status("nonexistent", PlanStatus.ACTIVE)
        assert result is False

    def test_planner_all_plans(self):
        p = StrategicPlanner()
        p.create_plan("Plan A")
        p.create_plan("Plan B")
        assert len(p.all_plans()) == 2

    def test_planner_active_plans(self):
        p = StrategicPlanner()
        p.create_plan("Draft Plan")
        plan2 = p.create_plan("Active Plan")
        p.update_status(plan2.id, PlanStatus.ACTIVE)
        assert len(p.active_plans()) == 1
        assert p.active_plans()[0].id == plan2.id

    def test_planner_summary(self):
        p = StrategicPlanner()
        p.create_plan("Plan A")
        p2 = p.create_plan("Plan B")
        p.update_status(p2.id, PlanStatus.ACTIVE)

        s = p.summary()
        assert s["level"] == "strategic"
        assert s["total_plans"] == 2
        assert s["active_count"] == 1


class TestPlanningSystem:
    @pytest.fixture
    def system(self):
        return PlanningSystem()

    def test_create(self):
        ps = PlanningSystem()
        assert ps.strategic.level == "strategic"
        assert ps.architectural.level == "architectural"
        assert ps.research.level == "research"
        assert ps.implementation.level == "implementation"
        assert ps.execution.level == "execution"
        assert ps.validation.level == "validation"
        assert ps.publication.level == "publication"
        assert len(ps._planners) == 7

    def test_get_planner(self, system):
        assert system.get_planner("strategic") is system.strategic
        assert system.get_planner("publication") is system.publication
        assert system.get_planner("nonexistent") is None

    def test_decompose(self, system):
        top = system.strategic.create_plan("Strategic goal")
        top.add_step("Build AI")
        top.add_step("Scale platform")

        children = system.decompose(top)
        assert len(children) == 2
        assert len(top.sub_plan_ids) == 2
        for child in children:
            assert child.parent_plan_id == top.id

    def test_decompose_terminal_level(self, system):
        pub = system.publication.create_plan("Publish docs")
        children = system.decompose(pub)
        assert children == []

    def test_decompose_full(self, system):
        plan = system.decompose_full(
            "Build the ultimate platform",
            objectives=["AI Engine", "Cloud Scale", "Developer Experience"],
        )
        assert plan.level == "strategic"
        assert len(plan.steps) == 3

        all_plans = system.all_plans()
        assert len(all_plans) >= 4  # 1 strategic + 3 architectural children

    def test_decompose_full_no_objectives(self, system):
        plan = system.decompose_full("Just a vision")
        assert plan.level == "strategic"
        assert len(plan.steps) == 0  # No objectives = no steps

    def test_negotiate_priorities(self, system):
        parent = system.strategic.create_plan("Parent", priority=0.8)
        parent.status = PlanStatus.ACTIVE
        child = system.architectural.create_plan(
            "Child", parent_plan_id=parent.id, priority=0.9
        )
        child.status = PlanStatus.ACTIVE
        parent.sub_plan_ids.append(child.id)

        conflicts = system.negotiate_priorities()
        assert len(conflicts) == 1
        assert conflicts[0]["plan_id"] == child.id
        assert child.priority < 0.9

    def test_negotiate_no_conflicts(self, system):
        parent = system.strategic.create_plan("Parent", priority=0.8)
        parent.status = PlanStatus.ACTIVE
        child = system.architectural.create_plan(
            "Child", parent_plan_id=parent.id, priority=0.7
        )
        child.status = PlanStatus.ACTIVE
        parent.sub_plan_ids.append(child.id)

        conflicts = system.negotiate_priorities()
        assert len(conflicts) == 0
        assert child.priority == 0.7

    def test_all_plans(self, system):
        system.strategic.create_plan("Strategic Plan")
        system.architectural.create_plan("Arch Plan")
        system.research.create_plan("Research Plan")

        all_p = system.all_plans()
        assert len(all_p) == 3

    def test_active_plans(self, system):
        p1 = system.strategic.create_plan("Plan 1")
        p2 = system.strategic.create_plan("Plan 2")
        system.strategic.update_status(p1.id, PlanStatus.ACTIVE)

        active = system.active_plans()
        assert len(active) == 1
        assert active[0].id == p1.id

    def test_plan_graph(self, system):
        parent = system.strategic.create_plan("Parent")
        child = system.architectural.create_plan(
            "Child", parent_plan_id=parent.id,
        )
        parent.sub_plan_ids.append(child.id)

        graph = system.plan_graph()
        assert len(graph["nodes"]) == 2
        assert len(graph["edges"]) >= 1

    def test_summary(self, system):
        system.strategic.create_plan("Plan 1")
        p2 = system.strategic.create_plan("Plan 2")
        system.strategic.update_status(p2.id, PlanStatus.ACTIVE)
        system.architectural.create_plan("Arch Plan")

        s = system.summary()
        assert s["total_plans"] == 3
        assert s["total_active"] == 1
        assert len(s["planners"]) == 7
        assert s["planners"]["strategic"]["total_plans"] == 2
        assert s["planners"]["architectural"]["total_plans"] == 1

    def test_level_order(self):
        assert len(LEVEL_ORDER) == 7
        assert LEVEL_ORDER[0].value == "strategic"
        assert LEVEL_ORDER[1].value == "architectural"
        assert LEVEL_ORDER[2].value == "research"
        assert LEVEL_ORDER[3].value == "implementation"
        assert LEVEL_ORDER[4].value == "execution"
        assert LEVEL_ORDER[5].value == "validation"
        assert LEVEL_ORDER[6].value == "publication"

    def test_planner_level_enum(self):
        assert PlannerLevel.STRATEGIC.value == "strategic"
        assert PlannerLevel.PUBLICATION.value == "publication"

    def test_brain_integration(self, system):
        brain = EngineeringBrain(storage_path=":memory:")
        system.brain = brain
        system.strategic.brain = brain
        plan = system.strategic.plan_epoch("Epoch vision",
                                           objectives=["Obj1", "Obj2"])
        entity = brain.find_by_source("planning", plan.id)
        assert entity is not None
        assert entity.attributes["level"] == "strategic"
