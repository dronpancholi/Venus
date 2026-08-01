"""Tests for Application Runtime (Mission 180)."""

from unittest.mock import MagicMock

from genesis.runtime import AppRuntime, AppStatus, AppPermission, AppInstance


class TestAppRuntime:
    def test_install(self):
        r = AppRuntime()
        app = r.install("test_app", version="2.0.0",
                        dependencies=["dep_a"],
                        permissions=["read:events", "write:engineering"])
        assert app.name == "test_app"
        assert app.status == AppStatus.INSTALLED
        assert len(app.permissions) == 2
        assert app.dependencies == ["dep_a"]

    def test_start_stop(self):
        r = AppRuntime()
        r.install("my_app")
        assert r.start("my_app") is True
        assert r.get("my_app").status == AppStatus.RUNNING
        assert r.stop("my_app") is True
        assert r.get("my_app").status == AppStatus.STOPPED

    def test_start_fails_if_missing_dep(self):
        r = AppRuntime()
        r.install("app", dependencies=["missing_dep"])
        assert r.start("app") is False
        assert r.get("app").status == AppStatus.FAILED

    def test_uninstall(self):
        r = AppRuntime()
        r.install("app")
        assert r.uninstall("app") is True
        assert r.get("app") is None

    def test_list(self):
        r = AppRuntime()
        r.install("a")
        r.install("b")
        apps = r.list()
        assert len(apps) == 2

    def test_check_permission(self):
        r = AppRuntime()
        r.install("app", permissions=["read:events"])
        assert r.check_permission("app", "read:events") is True
        assert r.check_permission("app", "write:engineering") is False

    def test_settings(self):
        r = AppRuntime()
        r.install("app")
        assert r.set_setting("app", "key1", "val1") is True
        assert r.get_setting("app", "key1") == "val1"
        assert r.get_setting("app", "nonexistent") is None

    def test_notifications(self):
        r = AppRuntime()
        r.install("app")
        n = r.notify("app", "Test Title", "Test body", severity="warning")
        assert n.title == "Test Title"
        assert n.severity == "warning"
        assert len(r.notifications()) == 1

    def test_kernel_integration(self):
        kernel = MagicMock()
        r = AppRuntime(kernel=kernel)
        r.install("app")
        assert kernel.emit.called

    def test_double_start(self):
        r = AppRuntime()
        r.install("app")
        r.start("app")
        assert r.start("app") is False

    def test_compatibility(self):
        r = AppRuntime()
        r.install("app", version="1.0")
        issues = r.check_compatibility("app", "2.0")
        assert len(issues) == 1
        issues = r.check_compatibility("nonexistent", "1.0")
        assert len(issues) == 1
