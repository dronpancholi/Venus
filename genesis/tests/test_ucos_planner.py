"""Tests for UCOS CapabilityPlanner."""

import pytest
from genesis.ucos.capability import CapabilityDefinition
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.resolver import CapabilityResolver
from genesis.ucos.planner import CapabilityPlanner


@pytest.fixture
def planner():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="pl_root", name="Root"))
    reg.register(CapabilityDefinition(id="pl_a", name="A", dependencies=["pl_root"]))
    reg.register(CapabilityDefinition(id="pl_b", name="B", dependencies=["pl_root"]))
    reg.register(CapabilityDefinition(id="pl_c", name="C", dependencies=["pl_a", "pl_b"]))
    resolver = CapabilityResolver(reg)
    p = CapabilityPlanner(reg, resolver)
    return reg, p


def test_create_plan(planner):
    reg, p = planner
    plan = p.create_plan("pl_root")
    assert plan is not None
    assert plan.capability_id == "pl_root"
    assert len(plan.steps) >= 1


def test_create_plan_with_deps(planner):
    reg, p = planner
    plan = p.create_plan("pl_c")
    assert plan is not None
    assert len(plan.steps) >= 3


def test_create_plan_missing():
    reg = CapabilityRegistry()
    p = CapabilityPlanner(reg)
    assert p.create_plan("missing") is None


def test_estimated_duration(planner):
    reg, p = planner
    plan = p.create_plan("pl_c")
    assert plan.estimated_duration > 0


def test_parallel_groups(planner):
    reg, p = planner
    plan = p.create_plan("pl_c")
    if plan.parallel_groups:
        for group in plan.parallel_groups:
            assert len(group) >= 1


def test_get_plan(planner):
    reg, p = planner
    plan = p.create_plan("pl_root")
    retrieved = p.get_plan(plan.id)
    assert retrieved is not None
    assert retrieved.id == plan.id


def test_estimate_resources(planner):
    reg, p = planner
    resources = p.estimate_resources("pl_root")
    assert isinstance(resources, dict)


def test_optimize_order(planner):
    reg, p = planner
    order = p.optimize_order(["pl_root", "pl_a", "pl_b", "pl_c"])
    assert len(order) == 4
    assert all(cid in order for cid in ["pl_root", "pl_a", "pl_b", "pl_c"])


def test_mark_started(planner):
    reg, p = planner
    plan = p.create_plan("pl_root")
    p.mark_started(plan.id)
    assert plan.status == "running"
    assert plan.started_at > 0


def test_mark_completed(planner):
    reg, p = planner
    plan = p.create_plan("pl_root")
    p.mark_completed(plan.id)
    assert plan.status == "completed"
    assert plan.completed_at > 0


def test_mark_failed(planner):
    reg, p = planner
    plan = p.create_plan("pl_root")
    p.mark_failed(plan.id, "test error")
    assert "test error" in plan.status


def test_risk_calculation(planner):
    reg, p = planner
    plan = p.create_plan("pl_c")
    assert plan.risk >= 0


def test_plan_without_resolver():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="simple", name="Simple"))
    p = CapabilityPlanner(reg)
    plan = p.create_plan("simple")
    assert plan is not None
