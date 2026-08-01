"""Tests for Workspace Manager (Mission 181)."""

from genesis.workspace import WorkspaceManager, WorkspaceLayout, WorkspaceTemplate


class TestWorkspaceManager:
    def test_templates(self):
        wm = WorkspaceManager()
        templates = wm.templates()
        assert len(templates) >= 3
        names = [t.name for t in templates]
        assert "engineering" in names
        assert "review" in names
        assert "minimal" in names

    def test_apply_template(self):
        wm = WorkspaceManager()
        layout = wm.apply_template("engineering")
        assert layout is not None
        assert layout.name == "engineering"
        assert wm.current_layout == "engineering"

    def test_apply_unknown(self):
        wm = WorkspaceManager()
        assert wm.apply_template("nonexistent") is None

    def test_pin_unpin(self):
        wm = WorkspaceManager()
        wm.pin_project("proj_a")
        wm.pin_project("proj_b")
        assert "proj_a" in wm.pinned_projects
        wm.unpin_project("proj_a")
        assert "proj_a" not in wm.pinned_projects

    def test_recent_work(self):
        wm = WorkspaceManager()
        wm.add_recent("item1")
        wm.add_recent("item2")
        wm.add_recent("item3")
        assert wm.recent_work[0] == "item3"
        assert len(wm.recent_work) == 3

    def test_recent_work_dedup(self):
        wm = WorkspaceManager()
        wm.add_recent("item1")
        wm.add_recent("item1")
        assert wm.recent_work.count("item1") == 1
        assert wm.recent_work[0] == "item1"

    def test_recent_work_max(self):
        wm = WorkspaceManager()
        for i in range(25):
            wm.add_recent(f"item{i}")
        assert len(wm.recent_work) <= 20

    def test_current_layout_default(self):
        wm = WorkspaceManager()
        assert wm.current_layout == "minimal"
