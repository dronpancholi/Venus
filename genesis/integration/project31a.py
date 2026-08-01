"""
CORE-14: Project 31A Integration

Deep integration. Project 31A becomes the first executable workload.

Capabilities:
  Compilation, Validation, Capability Analysis, Architecture Review,
  Dependency Graph, Prompt Generation, Documentation Generation,
  Roadmaps, Risk Analysis, Autonomous Review
"""

import json
from pathlib import Path
from typing import Any

from genesis.compiler.compiler import Compiler
from genesis.validation.engine import ValidationEngine
from genesis.validation.base import ValidationResult
from genesis.graph.engine import KnowledgeGraphEngine
from genesis.core.types import type_registry


class Project31AIntegration:
    """Integration layer for Project 31A as the first Venus workload."""

    def __init__(self):
        self.compiler = Compiler()
        self.validator = ValidationEngine()
        self.graph = KnowledgeGraphEngine()
        self.project_root: Path | None = None

    def set_project_root(self, path: str | Path):
        self.project_root = Path(path)

    # --- Compilation ---
    def compile_artifacts(self, paths: list[str]) -> dict[str, Any]:
        results = {}
        for path in paths:
            try:
                cu = self.compiler.compile(path)
                results[path] = {
                    "status": "compiled",
                    "ast_nodes": len(cu.ast.nodes),
                    "dependencies": len(cu.dependencies.edges),
                }
            except Exception as e:
                results[path] = {"status": "failed", "error": str(e)}
        return {
            "total": len(paths),
            "compiled": sum(1 for r in results.values() if r["status"] == "compiled"),
            "failed": sum(1 for r in results.values() if r["status"] == "failed"),
            "results": results,
        }

    # --- Validation ---
    def validate_artifacts(self, paths: list[str]) -> dict[str, Any]:
        all_results = []
        for path in paths:
            results = self.validator.validate_path(path)
            all_results.extend(results)
        summary = self.validator.summary(all_results)
        return summary

    # --- Capability Analysis ---
    def analyze_capabilities(self) -> dict[str, Any]:
        from genesis.capability.registry import capability_registry
        caps = capability_registry.all()
        return {
            "total_capabilities": len(caps),
            "capabilities": [c.to_dict() for c in caps],
        }

    # --- Architecture Review ---
    def architecture_review(self) -> dict[str, Any]:
        """Review the architecture of the integrated project."""
        review = {
            "total_nodes": len(self.graph.graph.nodes),
            "total_edges": len(self.graph.graph.edges),
            "node_types": dict(self.graph.count_by_type()),
            "circular_dependencies": len(self.graph.detect_circular_dependencies()),
            "orphans": len(self.graph.detect_orphans()),
        }

        recommendations = []
        if review["circular_dependencies"] > 0:
            recommendations.append("Break circular dependencies")
        if review["orphans"] > 5:
            recommendations.append("Connect or remove orphan nodes")
        if review["total_nodes"] == 0:
            recommendations.append("Build the knowledge graph first")

        review["recommendations"] = recommendations
        return review

    # --- Dependency Graph ---
    def dependency_graph(self) -> dict[str, Any]:
        deps = defaultdict(list)
        for edge in self.graph.graph.edges:
            if edge.edge_type == "depends_on":
                deps[edge.source].append(edge.target)
        return {
            "total_dependencies": len(self.graph.graph.edges),
            "dependencies": dict(deps),
        }

    # --- Prompt Generation ---
    def generate_prompts(self, target_type: str = "architecture") -> list[dict[str, Any]]:
        prompts = []
        if target_type == "architecture":
            prompts.append({
                "name": "architecture_review_prompt",
                "role": "system",
                "content": (
                    "You are an architecture reviewer for Project 31A. "
                    "Analyze the provided architecture artifacts and identify: "
                    "1) Structural issues 2) Missing components 3) Dependency problems "
                    "4) Scalability concerns 5) Security considerations."
                ),
            })
            prompts.append({
                "name": "capability_analysis_prompt",
                "role": "system",
                "content": (
                    "You are a capability analyst. Review the capabilities "
                    "and identify overlaps, gaps, and dependency issues."
                ),
            })
        return prompts

    # --- Documentation Generation ---
    def generate_documentation(self, output_dir: str | Path = "_docs") -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []

        # Architecture overview
        arch = self.architecture_review()
        content = [
            "# Project 31A — Architecture Overview",
            "",
            f"**Generated**: {__import__('datetime').datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Total nodes: {arch['total_nodes']}",
            f"- Total edges: {arch['total_edges']}",
            f"- Circular dependencies: {arch['circular_dependencies']}",
            f"- Orphan nodes: {arch['orphans']}",
            "",
            "## Recommendations",
        ]
        for rec in arch.get("recommendations", []):
            content.append(f"- {rec}")

        doc_path = output_dir / "ARCHITECTURE_REVIEW.md"
        doc_path.write_text("\n".join(content))
        generated.append(doc_path)

        # Roadmap skeleton
        roadmap = [
            "# Project 31A — Roadmap",
            "",
            "## Phase 1: Foundation",
            "- [ ] Integrate with Venus Genesis-I",
            "- [ ] Compile existing artifacts",
            "- [ ] Build knowledge graph",
            "",
            "## Phase 2: Analysis",
            "- [ ] Run capability analysis",
            "- [ ] Identify architectural issues",
            "- [ ] Generate improvement plan",
            "",
            "## Phase 3: Evolution",
            "- [ ] Implement recommendations",
            "- [ ] Continuous validation",
            "- [ ] Autonomous improvement",
        ]
        roadmap_path = output_dir / "ROADMAP.md"
        roadmap_path.write_text("\n".join(roadmap))
        generated.append(roadmap_path)

        return generated

    # --- Risk Analysis ---
    def risk_analysis(self) -> dict[str, Any]:
        risks = []
        cycles = self.graph.detect_circular_dependencies()
        if cycles:
            risks.append({
                "risk": "Circular Dependencies",
                "severity": "high",
                "description": f"{len(cycles)} circular dependency chains detected",
                "mitigation": "Refactor dependencies to break cycles",
            })

        orphans = self.graph.detect_orphans()
        if len(orphans) > 10:
            risks.append({
                "risk": "Orphaned Components",
                "severity": "medium",
                "description": f"{len(orphans)} nodes with no edges",
                "mitigation": "Connect or remove orphaned components",
            })

        return {
            "total_risks": len(risks),
            "risks": risks,
            "overall_risk": "high" if any(r["severity"] == "high" for r in risks) else "medium" if risks else "low",
        }

    # --- Autonomous Review ---
    def autonomous_review(self) -> dict[str, Any]:
        """Full autonomous review combining all analyses."""
        return {
            "architecture": self.architecture_review(),
            "capabilities": self.analyze_capabilities(),
            "risks": self.risk_analysis(),
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> list[dict[str, Any]]:
        recs = []
        cycles = self.graph.detect_circular_dependencies()
        if cycles:
            recs.append({
                "priority": "critical",
                "action": "Refactor circular dependencies",
                "details": f"Resolve {len(cycles)} dependency cycles",
            })
        return recs

    def summary(self) -> dict[str, Any]:
        return {
            "project": "Project 31A",
            "status": "integrated",
            "architecture_review": self.architecture_review(),
            "total_risks": self.risk_analysis()["total_risks"],
        }

from collections import defaultdict
