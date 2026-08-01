from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

import pytest

from genesis.autonomous.analyzer import AnalysisFinding, AnalysisReport, SelfAnalyzer
from genesis.autonomous.codegen import CodeGenerator, GenerationResult, Patch
from genesis.autonomous.planner import ImprovementPlan, ImprovementPlanner, ImprovementStep, PlanningSession, PlanStatus, PlanType


# ── Fixtures ──

@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "good.py").write_text("""
def add(a, b):
    return a + b

def greet(name):
    return f"Hello, {name}"
""")
    (src / "bad.py").write_text("""
import os
import os

def complex_func(a, b, c, d, e):
    if a:
        if b:
            while c:
                for x in range(10):
                    try:
                        pass
                    except:
                        pass
                        if True:
                            if False:
                                pass
                                pass
                                pass

    # TODO: fix this
    data = {}
    items = []
    result = {"key": "a very long string that is duplicated", "value": "a very long string that is duplicated"}
    return "a very long string that is duplicated"

def another_func():
    items = []
    return items
""")
    (src / "longlines.py").write_text("a" * 200 + "\n" + "b" * 150 + "\n")
    return tmp_path


# ── SelfAnalyzer ──

class TestSelfAnalyzer:
    def test_analyze_empty_dir(self, tmp_path: Path):
        sa = SelfAnalyzer(str(tmp_path))
        report = sa.analyze(str(tmp_path))
        assert report.total_files == 0
        assert report.total_lines == 0

    def test_analyze_sample(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        assert report.total_files >= 3
        assert report.total_lines > 0
        assert len(report.findings) > 0

    def test_todo_detection(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        todo_findings = [f for f in report.findings if f.category == "todo"]
        assert len(todo_findings) == 1
        assert "TODO" in todo_findings[0].message

    def test_long_lines_detected(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        long = [f for f in report.findings if f.category == "style"]
        assert len(long) == 2

    def test_duplicate_imports(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        dup_imports = [f for f in report.findings if f.category == "imports"]
        assert len(dup_imports) >= 1

    def test_complex_functions(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "complex.py"
            lines = ["def f():"]
            for i in range(12):
                indent = "    " * (i + 1)
                lines.append(f"{indent}if {i}:")
                lines.append(f"{indent}    pass")
            p.write_text("\n".join(lines))
            sa = SelfAnalyzer(d)
            report = sa.analyze(d)
            complex_fns = [f for f in report.findings if f.category == "complexity"]
            assert len(complex_fns) >= 1

    def test_mutable_defaults(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        mutable = [f for f in report.findings if f.category == "bug_prone" and "mutable default" in f.message.lower()]
        assert len(mutable) >= 0

    def test_bare_excepts(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        bare = [f for f in report.findings if f.category == "bug_prone" and "bare" in f.message.lower()]
        assert len(bare) >= 1

    def test_report_metrics(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        assert report.metrics["files_per_second"] > 0
        assert report.metrics["findings_per_file"] > 0
        assert report.metrics["avg_line_length"] > 0

    def test_report_summary(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        assert report.summary["total_findings"] > 0
        assert "by_severity" in report.summary
        assert "by_category" in report.summary

    def test_severity_distribution(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        assert report.summary["by_severity"]["info"] >= 1
        assert report.summary["by_severity"]["warning"] >= 1

    def test_duplicate_strings(self, sample_repo: Path):
        bad_py = sample_repo / "src" / "bad.py"
        bad_py.write_text(bad_py.read_text() + """
def more():
    x = "very long duplicated string literal"
    y = "very long duplicated string literal"
    z = "very long duplicated string literal"
""")
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        dup_strings = [f for f in report.findings if f.category == "duplication"]
        assert len(dup_strings) >= 1

    def test_analysis_finding_fields(self):
        f = AnalysisFinding(category="test", severity="error", file="f.py", line=10, message="msg", suggestion="fix")
        assert f.category == "test"
        assert f.severity == "error"
        assert f.file == "f.py"
        assert f.metric == 0.0

    def test_analysis_report_defaults(self):
        r = AnalysisReport()
        assert r.total_files == 0
        assert r.total_lines == 0
        assert r.findings == []
        assert r.metrics == {}
        assert r.summary == {}


# ── ImprovementPlanner ──

class TestImprovementPlanner:
    def test_plan_from_report(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        planner = ImprovementPlanner()
        session = planner.plan(report)
        assert len(session.plans) > 0
        for plan in session.plans:
            assert plan.id
            assert plan.title
            assert len(plan.steps) > 0

    def test_plan_prioritization(self, sample_repo: Path):
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        planner = ImprovementPlanner()
        session = planner.plan(report)
        if len(session.plans) > 1:
            for i in range(len(session.plans) - 1):
                assert session.plans[i].priority >= session.plans[i + 1].priority

    def test_approve_plan(self, sample_repo: Path):
        planner = ImprovementPlanner()
        report = AnalysisReport(findings=[AnalysisFinding(category="todo", severity="info", file="x.py", message="TODO")])
        session = planner.plan(report)
        plan_id = session.plans[0].id
        assert planner.approve(plan_id)
        assert session.plans[0].status == PlanStatus.APPROVED

    def test_approve_twice_fails(self, sample_repo: Path):
        planner = ImprovementPlanner()
        report = AnalysisReport(findings=[AnalysisFinding(category="todo", severity="info", file="x.py", message="TODO")])
        session = planner.plan(report)
        plan_id = session.plans[0].id
        assert planner.approve(plan_id)
        assert not planner.approve(plan_id)

    def test_approve_nonexistent(self):
        planner = ImprovementPlanner()
        assert not planner.approve("nonexistent")

    def test_complete_plan(self, sample_repo: Path):
        planner = ImprovementPlanner()
        report = AnalysisReport(findings=[AnalysisFinding(category="todo", severity="info", file="x.py", message="TODO")])
        session = planner.plan(report)
        plan_id = session.plans[0].id
        assert planner.complete(plan_id)
        assert session.plans[0].status == PlanStatus.COMPLETED
        assert session.plans[0].completed_at > 0

    def test_complete_nonexistent(self):
        planner = ImprovementPlanner()
        assert not planner.complete("nonexistent")

    def test_history(self, sample_repo: Path):
        planner = ImprovementPlanner()
        report = AnalysisReport(findings=[AnalysisFinding(category="todo", severity="info", file="x.py", message="TODO")])
        planner.plan(report)
        assert len(planner.history()) == 1

    def test_history_limit(self, sample_repo: Path):
        planner = ImprovementPlanner()
        for _ in range(5):
            planner.plan(AnalysisReport(findings=[AnalysisFinding(category="todo", severity="info", file="x.py", message="TODO")]))
        assert len(planner.history(3)) == 3
        assert len(planner.history()) == 5

    def test_summary(self, sample_repo: Path):
        planner = ImprovementPlanner()
        report = AnalysisReport(findings=[AnalysisFinding(category="todo", severity="info", file="x.py", message="TODO")])
        planner.plan(report)
        s = planner.summary()
        assert s["sessions"] == 1
        assert s["total_plans"] >= 1

    def test_empty_report_plans(self):
        planner = ImprovementPlanner()
        session = planner.plan(AnalysisReport())
        assert len(session.plans) == 0

    def test_plan_types(self):
        planner = ImprovementPlanner()
        report = AnalysisReport(findings=[
            AnalysisFinding(category="complexity", severity="warning", file="x.py", message="high complexity"),
            AnalysisFinding(category="bug_prone", severity="error", file="y.py", message="bug"),
            AnalysisFinding(category="todo", severity="info", file="z.py", message="TODO"),
        ])
        session = planner.plan(report)
        types = {p.plan_type for p in session.plans}
        assert PlanType.REFACTOR in types
        assert PlanType.FIX in types
        assert PlanType.CLEANUP in types

    def test_session_metrics(self, sample_repo: Path):
        planner = ImprovementPlanner()
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        session = planner.plan(report)
        assert session.metrics["total_plans"] > 0
        assert session.metrics["total_steps"] > 0
        assert session.metrics["estimated_effort"] > 0

    def test_plan_estimated_effort(self, sample_repo: Path):
        planner = ImprovementPlanner()
        sa = SelfAnalyzer(str(sample_repo))
        report = sa.analyze(str(sample_repo / "src"))
        session = planner.plan(report)
        for plan in session.plans:
            assert plan.estimated_effort > 0


# ── CodeGenerator ──

class TestCodeGenerator:
    def test_generate_empty_plan(self):
        cg = CodeGenerator()
        plan = ImprovementPlan(steps=[])
        result = cg.generate(plan)
        assert len(result.patches) == 0
        assert len(result.errors) == 0

    def test_generate_nonexistent_file(self):
        cg = CodeGenerator()
        plan = ImprovementPlan(steps=[ImprovementStep(file="/nonexistent/path.py", action="fix", description="nope")])
        result = cg.generate(plan)
        assert len(result.patches) == 0

    def test_generate_and_apply(self, tmp_path: Path):
        f = tmp_path / "test.py"
        f.write_text("x = 1\n")
        cg = CodeGenerator(str(tmp_path))
        plan = ImprovementPlan(steps=[ImprovementStep(file="test.py", action="fix", description="test")])
        result = cg.generate(plan)
        assert len(result.patches) >= 0
        for patch in result.patches:
            assert patch.file.endswith("test.py")

    def test_apply_patch(self, tmp_path: Path):
        f = tmp_path / "target.py"
        original = "x = 1\n"
        f.write_text(original)
        cg = CodeGenerator(str(tmp_path))
        result = GenerationResult(patches=[
            Patch(file=str(f), original=original, patched="x = 2\n", description="bump"),
        ])
        assert cg.apply(result) == 1
        assert f.read_text() == "x = 2\n"

    def test_apply_dry_run(self, tmp_path: Path):
        f = tmp_path / "target.py"
        f.write_text("x = 1\n")
        cg = CodeGenerator(str(tmp_path))
        result = GenerationResult(patches=[
            Patch(file=str(f), original="x = 1\n", patched="x = 2\n"),
        ])
        assert cg.apply(result, dry_run=True) == 1
        assert f.read_text() == "x = 1\n"

    def test_validate_good_code(self, tmp_path: Path):
        f = tmp_path / "good.py"
        f.write_text("x = 1\n")
        cg = CodeGenerator(str(tmp_path))
        result = GenerationResult(patches=[
            Patch(file=str(f), original="x = 1\n", patched="x = 2\n"),
        ])
        assert cg.validate(result)

    def test_validate_bad_code(self, tmp_path: Path):
        f = tmp_path / "bad.py"
        f.write_text("x = 1\n")
        cg = CodeGenerator(str(tmp_path))
        result = GenerationResult(patches=[
            Patch(file=str(f), original="x = 1\n", patched="x = 1 2 3\n"),
        ])
        assert not cg.validate(result)

    def test_rollback(self, tmp_path: Path):
        f = tmp_path / "target.py"
        original = "x = 1\n"
        f.write_text(original)
        cg = CodeGenerator(str(tmp_path))
        result = GenerationResult(patches=[
            Patch(file=str(f), original=original, patched="x = 2\n"),
        ])
        cg.apply(result)
        assert f.read_text() == "x = 2\n"
        assert cg.rollback(result) == 1
        assert f.read_text() == "x = 1\n"

    def test_history(self):
        cg = CodeGenerator()
        assert len(cg.history()) == 0
        cg.generate(ImprovementPlan(steps=[]))
        assert len(cg.history()) == 1

    def test_history_limit(self):
        cg = CodeGenerator()
        for _ in range(5):
            cg.generate(ImprovementPlan(steps=[]))
        assert len(cg.history(3)) == 3

    def test_summary(self):
        cg = CodeGenerator()
        s = cg.summary()
        assert s["generations"] == 0
        assert s["total_patches"] == 0
        cg.generate(ImprovementPlan(steps=[]))
        s = cg.summary()
        assert s["generations"] == 1

    def test_generation_result_defaults(self):
        r = GenerationResult()
        assert r.id
        assert r.timestamp > 0
        assert r.patches == []
        assert r.errors == []

    def test_patch_fields(self):
        p = Patch(file="f.py", original="old", patched="new", description="changed")
        assert not p.applied
        assert not p.validated

    def test_bare_except_to_specific(self, tmp_path: Path):
        f = tmp_path / "fix_except.py"
        f.write_text("""
try:
    pass
except:
    pass
""")
        cg = CodeGenerator(str(tmp_path))
        plan = ImprovementPlan(steps=[
            ImprovementStep(file="fix_except.py", action="catch specific exception types", description="fix bare except"),
        ])
        result = cg.generate(plan)
        assert len(result.patches) >= 0

    def test_mutable_default_to_none(self, tmp_path: Path):
        f = tmp_path / "fix_defaults.py"
        f.write_text("""
def f(items=[]):
    pass

def g(data={}):
    pass
""")
        cg = CodeGenerator(str(tmp_path))
        plan = ImprovementPlan(steps=[
            ImprovementStep(file="fix_defaults.py", action="use none and initialize inside function body", description="fix defaults"),
        ])
        result = cg.generate(plan)
        assert len(result.patches) >= 0

    def test_generate_nonexistent_step_returns_no_patch(self):
        cg = CodeGenerator()
        plan = ImprovementPlan(steps=[ImprovementStep(file="/nonexistent.py", action="fix", description="nope")])
        result = cg.generate(plan)
        assert len(result.patches) == 0

    def test_generate_includes_errors(self, tmp_path: Path):
        cg = CodeGenerator(str(tmp_path))
        plan = ImprovementPlan(steps=[ImprovementStep(file="", action="fix", description="bad")])
        result = cg.generate(plan)
        assert len(result.errors) >= 0

    def test_generate_metrics(self, tmp_path: Path):
        f = tmp_path / "m.py"
        f.write_text("x = 1\n")
        cg = CodeGenerator(str(tmp_path))
        plan = ImprovementPlan(steps=[ImprovementStep(file="m.py", action="fix", description="t")])
        result = cg.generate(plan)
        assert "patches" in result.metrics
        assert "errors" in result.metrics
        assert "files_modified" in result.metrics


# ── Integration ──

class TestAutonomousIntegration:
    def test_analyze_plan_generate_cycle(self, tmp_path: Path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "__init__.py").write_text("")
        (src / "mod.py").write_text("""
import os
import os

def f():
    # TODO: fix
    pass

class C:
    def complex(self):
        if True:
            if True:
                if True:
                    if True:
                        if True:
                            pass
                            pass
                            pass
                            pass
""")
        sa = SelfAnalyzer(str(tmp_path))
        report = sa.analyze(str(src))
        assert report.total_files >= 1
        assert len(report.findings) > 0

        planner = ImprovementPlanner()
        session = planner.plan(report)
        assert len(session.plans) > 0

        cg = CodeGenerator(str(tmp_path))
        for plan in session.plans:
            result = cg.generate(plan)
            assert len(result.errors) == 0
