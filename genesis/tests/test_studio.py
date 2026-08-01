"""Tests for Genesis Studio (Mission 184)."""

from genesis.studio import GenesisStudio, StudioScreen


class TestGenesisStudio:
    def test_manifest(self):
        s = GenesisStudio()
        m = s.manifest
        assert m["name"] == "genesis_studio"
        assert m["version"] == "1.0.0"
        assert len(m["capabilities"]) > 10

    def test_screens(self):
        s = GenesisStudio()
        screens = s.screens
        assert len(screens) == 10
        assert screens[0].name == "dashboard"
        assert screens[-1].name == "apps"

    def test_capability_summary(self):
        s = GenesisStudio()
        caps = s.capability_summary()
        assert len(caps) == len(s.manifest["capabilities"])
        assert all(caps.values())
