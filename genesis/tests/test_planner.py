"""Tests for GENESIS Ω² — Engineering Planner."""

import json
import time
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from genesis.planner import EngineeringPlanner, EngineeringPlan, PlanItem


class TestEngineeringPlanner:
    def test_create(self):
        p = EngineeringPlanner()
        assert p._plans == {}

    def test_boot(self):
        p = EngineeringPlanner()
        p.boot()
        assert p._planner_obj is not None
        assert p._planner_obj.name == "EngineeringPlanner"

    def test_generate_plan_no_kernel(self):
        p = EngineeringPlanner()
        plan = p.generate_plan("Test Plan")
        assert isinstance(plan, EngineeringPlan)
        assert plan.name == "Test Plan"
        assert plan.items == []

    def test_generate_plan_auto_name(self):
        p = EngineeringPlanner()
        plan = p.generate_plan()
        assert plan.name.startswith("Plan ")

    def test_list_plans_empty(self):
        p = EngineeringPlanner()
        assert p.list_plans() == []

    def test_list_plans_after_generate(self):
        p = EngineeringPlanner()
        p.generate_plan("Alpha")
        p.generate_plan("Beta")
        plans = p.list_plans()
        assert len(plans) == 2
        names = [pl["name"] for pl in plans]
        assert "Alpha" in names
        assert "Beta" in names

    def test_get_plan_found(self):
        p = EngineeringPlanner()
        plan = p.generate_plan("Test")
        assert p.get_plan("Test") is plan

    def test_get_plan_not_found(self):
        p = EngineeringPlanner()
        assert p.get_plan("nonexistent") is None

    def test_generate_plan_creates_registry_objects(self):
        p = EngineeringPlanner()
        p.generate_plan("RegTest")
        plans = p._registry.get_by_type("plan")
        regtest = [o for o in plans if o.name == "RegTest"]
        assert len(regtest) == 1
        assert regtest[0].tags == ["plan", "generated"]

    def test_generate_plan_with_kernel(self):
        kernel = MagicMock()
        kernel.twin = None
        kernel.reasoning = None
        kernel.knowledge = None
        p = EngineeringPlanner(kernel=kernel)
        plan = p.generate_plan("Kernel Plan")
        assert plan.name == "Kernel Plan"
        assert plan.items == []


class TestEngineeringPlan:
    def test_dataclass_defaults(self):
        plan = EngineeringPlan(name="P")
        assert plan.items == []
        assert plan.repository == ""
        assert plan.created_at == 0.0
        assert plan.total_items == 0
        assert plan.completed_items == 0

    def test_dataclass_custom(self):
        items = [PlanItem(title="A"), PlanItem(title="B")]
        plan = EngineeringPlan(
            name="P", items=items, repository="repo",
            created_at=100.0, total_items=2, completed_items=1,
        )
        assert plan.name == "P"
        assert len(plan.items) == 2
        assert plan.repository == "repo"
        assert plan.created_at == 100.0
        assert plan.total_items == 2
        assert plan.completed_items == 1


class TestPlanItem:
    def test_dataclass_defaults(self):
        item = PlanItem(title="T")
        assert item.title == "T"
        assert item.description == ""
        assert item.priority == "medium"
        assert item.effort == "medium"
        assert item.status == "pending"
        assert item.source == ""
        assert item.tags == []

    def test_dataclass_custom(self):
        item = PlanItem(
            title="T", description="D", priority="high", effort="large",
            status="active", source="test", tags=["urgent"],
        )
        assert item.priority == "high"
        assert item.effort == "large"
        assert item.status == "active"
        assert item.tags == ["urgent"]
