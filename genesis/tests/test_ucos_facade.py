"""Tests for UCOS facade."""

import pytest
from genesis.ucos.capability import Capability, CapabilityCategory, CapabilityDefinition, CapabilityState
from genesis.ucos.ucos import UCOS


@pytest.fixture
def ucos():
    return UCOS()


def test_ucos_initialization(ucos):
    assert ucos.name == "UCOS"
    assert ucos.registry.count == 0


def test_ucos_register_with_definition(ucos):
    d = CapabilityDefinition(id="uc_a", name="UCOSTest")
    cap = ucos.register(d)
    assert cap.id == "uc_a"
    assert ucos.registry.count == 1


def test_ucos_register_with_capability(ucos):
    c = Capability("uc_a", "UCOSTest")
    cap = ucos.register(c)
    assert cap.id == "uc_a"


def test_ucos_get(ucos):
    d = CapabilityDefinition(id="uc_b", name="GetTest")
    ucos.register(d)
    assert ucos.get("uc_b").name == "GetTest"
    assert ucos.get("missing") is None


def test_ucos_resolve_dependencies(ucos):
    ucos.register(CapabilityDefinition(id="uc_root", name="Root"))
    ucos.register(CapabilityDefinition(id="uc_c", name="C", dependencies=["uc_root"]))
    order = ucos.resolve_dependencies()
    assert "uc_root" in order


def test_ucos_boot_order(ucos):
    ucos.register(CapabilityDefinition(id="uc_root2", name="Root2"))
    ucos.register(CapabilityDefinition(id="uc_d", name="D", dependencies=["uc_root2"]))
    order = ucos.boot_order()
    assert len(order) >= 2


def test_ucos_plan(ucos):
    d = CapabilityDefinition(id="uc_e", name="E")
    ucos.register(d)
    plan = ucos.plan("test", "uc_e")
    assert plan is not None
    assert plan.capability_id == "uc_e"


def test_ucos_validate(ucos):
    d = CapabilityDefinition(id="uc_f", name="F")
    ucos.register(d)
    result = ucos.validate("uc_f")
    assert result.passed


def test_ucos_validate_all(ucos):
    ucos.register(CapabilityDefinition(id="uc_g", name="G"))
    ucos.register(CapabilityDefinition(id="uc_h", name="H"))
    results = ucos.validate_all()
    assert len(results) == 2


def test_ucos_execute(ucos):
    d = CapabilityDefinition(id="uc_i", name="I")
    cap = ucos.register(d)
    cap.state = CapabilityState.READY
    ctx = ucos.execute("uc_i")
    assert ctx.success


def test_ucos_start_stop(ucos):
    d = CapabilityDefinition(id="uc_j", name="J")
    ucos.register(d)
    ucos.lifecycle.verify("uc_j")
    ucos.lifecycle.ready("uc_j")
    assert ucos.start("uc_j")
    assert ucos.stop("uc_j")


def test_ucos_check_health(ucos):
    for i in range(3):
        ucos.register(CapabilityDefinition(id=f"uc_k_{i}", name=f"K{i}"))
    health = ucos.check_health()
    assert health["total"] >= 3


def test_ucos_overview(ucos):
    for i in range(3):
        ucos.register(CapabilityDefinition(
            id=f"uc_over_{i}", name=f"Over{i}",
            category=CapabilityCategory.STORAGE))
    overview = ucos.overview()
    assert overview["capabilities"] >= 3
    assert "storage" in overview["by_category"]
    assert overview["avg_health"] > 0
    assert not overview["has_cycles"]


def test_ucos_full_lifecycle(ucos):
    d = CapabilityDefinition(id="uc_full", name="FullLifecycle")
    ucos.register(d)
    ucos.lifecycle.verify("uc_full")
    ucos.lifecycle.ready("uc_full")
    ucos.lifecycle.start("uc_full")
    assert ucos.get("uc_full").state == CapabilityState.RUNNING
    ucos.lifecycle.stop("uc_full")
    assert ucos.get("uc_full").state == CapabilityState.STOPPED


def test_ucos_with_dependency_chain(ucos):
    ucos.register(CapabilityDefinition(id="uc_dep_root", name="DepRoot"))
    ucos.register(CapabilityDefinition(id="uc_dep_mid", name="DepMid",
                                         dependencies=["uc_dep_root"]))
    ucos.register(CapabilityDefinition(id="uc_dep_leaf", name="DepLeaf",
                                         dependencies=["uc_dep_mid"]))
    order = ucos.boot_order()
    assert len(order) >= 3


def test_ucos_exported_names():
    from genesis.ucos import __all__
    assert "UCOS" in __all__
    assert "CapabilityDefinition" in __all__
    assert "CapabilityRegistry" in __all__
