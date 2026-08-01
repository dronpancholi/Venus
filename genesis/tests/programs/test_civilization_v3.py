"""
Tests for GENESIS-IX Phase 9: Software Civilization V3.
"""

import pytest
from genesis.civilization_v3 import (
    InstituteType, ResearchProject, Institute, SoftwareCivilizationV3,
)


class TestResearchProject:
    def test_create(self):
        rp = ResearchProject(name="Study AI safety",
                              description="Research on safe AI deployment",
                              institute_id="inst:1")
        assert rp.id
        assert rp.status == "proposed"
        assert rp.created_at > 0


class TestInstitute:
    def test_create(self):
        inst = Institute(name="AI Lab", institute_type=InstituteType.AI,
                          capabilities=["ml", "nlp"])
        assert inst.id
        assert inst.name == "AI Lab"
        assert inst.institute_type == InstituteType.AI
        assert len(inst.capabilities) == 2


class TestSoftwareCivilizationV3:
    def setup_method(self):
        self.civ = SoftwareCivilizationV3()

    def test_18_institutes_created(self):
        assert len(self.civ._institutes) == 18
        s = self.civ.summary()
        assert s["institutes"] == 18

    def test_get_institute(self):
        inst = next(iter(self.civ._institutes.values()))
        assert self.civ.get_institute(inst.id) is inst
        assert self.civ.get_institute("nonexistent") is None

    def test_find_institutes_by_type(self):
        results = self.civ.find_institutes(institute_type=InstituteType.AI)
        assert len(results) == 1
        assert results[0].institute_type == InstituteType.AI

    def test_find_institutes_by_capability(self):
        results = self.civ.find_institutes(capability="reasoning")
        assert len(results) >= 1

    def test_add_member(self):
        inst = next(iter(self.civ._institutes.values()))
        assert self.civ.add_member(inst.id, "agent:1") is True
        assert "agent:1" in inst.members
        assert self.civ.add_member(inst.id, "agent:1") is False

    def test_add_member_nonexistent(self):
        assert self.civ.add_member("nonexistent", "agent:1") is False

    def test_start_research(self):
        inst = next(iter(self.civ._institutes.values()))
        proj = self.civ.start_research(inst.id, "Test Project", "Testing")
        assert proj.id
        assert proj.status == "active"
        assert proj.institute_id == inst.id
        assert proj.id in inst.projects
        assert inst.metrics.get("projects", 0) >= 1

    def test_start_research_nonexistent(self):
        proj = self.civ.start_research("nonexistent", "Orphan", "No inst")
        assert proj.id

    def test_publish_paper(self):
        inst = next(iter(self.civ._institutes.values()))
        proj = self.civ.start_research(inst.id, "Project", "Desc")
        pub_id = self.civ.publish_paper(proj.id, "Paper Title", "Findings")
        assert pub_id
        assert pub_id in inst.publications
        assert proj.status == "published"

    def test_propose_standard(self):
        inst = next(iter(self.civ._institutes.values()))
        std_id = self.civ.propose_standard(inst.id, "STD-001", "A standard")
        assert std_id
        assert std_id in inst.standards
        assert inst.metrics.get("standards", 0) >= 1

    def test_governance_action(self):
        inst = next(iter(self.civ._institutes.values()))
        record = self.civ.governance_action("approve_budget", inst.id, "Budget for Q3")
        assert record["approved"] is True
        assert record["action"] == "approve_budget"
        assert len(self.civ._governance_log) == 1

    def test_research_cycle(self):
        projects = self.civ.research_cycle()
        assert len(projects) == 18
        assert all(p.status == "published" for p in projects)

    def test_hierarchy(self):
        h = self.civ.hierarchy()
        assert len(h["roots"]) == 18

    def test_summary(self):
        s = self.civ.summary()
        assert s["institutes"] == 18
        assert s["projects"] == 0
        assert s["publications"] == 0
        assert s["standards"] == 0
        assert s["governance_actions"] == 0

    def test_summary_after_actions(self):
        inst = self.civ.find_institutes(institute_type=InstituteType.AI)[0]
        self.civ.start_research(inst.id, "P1", "D1")
        self.civ.propose_standard(inst.id, "S1", "D1")
        self.civ.governance_action("act", inst.id, "desc")
        s = self.civ.summary()
        assert s["projects"] >= 1
        assert s["standards"] >= 1
        assert s["governance_actions"] >= 1
