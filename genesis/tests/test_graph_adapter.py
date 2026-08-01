"""
Test GraphAdapter — universal graph convergence.
"""
from genesis.graph_v2.adapter import (
    GraphAdapter,
    _KnowledgeGraphEngineAdapter,
    _detect_adapter,
)
from genesis.graph_v2.core import UnifiedGraph, LayerType


class FakeLegacyGraph:
    """Simulates a legacy graph with _nodes and _edges dicts."""
    def __init__(self):
        self._nodes = {
            "n1": {"name": "Node1", "type": "test"},
            "n2": {"name": "Node2", "type": "test"},
        }
        self._edges = {
            "e1": {"source": "n1", "target": "n2", "type": "related"},
        }


def test_detect_adapter_generic():
    adapter = _detect_adapter(FakeLegacyGraph(), "test", LayerType.KNOWLEDGE)
    assert adapter is not None


def test_detect_knowledge_graph_engine():
    class FakeKnowledgeEngine:
        pass
    FakeKnowledgeEngine.__name__ = "KnowledgeGraphEngine"
    adapter = _detect_adapter(FakeKnowledgeEngine(), "kg", LayerType.KNOWLEDGE)
    assert isinstance(adapter, _KnowledgeGraphEngineAdapter)


def test_wrap_generic():
    g = UnifiedGraph()
    adapter = GraphAdapter(g)
    layer = adapter.wrap(FakeLegacyGraph(), "legacy", LayerType.STRUCTURAL)
    assert layer.name == "legacy"
    assert layer.node_count() >= 2


def test_wrap_knowledge_engine():
    g = UnifiedGraph()
    adapter = GraphAdapter(g)
    layer = adapter.wrap(FakeLegacyGraph(), "engine", LayerType.KNOWLEDGE)
    assert layer.name == "engine"


def test_sync_all():
    g = UnifiedGraph()
    adapter = GraphAdapter(g)
    adapter.wrap(FakeLegacyGraph(), "l1", LayerType.STRUCTURAL)
    adapter.wrap(FakeLegacyGraph(), "l2", LayerType.KNOWLEDGE)
    adapter.sync_all()
    assert len(adapter.list_adapters()) == 2


def test_list_adapters():
    g = UnifiedGraph()
    adapter = GraphAdapter(g)
    adapter.wrap(FakeLegacyGraph(), "test", LayerType.STRUCTURAL)
    result = adapter.list_adapters()
    assert "test" in result


def test_summary():
    g = UnifiedGraph()
    adapter = GraphAdapter(g)
    adapter.wrap(FakeLegacyGraph(), "test", LayerType.KNOWLEDGE)
    s = adapter.summary()
    assert s["total_adapters"] == 1
    assert "test" in s["adapters"]


def test_traversal_after_wrap():
    g = UnifiedGraph()
    adapter = GraphAdapter(g)
    adapter.wrap(FakeLegacyGraph(), "test", LayerType.KNOWLEDGE)
    results = list(adapter.traversal.bfs("n1"))
    assert len(results) > 0


def test_auto_detect_works():
    import re
    from genesis.graph_v2.adapter import _detect_adapter as da
    mapping = {
        "KnowledgeGraphEngine": "_KnowledgeGraphEngineAdapter",
        "KnowledgeGraph": "_KnowledgeGraphAdapter",
        "PlanetaryKnowledgeGraph": "_PlanetaryKnowledgeGraphAdapter",
        "HypergraphKnowledgeCore": "_HypergraphAdapter",
        "ExecutionGraph": "_ExecutionGraphAdapter",
        "UIRGraph": "_UIRGraphAdapter",
        "USIRGraph": "_USIRGraphAdapter",
        "WorkspaceDependencyGraph": "_WorkspaceGraphAdapter",
        "WorkspaceGraph": "_WorkspaceGraphAdapter",
        "BuildGraph": "_BuildGraphAdapter",
        "CapabilityDependencyGraph": "_CapabilityGraphAdapter",
        "WorldGraph": "_WorldGraphAdapter",
        "ObservatoryGraph": "_ObservatoryGraphAdapter",
        "PersistentTaskGraph": "_TaskGraphAdapter",
    }
    for cls_name, expected in mapping.items():
        class Fake:
            pass
        Fake.__name__ = cls_name
        adapter = da(Fake(), "test", LayerType.KNOWLEDGE)
        assert type(adapter).__name__ == expected, f"{cls_name} → {type(adapter).__name__} != {expected}"
