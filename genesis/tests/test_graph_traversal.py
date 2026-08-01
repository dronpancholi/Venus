import pytest

from genesis.graph_v2.core import GraphNode, GraphEdge, LayerType, UnifiedGraph
from genesis.graph_v2.traversal import (
    GraphTraversal, GraphSearch, GraphTransform,
    TraversalConfig, PathResult, SubgraphDef,
)


@pytest.fixture
def layered_graph() -> UnifiedGraph:
    g = UnifiedGraph()
    layer = g.create_layer("test", LayerType.STRUCTURAL)
    for nid, name in [("a", "alpha"), ("b", "beta"), ("c", "gamma"),
                       ("d", "delta"), ("e", "epsilon"), ("f", "phi")]:
        layer.add_node(GraphNode(id=nid, name=name, labels=["test"]))
    layer.add_edge(GraphEdge(source_id="a", target_id="b", edge_type="connects"))
    layer.add_edge(GraphEdge(source_id="b", target_id="c", edge_type="connects"))
    layer.add_edge(GraphEdge(source_id="c", target_id="d", edge_type="connects"))
    layer.add_edge(GraphEdge(source_id="a", target_id="e", edge_type="connects"))
    layer.add_edge(GraphEdge(source_id="e", target_id="f", edge_type="connects"))
    return g


class TestGraphSearch:
    def test_search_by_name(self):
        g = UnifiedGraph()
        layer = g.create_layer("test", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode(id="n1", name="database engine"))
        layer.add_node(GraphNode(id="n2", name="compiler frontend"))
        layer.add_node(GraphNode(id="n3", name="query optimizer"))
        searcher = GraphSearch(g)
        results = searcher.search("database")
        assert len(results) >= 1
        assert results[0].node.id == "n1"

    def test_search_multiple_terms(self):
        g = UnifiedGraph()
        layer = g.create_layer("test", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode(id="n1", name="database engine", node_type="engine"))
        layer.add_node(GraphNode(id="n2", name="compiler frontend", node_type="engine"))
        searcher = GraphSearch(g)
        results = searcher.search("engine")
        assert len(results) == 2

    def test_search_by_label(self):
        g = UnifiedGraph()
        layer = g.create_layer("test", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode(id="n1", name="svc_a", labels=["critical", "runtime"]))
        layer.add_node(GraphNode(id="n2", name="svc_b", labels=["optional"]))
        searcher = GraphSearch(g)
        results = searcher.search_by_label("critical")
        assert len(results) == 1
        assert results[0].id == "n1"

    def test_search_by_property(self):
        g = UnifiedGraph()
        layer = g.create_layer("test", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode(id="n1", name="svc_a", properties={"version": "2.0"}))
        layer.add_node(GraphNode(id="n2", name="svc_b", properties={"version": "1.0"}))
        searcher = GraphSearch(g)
        results = searcher.search_by_property("version", "2.0")
        assert len(results) == 1
        assert results[0].id == "n1"

    def test_search_limited_to_layer(self):
        g = UnifiedGraph()
        l1 = g.create_layer("layer_a", LayerType.STRUCTURAL)
        l2 = g.create_layer("layer_b", LayerType.SEMANTIC)
        l1.add_node(GraphNode(id="n1", name="target node"))
        l2.add_node(GraphNode(id="n2", name="target node"))
        searcher = GraphSearch(g)
        results = searcher.search("target", layer_name="layer_a")
        assert len(results) == 1
        assert results[0].node.id == "n1"

    def test_search_min_score_filter(self):
        g = UnifiedGraph()
        layer = g.create_layer("test", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode(id="n1", name="exact match engine"))
        searcher = GraphSearch(g)
        results = searcher.search("exact match engine", min_score=5.0)
        assert len(results) == 1


class TestGraphTraversal:
    def test_bfs_traversal(self, layered_graph):
        trav = GraphTraversal(layered_graph)
        result = trav.bfs("a")
        ids = [n.id for n in result]
        assert "a" in ids
        assert "b" in ids
        assert "e" in ids

    def test_bfs_max_depth(self, layered_graph):
        trav = GraphTraversal(layered_graph)
        result = trav.bfs("a", TraversalConfig(max_depth=1))
        assert len(result) == 3
        ids = [n.id for n in result]
        assert "c" not in ids

    def test_dfs_traversal(self, layered_graph):
        trav = GraphTraversal(layered_graph)
        result = trav.dfs("a")
        assert len(result) >= 3

    def test_shortest_path(self, layered_graph):
        trav = GraphTraversal(layered_graph)
        path = trav.shortest_path("a", "d")
        assert path is not None
        assert path.hops == 3
        ids = [n.id for n in path.nodes]
        assert ids == ["a", "b", "c", "d"]

    def test_shortest_path_same_node(self, layered_graph):
        trav = GraphTraversal(layered_graph)
        path = trav.shortest_path("a", "a")
        assert path is not None
        assert path.hops == 0

    def test_shortest_path_no_path(self, layered_graph):
        g = UnifiedGraph()
        layer = g.create_layer("test", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(id="x"))
        layer.add_node(GraphNode(id="y"))
        trav = GraphTraversal(g)
        path = trav.shortest_path("x", "y")
        assert path is None

    def test_all_paths(self, layered_graph):
        trav = GraphTraversal(layered_graph)
        paths = trav.all_paths("a", "d")
        assert len(paths) >= 1
        assert all(p.hops > 0 for p in paths)

    def test_bfs_with_edge_type_filter(self, layered_graph):
        g = UnifiedGraph()
        layer = g.create_layer("test", LayerType.STRUCTURAL)
        layer.add_node(GraphNode(id="a", name="a"))
        layer.add_node(GraphNode(id="b", name="b"))
        layer.add_node(GraphNode(id="c", name="c"))
        layer.add_edge(GraphEdge(source_id="a", target_id="b", edge_type="connects"))
        layer.add_edge(GraphEdge(source_id="a", target_id="c", edge_type="ignored"))
        trav = GraphTraversal(g)
        result = trav.bfs("a", TraversalConfig(edge_types=["connects"]))
        ids = [n.id for n in result]
        assert "b" in ids
        assert "c" not in ids


class TestGraphTransform:
    def test_extract_subgraph(self, layered_graph):
        transformer = GraphTransform(layered_graph)
        sub = transformer.extract_subgraph(SubgraphDef(root_id="a", depth=2))
        sub_layer = sub.get_layer("sub_test")
        assert sub_layer is not None
        assert sub_layer.get_node("a") is not None
        assert sub_layer.get_node("b") is not None
        assert sub_layer.get_node("c") is not None
        assert sub_layer.get_node("e") is not None

    def test_project_by_type(self):
        g = UnifiedGraph()
        layer = g.create_layer("main", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode(id="n1", name="engine", node_type="engine"))
        layer.add_node(GraphNode(id="n2", name="config", node_type="config"))
        transformer = GraphTransform(g)
        proj = transformer.project("main", node_type="engine")
        proj_layer = proj.get_layer("proj_main")
        assert proj_layer.get_node("n1") is not None
        assert proj_layer.get_node("n2") is None

    def test_project_by_labels(self):
        g = UnifiedGraph()
        layer = g.create_layer("main", LayerType.KNOWLEDGE)
        layer.add_node(GraphNode(id="n1", name="critical_svc", labels=["critical"]))
        layer.add_node(GraphNode(id="n2", name="normal_svc", labels=["normal"]))
        transformer = GraphTransform(g)
        proj = transformer.project("main", labels=["critical"])
        proj_layer = proj.get_layer("proj_main")
        assert proj_layer.get_node("n1") is not None
        assert proj_layer.get_node("n2") is None

    def test_diff_added_nodes(self):
        g1 = UnifiedGraph()
        g1.create_layer("main", LayerType.STRUCTURAL)
        g2 = UnifiedGraph()
        l2 = g2.create_layer("main", LayerType.STRUCTURAL)
        l2.add_node(GraphNode(id="new_node", name="new"))
        transformer = GraphTransform(g1)
        diff = transformer.diff(g2)
        assert len(diff.added_nodes) == 1
        assert diff.added_nodes[0].id == "new_node"

    def test_diff_removed_nodes(self):
        g1 = UnifiedGraph()
        l1 = g1.create_layer("main", LayerType.STRUCTURAL)
        l1.add_node(GraphNode(id="gone", name="gone"))
        g2 = UnifiedGraph()
        g2.create_layer("main", LayerType.STRUCTURAL)
        transformer = GraphTransform(g1)
        diff = transformer.diff(g2)
        assert len(diff.removed_nodes) == 1
        assert diff.removed_nodes[0].id == "gone"

    def test_diff_modified_nodes(self):
        g1 = UnifiedGraph()
        l1 = g1.create_layer("main", LayerType.STRUCTURAL)
        l1.add_node(GraphNode(id="n1", name="svc", properties={"ver": "1.0"}))
        g2 = UnifiedGraph()
        l2 = g2.create_layer("main", LayerType.STRUCTURAL)
        l2.add_node(GraphNode(id="n1", name="svc", properties={"ver": "2.0"}))
        transformer = GraphTransform(g1)
        diff = transformer.diff(g2)
        assert len(diff.modified_nodes) == 1
        assert "ver" in diff.modified_nodes[0][2]

    def test_merge_combines_disjoint_layers(self):
        g1 = UnifiedGraph()
        l1 = g1.create_layer("layer_a", LayerType.STRUCTURAL)
        l1.add_node(GraphNode(id="n1", name="from_a"))
        g2 = UnifiedGraph()
        l2 = g2.create_layer("layer_b", LayerType.SEMANTIC)
        l2.add_node(GraphNode(id="n2", name="from_b"))
        transformer = GraphTransform(g1)
        merged = transformer.merge(g2)
        assert merged.get_layer("layer_a") is not None
        assert merged.get_layer("layer_b") is not None
        assert merged.get_layer("layer_a").get_node("n1") is not None
        assert merged.get_layer("layer_b").get_node("n2") is not None

    def test_merge_keeps_source_in_conflict(self):
        g1 = UnifiedGraph()
        l1 = g1.create_layer("main", LayerType.STRUCTURAL)
        l1.add_node(GraphNode(id="n1", name="from_source", properties={"val": 1}))
        g2 = UnifiedGraph()
        l2 = g2.create_layer("main", LayerType.STRUCTURAL)
        l2.add_node(GraphNode(id="n1", name="from_other", properties={"val": 2}))
        transformer = GraphTransform(g1)
        merged = transformer.merge(g2, conflict_resolution="source_wins")
        merged_node = merged.get_layer("main").get_node("n1")
        assert merged_node.name == "from_source"
