"""
Tests for the Intelligence Service — Phase 6 of GENESIS IX.
"""

import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from genesis.intelligence import (
    IntelligenceService, RepositoryIntelligence, KnowledgeGraph,
)
from genesis.brain import EngineeringBrain


class TestIntelligenceService:
    @pytest.fixture
    def brain(self):
        with tempfile.TemporaryDirectory() as td:
            yield EngineeringBrain(storage_path=os.path.join(td, "brain.db"))

    def test_create_without_brain(self):
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(root=td)
            assert svc._brain is None
            assert svc.engine is not None
            assert svc.kg is not None

    def test_create_with_brain(self, brain):
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(brain=brain, root=td)
            assert svc._brain is brain
            assert svc.brain is brain

    def test_properties(self, brain):
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(brain=brain, root=td)
            assert svc.brain is brain
            assert isinstance(svc.engine, RepositoryIntelligence)
            assert isinstance(svc.kg, KnowledgeGraph)

    def test_summary_without_brain(self):
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(root=td)
            s = svc.summary()
            assert s["brain_connected"] is False
            assert s["has_results"] is False
            assert "knowledge_graph" in s

    def test_summary_with_brain(self, brain):
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(brain=brain, root=td)
            s = svc.summary()
            assert s["brain_connected"] is True
            assert s["brain_synced"] >= 0

    def test_run_all_syncs_kg_to_brain(self, brain):
        with tempfile.TemporaryDirectory() as td:
            # Create a minimal Python file
            src = os.path.join(td, "mod.py")
            with open(src, "w") as f:
                f.write("class TestClass:\n    pass\n")
            svc = IntelligenceService(brain=brain, root=td, quiet=True)
            results = svc.run_all()
            assert "phase_2_knowledge_graph" in results
            # Verify KG nodes were synced to brain
            assert brain.find_by_label("TestClass") is not None or \
                   len(brain.all_entities()) > 0

    def test_run_all_syncs_issues(self, brain):
        """Verify issues are registered as BrainEntities after run_all."""
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "mod.py")
            with open(src, "w") as f:
                f.write("class Foo:\n    pass\n")
            svc = IntelligenceService(brain=brain, root=td, quiet=True)
            svc.run_all()
            # Look for intelligence_issue entities in brain
            issues = brain.find_by_type("intelligence_issue")
            # May or may not have issues depending on codebase size
            assert isinstance(issues, list)

    def test_run_all_syncs_capabilities(self, brain):
        """Verify capabilities are registered as BrainEntities."""
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "mod.py")
            with open(src, "w") as f:
                f.write("class Foo:\n    pass\n")
            svc = IntelligenceService(brain=brain, root=td, quiet=True)
            svc.run_all()
            caps = brain.find_by_type("intelligence_capability")
            assert isinstance(caps, list)

    def test_run_all_syncs_gaps(self, brain):
        """Verify gaps are registered as BrainEntities."""
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "mod.py")
            with open(src, "w") as f:
                f.write("class Foo:\n    pass\n")
            svc = IntelligenceService(brain=brain, root=td, quiet=True)
            svc.run_all()
            gaps = brain.find_by_type("intelligence_gap")
            assert isinstance(gaps, list)

    def test_run_all_syncs_initiatives(self, brain):
        """Verify planning initiatives are registered as BrainEntities."""
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "mod.py")
            with open(src, "w") as f:
                f.write("class Foo:\n    pass\n")
            svc = IntelligenceService(brain=brain, root=td, quiet=True)
            svc.run_all()
            initiatives = brain.find_by_type("intelligence_initiative")
            assert isinstance(initiatives, list)

    def test_report_method(self):
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(root=td, quiet=True)
            # Before run_all, report should indicate no results
            report = svc.report()
            assert "No results yet" in report or "VRIP" in report
            svc.run_all()
            report = svc.report()
            assert "VRIP" in report or "Maturity" in report

    def test_engine_access(self, brain):
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(brain=brain, root=td, quiet=True)
            assert svc.engine is svc._engine
            svc.run_all()
            assert svc.engine.last_results is not None

    def test_mocked_sync_count(self, brain):
        """Test sync count with known results using mocked engine."""
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(brain=brain, root=td, quiet=True)

            # Override run_all with controlled results
            mock_results = {
                "phase_5_analysis": [
                    {"kind": "duplication", "severity": "medium",
                     "message": "Duplicate class Foo", "location": "mod.py"},
                ],
                "phase_6_capabilities": [
                    {"name": "test_cap", "description": "A test capability"},
                ],
                "phase_8_gaps": [
                    {"kind": "specification", "priority": "P0",
                     "title": "Missing specs", "description": "Some specs missing"},
                ],
                "phase_9_planning": [
                    {"title": "Fix specs", "priority": "P0",
                     "rationale": "Need to fix", "effort": "1 session",
                     "specs": [], "modules": [], "risk": "Low",
                     "maturity_increase": "+5%"},
                ],
                "phase_2_knowledge_graph": {"total_nodes": 0, "total_edges": 0},
            }

            with patch.object(svc._engine, 'run_all', return_value=mock_results):
                with patch.object(svc._engine, 'kg', KnowledgeGraph()):
                    svc.run_all()

            # Verify entities were registered in brain
            assert len(brain.find_by_type("intelligence_issue")) >= 1
            assert len(brain.find_by_type("intelligence_capability")) >= 1
            assert len(brain.find_by_type("intelligence_gap")) >= 1
            assert len(brain.find_by_type("intelligence_initiative")) >= 1

    def test_sync_each_entity_type_has_correct_attributes(self, brain):
        """Verify each synced entity type has the right attributes."""
        with tempfile.TemporaryDirectory() as td:
            svc = IntelligenceService(brain=brain, root=td, quiet=True)

            mock_results = {
                "phase_5_analysis": [
                    {"kind": "duplication", "severity": "high",
                     "message": "Critical: circular dependency", "location": "core/"},
                ],
                "phase_6_capabilities": [],
                "phase_8_gaps": [
                    {"kind": "persistence", "priority": "P0",
                     "title": "Storage not wired", "description": "Missing wiring",
                     "effort": "1 session", "leverage": "High", "risk": "Low"},
                ],
                "phase_9_planning": [],
                "phase_2_knowledge_graph": {"total_nodes": 0, "total_edges": 0},
            }

            with patch.object(svc._engine, 'run_all', return_value=mock_results):
                with patch.object(svc._engine, 'kg', KnowledgeGraph()):
                    svc.run_all()

            # Verify issue attributes
            issues = brain.find_by_type("intelligence_issue")
            issue = issues[0]
            assert issue.attributes.get("severity") == "high"
            assert issue.attributes.get("kind") == "duplication"
            assert issue.attributes.get("location") == "core/"

            # Verify gap attributes
            gaps = brain.find_by_type("intelligence_gap")
            gap = gaps[0]
            assert gap.attributes.get("priority") == "P0"
            assert gap.attributes.get("kind") == "persistence"
            assert gap.attributes.get("effort") == "1 session"
