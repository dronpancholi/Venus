"""Tests for Marketplace Foundation (Mission 183)."""

from genesis.marketplace import (
    AppManifest, MarketplacePackage, MarketplaceRegistry,
)


class TestAppManifest:
    def test_create(self):
        m = AppManifest(name="test_app", version="2.0.0", entry_point="run")
        assert m.name == "test_app"
        assert m.version == "2.0.0"

    def test_validation_passes(self):
        m = AppManifest(name="app", version="1.0", entry_point="main")
        assert m.validate() == []

    def test_validation_fails(self):
        m = AppManifest(name="", version="", entry_point="")
        errors = m.validate()
        assert len(errors) >= 3

    def test_json_roundtrip(self):
        m = AppManifest(name="app", version="1.0", entry_point="main",
                        dependencies=[{"name": "dep1"}])
        raw = m.to_json()
        restored = AppManifest.from_json(raw)
        assert restored.name == "app"
        assert restored.dependencies == [{"name": "dep1"}]

    def test_hash(self):
        m = AppManifest(name="app", version="1.0", entry_point="main")
        assert len(m.hash) == 16


class TestMarketplaceRegistry:
    def test_register_and_get(self):
        r = MarketplaceRegistry()
        pkg = MarketplacePackage(
            manifest=AppManifest(name="app", version="1.0", entry_point="run")
        )
        r.register(pkg)
        assert r.get("app") is pkg

    def test_register_invalid(self):
        r = MarketplaceRegistry()
        pkg = MarketplacePackage(manifest=AppManifest(name="", version="", entry_point=""))
        try:
            r.register(pkg)
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_search(self):
        r = MarketplaceRegistry()
        r.register(MarketplacePackage(
            manifest=AppManifest(name="finder", version="1.0", entry_point="run",
                                 description="Finds things")
        ))
        r.register(MarketplacePackage(
            manifest=AppManifest(name="other", version="1.0", entry_point="run",
                                 description="Something else")
        ))
        results = r.search("find")
        assert len(results) == 1
        assert results[0].manifest.name == "finder"

    def test_list(self):
        r = MarketplaceRegistry()
        r.register(MarketplacePackage(
            manifest=AppManifest(name="a", version="1.0", entry_point="run")
        ))
        r.register(MarketplacePackage(
            manifest=AppManifest(name="b", version="1.0", entry_point="run")
        ))
        assert len(r.list()) == 2

    def test_check_dependencies(self):
        r = MarketplaceRegistry()
        r.register(MarketplacePackage(
            manifest=AppManifest(name="app", version="1.0", entry_point="run",
                                 dependencies=[{"name": "missing_dep"}])
        ))
        missing = r.check_dependencies("app")
        assert "missing_dep" in missing[0]

    def test_find_updates(self):
        r = MarketplaceRegistry()
        r.register(MarketplacePackage(
            manifest=AppManifest(name="app", version="2.0", entry_point="run")
        ))
        update = r.find_updates("app", "1.0")
        assert update is not None
        assert update.manifest.version == "2.0"
        assert r.find_updates("app", "2.0") is None
