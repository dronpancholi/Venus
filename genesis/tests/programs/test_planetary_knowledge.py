"""
Tests for GENESIS-IX Phase 7: Planetary Engineering Knowledge.
"""

import pytest
from genesis.planetary_knowledge import (
    SourceDomain, Artifact, SourceConnector, PlanetaryKnowledgeEngine,
)


class TestArtifact:
    def test_create_minimal(self):
        a = Artifact()
        assert a.id
        assert a.domain == SourceDomain.GITHUB
        assert a.confidence == 1.0
        assert a.discovered_at > 0

    def test_create_with_fields(self):
        a = Artifact(name="pandas", domain=SourceDomain.PYPI, version="2.0.0",
                      description="Data analysis library", tags=["python", "data"])
        assert a.name == "pandas"
        assert a.domain == SourceDomain.PYPI
        assert a.version == "2.0.0"


class TestSourceConnector:
    def setup_method(self):
        self.conn = SourceConnector(SourceDomain.PYPI)

    def test_ingest_and_get(self):
        a = Artifact(name="requests", domain=SourceDomain.PYPI)
        self.conn.ingest(a)
        assert self.conn.get(a.id) is a
        assert self.conn.count == 1

    def test_find_by_name(self):
        self.conn.ingest(Artifact(name="flask"))
        self.conn.ingest(Artifact(name="django"))
        results = self.conn.find(name_contains="flask")
        assert len(results) == 1

    def test_find_by_tag(self):
        a = Artifact(name="torch", tags=["ml", "deep_learning"])
        self.conn.ingest(a)
        results = self.conn.find(tag="ml")
        assert len(results) == 1

    def test_dependencies_of(self):
        a = Artifact(name="web_framework", dependencies=["router", "templates"])
        self.conn.ingest(a)
        deps = self.conn.dependencies_of(a.id)
        assert len(deps) == 0  # dependent artifacts not ingested

    def test_no_dependencies(self):
        a = Artifact(name="standalone", dependencies=[])
        self.conn.ingest(a)
        assert self.conn.dependencies_of(a.id) == []


class TestPlanetaryKnowledgeEngine:
    def setup_method(self):
        self.engine = PlanetaryKnowledgeEngine()

    def test_connector_access(self):
        c = self.engine.connector(SourceDomain.PYPI)
        assert c.domain == SourceDomain.PYPI

    def test_ingest(self):
        a = Artifact(name="numpy", domain=SourceDomain.PYPI, tags=["ml"])
        self.engine.ingest(a)
        assert self.engine.connector(SourceDomain.PYPI).count == 1

    def test_ingest_tracks_dependencies(self):
        a = Artifact(name="fastapi", domain=SourceDomain.PYPI,
                      dependencies=["starlette", "pydantic"])
        self.engine.ingest(a)
        chains = self.engine.dependency_chain(a.id)
        assert len(chains) >= 1

    def test_query_by_name(self):
        self.engine.ingest(Artifact(name="react", domain=SourceDomain.NPM))
        results = self.engine.query(name_contains="react")
        assert len(results) == 1

    def test_query_by_domain(self):
        self.engine.ingest(Artifact(name="tensorflow", domain=SourceDomain.TENSORFLOW))
        results = self.engine.query(domain=SourceDomain.TENSORFLOW)
        assert len(results) == 1

    def test_query_by_tag(self):
        self.engine.ingest(Artifact(name="redis", tags=["database"]))
        results = self.engine.query(tag="database")
        assert len(results) == 1

    def test_dependency_chain_max_depth(self):
        a = Artifact(name="app", dependencies=["dep1"])
        self.engine.ingest(a)
        chains = self.engine.dependency_chain(a.id, max_depth=1)
        assert len(chains) >= 1

    def test_dependency_chain_no_deps(self):
        a = Artifact(name="leaf")
        self.engine.ingest(a)
        chains = self.engine.dependency_chain(a.id)
        assert len(chains) == 1
        assert chains[0] == [a.id]

    def test_ecosystem_overview(self):
        self.engine.ingest(Artifact(name="pkg1", domain=SourceDomain.PYPI))
        overview = self.engine.ecosystem_overview()
        assert overview["total_artifacts"] == 1
        assert overview["by_domain"]["pypi"] == 1

    def test_summary(self):
        s = self.engine.summary()
        assert s["total_artifacts"] == 0
        assert "by_domain" in s

    def test_all_domains_have_connectors(self):
        for d in SourceDomain:
            c = self.engine.connector(d)
            assert c.domain == d
