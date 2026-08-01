"""
Tests for Continuous Engineering watchers (Mission 62).
"""

import os
import tempfile
import time
import pytest

from genesis.fabric.kernel import FabricKernel
from genesis.watch import FilesystemWatcher, WatcherState


class TestWatcherBase:
    def test_watcher_state_defaults(self):
        s = WatcherState()
        assert s.active is True
        assert s.scan_count == 0
        assert s.change_count == 0

    def test_watcher_state_updates(self):
        s = WatcherState(active=False, scan_count=5, change_count=10)
        assert s.active is False
        assert s.scan_count == 5


class TestFilesystemWatcher:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance()

    def test_detect_created_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            w = FilesystemWatcher(tmpdir, self.kernel, extensions=[".txt"])
            w.scan()  # initial scan, no events
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("hello")

            events = w.scan()
            created = [e for e in events if e.type == "fs.file.created"]
            assert len(created) == 1
            assert "test.txt" in created[0].payload["path"]

    def test_detect_changed_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            w = FilesystemWatcher(tmpdir, self.kernel, extensions=[".txt"])
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("original")
            w.scan()  # capture baseline

            with open(test_file, "w") as f:
                f.write("modified")

            events = w.scan()
            changed = [e for e in events if e.type == "fs.file.changed"]
            assert len(changed) == 1

    def test_detect_deleted_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            w = FilesystemWatcher(tmpdir, self.kernel, extensions=[".txt"])
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("hello")
            w.scan()  # capture baseline

            os.remove(test_file)

            events = w.scan()
            deleted = [e for e in events if e.type == "fs.file.deleted"]
            assert len(deleted) == 1

    def test_extension_filtering(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            w = FilesystemWatcher(tmpdir, self.kernel, extensions=[".py"])
            with open(os.path.join(tmpdir, "a.py"), "w") as f:
                f.write("x")
            with open(os.path.join(tmpdir, "b.txt"), "w") as f:
                f.write("x")
            events = w.scan()
            created = [e for e in events if e.type == "fs.file.created"]
            assert len(created) == 1  # only .py
            assert "a.py" in created[0].payload["path"]

    def test_watcher_start_stop(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            w = FilesystemWatcher(tmpdir, self.kernel)
            w.start()
            time.sleep(0.1)
            s = w.state
            assert s.active is True
            assert s.scan_count >= 0
            w.stop()
            assert w.state.active is False

    def test_watcher_events_have_tags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            w = FilesystemWatcher(tmpdir, self.kernel, extensions=[".txt"])
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("x")
            events = w.scan()
            for e in events:
                assert "watch" in e.tags
                assert e.origin == "filesystem_watcher"
