"""Tests for UCOS CapabilityRegistry."""

import pytest
from genesis.ucos.capability import (
    Capability, CapabilityDefinition, CapabilityCategory, MaturityLevel, CapabilityState,
)
from genesis.ucos.registry import CapabilityRegistry


@pytest.fixture
def registry():
    return CapabilityRegistry()


@pytest.fixture
def sample_definition():
    return CapabilityDefinition(
        id="reg_a", name="Alpha", category=CapabilityCategory.PLATFORM,
        maturity=MaturityLevel.STABLE, tags=["ml", "inference"],
    )


def test_register(registry, sample_definition):
    cap = registry.register(sample_definition)
    assert cap.id == "reg_a"
    assert registry.count == 1
    assert cap.state == CapabilityState.REGISTERED


def test_register_with_implementation(registry, sample_definition):
    cap = registry.register(sample_definition, implementation=lambda: 42)
    assert cap.execution_count == 0


def test_get(registry, sample_definition):
    registry.register(sample_definition)
    assert registry.get("reg_a").name == "Alpha"
    assert registry.get("missing") is None


def test_get_definition(registry, sample_definition):
    registry.register(sample_definition)
    d = registry.get_definition("reg_a")
    assert d.name == "Alpha"


def test_unregister(registry):
    d1 = CapabilityDefinition(id="u_a", name="U1")
    d2 = CapabilityDefinition(id="u_b", name="U2")
    registry.register(d1)
    registry.register(d2)
    assert registry.count == 2
    assert registry.unregister("u_a")
    assert registry.count == 1
    assert registry.get("u_a") is None
    assert not registry.unregister("missing")


def test_find_by_category(registry):
    registry.register(CapabilityDefinition(id="f_a", name="F1", category=CapabilityCategory.STORAGE))
    registry.register(CapabilityDefinition(id="f_b", name="F2", category=CapabilityCategory.PLATFORM))
    results = registry.find(category=CapabilityCategory.STORAGE)
    assert len(results) == 1
    assert results[0].id == "f_a"


def test_find_by_tag(registry):
    d = CapabilityDefinition(id="f_c", name="F3", tags=["ml"])
    registry.register(d)
    results = registry.find(tag="ml")
    assert len(results) == 1


def test_find_by_maturity(registry):
    registry.register(CapabilityDefinition(id="f_d", name="F4", maturity=MaturityLevel.CRITICAL))
    results = registry.find(maturity=MaturityLevel.CRITICAL)
    assert len(results) == 1


def test_find_by_state(registry):
    d = CapabilityDefinition(id="f_e", name="F5")
    registry.register(d)
    registry.set_state("f_e", CapabilityState.RUNNING)
    results = registry.find(state=CapabilityState.RUNNING)
    assert len(results) == 1


def test_find_by_name(registry):
    registry.register(CapabilityDefinition(id="f_f", name="FindByName"))
    results = registry.find(name_contains="ByName")
    assert len(results) == 1


def test_find_combined(registry):
    d = CapabilityDefinition(
        id="f_g", name="F7", category=CapabilityCategory.PLATFORM,
        maturity=MaturityLevel.STABLE, tags=["ml"],
    )
    registry.register(d)
    results = registry.find(category=CapabilityCategory.PLATFORM, tag="ml")
    assert len(results) == 1


def test_all_property(registry):
    d1 = CapabilityDefinition(id="all_a", name="All1")
    d2 = CapabilityDefinition(id="all_b", name="All2")
    registry.register(d1)
    registry.register(d2)
    assert len(registry.all) == 2


def test_set_state(registry):
    d = CapabilityDefinition(id="state_a", name="StateCap")
    registry.register(d)
    assert registry.set_state("state_a", CapabilityState.FAILED)
    assert registry.get("state_a").state == CapabilityState.FAILED
    assert not registry.set_state("missing", CapabilityState.READY)


def test_update_maturity(registry):
    d = CapabilityDefinition(id="mat_a", name="MatCap", maturity=MaturityLevel.ALPHA)
    registry.register(d)
    assert registry.update_maturity("mat_a", MaturityLevel.STABLE)
    assert registry.get("mat_a").definition.maturity == MaturityLevel.STABLE


def test_register_consumer(registry):
    d = CapabilityDefinition(id="cons_a", name="ConsCap")
    registry.register(d)
    assert registry.register_consumer("cons_a", "consumer_1")
    assert "consumer_1" in registry.get("cons_a").definition.consumers


def test_register_provider(registry):
    d = CapabilityDefinition(id="prov_a", name="ProvCap")
    registry.register(d)
    assert registry.register_provider("prov_a", "provider_1")


def test_dependency_chain(registry):
    root = CapabilityDefinition(id="dep_root", name="Root")
    mid = CapabilityDefinition(id="dep_mid", name="Mid", dependencies=["dep_root"])
    leaf = CapabilityDefinition(id="dep_leaf", name="Leaf", dependencies=["dep_mid"])
    registry.register(root)
    registry.register(mid)
    registry.register(leaf)
    chains = registry.dependency_chain("dep_leaf")
    assert len(chains) >= 1
    assert "dep_root" in chains[0]


def test_resolve_dependencies(registry):
    root = CapabilityDefinition(id="res_root", name="Root")
    mid = CapabilityDefinition(id="res_mid", name="Mid", dependencies=["res_root"])
    registry.register(root)
    registry.register(mid)
    resolved = registry.resolve_dependencies("res_mid")
    ids = [c.id for c in resolved]
    assert "res_root" in ids


def test_version_history(registry):
    d = CapabilityDefinition(id="ver_a", name="V1")
    registry.register(d)
    registry.record_version("ver_a")
    history = registry.get_version_history("ver_a")
    assert len(history) >= 1


def test_summary(registry):
    d1 = CapabilityDefinition(id="sum_a", name="S1", category=CapabilityCategory.STORAGE)
    d2 = CapabilityDefinition(id="sum_b", name="S2", category=CapabilityCategory.PLATFORM)
    registry.register(d1)
    registry.register(d2)
    summary = registry.summary()
    assert summary["total_capabilities"] == 2
    assert "storage" in summary["by_category"]
