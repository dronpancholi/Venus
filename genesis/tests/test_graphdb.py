"""
test_graphdb.py — Tests for the Persistent Knowledge Graph (Phase 5).
"""

from __future__ import annotations

import gzip
import json
import os
import time
from pathlib import Path

from genesis.graphdb import (
    PersistentGraphDB, Node, Edge, GraphQueryBuilder,
)


# ── Node Tests ──

class TestNode:
    def test_defaults(self):
        n = Node(name="test-node")
        assert n.name == "test-node"
        assert n.node_type == "entity"
        assert n.uid != ""
        assert n.confidence == 1.0
        assert n.tags == []
        assert n.created_at > 0

    def test_auto_uid(self):
        n = Node(name="auto")
        assert n.uid != ""

    def test_custom_uid(self):
        n = Node(uid="custom:1", name="custom")
        assert n.uid == "custom:1"

    def test_to_dict(self):
        n = Node(uid="n:1", name="test", node_type="module",
                 attributes={"lang": "py"}, tags=["python"])
        d = n.to_dict()
        assert d["uid"] == "n:1"
        assert d["name"] == "test"
        assert d["node_type"] == "module"
        assert d["attributes"]["lang"] == "py"
        assert "python" in d["tags"]

    def test_from_dict_roundtrip(self):
        n = Node(uid="rt:1", name="roundtrip", node_type="service",
                 attributes={"port": 8080}, tags=["web"], confidence=0.9)
        d = n.to_dict()
        n2 = Node.from_dict(d)
        assert n2.uid == "rt:1"
        assert n2.name == "roundtrip"
        assert n2.node_type == "service"
        assert n2.attributes["port"] == 8080
        assert n2.tags == ["web"]
        assert n2.confidence == 0.9

    def test_to_json(self):
        n = Node(uid="j:1", name="json-test")
        j = n.to_json()
        assert isinstance(j, str)
        assert "json-test" in j


# ── Edge Tests ──

class TestEdge:
    def test_defaults(self):
        e = Edge(source_uid="a", target_uid="b")
        assert e.source_uid == "a"
        assert e.target_uid == "b"
        assert e.relation == "references"
        assert e.weight == 1.0
        assert e.id != ""

    def test_custom_id(self):
        e = Edge(id="e:1", source_uid="a", target_uid="b", relation="depends_on")
        assert e.id == "e:1"
        assert e.relation == "depends_on"

    def test_to_dict(self):
        e = Edge(id="e:1", source_uid="a", target_uid="b",
                 relation="depends_on", weight=0.8, confidence=0.95)
        d = e.to_dict()
        assert d["relation"] == "depends_on"
        assert d["weight"] == 0.8
        assert d["confidence"] == 0.95

    def test_from_dict_roundtrip(self):
        e = Edge(id="e:1", source_uid="a", target_uid="b",
                 relation="contains", weight=0.5, attributes={"scope": "all"})
        d = e.to_dict()
        e2 = Edge.from_dict(d)
        assert e2.id == "e:1"
        assert e2.source_uid == "a"
        assert e2.target_uid == "b"
        assert e2.relation == "contains"
        assert e2.attributes["scope"] == "all"


# ── PersistentGraphDB Tests ──

class TestPersistentGraphDB:
    def test_init(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "test.db"))
        assert db.node_count() == 0
        assert db.edge_count() == 0

    def test_add_and_get_node(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "nodes.db"))
        node = Node(name="test-node", node_type="test")
        db.add_node(node)
        retrieved = db.get_node(node.uid)
        assert retrieved is not None
        assert retrieved.name == "test-node"
        assert retrieved.node_type == "test"

    def test_add_node_with_attributes(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "attrs.db"))
        node = Node(name="attr-node", node_type="service",
                    attributes={"version": "2.0", "port": 8080},
                    tags=["web", "api"], confidence=0.95)
        db.add_node(node)
        retrieved = db.get_node(node.uid)
        assert retrieved.attributes["version"] == "2.0"
        assert retrieved.attributes["port"] == 8080
        assert "web" in retrieved.tags
        assert retrieved.confidence == 0.95

    def test_delete_node(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "delete.db"))
        node = Node(name="to-delete")
        db.add_node(node)
        assert db.node_count() == 1
        db.delete_node(node.uid)
        assert db.node_count() == 0
        assert db.get_node(node.uid) is None

    def test_add_and_get_edge(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "edges.db"))
        n1 = Node(uid="a:1", name="node-a")
        n2 = Node(uid="b:1", name="node-b")
        db.add_node(n1)
        db.add_node(n2)
        edge = Edge(source_uid="a:1", target_uid="b:1", relation="connects_to")
        db.add_edge(edge)
        retrieved = db.get_edge(edge.id)
        assert retrieved is not None
        assert retrieved.source_uid == "a:1"
        assert retrieved.target_uid == "b:1"
        assert retrieved.relation == "connects_to"

    def test_get_edges_by_source(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "edges2.db"))
        n1 = Node(uid="s:1", name="source")
        n2 = Node(uid="t:1", name="target")
        n3 = Node(uid="t:2", name="target2")
        db.add_node_bulk([n1, n2, n3])
        e1 = Edge(source_uid="s:1", target_uid="t:1", relation="depends")
        e2 = Edge(source_uid="s:1", target_uid="t:2", relation="depends")
        db.add_edge_bulk([e1, e2])
        edges = db.get_edges(source_uid="s:1")
        assert len(edges) == 2

    def test_delete_edge(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "delete_edge.db"))
        n1 = Node(uid="de:a", name="a")
        n2 = Node(uid="de:b", name="b")
        db.add_node_bulk([n1, n2])
        e = Edge(source_uid="de:a", target_uid="de:b")
        db.add_edge(e)
        assert db.edge_count() == 1
        db.delete_edge(e.id)
        assert db.edge_count() == 0

    def test_bulk_node_insert(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "bulk.db"))
        nodes = [Node(name=f"bulk-{i}", node_type="bulk-test") for i in range(100)]
        count = db.add_node_bulk(nodes)
        assert count == 100
        assert db.node_count() == 100

    def test_bulk_edge_insert(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "bulk_edge.db"))
        nodes = [Node(uid=f"bulk:n{i}", name=f"n{i}") for i in range(10)]
        db.add_node_bulk(nodes)
        edges = [
            Edge(source_uid=f"bulk:n{i}", target_uid=f"bulk:n{(i+1)%10}",
                 relation="chain")
            for i in range(10)
        ]
        db.add_edge_bulk(edges)
        assert db.edge_count() == 10

    def test_query_nodes(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "query.db"))
        db.add_node_bulk([
            Node(name="alpha", node_type="letter", tags=["greek"]),
            Node(name="beta", node_type="letter", tags=["greek"]),
            Node(name="one", node_type="number", tags=["english"]),
        ])
        results = db._query_nodes(node_type="letter")
        assert len(results) == 2

    def test_query_by_name(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "name_q.db"))
        db.add_node_bulk([
            Node(name="hello-world", node_type="test"),
            Node(name="goodbye-world", node_type="test"),
        ])
        results = db._query_nodes(name_contains="hello")
        assert len(results) == 1
        assert results[0].name == "hello-world"

    def test_query_by_tag(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "tag_q.db"))
        db.add_node(Node(name="tagged-a", node_type="t", tags=["important"]))
        db.add_node(Node(name="tagged-b", node_type="t", tags=["minor"]))
        results = db._query_nodes(tag="important")
        assert len(results) == 1

    def test_query_builder_fluent(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "fb.db"))
        db.add_node_bulk([
            Node(name="target", node_type="service", tags=["web"], confidence=0.9),
            Node(name="other", node_type="service", tags=["db"], confidence=0.5),
        ])
        results = (db.query()
                   .of_type("service")
                   .named("target")
                   .with_tag("web")
                   .with_confidence(0.8)
                   .execute())
        assert len(results) == 1
        assert results[0].name == "target"

    def test_query_builder_first(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "first.db"))
        db.add_node(Node(name="first-test", node_type="t"))
        assert db.query().named("first-test").first() is not None
        assert db.query().named("nonexistent").first() is None

    def test_query_builder_exists(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "exists.db"))
        db.add_node(Node(name="exists-test", node_type="t"))
        assert db.query().named("exists-test").exists()
        assert not db.query().named("nope").exists()

    def test_neighbors(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "neighbors.db"))
        n1 = Node(uid="n:1", name="center")
        n2 = Node(uid="n:2", name="neighbor")
        n3 = Node(uid="n:3", name="distant")
        db.add_node_bulk([n1, n2, n3])
        db.add_edge_bulk([
            Edge(source_uid="n:1", target_uid="n:2", relation="connects"),
            Edge(source_uid="n:2", target_uid="n:3", relation="connects"),
        ])
        neighbors = db.neighbors("n:1", max_depth=1)
        assert len(neighbors) >= 1
        assert any(n.uid == "n:2" for n in neighbors)

    def test_neighbors_depth(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "depth.db"))
        nodes = [Node(uid=f"d:{i}", name=f"node-{i}") for i in range(4)]
        db.add_node_bulk(nodes)
        edges = [Edge(source_uid=f"d:{i}", target_uid=f"d:{i+1}", relation="chain")
                 for i in range(3)]
        db.add_edge_bulk(edges)
        neighbors = db.neighbors("d:0", max_depth=2)
        assert len(neighbors) >= 2

    def test_bfs(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "bfs.db"))
        nodes = [Node(uid=f"bfs:{i}", name=f"n{i}") for i in range(5)]
        db.add_node_bulk(nodes)
        edges = [Edge(source_uid=f"bfs:{i}", target_uid=f"bfs:{i+1}", relation="next")
                 for i in range(4)]
        db.add_edge_bulk(edges)
        paths = db.bfs("bfs:0", target_uid="bfs:4")
        assert len(paths) >= 1
        assert paths[0][-1] == "bfs:4"

    def test_bfs_all_paths(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "bfs_all.db"))
        nodes = [Node(uid=f"ba:{i}", name=f"n{i}") for i in range(4)]
        db.add_node_bulk(nodes)
        db.add_edge_bulk([
            Edge(source_uid="ba:0", target_uid="ba:1", relation="edge"),
            Edge(source_uid="ba:1", target_uid="ba:2", relation="edge"),
            Edge(source_uid="ba:1", target_uid="ba:3", relation="edge"),
        ])
        paths = db.bfs("ba:0", target_uid="ba:2")
        assert len(paths) >= 1

    def test_degree_centrality(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "centrality.db"))
        db.add_node_bulk([
            Node(uid="hub", name="hub"),
            Node(uid="a", name="a"),
            Node(uid="b", name="b"),
        ])
        db.add_edge_bulk([
            Edge(source_uid="hub", target_uid="a", relation="connects"),
            Edge(source_uid="hub", target_uid="b", relation="connects"),
        ])
        cent = db.degree_centrality("hub")
        assert cent["out_degree"] == 2
        assert cent["total_degree"] == 2

    def test_clustering_coefficient(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "cluster.db"))
        db.add_node_bulk([
            Node(uid="t:1", name="center"),
            Node(uid="t:2", name="a"),
            Node(uid="t:3", name="b"),
        ])
        db.add_edge_bulk([
            Edge(source_uid="t:1", target_uid="t:2", relation="link"),
            Edge(source_uid="t:1", target_uid="t:3", relation="link"),
            Edge(source_uid="t:2", target_uid="t:3", relation="link"),
        ])
        cc = db.clustering_coefficient("t:1")
        assert cc > 0

    def test_density(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "density.db"))
        assert db.density() == 0.0
        nodes = [Node(uid=f"den:{i}", name=f"n{i}") for i in range(5)]
        db.add_node_bulk(nodes)
        edges = [Edge(source_uid=f"den:{i}", target_uid=f"den:{(i+1)%5}", relation="e")
                 for i in range(5)]
        db.add_edge_bulk(edges)
        assert db.density() > 0

    def test_statistics(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "stats.db"))
        db.add_node_bulk([
            Node(name="a", node_type="type_a", source="src1"),
            Node(name="b", node_type="type_b", source="src2"),
        ])
        stats = db.statistics()
        assert stats["node_count"] >= 2
        assert "type_a" in stats["type_distribution"]
        assert stats["db_size_bytes"] > 0

    def test_node_type_distribution(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "ntype.db"))
        db.add_node_bulk([
            Node(name="a", node_type="python"),
            Node(name="b", node_type="python"),
            Node(name="c", node_type="rust"),
        ])
        dist = db.node_type_distribution()
        assert dist.get("python") == 2
        assert dist.get("rust") == 1

    def test_relation_distribution(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "rtype.db"))
        n1 = Node(uid="r:a", name="a")
        n2 = Node(uid="r:b", name="b")
        n3 = Node(uid="r:c", name="c")
        db.add_node_bulk([n1, n2, n3])
        db.add_edge_bulk([
            Edge(source_uid="r:a", target_uid="r:b", relation="depends"),
            Edge(source_uid="r:a", target_uid="r:c", relation="depends"),
        ])
        dist = db.relation_distribution()
        assert dist.get("depends", 0) == 2

    def test_export_json(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "export.db"))
        n1 = Node(uid="e:1", name="export1")
        n2 = Node(uid="e:2", name="export2")
        db.add_node_bulk([n1, n2])
        e = Edge(source_uid="e:1", target_uid="e:2", relation="link")
        db.add_edge(e)
        out = str(tmp_path / "export.json")
        result = db.export_json(out)
        data = json.loads(Path(result).read_text())
        assert len(data["nodes"]) >= 2
        assert len(data["edges"]) >= 1

    def test_export_csv(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "csv_export.db"))
        n = Node(name="csv-node")
        db.add_node(n)
        nodes_path, edges_path = db.export_csv(str(tmp_path / "csv"))
        assert Path(nodes_path).exists()
        content = Path(nodes_path).read_text()
        assert "csv-node" in content

    def test_export_gexf(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "gexf_export.db"))
        n1 = Node(uid="gx:1", name="g1")
        n2 = Node(uid="gx:2", name="g2")
        db.add_node_bulk([n1, n2])
        db.add_edge(Edge(source_uid="gx:1", target_uid="gx:2", relation="link"))
        out = str(tmp_path / "graph.gexf")
        db.export_gexf(out)
        assert Path(out).exists()
        content = Path(out).read_text()
        assert "g1" in content
        assert "g2" in content

    def test_reconnect(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "reconnect.db"))
        db.add_node(Node(name="before-reconnect"))
        db.reconnect()
        assert db.node_count() >= 1

    def test_vacuum(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "vacuum.db"))
        n = Node(name="vacuum-test")
        db.add_node(n)
        db.delete_node(n.uid)
        db.vacuum()
        assert db.node_count() == 0

    def test_close(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "close.db"))
        db.add_node(Node(name="close-test"))
        db.close()
        # After close, should reconnect on next operation
        assert db.node_count() >= 1

    def test_compressed_export(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "compress.db"))
        n = Node(name="compress-test")
        db.add_node(n)
        out = str(tmp_path / "export.json")
        result = db.export_json(out, compress=True)
        assert result.endswith(".json.gz")
        assert Path(result).exists()
        with gzip.open(result, "rt") as f:
            data = json.loads(f.read())
            assert len(data["nodes"]) >= 1

    def test_large_bulk_insert(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "large.db"))
        nodes = [Node(uid=f"big:{i}", name=f"n{i}", node_type="bulk")
                 for i in range(1000)]
        db.add_node_bulk(nodes)
        assert db.node_count() == 1000
        edges = [Edge(source_uid=f"big:{i}", target_uid=f"big:{(i+1)%1000}",
                      relation="chain") for i in range(1000)]
        db.add_edge_bulk(edges)
        assert db.edge_count() == 1000

    def test_persistence_across_instances(self, tmp_path):
        db1 = PersistentGraphDB(db_path=str(tmp_path / "persist.db"))
        n = Node(uid="persist:1", name="persistent")
        db1.add_node(n)
        db1.close()
        db2 = PersistentGraphDB(db_path=str(tmp_path / "persist.db"))
        retrieved = db2.get_node("persist:1")
        assert retrieved is not None
        assert retrieved.name == "persistent"

    def test_query_with_limit_offset(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "limit.db"))
        nodes = [Node(name=f"lim-{i}", node_type="limit-test") for i in range(10)]
        db.add_node_bulk(nodes)
        first_5 = db._query_nodes(node_type="limit-test", limit=5)
        assert len(first_5) == 5

    def test_query_with_source(self, tmp_path):
        db = PersistentGraphDB(db_path=str(tmp_path / "source_q.db"))
        db.add_node_bulk([
            Node(name="from-github", node_type="t", source="github"),
            Node(name="from-pypi", node_type="t", source="pypi"),
        ])
        results = db._query_nodes(source="github")
        assert len(results) == 1
