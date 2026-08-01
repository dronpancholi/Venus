"""Tests for UCOS CapabilityValidator."""

import pytest
from genesis.ucos.capability import Capability, CapabilityDefinition, CapabilityHealth
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.validator import CapabilityValidator


@pytest.fixture
def validator():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="val_a", name="ValidCap"))
    v = CapabilityValidator(reg)
    return reg, v


def test_validate_healthy(validator):
    reg, v = validator
    result = v.validate("val_a")
    assert result.passed
    assert result.score > 0.5
    assert len(result.errors) == 0


def test_validate_missing(validator):
    reg, v = validator
    result = v.validate("missing")
    assert not result.passed
    assert result.score == 0.0


def test_validate_missing_dependency():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="val_b", name="WithDep", dependencies=["missing"]))
    v = CapabilityValidator(reg)
    result = v.validate("val_b")
    assert not result.passed
    assert any("missing" in e for e in result.errors)


def test_validate_high_failure_count():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="val_c", name="Unhealthy",
                                       health=CapabilityHealth(score=0.3, failure_count=20, error_rate=0.8)))
    v = CapabilityValidator(reg)
    result = v.validate("val_c")
    assert result.passed
    assert result.score < 1.0


def test_custom_rule(validator):
    reg, v = validator
    def rule(cap):
        if cap.definition.name == "ValidCap":
            return ["Custom error: name is too generic"]
        return None
    v.add_rule(rule)
    result = v.validate("val_a")
    assert not result.passed
    assert any("generic" in e for e in result.errors)


def test_validate_all(validator):
    reg, v = validator
    results = v.validate_all()
    assert "val_a" in results


def test_healthy_and_unhealthy(validator):
    reg, v = validator
    healthy = v.healthy_capabilities()
    unhealthy = v.unhealthy_capabilities()
    assert len(healthy) >= 1
    assert len(unhealthy) == 0


def test_get_result(validator):
    reg, v = validator
    assert v.get_result("val_a") is None
    v.validate("val_a")
    result = v.get_result("val_a")
    assert result is not None
