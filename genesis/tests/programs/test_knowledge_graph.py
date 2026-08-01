"""
Tests for GENESIS-VIII Program 6: Planetary Knowledge Graph.
"""

import pytest
from genesis.knowledge_graph import (
    KEntity, KRelation, KnowledgeGraph, PlanetaryKnowledgeGraph,
    EntityDomain, GraphType,
)


class TestKnowledgeGraph:
    def test_add_entity(self):
        kg = KnowledgeGraph()
        e = KEntity(name="test-pkg", domain=EntityDomain.PACKAGE)
        kg.add_entity(e)
        assert kg.entity_count == 1

    def test_add_relation(self):
        kg = KnowledgeGraph()
        e1 = kg.add_entity(KEntity(name="a"))
        e2 = kg.add_entity(KEntity(name="b"))
        kg.relate(e1.id, e2.id, "depends_on")
        assert kg.relation_count == 1

    def test_find_entities(self):
        kg = KnowledgeGraph()
        kg.add_entity(KEntity(name="django", domain=EntityDomain.FRAMEWORK, tags=["python"]))
        kg.add_entity(KEntity(name="flask", domain=EntityDomain.FRAMEWORK, tags=["python"]))
        results = kg.find_entities(domain=EntityDomain.FRAMEWORK)
        assert len(results) == 2

    def test_neighbors_of(self):
        kg = KnowledgeGraph()
        e1 = kg.add_entity(KEntity(name="a"))
        e2 = kg.add_entity(KEntity(name="b"))
        kg.relate(e1.id, e2.id, "depends")
        neighbors = kg.neighbors_of(e1.id)
        assert len(neighbors) == 1

    def test_subgraph(self):
        kg = KnowledgeGraph()
        e = kg.add_entity(KEntity(name="test", graph_types=[GraphType.GLOBAL]))
        sg = kg.subgraph(GraphType.GLOBAL)
        assert len(sg["entities"]) == 1

    def test_query(self):
        kg = KnowledgeGraph()
        kg.add_entity(KEntity(name="my-package", domain=EntityDomain.PACKAGE))
        results = kg.query("MATCH (n:package) WHERE n.name CONTAINS 'my'")
        assert len(results) == 1

    def test_global_graph(self):
        kg = KnowledgeGraph()
        e = kg.add_entity(KEntity(name="global-entity"))
        gg = kg.global_graph()
        assert len(gg["entities"]) == 1


class TestPlanetaryKnowledgeGraph:
    def test_ingest_repository(self):
        pkg = PlanetaryKnowledgeGraph()
        pkg.ingest_repository("my-repo", "python", stars=100)
        assert pkg.global_graph.entity_count >= 1

    def test_ingest_package(self):
        pkg = PlanetaryKnowledgeGraph()
        pkg.ingest_package("requests", "pypi", "2.28.0")
        assert pkg.global_graph.entity_count >= 1

    def test_ingest_cve(self):
        pkg = PlanetaryKnowledgeGraph()
        pkg.ingest_cve("CVE-2024-1234", "high", ["dep1", "dep2"])
        assert pkg.global_graph.entity_count >= 3
        assert pkg.causal_graph.entity_count >= 1

    def test_multiple_graphs(self):
        pkg = PlanetaryKnowledgeGraph()
        pkg.ingest_entity(KEntity(name="e1", graph_types=[GraphType.GLOBAL, GraphType.SEMANTIC]))
        assert pkg.global_graph.entity_count == 1
        assert pkg.semantic_graph.entity_count == 1

    def test_summary(self):
        pkg = PlanetaryKnowledgeGraph()
        pkg.ingest_repository("r1", "go")
        s = pkg.summary()
        assert "graphs" in s
        assert "ingestion" in s
