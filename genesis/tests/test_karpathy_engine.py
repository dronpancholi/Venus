"""
Unit tests for Karpathy Execution Engine & Guidelines Provisioning.
"""

import os
import tempfile
import pytest
from genesis.agentos.karpathy import (
    KarpathyExecutionEngine,
    KarpathyDiffValidator,
    KARPATHY_GUIDELINES_TEXT,
)
from genesis.karpathy_provisioning import provision_karpathy_rules


def test_karpathy_guidelines_text():
    assert "Think Before Coding" in KARPATHY_GUIDELINES_TEXT
    assert "Simplicity First" in KARPATHY_GUIDELINES_TEXT
    assert "Surgical Changes" in KARPATHY_GUIDELINES_TEXT
    assert "Goal-Driven Execution" in KARPATHY_GUIDELINES_TEXT


def test_think_before_coding():
    engine = KarpathyExecutionEngine(".")
    thought = engine.think_before_coding("Please refactor the user authentication framework")
    assert len(thought.assumptions) > 0
    assert len(thought.tradeoffs) > 0
    assert len(thought.simpler_alternatives) > 0


def test_ast_orphan_detection():
    clean_code = "import os\nprint(os.getcwd())\n"
    imported, orphans = KarpathyDiffValidator.analyze_python_ast(clean_code)
    assert "os" in imported
    assert len(orphans) == 0

    orphaned_code = "import os\nimport sys\nprint(os.getcwd())\n"
    imported, orphans = KarpathyDiffValidator.analyze_python_ast(orphaned_code)
    assert "sys" in orphans


def test_surgical_diff_audit():
    old_code = "def add(a, b):\n    return a + b\n"
    new_code = "import math\ndef add(a, b):\n    return a + b\n"
    report = KarpathyDiffValidator.audit_file_change("test.py", old_code, new_code)
    assert "math" in report.orphaned_imports
    assert report.surgical_score < 1.0


def test_execute_goal_success():
    engine = KarpathyExecutionEngine(".")
    res = engine.execute_goal(
        goal_description="Verify basic python math",
        verification_cmd="python3 -c 'assert 2 + 2 == 4'",
    )
    assert res.success is True
    assert res.iterations == 1
    assert len(res.steps) == 1
    assert res.steps[0].status == "passed"


def test_provision_karpathy_rules():
    with tempfile.TemporaryDirectory() as tmpdir:
        res = provision_karpathy_rules(tmpdir)
        assert res["CLAUDE.md"] == "created"
        assert res[".cursor/rules/karpathy-guidelines.mdc"] == "created"
        assert res[".genesis/rules/karpathy-guidelines.md"] == "created"
        assert os.path.exists(os.path.join(tmpdir, "CLAUDE.md"))
        assert os.path.exists(os.path.join(tmpdir, ".cursor", "rules", "karpathy-guidelines.mdc"))
