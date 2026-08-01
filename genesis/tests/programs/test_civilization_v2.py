"""
Tests for GENESIS-VIII Program 8: Software Civilization V2.
"""

import pytest
from genesis.civilization_v2 import (
    InstituteType, WorkProduct, Institute, Project, Deliverable,
    SoftwareCivilization,
)


class TestSoftwareCivilization:
    def test_create_institute(self):
        civ = SoftwareCivilization()
        inst = civ.create_institute("AI Lab", InstituteType.AI_INSTITUTE,
                                     capabilities=["ml", "nlp"],
                                     focus_areas=["deep_learning"])
        assert inst.name == "AI Lab"
        assert civ.get_institute(inst.id) is not None

    def test_institute_hierarchy(self):
        civ = SoftwareCivilization()
        parent = civ.create_institute("Parent", InstituteType.UNIVERSITY)
        child = civ.create_institute("Child", InstituteType.LABORATORY,
                                      parent_id=parent.id)
        hierarchy = civ.institute_hierarchy()
        assert len(hierarchy["roots"]) == 1
        assert len(hierarchy["roots"][0]["children"]) == 1

    def test_find_institutes(self):
        civ = SoftwareCivilization()
        civ.create_institute("AI", InstituteType.AI_INSTITUTE,
                              capabilities=["ml"], focus_areas=["ai"])
        civ.create_institute("Physics", InstituteType.PHYSICS_INSTITUTE,
                              capabilities=["physics"], focus_areas=["mechanics"])
        results = civ.find_institutes(capability="ml")
        assert len(results) == 1

    def test_add_member(self):
        civ = SoftwareCivilization()
        inst = civ.create_institute("Lab", InstituteType.LABORATORY)
        assert civ.add_member(inst.id, "agent:1") is True
        assert "agent:1" in inst.members

    def test_create_project(self):
        civ = SoftwareCivilization()
        inst = civ.create_institute("Lab", InstituteType.LABORATORY)
        proj = civ.create_project("Research", "Test project", inst.id)
        assert proj.name == "Research"

    def test_create_deliverable(self):
        civ = SoftwareCivilization()
        inst = civ.create_institute("Lab", InstituteType.LABORATORY)
        d = civ.create_deliverable("Report", WorkProduct.REPORT, inst.id)
        assert d.status == "draft"
        assert len(inst.work_history) == 1

    def test_publish_deliverable(self):
        civ = SoftwareCivilization()
        inst = civ.create_institute("Lab", InstituteType.LABORATORY)
        d = civ.create_deliverable("Report", WorkProduct.REPORT, inst.id)
        assert civ.publish_deliverable(d.id) is True
        assert d.status == "published"

    def test_work_cycle(self):
        civ = SoftwareCivilization()
        inst = civ.create_institute("Lab", InstituteType.LABORATORY,
                                     focus_areas=["physics"])
        deliverables = civ.work_cycle(capacity=10)
        assert len(deliverables) >= 1

    def test_summary(self):
        civ = SoftwareCivilization()
        civ.create_institute("Lab", InstituteType.LABORATORY)
        civ.create_institute("Uni", InstituteType.UNIVERSITY)
        s = civ.summary()
        assert s["institutes"]["total"] == 2
        assert s["institutes"]["by_type"]["laboratory"] == 1
