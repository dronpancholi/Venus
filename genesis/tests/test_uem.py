"""Tests for GENESIS Ω² — Civilization I: Universal Engineering Model (UEM)."""

import json
import tempfile
from pathlib import Path

from genesis.ontology import (
    UniversalEntity, EntityDefinition, EntityAttribute, EntityRelation,
    EntityLifecycle, EntityRegistry, EvidenceLink, EntityCategory,
    build_default_ontology, build_uem_registry,
)


class TestUniversalEntity:
    def test_create_minimal(self):
        e = UniversalEntity(type_name="Test", identity="test.1")
        assert e.type_name == "Test"
        assert e.identity == "test.1"
        assert e.id == "Test:test.1"
        assert e.lifecycle == "created"
        assert e.version == 1

    def test_auto_timestamps(self):
        e = UniversalEntity(type_name="T", identity="x")
        assert e.created_at != ""
        assert e.updated_at != ""

    def test_fingerprint(self):
        a = UniversalEntity(type_name="M", identity="x", attributes={"a": 1})
        b = UniversalEntity(type_name="M", identity="x", attributes={"a": 1})
        assert a.fingerprint == b.fingerprint

    def test_fingerprint_changes(self):
        a = UniversalEntity(type_name="M", identity="x", attributes={"a": 1})
        b = UniversalEntity(type_name="M", identity="x", attributes={"a": 2})
        assert a.fingerprint != b.fingerprint

    def test_add_evidence(self):
        e = UniversalEntity(type_name="T", identity="ev_test")
        e.add_evidence("test_suite", "verification", 0.95)
        assert len(e.evidence) == 1
        assert e.evidence[0].type == "verification"
        assert e.evidence[0].confidence == 0.95

    def test_to_dict(self):
        e = UniversalEntity(type_name="T", identity="d", attributes={"x": 1})
        d = e.to_dict()
        assert d["id"] == "T:d"
        assert d["attributes"] == {"x": 1}
        assert d["type_name"] == "T"

    def test_version_increment(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="T"))
        e1 = UniversalEntity(type_name="T", identity="v", attributes={"val": 1})
        reg.add(e1)
        e2 = UniversalEntity(type_name="T", identity="v", attributes={"val": 2})
        reg.add(e2)
        assert reg.get("T", "v").version == 2


class TestEntityRegistry:
    def test_define_and_get_definition(self):
        reg = EntityRegistry()
        ed = reg.define(EntityDefinition(name="MyType"))
        assert reg.get_definition("MyType") is ed
        assert reg.get_definition("Missing") is None

    def test_all_definitions(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="A"))
        reg.define(EntityDefinition(name="B"))
        assert len(reg.all_definitions()) == 2

    def test_children_of(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="Base"))
        reg.define(EntityDefinition(name="Child", parent="Base"))
        children = reg.children_of("Base")
        assert len(children) == 1
        assert children[0].name == "Child"

    def test_add_and_get_instance(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="Module"))
        e = UniversalEntity(type_name="Module", identity="my_mod")
        errors = reg.add(e)
        assert errors == []
        assert reg.get("Module", "my_mod") is e
        assert reg.count() == 1

    def test_add_validates_required_attributes(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="T", attributes=[
            EntityAttribute("name", "string", required=True),
        ]))
        e = UniversalEntity(type_name="T", identity="bad", attributes={})
        errors = reg.add(e)
        assert len(errors) == 1
        assert "name" in errors[0]

    def test_find_by_type(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="M"))
        reg.add(UniversalEntity(type_name="M", identity="a"))
        reg.add(UniversalEntity(type_name="M", identity="b"))
        assert len(reg.find(type_name="M")) == 2

    def test_find_by_attr(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="M"))
        reg.add(UniversalEntity(type_name="M", identity="a", attributes={"lang": "py"}))
        reg.add(UniversalEntity(type_name="M", identity="b", attributes={"lang": "rs"}))
        assert len(reg.find(lang="py")) == 1

    def test_types_count(self):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="M"))
        reg.define(EntityDefinition(name="C"))
        reg.add(UniversalEntity(type_name="M", identity="a"))
        reg.add(UniversalEntity(type_name="C", identity="b"))
        reg.add(UniversalEntity(type_name="C", identity="c"))
        assert reg.types_count() == {"M": 1, "C": 2}

    def test_save_load(self, tmp_path):
        reg = EntityRegistry()
        reg.define(EntityDefinition(name="T"))
        reg.add(UniversalEntity(type_name="T", identity="x"))
        p = tmp_path / "uem.json"
        reg.save(str(p))
        data = json.loads(p.read_text())
        assert data["summary"]["instances"] == 1
        assert data["summary"]["definitions"] == 1


class TestBuildDefaultOntology:
    def test_standard_entities(self):
        onto = build_default_ontology()
        assert onto.get("Repository") is not None
        assert onto.get("Module") is not None
        assert onto.get("Class") is not None
        assert onto.get("Specification") is not None  # Ω² addition

    def test_entity_count(self):
        onto = build_default_ontology()
        names = sorted(onto.all_definitions(), key=lambda x: x.name)
        assert len(names) >= 29

    def test_build_uem_registry(self):
        reg = build_uem_registry()
        assert len(reg.all_definitions()) >= 29


class TestEngineeringOntologyCompat:
    def test_backward_compatible(self):
        from genesis.ontology import EngineeringOntology
        onto = EngineeringOntology()
        onto = onto.build_default()
        ed = onto.get("Module")
        assert ed is not None
        assert ed.name == "Module"
        assert onto.children_of("Package") is not None
        assert onto.get("NonExistent") is None

    def test_summary(self):
        onto = build_default_ontology()
        s = onto.summary()
        assert s["total_entities"] >= 29
        assert "entity_names" in s


class TestEvidenceLink:
    def test_create(self):
        ev = EvidenceLink(source="test", type="verification", confidence=0.9)
        assert ev.source == "test"
        assert ev.type == "verification"
        assert ev.confidence == 0.9
        assert ev.timestamp > 0

    def test_auto_timestamp(self):
        ev = EvidenceLink(source="s", type="t")
        assert ev.timestamp > 0
