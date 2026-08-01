"""Tests for UCOS CapabilityDependencyGraph."""

import pytest
from genesis.ucos.capability import Capability, CapabilityDefinition
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.graph import CapabilityDependencyGraph


@pytest.fixture
def graph():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="g_root", name="Root"))
    reg.register(CapabilityDefinition(id="g_a", name="A", dependencies=["g_root"]))
    reg.register(CapabilityDefinition(id="g_b", name="B", dependencies=["g_root"]))
    reg.register(CapabilityDefinition(id="g_c", name="C", dependencies=["g_a"]))
    reg.register(CapabilityDefinition(id="g_d", name="D", dependencies=["g_b", "g_c"]))
    g = CapabilityDependencyGraph(reg)
    return reg, g


def test_no_cycles(graph):
    reg, g = graph
    assert not g.has_cycles()


def test_cycle_detection():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="cyc_a", name="A", dependencies=["cyc_b"]))
    reg.register(CapabilityDefinition(id="cyc_b", name="B", dependencies=["cyc_a"]))
    g = CapabilityDependencyGraph(reg)
    assert g.has_cycles()
    assert len(g.cycles()) >= 1


def test_topsort(graph):
    reg, g = graph
    order = g.topsort()
    assert "g_root" in order
    assert "g_a" in order
    assert "g_d" in order
    assert order.index("g_root") < order.index("g_a")
    assert order.index("g_root") < order.index("g_b")
    assert order.index("g_a") < order.index("g_c")
    assert order.index("g_d") > order.index("g_root")


def test_fan_in_fan_out(graph):
    reg, g = graph
    assert g.fan_in("g_root") == 2
    assert g.fan_in("g_a") == 1
    assert g.fan_in("g_d") == 0
    assert g.fan_out("g_root") == 0
    assert g.fan_out("g_a") == 1
    assert g.fan_out("g_d") == 2


def test_degree(graph):
    reg, g = graph
    assert g.degree("g_root") == 2
    assert g.degree("g_a") == 2


def test_dependency_depth(graph):
    reg, g = graph
    assert g.dependency_depth("g_root") == 0
    assert g.dependency_depth("g_a") == 1
    assert g.dependency_depth("g_c") == 2
    assert g.dependency_depth("g_d") == 3


def test_critical_path(graph):
    reg, g = graph
    critical = g.critical_path()
    assert len(critical) >= 1
    assert "g_d" in critical


def test_dependency_subgraph(graph):
    reg, g = graph
    sub = g.dependency_subgraph("g_d")
    assert "g_d" in sub
    assert "g_c" in sub
    assert "g_a" in sub
    assert "g_root" in sub


def test_consumer_subgraph(graph):
    reg, g = graph
    consumers = g.consumer_subgraph("g_root")
    assert "g_a" in consumers
    assert "g_b" in consumers
    assert "g_c" in consumers
    assert "g_d" in consumers


def test_orphans():
    reg = CapabilityRegistry()
    g = CapabilityDependencyGraph(reg)
    reg.register(CapabilityDefinition(id="orph", name="Orphan"))
    assert len(g.orphan_capabilities()) == 1


def test_layer_assignment(graph):
    reg, g = graph
    layers = g.layer_assignment()
    assert layers["g_root"] == 0


def test_summary(graph):
    reg, g = graph
    summary = g.summary()
    assert summary["total_nodes"] == 5
    assert not summary["has_cycles"]
    assert summary["max_depth"] >= 2
