"""Tests for UCOS Capability model."""

import pytest
from genesis.ucos.capability import (
    Capability, CapabilityCategory, CapabilityDefinition, CapabilityState,
    CapabilityContract, CapabilityVersion, CapabilityHealth, CapabilityPermission,
    CapabilityState, MaturityLevel,
)


def test_capability_construct_with_id_name():
    c = Capability("cap_a", "TestCap")
    assert c.id == "cap_a"
    assert c.name == "TestCap"
    assert c.state == CapabilityState.DORMANT
    assert c.definition.category == CapabilityCategory.PLATFORM
    assert c.definition.version.semver == "1.0.0"


def test_capability_construct_with_definition():
    d = CapabilityDefinition(
        id="cap_b", name="FullCap", category=CapabilityCategory.KNOWLEDGE,
        maturity=MaturityLevel.STABLE,
        dependencies=["dep_x"], tags=["test", "full"],
    )
    c = Capability(d)
    assert c.id == "cap_b"
    assert c.definition.category == CapabilityCategory.KNOWLEDGE
    assert c.definition.maturity == MaturityLevel.STABLE
    assert c.definition.dependencies == ["dep_x"]
    assert "test" in c.definition.tags


def test_capability_with_definition_kwargs():
    c = Capability("cap_c", "KwargsCap", definition__category=CapabilityCategory.KNOWLEDGE,
                   definition__maturity=MaturityLevel.CRITICAL)
    assert c.definition.category == CapabilityCategory.KNOWLEDGE
    assert c.definition.maturity == MaturityLevel.CRITICAL
    assert c.state == CapabilityState.DORMANT


def test_state_property():
    c = Capability("cap_d", "StateTest")
    assert c.state == CapabilityState.DORMANT
    c.state = CapabilityState.READY
    assert c.state == CapabilityState.READY


def test_is_running_is_ready():
    c = Capability("cap_e", "StateFlags")
    assert not c.is_running
    assert not c.is_ready
    c.state = CapabilityState.READY
    assert c.is_ready
    assert not c.is_running
    c.state = CapabilityState.RUNNING
    assert c.is_running
    assert not c.is_ready


def test_capability_categories():
    assert len(CapabilityCategory) > 20
    assert "infrastructure" in {e.value for e in CapabilityCategory}
    assert "storage" in {e.value for e in CapabilityCategory}
    assert "knowledge" in {e.value for e in CapabilityCategory}
    assert "analysis" not in {e.value for e in CapabilityCategory}


def test_maturity_levels():
    assert len(MaturityLevel) == 7
    levels = list(MaturityLevel)
    assert levels[0] == MaturityLevel.PROPOSED
    assert levels[-1] == MaturityLevel.DEPRECATED


def test_capability_contract():
    contract = CapabilityContract(
        inputs=[{"name": "a", "type": "str"}],
        outputs=[{"name": "b", "type": "int"}],
        preconditions=["x is not None"],
    )
    assert contract.inputs[0]["name"] == "a"
    errors = contract.validate_input({"b": 1})
    assert not errors
    errors = contract.validate_input({})
    assert not errors


def test_capability_version():
    v = CapabilityVersion(major=1, minor=2, patch=3)
    assert v.semver == "1.2.3"
    v.bump_major()
    assert v.semver == "2.0.0"
    v.bump_minor()
    assert v.semver == "2.1.0"
    v.bump_patch()
    assert v.semver == "2.1.1"


def test_capability_version_comparison():
    v1 = CapabilityVersion(major=1, minor=0, patch=0)
    v2 = CapabilityVersion(major=2, minor=0, patch=0)
    assert v2.major > v1.major


def test_capability_health_default():
    h = CapabilityHealth()
    assert h.score == 1.0
    assert h.healthy
    assert h.failure_count == 0


def test_capability_health_unhealthy():
    h = CapabilityHealth(healthy=False, score=0.3, failure_count=20, error_rate=0.8)
    assert not h.healthy
    assert h.score == 0.3


def test_capability_permission():
    p = CapabilityPermission(actions=["read", "write"], roles=["admin"])
    assert "read" in p.actions
    assert "admin" in p.roles


def test_capability_execute_no_impl():
    c = Capability("cap_f", "NoImpl")
    result = c.execute(x=1)
    assert result is None


def test_capability_execute_with_impl():
    c = Capability("cap_g", "WithImpl", implementation=lambda x, y: x + y)
    result = c.execute(x=3, y=4)
    assert result == 7


def test_capability_execution_count():
    c = Capability("cap_h", "Counter", implementation=lambda: 42)
    assert c.execution_count == 0
    c.execute()
    assert c.execution_count == 1
    c.execute()
    assert c.execution_count == 2


def test_capability_avg_execution_time():
    c = Capability("cap_i", "AvgTime", implementation=lambda: None)
    assert c.avg_execution_time == 0.0
    c.execute()
    assert c.execution_count == 1


def test_capability_start_stop():
    c = Capability("cap_j", "StartStop")
    c.start()
    assert c.is_running
    c.stop()
    assert c.state == CapabilityState.STOPPED


def test_capability_definition_defaults():
    d = CapabilityDefinition(name="Test")
    assert d.name == "Test"
    assert d.category == CapabilityCategory.PLATFORM
    assert d.maturity == MaturityLevel.PROPOSED
    assert not d.dependencies
    assert not d.tags
    assert d.id


def test_capability_definition_to_dict():
    d = CapabilityDefinition(id="dict_test", name="DictCap")
    data = d.to_dict()
    assert data["id"] == "dict_test"
    assert data["name"] == "DictCap"
    assert "category" in data


def test_capability_definition_register_consumer():
    d = CapabilityDefinition(id="reg_cons", name="RegCons")
    d.register_consumer("consumer_a")
    assert "consumer_a" in d.consumers


def test_capability_definition_has_permission():
    p = CapabilityPermission(actions=["read"], roles=["viewer"])
    d = CapabilityDefinition(id="perm_test", name="PermTest", permissions=[p])
    assert d.has_permission("read", "viewer")
    assert not d.has_permission("write")
