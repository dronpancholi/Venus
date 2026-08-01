"""Tests for Production Hardening (Mission 188)."""

import os
from unittest.mock import MagicMock

from genesis.hardening import (
    GenesisError, LifecycleError, ResourceError,
    Logger, LogEntry, get_logger,
    safe, retry, production_hardening_pass,
)


class TestLogEntry:
    def test_default_timestamp(self):
        e = LogEntry(level="INFO", message="test")
        assert e.timestamp > 0

    def test_format(self):
        e = LogEntry(level="INFO", message="hello", subsystem="test")
        formatted = e.format()
        assert "INFO" in formatted
        assert "test" in formatted
        assert "hello" in formatted


class TestLogger:
    def test_log_levels(self):
        logger = Logger(min_level="DEBUG")
        logger.debug("debug msg")
        logger.info("info msg")
        logger.warning("warning msg")
        logger.error("error msg")
        assert len(logger.recent()) >= 4

    def test_min_level_filter(self):
        logger = Logger(min_level="ERROR")
        logger.info("should be filtered")
        logger.error("should be visible")
        recent = logger.recent()
        assert all(e.level != "INFO" for e in recent)

    def test_kernel_integration(self):
        kernel = MagicMock()
        logger = Logger(kernel=kernel)
        logger.info("test message")
        assert kernel.emit.called

    def test_export(self):
        logger = Logger()
        logger.info("a")
        logger.warning("b")
        exported = logger.export()
        assert len(exported) >= 2
        assert exported[0]["level"] == "INFO"


class TestErrors:
    def test_genesis_error(self):
        e = GenesisError("test error", subsystem="test")
        assert str(e) == "test error"
        assert e.subsystem == "test"

    def test_lifecycle_error(self):
        e = LifecycleError("lifecycle failed", details={"phase": "boot"})
        assert e.details["phase"] == "boot"

    def test_resource_error(self):
        e = ResourceError("out of memory")
        assert "memory" in str(e)


class TestHardeningPass:
    def test_finds_large_files(self):
        import tempfile
        # Create a temporarily large file
        test_dir = os.path.join(tempfile.gettempdir(), "genesis_harden_test")
        os.makedirs(test_dir, exist_ok=True)
        large_file = os.path.join(test_dir, "large.py")
        with open(large_file, "w") as f:
            f.write("\n" * 4000)

        findings = production_hardening_pass(test_dir)
        assert len(findings) > 0
        assert any("4000" in f.issue for f in findings)

        os.remove(large_file)
        os.rmdir(test_dir)

    def test_finding_structure(self):
        findings = production_hardening_pass("/nonexistent")
        assert isinstance(findings, list)


class TestSafe:
    def test_safe_success(self):
        @safe("test_op")
        def works():
            return 42
        assert works() == 42

    def test_safe_failure(self):
        @safe("test_op")
        def fails():
            raise ValueError("oops")
        assert fails() is None


class TestRetry:
    def test_retry_success(self):
        @retry(max_attempts=3)
        def works():
            return "ok"
        assert works() == "ok"

    def test_retry_eventually_succeeds(self):
        call_count = [0]

        @retry(max_attempts=3, delay=0.01)
        def eventually():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("not yet")
            return "ok"

        assert eventually() == "ok"
        assert call_count[0] == 2

    def test_retry_all_fail(self):
        call_count = [0]

        @retry(max_attempts=3, delay=0.01)
        def always_fails():
            call_count[0] += 1
            raise ValueError("always")

        assert always_fails() is None
        assert call_count[0] == 3
