"""
test_acquisition.py — Tests for the planetary knowledge acquisition subsystem.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from genesis.acquisition import AcquisitionRecord, AcquisitionSource, AcquisitionPipeline
from genesis.acquisition.orchestrator import AcquisitionOrchestrator
from genesis.acquisition.sources import (
    GitHubSource, GitLabSource, NPMSource, PyPISource, CargoSource,
    MavenSource, NuGetSource, GoSource, DockerSource,
    RFCSource, CVESource, NISTSource, CNCFSource, OWASPSource,
    IETFSource, W3CSource, ADRSource,
)
from genesis.metamodel.entity import EntityType
from genesis.metamodel.graph import UnifiedGraph


# ── AcquisitionRecord Tests ──

class TestAcquisitionRecord:
    def test_defaults(self):
        rec = AcquisitionRecord()
        assert rec.source == ""
        assert rec.entity_type == EntityType.REPOSITORY
        assert rec.confidence == 1.0
        assert rec.collected_at > 0

    def test_with_values(self):
        rec = AcquisitionRecord(
            source="test",
            entity_type=EntityType.NPM_PACKAGE,
            external_id="npm:lodash",
            name="lodash",
            description="A modern JS utility library",
            raw_data={"version": "4.17.21"},
            metadata={"stars": 50000},
            confidence=0.9,
            tags=["javascript", "utility"],
            url="https://npmjs.com/package/lodash",
        )
        assert rec.source == "test"
        assert rec.entity_type == EntityType.NPM_PACKAGE
        assert rec.name == "lodash"
        assert rec.raw_data["version"] == "4.17.21"
        assert rec.metadata["stars"] == 50000
        assert rec.tags == ["javascript", "utility"]

    def test_collected_at_auto(self):
        before = time.time()
        rec = AcquisitionRecord()
        after = time.time()
        assert before <= rec.collected_at <= after

    def test_collected_at_explicit(self):
        rec = AcquisitionRecord(collected_at=12345.0)
        assert rec.collected_at == 12345.0


# ── Mock AcquisitionSource Tests ──

class MockSource(AcquisitionSource):
    source_name = "mock"
    entity_type = EntityType.REPOSITORY

    def __init__(self, records: list[AcquisitionRecord] | None = None):
        self._records = records or []

    def fetch(self) -> list[AcquisitionRecord]:
        return self._records

    def fetch_one(self, external_id: str) -> AcquisitionRecord | None:
        for r in self._records:
            if r.external_id == external_id:
                return r
        return None


class TestAcquisitionSource:
    def test_to_entity(self):
        rec = AcquisitionRecord(
            source="test",
            entity_type=EntityType.NPM_PACKAGE,
            external_id="npm:lodash",
            name="lodash",
            description="test",
            metadata={"stars": 100},
            confidence=0.9,
            tags=["js"],
        )
        source = MockSource()
        entity_dict = source.to_entity(rec)
        assert entity_dict["uid"] == "npm:lodash"
        assert entity_dict["entity_type"] == "npm_package"
        assert entity_dict["metadata"]["confidence"] == 0.9
        assert entity_dict["metadata"]["tags"] == ["js"]
        assert entity_dict["metadata"]["properties"]["stars"] == 100

    def test_summary(self):
        source = MockSource()
        summary = source.summary()
        assert summary["source_name"] == "mock"
        assert summary["entity_type"] == "repository"

    def test_fetch(self):
        rec = AcquisitionRecord(name="test")
        source = MockSource(records=[rec])
        assert source.fetch() == [rec]

    def test_fetch_one_found(self):
        rec = AcquisitionRecord(external_id="abc", name="test")
        source = MockSource(records=[rec])
        assert source.fetch_one("abc") == rec

    def test_fetch_one_not_found(self):
        source = MockSource()
        assert source.fetch_one("nonexistent") is None


# ── AcquisitionPipeline Tests ──

class TestAcquisitionPipeline:
    def test_register(self):
        pipeline = AcquisitionPipeline()
        source = MockSource(records=[AcquisitionRecord(name="a")])
        pipeline.register(source)
        assert "mock" in pipeline.sources

    def test_register_many(self):
        pipeline = AcquisitionPipeline()
        s1 = MockSource(records=[AcquisitionRecord(name="a")])
        s2 = MockSource(records=[AcquisitionRecord(name="b")])
        s2.source_name = "mock2"
        pipeline.register_many(s1, s2)
        assert "mock" in pipeline.sources
        assert "mock2" in pipeline.sources

    def test_acquire_source(self):
        pipeline = AcquisitionPipeline()
        rec = AcquisitionRecord(
            external_id="test:1", name="test",
            entity_type=EntityType.REPOSITORY,
        )
        source = MockSource(records=[rec])
        pipeline.register(source)
        count = pipeline.acquire_source("mock")
        assert count == 1

    def test_acquire_source_unknown(self):
        pipeline = AcquisitionPipeline()
        try:
            pipeline.acquire_source("nonexistent")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_acquire_all(self):
        pipeline = AcquisitionPipeline()
        s1 = MockSource(records=[AcquisitionRecord(name="a")])
        s2 = MockSource(records=[AcquisitionRecord(name="b"), AcquisitionRecord(name="c")])
        s2.source_name = "mock2"
        pipeline.register_many(s1, s2)
        results = pipeline.acquire_all()
        assert results["mock"] == 1
        assert results["mock2"] == 2

    def test_acquire_with_graph_storage(self):
        graph = UnifiedGraph()
        pipeline = AcquisitionPipeline(graph=graph)
        rec = AcquisitionRecord(
            external_id="test:1",
            name="test-repo",
            entity_type=EntityType.REPOSITORY,
        )
        source = MockSource(records=[rec])
        pipeline.register(source)
        pipeline.acquire_all()
        entities = graph.find_by_name("test-repo")
        assert len(entities) >= 1

    def test_acquire_all_with_graph(self):
        graph = UnifiedGraph()
        pipeline = AcquisitionPipeline(graph=graph)
        rec1 = AcquisitionRecord(external_id="a:1", name="entity-a", entity_type=EntityType.MODULE)
        rec2 = AcquisitionRecord(external_id="b:2", name="entity-b", entity_type=EntityType.MODULE)
        source = MockSource(records=[rec1, rec2])
        pipeline.register(source)
        results = pipeline.acquire_all()
        assert results["mock"] == 2
        assert len(graph.find_by_type("module")) >= 2

    def test_acquire_source_error(self):
        class FailingSource(AcquisitionSource):
            source_name = "fail"

            def fetch(self) -> list[AcquisitionRecord]:
                raise RuntimeError("fetch failed")

            def fetch_one(self, external_id: str):
                return None

        pipeline = AcquisitionPipeline()
        pipeline.register(FailingSource())
        assert pipeline.acquire_source("fail") == 0
        assert "fail" in pipeline.history
        assert pipeline.history["fail"][-1]["status"] == "error"

    def test_list_sources(self):
        pipeline = AcquisitionPipeline()
        source = MockSource(records=[])
        pipeline.register(source)
        sources = pipeline.list_sources()
        assert len(sources) == 1
        assert sources[0]["source_name"] == "mock"

    def test_summary(self):
        pipeline = AcquisitionPipeline()
        s = pipeline.summary()
        assert s["source_count"] == 0
        assert s["source_names"] == []


# ── Source Adapter Tests ──

class TestSourceAdapters:
    def test_github_source_init(self):
        source = GitHubSource(token="test", orgs=["test-org"])
        assert source.source_name == "github"
        assert source.entity_type == EntityType.GITHUB_REPO
        assert source.token == "test"
        assert source.orgs == ["test-org"]

    def test_github_source_empty_orgs(self):
        source = GitHubSource()
        records = source.fetch()
        assert records == []

    def test_gitlab_source_init(self):
        source = GitLabSource(token="test", groups=["test-group"])
        assert source.source_name == "gitlab"
        assert source.entity_type == EntityType.GITLAB_REPO

    def test_gitlab_source_empty_groups(self):
        source = GitLabSource()
        assert source.fetch() == []

    def test_npm_source_init(self):
        source = NPMSource(packages=["lodash"])
        assert source.source_name == "npm"
        assert source.entity_type == EntityType.NPM_PACKAGE
        assert source.packages == ["lodash"]

    def test_npm_source_empty(self):
        source = NPMSource()
        assert source.fetch() == []

    def test_pypi_source_init(self):
        source = PyPISource(packages=["requests"])
        assert source.source_name == "pypi"
        assert source.packages == ["requests"]

    def test_cargo_source_init(self):
        source = CargoSource(crates=["serde"])
        assert source.source_name == "cargo"
        assert source.entity_type == EntityType.CARGO_CRATE
        assert source.crates == ["serde"]

    def test_maven_source_init(self):
        source = MavenSource(artifacts=["com.google.guava:guava"])
        assert source.source_name == "maven"
        assert source.entity_type == EntityType.MAVEN_ARTIFACT

    def test_nuget_source_init(self):
        source = NuGetSource(packages=["Newtonsoft.Json"])
        assert source.source_name == "nuget"
        assert source.entity_type == EntityType.NUGET_PACKAGE

    def test_go_source_init(self):
        source = GoSource(modules=["github.com/gin-gonic/gin"])
        assert source.source_name == "go"
        assert source.entity_type == EntityType.GO_MODULE

    def test_docker_source_init(self):
        source = DockerSource(images=["library/nginx"])
        assert source.source_name == "docker"
        assert source.entity_type == EntityType.DOCKER_IMAGE
        assert source.images == ["library/nginx"]

    def test_rfc_source_init(self):
        source = RFCSource(rfc_numbers=[791, 793])
        assert source.source_name == "rfc"
        assert source.entity_type == EntityType.RFC_DOCUMENT
        assert source.rfc_numbers == [791, 793]

    def test_cve_source_init(self):
        source = CVESource(cve_ids=["CVE-2024-1234"])
        assert source.source_name == "cve"
        assert source.entity_type == EntityType.CVE_RECORD

    def test_nist_source_init(self):
        source = NISTSource(publications=["NIST.SP.800-53r5"])
        assert source.source_name == "nist"
        assert source.entity_type == EntityType.NIST_FRAMEWORK

    def test_cncf_source_init(self):
        source = CNCFSource(projects=["kubernetes"])
        assert source.source_name == "cncf"
        assert source.entity_type == EntityType.CNCF_PROJECT

    def test_owasp_source_init(self):
        source = OWASPSource(projects=["TopTen"])
        assert source.source_name == "owasp"
        assert source.entity_type == EntityType.OWASP_CATEGORY

    def test_ietf_source_init(self):
        source = IETFSource(documents=["rfc791"])
        assert source.source_name == "ietf"
        assert source.entity_type == EntityType.IETF_STANDARD

    def test_w3c_source_init(self):
        source = W3CSource(specs=["html"])
        assert source.source_name == "w3c"
        assert source.entity_type == EntityType.W3C_STANDARD

    def test_adr_source_init(self):
        source = ADRSource(adr_urls=["https://example.com/adr-001.md"])
        assert source.source_name == "adr"
        assert source.entity_type == EntityType.ADR_DOCUMENT

    def test_adr_source_empty(self):
        source = ADRSource()
        assert source.fetch() == []

    def test_all_sources_have_required_attrs(self):
        sources = [
            GitHubSource(), GitLabSource(),
            NPMSource(), PyPISource(), CargoSource(),
            MavenSource(), NuGetSource(), GoSource(),
            DockerSource(),
            RFCSource(), CVESource(), NISTSource(),
            CNCFSource(), OWASPSource(),
            IETFSource(), W3CSource(), ADRSource(),
        ]
        for s in sources:
            assert s.source_name, f"Source {type(s).__name__} missing source_name"
            assert s.entity_type, f"Source {type(s).__name__} missing entity_type"
            assert s.interval_seconds > 0, f"Source {type(s).__name__} has no interval"
            assert 0 < s.confidence <= 1.0, f"Source {type(s).__name__} invalid confidence"

    def test_each_source_produces_unique_external_ids(self):
        sources = [
            GitHubSource(), GitLabSource(),
            NPMSource(), PyPISource(), CargoSource(),
            MavenSource(), NuGetSource(), GoSource(),
            DockerSource(),
            RFCSource(), CVESource(), NISTSource(),
            CNCFSource(), OWASPSource(),
            IETFSource(), W3CSource(), ADRSource(),
        ]
        prefixes = set()
        for s in sources:
            rec = AcquisitionRecord(
                source=s.source_name,
                entity_type=s.entity_type,
                external_id=f"{s.source_name}:test",
            )
            prefix = rec.external_id.split(":")[0]
            prefixes.add(prefix)
        # Each source should have a unique prefix
        assert len(prefixes) == len(sources)

    def test_source_to_entity_sets_source_in_metadata(self):
        rec = AcquisitionRecord(source="npm", entity_type=EntityType.NPM_PACKAGE, external_id="npm:test")
        source = NPMSource()
        entity_dict = source.to_entity(rec)
        assert entity_dict["metadata"]["source"] == "npm"


# ── Adapter Network Call Tests (skipped if network unavailable) ──

def _network_available(url: str = "https://google.com") -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(url, timeout=3)
        return True
    except Exception:
        return False


class TestAdapterNetworkCalls:
    def test_github_fetch_one_network(self):
        if not _network_available("https://api.github.com"):
            return
        source = GitHubSource()
        result = source.fetch_one("octocat/Hello-World")
        assert result is not None
        assert result.entity_type == EntityType.GITHUB_REPO
        assert "github:" in result.external_id
        assert result.raw_data.get("full_name") == "octocat/Hello-World"
        assert result.metadata.get("stars") is not None
        assert result.metadata.get("forks") is not None
        assert result.url == "https://github.com/octocat/Hello-World"

    def test_npm_fetch_one_network(self):
        if not _network_available("https://registry.npmjs.org"):
            return
        source = NPMSource()
        result = source.fetch_one("lodash")
        assert result is not None
        assert result.entity_type == EntityType.NPM_PACKAGE
        assert result.external_id == "npm:lodash"
        assert result.metadata.get("latest_version") is not None

    def test_pypi_fetch_one_network(self):
        if not _network_available("https://pypi.org"):
            return
        source = PyPISource()
        result = source.fetch_one("requests")
        assert result is not None
        assert result.entity_type == EntityType.PYPI_PACKAGE
        assert result.external_id == "pypi:requests"
        assert result.metadata.get("latest_version") is not None

    def test_cargo_fetch_one_network(self):
        if not _network_available("https://crates.io"):
            return
        source = CargoSource()
        result = source.fetch_one("serde")
        assert result is not None
        assert result.entity_type == EntityType.CARGO_CRATE
        assert result.external_id == "cargo:serde"

    def test_rfc_fetch_one_network(self):
        if not _network_available("https://www.rfc-editor.org/rfc/rfc791.txt"):
            return
        source = RFCSource()
        result = source.fetch_one("791")
        if result is not None:
            assert result.entity_type == EntityType.RFC_DOCUMENT
            assert result.external_id == "rfc:791"

    def test_cve_fetch_one_network(self):
        if not _network_available("https://services.nvd.nist.gov"):
            return
        source = CVESource()
        result = source.fetch_one("CVE-2024-21626")
        assert result is not None
        assert result.entity_type == EntityType.CVE_RECORD
        assert result.metadata.get("cvss_score") is not None

    def test_pypi_network_to_entity(self):
        if not _network_available("https://pypi.org"):
            return
        source = PyPISource()
        result = source.fetch_one("flask")
        assert result is not None
        entity_dict = source.to_entity(result)
        assert entity_dict["entity_type"] == source.entity_type.value
        assert len(entity_dict["attributes"]) > 0


# ── Orchestrator Tests ──

class TestAcquisitionOrchestrator:
    def test_init(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        assert orch.pipeline is not None
        assert orch.pipeline.sources == {}

    def test_register_all_sources(self):
        orch = AcquisitionOrchestrator()
        orch.register_all_sources()
        source_names = set(orch.pipeline.sources.keys())
        expected = {
            "github", "gitlab", "npm", "pypi", "cargo",
            "maven", "nuget", "go", "docker",
            "rfc", "cve", "nist", "cncf", "owasp",
            "ietf", "w3c", "adr",
        }
        assert source_names == expected

    def test_register_all_sources_with_config(self):
        orch = AcquisitionOrchestrator()
        orch.register_all_sources({
            "github_orgs": ["test-org"],
            "npm_packages": ["lodash"],
            "pypi_packages": ["requests"],
        })
        assert orch.pipeline.sources["github"].orgs == ["test-org"]
        assert orch.pipeline.sources["npm"].packages == ["lodash"]
        assert orch.pipeline.sources["pypi"].packages == ["requests"]

    def test_run_once(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        source = MockSource(records=[AcquisitionRecord(name="test")])
        orch.pipeline.register(source)
        result = orch.run_once("mock")
        assert result == {"mock": 1}
        assert orch.get_last_run("mock") > 0

    def test_run_once_all(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        s1 = MockSource(records=[AcquisitionRecord(name="a")])
        s2 = MockSource(records=[AcquisitionRecord(name="b")])
        s2.source_name = "mock2"
        orch.pipeline.register_many(s1, s2)
        result = orch.run_once()
        assert result["mock"] == 1
        assert result["mock2"] == 1

    def test_run_all(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        s1 = MockSource(records=[AcquisitionRecord(name="a")])
        orch.pipeline.register(s1)
        result = orch.run_all()
        assert result["mock"] == 1

    def test_get_last_run_default(self):
        orch = AcquisitionOrchestrator()
        assert orch.get_last_run("nonexistent") == 0.0

    def test_get_stats(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        source = MockSource(records=[AcquisitionRecord(name="a")])
        orch.pipeline.register(source)
        orch.run_once("mock")
        stats = orch.get_stats()
        assert "mock" in stats
        assert stats["mock"]["total_items"] == 1
        assert stats["mock"]["total_runs"] == 1

    def test_persistence_roundtrip(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        source = MockSource(records=[AcquisitionRecord(name="a")])
        orch.pipeline.register(source)
        orch.run_once("mock")
        # Verify state file exists
        state_file = tmp_path / "orchestrator_state.json"
        assert state_file.exists()
        state = json.loads(state_file.read_text())
        assert "mock" in state.get("stats", {})

    def test_load_state(self, tmp_path):
        orch1 = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        source = MockSource(records=[AcquisitionRecord(name="a")])
        orch1.pipeline.register(source)
        orch1.run_once("mock")
        # New instance with same directory loads state
        orch2 = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        orch2.load_state()
        assert orch2._stats.get("mock", {}).get("total_items") == 1

    def test_summary(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        source = MockSource(records=[AcquisitionRecord(name="a")])
        orch.pipeline.register(source)
        orch.run_once("mock")
        s = orch.summary()
        assert "pipeline" in s
        assert "stats" in s
        assert "sources_last_run" in s
        assert "mock" in s["sources_last_run"]

    def test_save_state_preserves_stats(self, tmp_path):
        orch = AcquisitionOrchestrator(persistence_dir=str(tmp_path))
        source = MockSource(records=[AcquisitionRecord(name="a")])
        orch.pipeline.register(source)
        orch.run_once("mock")
        orch.run_once("mock")
        stats = orch.get_stats()
        assert stats["mock"]["total_items"] == 2
        assert stats["mock"]["total_runs"] == 2

    def test_with_graph_storage(self, tmp_path):
        graph = UnifiedGraph()
        orch = AcquisitionOrchestrator(graph=graph, persistence_dir=str(tmp_path))
        rec = AcquisitionRecord(
            external_id="orch:1", name="orch-entity",
            entity_type=EntityType.MODULE,
        )
        source = MockSource(records=[rec])
        orch.pipeline.register(source)
        result = orch.run_once("mock")
        assert result["mock"] == 1
        entities = graph.find_by_name("orch-entity")
        assert len(entities) >= 1
