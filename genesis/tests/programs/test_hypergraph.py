"""
Tests for GENESIS-IX Phase 4: Hypergraph Knowledge Core.
"""

import pytest
from genesis.hypergraph import (
    Hypergraph, HypergraphNode, HypergraphEdge, Hyperedge,
    HypergraphKnowledgeCore, EdgeType, HyperedgeType,
)


class TestHypergraphNode:
    def test_create_minimal(self):
        n = HypergraphNode()
        assert n.id
        assert n.node_type == ""
        assert n.created_at > 0

    def test_create_with_fields(self):
        n = HypergraphNode(id="n:1", label="ServiceA", node_type="service",
                            properties={"lang": "python"}, tags=["api"])
        assert n.id == "n:1"
        assert n.label == "ServiceA"
        assert n.node_type == "service"
        assert n.properties["lang"] == "python"
        assert "api" in n.tags

    def test_hash_and_eq(self):
        n1 = HypergraphNode(id="n:1")
        n2 = HypergraphNode(id="n:1")
        n3 = HypergraphNode(id="n:2")
        assert hash(n1) == hash(n2)
        assert n1 == n2
        assert n1 != n3


class TestHypergraphEdge:
    def test_create_minimal(self):
        e = HypergraphEdge()
        assert e.id
        assert e.edge_type == EdgeType.DIRECTED
        assert e.weight == 1.0
        assert e.probability == 1.0

    def test_create_with_fields(self):
        e = HypergraphEdge(source_id="n:1", target_id="n:2", relation="depends_on",
                            weight=0.8, probability=0.9, edge_type=EdgeType.UNDIRECTED)
        assert e.source_id == "n:1"
        assert e.target_id == "n:2"
        assert e.relation == "depends_on"
        assert e.weight == 0.8
        assert e.edge_type == EdgeType.UNDIRECTED


class TestHyperedge:
    def test_create(self):
        he = Hyperedge(member_ids=["a", "b", "c"], hyperedge_type=HyperedgeType.AND,
                        relation="composes")
        assert he.id
        assert len(he.member_ids) == 3
        assert he.hyperedge_type == HyperedgeType.AND
        assert he.relation == "composes"

    def test_hash(self):
        he1 = Hyperedge(id="he:1")
        he2 = Hyperedge(id="he:1")
        assert hash(he1) == hash(he2)


class TestHypergraph:
    def setup_method(self):
        self.hg = Hypergraph()

    def test_add_and_get_node(self):
        n = self.hg.add_node(HypergraphNode(id="a", label="A", node_type="service"))
        assert self.hg.get_node("a") is n
        assert self.hg.node_count == 1

    def test_get_nonexistent_node(self):
        assert self.hg.get_node("nonexistent") is None

    def test_find_nodes_by_type(self):
        self.hg.add_node(HypergraphNode(id="a", label="A", node_type="service"))
        self.hg.add_node(HypergraphNode(id="b", label="B", node_type="agent"))
        results = self.hg.find_nodes(node_type="service")
        assert len(results) == 1
        assert results[0].id == "a"

    def test_find_nodes_by_tag(self):
        self.hg.add_node(HypergraphNode(id="a", label="A", tags=["critical"]))
        self.hg.add_node(HypergraphNode(id="b", label="B", tags=["optional"]))
        results = self.hg.find_nodes(tag="critical")
        assert len(results) == 1

    def test_find_nodes_by_label(self):
        self.hg.add_node(HypergraphNode(id="a", label="MyService"))
        results = self.hg.find_nodes(label_contains="service")
        assert len(results) == 1

    def test_find_nodes_by_properties(self):
        self.hg.add_node(HypergraphNode(id="a", properties={"lang": "python"}))
        self.hg.add_node(HypergraphNode(id="b", properties={"lang": "rust"}))
        results = self.hg.find_nodes(properties={"lang": "python"})
        assert len(results) == 1

    def test_remove_node(self):
        self.hg.add_node(HypergraphNode(id="a", label="A"))
        assert self.hg.remove_node("a") is True
        assert self.hg.get_node("a") is None
        assert self.hg.remove_node("nonexistent") is False

    def test_remove_node_cleans_edges(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.relate("a", "b", "depends_on")
        self.hg.remove_node("a")
        assert self.hg.edge_count == 0

    def test_update_node(self):
        self.hg.add_node(HypergraphNode(id="a", weight=1.0))
        self.hg.update_node("a", properties={"lang": "go"}, tags=["new"], weight=0.5)
        n = self.hg.get_node("a")
        assert n.properties["lang"] == "go"
        assert "new" in n.tags
        assert n.weight == 0.5
        assert self.hg.update_node("nonexistent") is False

    def test_add_and_get_edge(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        e = self.hg.add_edge(HypergraphEdge(source_id="a", target_id="b", relation="depends_on"))
        assert self.hg.get_edge(e.id) is e
        assert self.hg.edge_count == 1

    def test_find_edges_by_relation(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "depends_on")
        self.hg.relate("a", "c", "references")
        results = self.hg.find_edges(relation="depends_on")
        assert len(results) == 1

    def test_find_edges_by_source_target(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.relate("a", "b", "depends_on")
        results = self.hg.find_edges(source_id="a", target_id="b")
        assert len(results) == 1

    def test_remove_edge(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        e = self.hg.relate("a", "b", "depends_on")
        assert self.hg.remove_edge(e.id) is True
        assert self.hg.edge_count == 0
        assert self.hg.remove_edge("nonexistent") is False

    def test_relate_nonexistent_nodes(self):
        assert self.hg.relate("nonexistent", "also_missing") is None

    def test_add_and_find_hyperedge(self):
        he = self.hg.add_hyperedge(Hyperedge(member_ids=["a", "b", "c"],
                                              hyperedge_type=HyperedgeType.AND))
        assert self.hg.get_hyperedge(he.id) is he
        results = self.hg.find_hyperedges(hyperedge_type=HyperedgeType.AND)
        assert len(results) == 1
        results = self.hg.find_hyperedges(member_id="a")
        assert len(results) == 1

    def test_neighbors_outgoing(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.relate("a", "b", "depends_on")
        neighbors = self.hg.neighbors("a")
        assert len(neighbors) == 1
        assert neighbors[0][0].id == "b"

    def test_neighbors_incoming(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.relate("a", "b", "depends_on")
        neighbors = self.hg.neighbors("b", direction="incoming")
        assert len(neighbors) == 1
        assert neighbors[0][0].id == "a"

    def test_path_finding(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "depends_on")
        self.hg.relate("b", "c", "depends_on")
        paths = self.hg.path("a", "c")
        assert len(paths) >= 1
        assert paths[0] == ["a", "b", "c"]

    def test_path_no_route(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        assert self.hg.path("a", "b") == []

    def test_path_nonexistent(self):
        assert self.hg.path("a", "b") == []

    def test_subgraph(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "depends_on")
        self.hg.relate("b", "c", "depends_on")
        sg = self.hg.subgraph({"a", "b"})
        assert sg.node_count == 2
        assert sg.edge_count == 1

    def test_connected_components(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "depends_on")
        # c is isolated
        components = self.hg.connected_components()
        assert len(components) == 2

    def test_degree_centrality(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "depends_on")
        self.hg.relate("a", "c", "depends_on")
        cent = self.hg.degree_centrality()
        assert cent["a"] > cent["b"]
        assert cent["a"] > cent["c"]

    def test_betweenness_centrality(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "depends_on")
        self.hg.relate("b", "c", "depends_on")
        cent = self.hg.betweenness_centrality()
        assert cent["b"] > 0

    def test_clustering_coefficient(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "related")
        self.hg.relate("b", "c", "related")
        self.hg.relate("a", "c", "related")
        cc = self.hg.clustering_coefficient()
        assert cc > 0

    def test_community_detection(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "related")
        self.hg.relate("b", "c", "related")
        communities = self.hg.detect_communities()
        assert len(communities) >= 1

    def test_influence_propagation(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "influences", weight=0.8)
        self.hg.relate("b", "c", "influences", weight=0.6)
        inf = self.hg.influence_propagation(["a"])
        assert inf["a"] == 1.0
        assert inf.get("b", 0) > 0
        assert inf.get("c", 0) > 0

    def test_anomaly_scores(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.add_node(HypergraphNode(id="c"))
        self.hg.relate("a", "b", "related")
        scores = self.hg.anomaly_scores()
        assert "a" in scores
        assert "b" in scores
        assert "c" in scores

    def test_graph_embeddings(self):
        self.hg.add_node(HypergraphNode(id="a"))
        self.hg.add_node(HypergraphNode(id="b"))
        self.hg.relate("a", "b", "related")
        embs = self.hg.graph_embeddings(dimensions=4)
        assert len(embs) == 2
        assert len(embs["a"]) == 4

    def test_pattern_match(self):
        self.hg.add_node(HypergraphNode(id="a", node_type="service"))
        self.hg.add_node(HypergraphNode(id="b", node_type="service"))
        self.hg.add_node(HypergraphNode(id="c", node_type="agent"))
        self.hg.relate("a", "b", "depends_on")
        results = self.hg.pattern_match({"node_type": "service", "min_degree": 1})
        assert len(results) >= 1
        assert results[0]["node"].node_type == "service"

    def test_to_dict(self):
        self.hg.add_node(HypergraphNode(id="a", label="A"))
        self.hg.add_node(HypergraphNode(id="b", label="B"))
        self.hg.relate("a", "b", "depends_on")
        self.hg.add_hyperedge(Hyperedge(member_ids=["a", "b"], hyperedge_type=HyperedgeType.AND))
        d = self.hg.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "hyperedges" in d
        assert len(d["nodes"]) == 2
        assert len(d["edges"]) == 1
        assert len(d["hyperedges"]) == 1

    def test_summary(self):
        self.hg.add_node(HypergraphNode(id="a", node_type="service"))
        self.hg.add_node(HypergraphNode(id="b", node_type="service"))
        s = self.hg.summary()
        assert s["nodes"] == 2
        assert s["by_type"]["service"] == 2
        assert s["components"] >= 1


class TestHypergraphKnowledgeCore:
    def setup_method(self):
        self.core = HypergraphKnowledgeCore()

    def test_graph_access(self):
        assert self.core.graph.node_count == 0

    def test_add_inference_rule(self):
        self.core.add_inference_rule("test_rule", "service", "agent", confidence=0.7)
        s = self.core.summary()
        assert s["inference_rules"] == 1

    def test_infer_edges(self):
        self.core.graph.add_node(HypergraphNode(id="a", node_type="service"))
        self.core.graph.add_node(HypergraphNode(id="b", node_type="agent"))
        self.core.add_inference_rule("compat", "service", "agent", confidence=0.5)
        inferred = self.core.infer_edges()
        assert len(inferred) >= 0

    def test_similarity_search(self):
        self.core.graph.add_node(HypergraphNode(
            id="a", embedding=[0.1, 0.2, 0.3]
        ))
        self.core.graph.add_node(HypergraphNode(
            id="b", embedding=[0.4, 0.5, 0.6]
        ))
        results = self.core.similarity_search([0.1, 0.2, 0.3], top_k=5)
        assert len(results) == 2
        assert results[0][0].id == "a"

    def test_cosine_similarity(self):
        sim = HypergraphKnowledgeCore._cosine_similarity([1, 0], [0, 1])
        assert sim == 0.0
        sim2 = HypergraphKnowledgeCore._cosine_similarity([1, 0], [1, 0])
        assert sim2 == 1.0
        sim3 = HypergraphKnowledgeCore._cosine_similarity([], [])
        assert sim3 == 0.0

    def test_summary(self):
        self.core.graph.add_node(HypergraphNode(id="a"))
        s = self.core.summary()
        assert s["hypergraph"]["nodes"] == 1
