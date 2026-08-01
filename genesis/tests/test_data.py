"""Tests for Engineering Data Platform (Mission 178)."""

from genesis.data import (
    ModelRegistry, ModelDescriptor, ModelCategory,
    VersionedPayload,
)


class TestModelRegistry:
    def test_register_and_get(self):
        r = ModelRegistry()
        desc = ModelDescriptor(name="test.event", category=ModelCategory.EVENT, version="1.0.0")
        r.register(desc)
        assert r.get("test.event") is desc

    def test_list(self):
        r = ModelRegistry()
        r.register(ModelDescriptor(name="a", category=ModelCategory.EVENT))
        r.register(ModelDescriptor(name="b", category=ModelCategory.KNOWLEDGE))
        assert len(r.list()) == 2

    def test_by_category(self):
        r = ModelRegistry()
        r.register(ModelDescriptor(name="e1", category=ModelCategory.EVENT))
        r.register(ModelDescriptor(name="e2", category=ModelCategory.EVENT))
        r.register(ModelDescriptor(name="k1", category=ModelCategory.KNOWLEDGE))
        assert len(r.by_category(ModelCategory.EVENT)) == 2
        assert len(r.by_category(ModelCategory.KNOWLEDGE)) == 1

    def test_validate_required_fields(self):
        r = ModelRegistry()
        desc = ModelDescriptor(
            name="test", category=ModelCategory.OBJECT,
            required_fields=["id", "name"],
        )
        r.register(desc)
        errors = r.validate("test", {"id": "1"})
        assert len(errors) == 1
        assert "name" in errors[0]
        errors = r.validate("test", {"id": "1", "name": "foo"})
        assert len(errors) == 0

    def test_validate_rules(self):
        r = ModelRegistry()
        desc = ModelDescriptor(
            name="test", category=ModelCategory.OBJECT,
            validation_rules={"score": "positive", "title": "non_empty_string"},
        )
        r.register(desc)
        errors = r.validate("test", {"score": -1, "title": ""})
        assert len(errors) == 2

    def test_upgrade_noop(self):
        r = ModelRegistry()
        r.register(ModelDescriptor(name="test", category=ModelCategory.EVENT, version="2.0.0"))
        p = VersionedPayload(model="test", version="2.0.0", data={"key": "val"})
        upgraded = r.upgrade(p)
        assert upgraded is p

    def test_unknown_model_validate(self):
        r = ModelRegistry()
        errors = r.validate("nonexistent", {})
        assert len(errors) == 1


class TestVersionedPayload:
    def test_default_timestamp(self):
        p = VersionedPayload(model="m", version="1.0", data={})
        assert p.timestamp.endswith("Z")

    def test_json_roundtrip(self):
        p = VersionedPayload(model="m", version="1.0", data={"key": "val"})
        raw = p.to_json()
        restored = VersionedPayload.from_json(raw)
        assert restored.model == "m"
        assert restored.data["key"] == "val"
