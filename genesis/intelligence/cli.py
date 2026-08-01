"""
VRIP CLI — Multi-Repository Intelligence Analyzer.

Analyze ANY repository, not just Venus.
Produces standardized VRIP reports (JSON or text).

Usage:
  python -m genesis.intelligence.cli /path/to/repo [--json] [--output report.json]
  python -m genesis.intelligence.cli --self           # Analyze Venus itself
  python -m genesis.intelligence.cli --list-languages  # Show supported languages
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from genesis.digital_twin.analyzers import SmellAnalyzer, DriftAnalyzer, CouplingAnalyzer, EvolutionAnalyzer
from genesis.digital_twin.builder import DigitalTwinBuilder
from genesis.digital_twin.metrics import RepositoryMetrics
from genesis.digital_twin.discovery import InitiativeDiscovery
from genesis.intelligence.census import RepositoryCensus
from genesis.intelligence.engine import RepositoryIntelligence
from genesis.intelligence.kgraph import KnowledgeGraph
from genesis.intelligence.report import (
    build_standard_report,
    detect_languages,
    format_report_text,
)
from genesis.observatory.cli import register_subcommands, run_observe
from genesis.laboratory.cli import register_subcommands as register_lab_subcommands, run_lab


def analyze_repository(root: str | Path, json_output: bool = False) -> dict[str, Any]:
    """Run VRIP analysis on any repository, returning standardized report.

    Uses DigitalTwin as primary representation. Falls back to legacy
    KnowledgeGraph if DigitalTwin build fails.
    """
    root = Path(root).resolve()
    if not root.exists():
        print(f"Error: path does not exist: {root}", file=sys.stderr)
        sys.exit(1)

    # — Primary: DigitalTwin —
    try:
        builder = DigitalTwinBuilder(root)
        twin = builder.build()
        kg_summary = twin.summary()

        census_style_summary = {
            "total_files": len(twin.find_nodes(kind="file")),
            "total_lines": sum(
                (n.last_line or 0) for n in twin.find_nodes(kind="file")
            ),
        }

        python_files = twin.find_nodes(kind="file")
        all_classes = twin.find_nodes(kind="class")
        all_funcs = twin.find_nodes(kind="function")

        architecture = {
            "total_modules": len(python_files),
            "total_classes": len(all_classes),
            "total_functions": len(all_funcs),
            "layers_detected": list(twin.count_by_kind().keys()),
            "dependencies": {
                "total_edges": twin.edge_count,
                "cycles": [],
            },
        }

        report = build_standard_report(
            root=root,
            census_summary=census_style_summary,
            kg_summary=kg_summary,
            architecture=architecture,
        )

        # — Persistence from Twin —
        stores = twin.find_nodes(kind="store")
        wired_stores = [s for s in stores if s.persistence_kind]
        report["persistence"]["stores_detected"] = len(stores)
        report["persistence"]["wired_count"] = len(wired_stores)

        # — Capabilities from Twin —
        capability_classes = [n for n in twin.find_nodes(kind="class") if "capability" in (n.label or "").lower()]
        report["capabilities"]["total_detected"] = len(capability_classes)
        report["capabilities"]["list"] = [n.label for n in capability_classes]

        # — Enrich with DigitalTwin analyzers —
        smells = SmellAnalyzer().run(twin)
        drift = DriftAnalyzer().run(twin)
        coupling = CouplingAnalyzer().run(twin)
        evolution = EvolutionAnalyzer().run(twin)
        all_findings = smells + drift + coupling + evolution
        report["gaps"] = all_findings

        # — Repository mathematics —
        metrics = RepositoryMetrics().compute(twin)
        report["maturity"]["overall"] = metrics.get("repository_intelligence_score", 0)
        report["maturity"]["specification_coverage"] = metrics.get("specification_completeness", 0)
        report["maturity"]["architecture_health"] = metrics.get("maintainability_index", 0)
        report["maturity"]["test_density"] = metrics.get("contract_coverage", 0)
        report["metrics"] = metrics

        # — Initiatives —
        try:
            discovery = InitiativeDiscovery(twin)
            initiatives = discovery.discover_all()
            report["initiatives"] = initiatives
        except Exception:
            report["initiatives"] = []

    except Exception as e:
        # — Fallback: legacy KnowledgeGraph pipeline —
        print(f"  [VRIP] DigitalTwin build failed ({e}), falling back to KG", file=sys.stderr)
        kg = KnowledgeGraph()

        census = RepositoryCensus(root)
        census_data = census.run(kg)
        census_summary = census.summary()

        extractor = SemanticExtractor(root)
        extraction = extractor.run(kg)

        reverse = ReverseEngineer(kg)
        reverse_data = reverse.run()

        python_files = [n for n in kg.find_nodes(kind="file") if "py" in n.label]
        all_classes = kg.find_nodes(kind="class")
        all_funcs = kg.find_nodes(kind="function")

        architecture = {
            "total_modules": len(python_files),
            "total_classes": len(all_classes),
            "total_functions": len(all_funcs),
            "layers_detected": list(kg.count_by_kind().keys()),
            "dependencies": {
                "total_edges": len(reverse_data.get("import_edges", [])),
                "cycles": reverse_data.get("cycles", []),
            },
        }

        kg_summary = kg.summary()

        report = build_standard_report(
            root=root,
            census_summary=census_summary,
            kg_summary=kg_summary,
            architecture=architecture,
        )

        # Venus enrichment (fallback path only)
        if _is_venus_repo(root):
            venus_data = _enrich_venus(kg, root)
            report["capabilities"] = venus_data.get("capabilities", report["capabilities"])
            if "persistence" in venus_data:
                p = venus_data["persistence"]
                report["persistence"]["stores_detected"] = p.get("providers", p.get("stores_detected", 0))
                report["persistence"]["wired_count"] = p.get("wired_to_services", p.get("wired_count", 0))
            if "observability" in venus_data:
                o = venus_data["observability"]
                report["observability"]["services_with_events"] = o.get("services_with_events", 0)
                report["observability"]["wired_services"] = o.get("wired_services", [])
            report["gaps"] = venus_data.get("gaps", report["gaps"])
            if "maturity" in venus_data:
                m = venus_data["maturity"]
                report["maturity"]["overall"] = m.get("overall", report["maturity"]["overall"])

    return report


def _is_venus_repo(root: Path) -> bool:
    """Detect if a repository is a Venus platform repository."""
    indicators = [
        root / "VENUS_PLATFORM_SPECIFICATION.md",
        root / "genesis" / "VENUS_PLATFORM_SPECIFICATION.md",
        root / "genesis" / "intelligence",
        root / "genesis" / "capability",
    ]
    return any(p.exists() for p in indicators)


def _enrich_venus(kg: KnowledgeGraph, root: Path) -> dict[str, Any]:
    """Add Venus-specific analysis when running on Venus itself."""
    try:
        sys.path.insert(0, str(root))
        ri = RepositoryIntelligence(root=root, quiet=True)
        results = ri.run_all()
        metrics = results.get("phase_7_metrics", {})
        gaps = results.get("phase_8_gaps", [])

        capabilities = {
            "total_detected": len(kg.find_nodes(kind="capability")),
            "list": [n.label for n in kg.find_nodes(kind="capability")],
        }

        persistence = metrics.get("persistence", {"providers": 0, "wired_to_services": 0})
        events = metrics.get("event_coverage", {})
        maturity = results.get("platform_maturity", {"overall": 0})

        return {
            "capabilities": capabilities,
            "persistence": persistence,
            "observability": {
                "services_with_events": events.get("services_with_events", 0),
                "wired_services": events.get("wired_services", []),
            },
            "gaps": gaps,
            "maturity": {
                "overall": maturity.get("overall", 0) / 100,
            },
        }
    except Exception as e:
        return {"gaps": [{"priority": "P0", "title": f"Venus enrichment failed: {e}"}]}


def _run_evolution(root: Path, report: dict, max_changes: int = 5, list_hypotheses: bool = False):
    """Run the full Hypothesis→Simulate→Evolve pipeline."""
    from genesis.digital_twin.analyzers import (
        CouplingAnalyzer,
        DriftAnalyzer,
        EvolutionAnalyzer,
        SmellAnalyzer,
    )
    from genesis.digital_twin.builder import DigitalTwinBuilder
    from genesis.digital_twin.evolution import EvolutionEngine
    from genesis.digital_twin.hypothesis import HypothesisEngine
    from genesis.digital_twin.metrics import RepositoryMetrics
    from genesis.digital_twin.self_analysis import SelfAnalyzer

    print("  [Evolve] Building DigitalTwin...", file=sys.stderr)
    twin = DigitalTwinBuilder(root).build()

    print("  [Evolve] Running analyzers...", file=sys.stderr)
    all_findings = []
    for analyzer in [SmellAnalyzer(), DriftAnalyzer(), CouplingAnalyzer(), EvolutionAnalyzer()]:
        all_findings.extend(analyzer.run(twin))

    print(f"  [Evolve] Self-analysis...", file=sys.stderr)
    all_findings.extend(SelfAnalyzer(twin).analyze())

    print("  [Evolve] Computing metrics...", file=sys.stderr)
    metrics = RepositoryMetrics().compute(twin)

    print("  [Evolve] Generating hypotheses...", file=sys.stderr)
    hypotheses = HypothesisEngine(twin).generate(all_findings, metrics)
    print(f"  [Evolve] {len(hypotheses)} hypotheses generated", file=sys.stderr)

    if list_hypotheses:
        print(f"\nTop 20 hypotheses (of {len(hypotheses)}):")
        print(f"{'ROE':>8} {'Conf':>5} {'Risk':>5} {'Kind':25} {'Title'}")
        print("-" * 80)
        for h in hypotheses[:20]:
            print(f"{h.roe:>8.3f} {h.confidence:>4.0%} {h.risk:>4.1f} {h.kind:25} {h.title[:50]}")
        return

    print("  [Evolve] Simulating and applying changes...", file=sys.stderr)
    evolver = EvolutionEngine(twin)
    applied = evolver.evolve(hypotheses, max_changes=max_changes)

    print(evolver.generate_evolution_report())

    if not applied:
        print("\nNo quality-improving changes found. The platform is at local equilibrium.")
        print("Consider expanding scope or increasing metric sensitivity.")


def _run_omega(root: Path):
    """Run the complete OMEGA loop — all stages 0-22."""
    from genesis.digital_twin.analyzers import (
        CouplingAnalyzer,
        DriftAnalyzer,
        EvolutionAnalyzer,
        SmellAnalyzer,
    )
    from genesis.digital_twin.builder import DigitalTwinBuilder
    from genesis.digital_twin.evolution import EvolutionEngine
    from genesis.digital_twin.hypothesis import HypothesisEngine
    from genesis.digital_twin.metrics import RepositoryMetrics
    from genesis.digital_twin.predict import PredictionEngine
    from genesis.digital_twin.reasoning import ReasoningEngine
    from genesis.digital_twin.ris import RIScore
    from genesis.digital_twin.self_analysis import SelfAnalyzer
    from genesis.digital_twin.validation import EquilibriumDetector, ScientificValidator

    print("=" * 60)
    print("VENUS OMEGA LOOP")
    print("=" * 60)
    print()

    # Stages 0-2: Build DigitalTwin
    print("[Stage 0-2] Building DigitalTwin...")
    twin = DigitalTwinBuilder(root).build()
    print(f"  Twin: {twin.node_count} nodes, {twin.edge_count} edges")
    print(f"  Node kinds: {twin.count_by_kind()}")
    print()

    # Stage 3: Understanding (reasoning engine)
    print("[Stage 3-4] Reasoning & Understanding...")
    reasoning = ReasoningEngine(twin)
    conclusions = reasoning.reason_all()
    print(f"  Conclusions: {len(conclusions)}")
    for kind in ("deduction", "induction", "abduction", "explanatory"):
        count = len([c for c in conclusions if c.kind == kind])
        print(f"    {kind}: {count}")
    print()

    # Stage 5: Gap Discovery
    print("[Stage 5] Gap Discovery...")
    all_findings = []
    for analyzer in [SmellAnalyzer(), DriftAnalyzer(), CouplingAnalyzer(), EvolutionAnalyzer()]:
        all_findings.extend(analyzer.run(twin))
    all_findings.extend(SelfAnalyzer(twin).analyze())
    print(f"  Findings: {len(all_findings)}")
    print()

    # Stage 6: Scientific Hypothesis Generation
    print("[Stage 6] Hypothesis Generation...")
    metrics = RepositoryMetrics().compute(twin)
    hypotheses = HypothesisEngine(twin).generate(all_findings, metrics)
    print(f"  Hypotheses: {len(hypotheses)}")
    for h in hypotheses[:5]:
        print(f"    ROE={h.roe:.3f} {h.kind:25s} {h.title[:50]}")
    print()

    # Stage 7: Massive Simulation
    print("[Stage 7] Simulation & Evolution...")
    evolver = EvolutionEngine(twin)
    applied = evolver.evolve(hypotheses, max_changes=5)
    print(f"  Applied: {len(applied)} changes")
    for change in applied:
        print(f"    Δ={change.quality_delta:+.4f} {change.hypothesis.title[:60]}")
    print()

    # Stage 8: Repository Physics (in metrics)
    print("[Stage 8] Repository Physics...")
    for k in ["architectural_entropy", "information_density", "maintainability_index",
              "graph_diameter", "architectural_fractal_score", "subsystem_cohesion"]:
        print(f"    {k}: {metrics.get(k, '?')}")
    print()

    # Stage 11: Reasoning
    print("[Stage 11] Reasoning Conclusions...")
    for c in conclusions[:5]:
        print(f"    [{c.confidence:.0%}] {c.statement[:90]}")

    # Stage 12: Prediction
    print()
    print("[Stage 12] Prediction...")
    predictions = PredictionEngine(twin).predict_all()
    for p in predictions:
        print(f"    [{p.confidence:.0%}] {p.statement[:90]}")
    print()

    # Stage 20: Scientific Validation
    print("[Stage 20] Scientific Validation...")
    validator = ScientificValidator(twin, metrics)
    for h in hypotheses[:5]:
        result = validator.validate(h)
        print(f"    {'✓' if result.passed else ' '} {result.hypothesis_title[:55]} "
              f"score={result.overall_score:.2f}")
    print()

    # Stage 21: Repository Intelligence Score
    print("[Stage 21] Repository Intelligence Score...")
    ris = RIScore()
    score = ris.compute(twin)
    print(f"    Overall: {score['overall']:.4f}")
    print(f"    Trend: {score['trend_direction']}")
    for k, v in sorted(score['factors'].items(), key=lambda x: -x[1])[:10]:
        bar = '█' * int(v * 20)
        print(f"    {k:20s} {v:.3f} {bar}")
    print()

    # Stage 22: Equilibrium Detection
    print("[Stage 22] Equilibrium Detection...")
    signals = EquilibriumDetector(twin).analyze(hypotheses, metrics)
    for s in signals:
        print(f"    [{s.strength:.0%}] {s.kind}: {s.signal[:70]}")
        if s.assumption_challenged:
            print(f"      ↳ Challenge: {s.assumption_challenged[:70]}")
        if s.new_direction:
            print(f"      ↳ Next: {s.new_direction[:70]}")
    print()

    print("=" * 60)
    print("OMEGA LOOP COMPLETE")
    print(f"RIS: {score['overall']:.4f} | Hypotheses: {len(hypotheses)} | "
          f"Changes applied: {len(applied)} | Predictions: {len(predictions)}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="VRIP — Multi-Repository Intelligence Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m genesis.intelligence.cli /path/to/repo
  python -m genesis.intelligence.cli . --json
  python -m genesis.intelligence.cli --self --json --output report.json
  python -m genesis.intelligence.cli --list-languages
        """,
    )
    parser.add_argument("path", nargs="?", default=None, help="Repository path to analyze")
    parser.add_argument("--self", action="store_true", help="Analyze Venus itself (default if no path)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", type=str, help="Write output to file")
    parser.add_argument("--list-languages", action="store_true", help="List detected languages")
    parser.add_argument("--evolve", action="store_true", help="Run Hypothesis→Simulate→Evolve pipeline")
    parser.add_argument("--omega", action="store_true", help="Run full OMEGA loop (all stages)")
    parser.add_argument("--max-changes", type=int, default=5, help="Max changes for evolution cycle")
    parser.add_argument("--hypotheses", action="store_true", help="List generated hypotheses only")

    # — Observatory subcommand —
    sp = parser.add_subparsers(dest="command")
    register_subcommands(sp)
    register_lab_subcommands(sp)

    args = parser.parse_args()

    if args.command == "observe":
        return run_observe(args)
    if args.command == "lab":
        return run_lab(args)

    if args.list_languages:
        print("Supported languages:")
        for lang in sorted(detect_languages(Path.cwd()).keys()):
            print(f"  - {lang}")
        return

    if args.self or args.path is None:
        root = Path(__file__).resolve().parent.parent.parent
    else:
        root = Path(args.path)

    report = analyze_repository(root, json_output=args.json)

    if args.evolve:
        _run_evolution(root, report, args.max_changes, args.hypotheses)
        return

    if args.omega:
        _run_omega(root)
        return

    if args.output:
        output_path = Path(args.output)
        if args.json or output_path.suffix == ".json":
            output_path.write_text(json.dumps(report, indent=2))
        else:
            output_path.write_text(format_report_text(report))
        print(f"Report written to {output_path}")
    elif args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_report_text(report))


if __name__ == "__main__":
    main()
