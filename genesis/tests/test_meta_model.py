"""Tests for GENESIS XIII Phase 4 — Engineering Meta Model."""

import json

import pytest
from genesis.meta_model import (
    MetaType, MetaTypeKind, MetaAttribute, MetaRelation,
    MetaInstance, MetaModel, MetaModelRepository,
    MetaModelRepositoryScanner, EvolutionTracker, EvolutionEvent,
    MetaModelEngine,
)


class TestMetaType:
    def test_create(self):
        mt = MetaType(name="Module", kind=MetaTypeKind.COMPOUND)
        assert mt.name == "Module"
        assert mt.kind == MetaTypeKind.COMPOUND

    def test_attribute_names(self):
        mt = MetaType(name="X", attributes=[
            MetaAttribute("a", "string"),
            MetaAttribute("b", "integer"),
        ])
        assert mt.attribute_names() == ["a", "b"]

    def test_relation_names(self):
        mt = MetaType(name="X", relations=[
            MetaRelation("imports", "Module", "many"),
        ])
        assert mt.relation_names() == ["imports"]


class TestMetaInstance:
    def test_create(self):
        inst = MetaInstance(type_name="Module", identity="foo.bar")
        assert inst.type_name == "Module"
        assert inst.identity == "foo.bar"
        assert inst.id == "Module:foo.bar"
        assert inst.version == 1

    def test_fingerprint(self):
        a = MetaInstance(type_name="M", identity="x", attributes={"a": 1})
        b = MetaInstance(type_name="M", identity="x", attributes={"a": 1})
        assert a.fingerprint() == b.fingerprint()

    def test_fingerprint_changes(self):
        a = MetaInstance(type_name="M", identity="x", attributes={"a": 1})
        b = MetaInstance(type_name="M", identity="x", attributes={"a": 2})
        assert a.fingerprint() != b.fingerprint()


class TestMetaModel:
    def test_define_and_get(self):
        mm = MetaModel()
        mt = mm.define(MetaType(name="Module"))
        assert mm.get("Module") is mt
        assert mm.get("Unknown") is None

    def test_all_types(self):
        mm = MetaModel()
        mm.define(MetaType(name="A"))
        mm.define(MetaType(name="B"))
        assert len(mm.all_types()) == 2

    def test_children_of(self):
        mm = MetaModel()
        mm.define(MetaType(name="Base"))
        mm.define(MetaType(name="Child", parent="Base"))
        assert len(mm.children_of("Base")) == 1
        assert mm.children_of("Base")[0].name == "Child"

    def test_validate_required_attribute(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module", attributes=[
            MetaAttribute("name", "string", required=True),
        ]))
        inst = MetaInstance(type_name="Module", identity="x", attributes={})
        errors = mm.validate_instance(inst)
        assert len(errors) == 1
        assert "name" in errors[0]

    def test_validate_type_mismatch(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module", attributes=[
            MetaAttribute("count", "integer", required=True),
        ]))
        inst = MetaInstance(type_name="Module", identity="x", attributes={"count": "not_int"})
        errors = mm.validate_instance(inst)
        assert len(errors) >= 1

    def test_validate_unknown_type(self):
        mm = MetaModel()
        inst = MetaInstance(type_name="Unknown", identity="x")
        errors = mm.validate_instance(inst)
        assert len(errors) == 1
        assert "Unknown" in errors[0]

    def test_validate_valid_instance(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module", attributes=[
            MetaAttribute("name", "string", required=True),
        ]))
        inst = MetaInstance(type_name="Module", identity="x", attributes={"name": "foo"})
        errors = mm.validate_instance(inst)
        assert errors == []


class TestMetaModelRepository:
    def test_add_and_get(self):
        mm = MetaModel()
        repo = MetaModelRepository(mm)
        inst = MetaInstance(type_name="Module", identity="foo")
        errors = repo.add(inst)
        # Should have errors because Module type not defined
        assert len(errors) > 0

    def test_add_with_defined_type(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module"))
        repo = MetaModelRepository(mm)
        inst = MetaInstance(type_name="Module", identity="foo")
        errors = repo.add(inst)
        assert errors == []
        assert repo.get("Module", "foo") is inst
        assert repo.count() == 1

    def test_add_updates_existing(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module"))
        repo = MetaModelRepository(mm)
        a = MetaInstance(type_name="Module", identity="foo", attributes={"v": 1})
        b = MetaInstance(type_name="Module", identity="foo", attributes={"v": 2})
        repo.add(a)
        repo.add(b)
        assert repo.count() == 1
        assert repo.get("Module", "foo").version == 2

    def test_find_by_type(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module"))
        repo = MetaModelRepository(mm)
        repo.add(MetaInstance(type_name="Module", identity="a"))
        repo.add(MetaInstance(type_name="Module", identity="b"))
        assert len(repo.find(type_name="Module")) == 2

    def test_find_by_attr(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module"))
        repo = MetaModelRepository(mm)
        repo.add(MetaInstance(type_name="Module", identity="a", attributes={"lang": "py"}))
        repo.add(MetaInstance(type_name="Module", identity="b", attributes={"lang": "rs"}))
        assert len(repo.find(lang="py")) == 1

    def test_types_count(self):
        mm = MetaModel()
        mm.define(MetaType(name="Module"))
        mm.define(MetaType(name="Class"))
        repo = MetaModelRepository(mm)
        repo.add(MetaInstance(type_name="Module", identity="a"))
        repo.add(MetaInstance(type_name="Class", identity="b"))
        repo.add(MetaInstance(type_name="Class", identity="c"))
        assert repo.types_count() == {"Module": 1, "Class": 2}


class TestEvolutionTracker:
    def test_record_and_replay(self):
        et = EvolutionTracker()
        et.record(EvolutionEvent(instance_id="m:x", event_type="created"))
        et.record(EvolutionEvent(instance_id="m:y", event_type="updated"))
        assert len(et.all_events()) == 2
        assert len(et.events_for("m:x")) == 1

    def test_by_type(self):
        et = EvolutionTracker()
        et.record(EvolutionEvent(instance_id="a", event_type="created"))
        et.record(EvolutionEvent(instance_id="b", event_type="created"))
        et.record(EvolutionEvent(instance_id="c", event_type="updated"))
        assert len(et.by_type("created")) == 2
        assert len(et.by_type("updated")) == 1

    def test_recent(self):
        et = EvolutionTracker()
        for i in range(10):
            et.record(EvolutionEvent(instance_id=str(i), event_type="created"))
        assert len(et.recent(5)) == 5


class TestMetaModelEngine:
    def test_define_builtin_types(self):
        engine = MetaModelEngine()
        engine.define_builtin_types()
        assert engine.model.get("Module") is not None
        assert engine.model.get("Class") is not None
        assert engine.model.get("Function") is not None

    def test_scan(self, tmp_path):
        """Scan a small test file to verify scanner works."""
        f = tmp_path / "test_mod.py"
        f.write_text("class A: pass\ndef f(): pass\n")
        engine = MetaModelEngine(str(tmp_path))
        engine.define_builtin_types()
        count = engine.scan()
        assert count == 3
        assert engine.repository.count() == 3

    def test_summary(self):
        engine = MetaModelEngine()
        engine.define_builtin_types()
        s = engine.summary()
        assert "types" in s
        assert "total_instances" in s

    def test_save(self, tmp_path):
        engine = MetaModelEngine()
        engine.define_builtin_types()
        p = tmp_path / "test_meta.json"
        engine.save(str(p))
        assert p.exists()
        data = json.loads(p.read_text())
        assert "summary" in data
        assert "instances" in data


class TestMetaModelRepositoryScanner:
    def test_scan_file(self, tmp_path):
        mm = MetaModel()
        mm.define(MetaType(name="Module"))
        mm.define(MetaType(name="Class"))
        mm.define(MetaType(name="Function"))
        repo = MetaModelRepository(mm)
        scanner = MetaModelRepositoryScanner(str(tmp_path), repo)

        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "import os\n"
            "from pathlib import Path\n\n"
            "class MyClass:\n    pass\n\n"
            "def my_func():\n    pass\n"
        )

        count = scanner._scan_file(test_file)
        assert count == 3  # 1 module + 1 class + 1 function
        assert repo.count() == 3
        assert repo.get("Module", "test_module") is not None
        assert repo.get("Class", "test_module.MyClass") is not None
        assert repo.get("Function", "test_module.my_func") is not None

    def test_scan_all(self, tmp_path):
        mm = MetaModel()
        mm.define(MetaType(name="Module"))
        mm.define(MetaType(name="Class"))
        mm.define(MetaType(name="Function"))
        repo = MetaModelRepository(mm)
        scanner = MetaModelRepositoryScanner(str(tmp_path), repo)

        # Create two test modules
        (tmp_path / "a.py").write_text("class A: pass\ndef fa(): pass\n")
        (tmp_path / "b.py").write_text("class B: pass\nclass C: pass\n")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "c.py").write_text("def fc(): pass\n")

        count = scanner.scan_all()
        assert count == 8
        assert repo.count() == 8
