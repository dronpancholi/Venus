"""
Tests for the World Model — Phase 2 of GENESIS IX.
"""

import os
import tempfile
import time

import pytest

from genesis.brain import EngineeringBrain, BrainEntity
from genesis.civilization.world_model import (
    WorldModel, BayesianPredictor, Prediction, Observation,
)


class TestBayesianPredictor:
    def test_create(self):
        p = BayesianPredictor()
        assert p.summary()["variables_tracked"] == 0
        assert p.summary()["total_observations"] == 0

    def test_set_prior(self):
        p = BayesianPredictor()
        p.set_prior("test_ratio", 3.0, 3.0, 0.5, 0.15)
        assert "test_ratio" in p.priors

    def test_add_observation(self):
        p = BayesianPredictor()
        p.add_observation("test_ratio", 0.6, source="genome:1")
        assert len(p.observations) == 1
        assert p.observations[0].variable == "test_ratio"
        assert p.observations[0].value == 0.6

    def test_predict_beta(self):
        p = BayesianPredictor()
        p.set_prior("test_ratio", 3.0, 3.0, 0.5, 0.15)
        for v in [0.6, 0.7, 0.65, 0.72, 0.68]:
            p.add_observation("test_ratio", v)
        pred = p.predict("test_ratio")
        assert pred is not None
        assert pred.variable == "test_ratio"
        assert pred.current_value == 0.68
        assert 0 < pred.predicted_value < 1
        assert 0 < pred.confidence <= 1
        assert pred.lower_bound < pred.predicted_value < pred.upper_bound

    def test_predict_gaussian(self):
        p = BayesianPredictor()
        p.set_prior("complexity_ratio", 2.0, 2.0, 0.5, 0.2)
        for v in [0.4, 0.45, 0.5, 0.48, 0.52]:
            p.add_observation("complexity_ratio", v)
        pred = p.predict("complexity_ratio")
        assert pred is not None
        assert pred.variable == "complexity_ratio"

    def test_predict_nonexistent(self):
        p = BayesianPredictor()
        pred = p.predict("nonexistent")
        assert pred is None

    def test_predict_no_observations(self):
        p = BayesianPredictor()
        p.set_prior("some_var", 2.0, 2.0)
        pred = p.predict("some_var")
        assert pred is None  # No observations

    def test_predict_all(self):
        p = BayesianPredictor()
        p.set_prior("test_ratio", 3.0, 3.0)
        p.set_prior("complexity_ratio", 2.0, 2.0)
        p.add_observation("test_ratio", 0.6)
        p.add_observation("test_ratio", 0.7)
        p.add_observation("complexity_ratio", 0.5)

        predictions = p.predict_all()
        assert len(predictions) == 2

    def test_predict_all_empty(self):
        p = BayesianPredictor()
        assert p.predict_all() == []

    def test_summary(self):
        p = BayesianPredictor()
        p.set_prior("test_ratio", 3.0, 3.0)
        p.add_observation("test_ratio", 0.6)
        s = p.summary()
        assert s["variables_tracked"] == 1
        assert s["total_observations"] == 1

    def test_multiple_variables(self):
        p = BayesianPredictor()
        for var in ("var_a", "var_b", "var_c"):
            p.set_prior(var, 2.0, 2.0)
        for var in ("var_a", "var_b", "var_a", "var_c", "var_b"):
            p.add_observation(var, 0.5)
        assert p.summary()["variables_tracked"] == 3
        assert p.summary()["total_observations"] == 5


class TestWorldModel:
    @pytest.fixture
    def model(self):
        with tempfile.TemporaryDirectory() as td:
            brain = EngineeringBrain(storage_path=os.path.join(td, "wm.db"))
            yield WorldModel(brain=brain)

    def test_create(self, model):
        s = model.summary()
        assert s["total_entities"] == 0
        assert s["predictor"]["variables_tracked"] == 0

    def test_register_repository(self, model):
        repo = model.register_repository(
            "my-project", url="https://github.com/user/my-project",
            language="Python", description="A test project",
            organization="test-org", stars=100, forks=20,
        )
        assert repo.entity_type == "repository"
        assert repo.label == "my-project"
        assert repo.attributes["url"] == "https://github.com/user/my-project"
        assert repo.attributes["language"] == "Python"
        assert repo.attributes["stars"] == 100

        found = model.find_repositories()
        assert len(found) == 1

    def test_register_repository_with_topics(self, model):
        repo = model.register_repository("repo-1", topics=["web", "api", "python"])
        assert repo.tags == ["web", "api", "python"]

    def test_register_organization(self, model):
        org = model.register_organization(
            "MyCorp", description="A software company",
            location="San Francisco", website="https://mycorp.com",
            member_count=500,
        )
        assert org.entity_type == "organization"
        assert org.label == "MyCorp"
        assert org.attributes["member_count"] == 500
        assert org.attributes["location"] == "San Francisco"

    def test_register_developer(self, model):
        dev = model.register_developer(
            "Alice", email="alice@example.com", github="alice-dev",
            organization="MyCorp", role="senior-engineer",
            languages=["Python", "Go"], expertise=["distributed-systems", "ml"],
        )
        assert dev.entity_type == "developer"
        assert dev.label == "Alice"
        assert dev.attributes["github"] == "alice-dev"
        assert dev.attributes["languages"] == ["Python", "Go"]

    def test_register_language(self, model):
        lang = model.register_language(
            "Rust", version="1.70", paradigm="multi-paradigm",
            typing="static", first_appeared=2010,
        )
        assert lang.entity_type == "language"
        assert lang.label == "Rust"
        assert lang.attributes["paradigm"] == "multi-paradigm"
        assert lang.attributes["typing"] == "static"

    def test_register_framework(self, model):
        fw = model.register_framework(
            "React", language="JavaScript", category="frontend",
            version="18.2", website="https://react.dev",
        )
        assert fw.entity_type == "framework"
        assert fw.label == "React"
        assert fw.attributes["category"] == "frontend"

    def test_register_library(self, model):
        lib = model.register_library(
            "pandas", language="Python", version="2.0",
            description="Data analysis library",
            package_url="https://pypi.org/project/pandas",
        )
        assert lib.entity_type == "library"
        assert lib.label == "pandas"
        assert lib.attributes["package_url"] is not None

    def test_register_cloud_provider(self, model):
        cloud = model.register_cloud_provider(
            "AWS", services=["EC2", "S3", "Lambda"],
            regions=30, market_share=0.32,
        )
        assert cloud.entity_type == "cloud_provider"
        assert cloud.attributes["regions"] == 30
        assert "S3" in cloud.attributes["services"]

    def test_register_standard(self, model):
        std = model.register_standard(
            "OpenAPI 3.1", organization="OpenAPI Initiative",
            version="3.1", category="api-specification",
            description="OpenAPI Specification v3.1",
        )
        assert std.entity_type == "standard"
        assert std.attributes["organization"] == "OpenAPI Initiative"

    def test_register_security_advisory(self, model):
        adv = model.register_security_advisory(
            "Log4Shell", cve_id="CVE-2021-44228",
            severity="critical", package="log4j",
            description="Remote code execution in Log4j",
        )
        assert adv.entity_type == "security_advisory"
        assert adv.attributes["cve_id"] == "CVE-2021-44228"
        assert adv.confidence.overall == 0.95

    def test_register_security_advisory_low_severity(self, model):
        adv = model.register_security_advisory("Minor Issue", severity="low")
        assert adv.confidence.overall == 0.5

    def test_find_by_ecosystem(self, model):
        model.register_language("Python")
        model.register_language("Rust")
        model.register_framework("React", language="JavaScript")

        langs = model.find_by_ecosystem("language")
        assert len(langs) == 2

        frameworks = model.find_by_ecosystem("framework")
        assert len(frameworks) == 1

    def test_count_by_ecosystem(self, model):
        model.register_language("Python")
        model.register_language("Go")
        model.register_framework("Django", language="Python")
        model.register_repository("repo-1")

        counts = model.count_by_ecosystem()
        assert counts.get("language", 0) == 2
        assert counts.get("framework", 0) == 1
        assert counts.get("repository", 0) == 1

    def test_relationships(self, model):
        org = model.register_organization("AcmeCorp")
        dev = model.register_developer("Bob", organization="AcmeCorp")
        repo = model.register_repository("acme-app", organization="AcmeCorp")

        model.relate_developer_org(dev.brain_id, org.brain_id)
        model.relate_repository_org(repo.brain_id, org.brain_id)

        dev_rels = model.brain.relationships(dev.brain_id)
        assert any(r.target_id == org.brain_id and r.relation == "member_of" for r in dev_rels)

        repo_rels = model.brain.relationships(repo.brain_id)
        assert any(r.target_id == org.brain_id and r.relation == "owned_by" for r in repo_rels)

    def test_evolve_entity(self, model):
        repo = model.register_repository("growing-project", stars=10)
        assert repo.attributes["stars"] == 10

        evolved = model.evolve(repo.brain_id, "stars", 50, reason="popularity growth")
        assert evolved is not None
        assert evolved.attributes["stars"] == 50
        assert evolved.version > 1

    def test_evolve_nonexistent(self, model):
        result = model.evolve("nonexistent", "stars", 100)
        assert result is None

    def test_snapshot(self, model):
        model.register_language("Python")
        model.register_repository("test-repo", stars=5)
        model.predictor.add_observation("test_ratio", 0.5)

        snap = model.snapshot()
        assert "timestamp" in snap
        assert len(snap["entities"]) == 2
        assert len(snap["predictions"]) >= 0

    def test_ecosystem_health(self, model):
        model.register_language("Python")
        model.register_language("Go")
        model.register_repository("repo-1")
        model.predictor.add_observation("test_ratio", 0.7)
        model.predictor.add_observation("test_ratio", 0.8)

        health = model.ecosystem_health()
        assert health["total_entities"] == 3
        assert health["average_confidence"] > 0
        assert "ecosystem_distribution" in health
        assert "predictions" in health

    def test_ecosystem_health_empty(self, model):
        health = model.ecosystem_health()
        assert health["total_entities"] == 0

    def test_observe_genome(self, model):
        class MockGene:
            def __init__(self):
                self.dependencies = ["dep1", "dep2"]
                self.name = "gene1"
                self.gene_id = "g1"

        class MockGenome:
            def __init__(self):
                self.id = "genome:1"
                self.traits = {"test_ratio": 0.6, "avg_complexity": 0.4}
                self.all_genes = [MockGene()]

        model.observe_genome(MockGenome())

        pred = model.predict_evolution("test_ratio")
        assert pred is not None
        assert pred.current_value == 0.6

    def test_predict_all(self, model):
        model.predictor.add_observation("test_ratio", 0.6)
        model.predictor.add_observation("complexity_ratio", 0.4)
        model.predictor.set_prior("test_ratio", 3.0, 3.0)
        model.predictor.set_prior("complexity_ratio", 2.0, 2.0)

        predictions = model.predict_all()
        assert len(predictions) >= 2

    def test_find_repositories_filtered(self, model):
        model.register_repository("py-proj", language="Python", organization="org-a")
        model.register_repository("go-proj", language="Go", organization="org-b")
        model.register_repository("py-other", language="Python", organization="org-b")

        py_repos = model.find_repositories(language="Python")
        assert len(py_repos) == 2

        org_b_repos = model.find_repositories(org="org-b")
        assert len(org_b_repos) == 2

        py_org_b = model.find_repositories(language="Python", org="org-b")
        assert len(py_org_b) == 1
        assert py_org_b[0].label == "py-other"

    def test_full_ecosystem_scenario(self, model):
        org = model.register_organization("TechCorp", member_count=1000)
        dev = model.register_developer("Charlie", organization="TechCorp",
                                       languages=["Python", "TypeScript"])
        lang1 = model.register_language("Python", paradigm="multi", typing="dynamic")
        lang2 = model.register_language("TypeScript", paradigm="multi", typing="static")
        fw = model.register_framework("Django", language="Python", category="web")
        repo = model.register_repository("tech-app", language="Python",
                                          organization="TechCorp")
        cloud = model.register_cloud_provider("AWS", services=["EC2", "S3"])

        model.relate_developer_org(dev.brain_id, org.brain_id)
        model.relate_repository_org(repo.brain_id, org.brain_id)
        model.relate_repository_language(repo.brain_id, lang1.brain_id)
        model.relate_repository_framework(repo.brain_id, fw.brain_id)
        model.relate_deployed_on(repo.brain_id, cloud.brain_id)

        health = model.ecosystem_health()
        assert health["total_entities"] == 7
        assert health["ecosystem_distribution"]["organization"] == 1
        assert health["ecosystem_distribution"]["developer"] == 1
        assert health["ecosystem_distribution"]["language"] == 2

        counts = model.count_by_ecosystem()
        assert counts.get("repository") == 1
        assert counts.get("framework") == 1
        assert counts.get("cloud_provider") == 1

        snap = model.snapshot()
        assert len(snap["entities"]) == 7

    def test_summary(self, model):
        model.register_language("Python")
        s = model.summary()
        assert s["total_entities"] == 1
        assert "ecosystem" in s
        assert "predictor" in s
        assert "health" in s
