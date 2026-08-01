"""
VRIP Standardized Report — Repository-agnostic intelligence output.

Every VRIP analysis produces this canonical report format.
Allows Venus to analyze ANY repository, not just itself.

Schema:
  vrip_version     — Report format version
  repository       — Census data (files, lines, languages)
  architecture     — Module/class/function counts, layer analysis
  dependencies     — Import graph analysis, cycle detection
  capabilities     — Detected capability patterns
  persistence      — Detected storage patterns
  observability    — Detected event/logging patterns
  knowledge_graph  — Node/edge summary
  gaps             — Detected improvement opportunities
  maturity         — Composite maturity score
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EMPTY_REPORT: dict[str, Any] = {
    "vrip_version": "1.0",
    "repository": {
        "root": "",
        "analyzed_at": "",
        "files": 0,
        "lines": 0,
        "languages": {},
    },
    "architecture": {
        "total_modules": 0,
        "total_classes": 0,
        "total_functions": 0,
        "layers_detected": [],
        "dependencies": {"total_edges": 0, "cycles": []},
    },
    "capabilities": {
        "total_detected": 0,
        "list": [],
    },
    "persistence": {
        "stores_detected": 0,
        "wired_count": 0,
    },
    "observability": {
        "event_systems": [],
        "logging_frameworks": [],
        "services_with_events": 0,
    },
    "knowledge_graph": {
        "total_nodes": 0,
        "total_edges": 0,
    },
    "gaps": [],
    "maturity": {
        "overall": 0.0,
        "specification_coverage": 0.0,
        "architecture_health": 0.0,
        "test_density": 0.0,
    },
}


def detect_languages(root: Path) -> dict[str, int]:
    """Detect file types in a repository for language distribution."""
    counts: dict[str, int] = {}
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".rb": "ruby",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".html": "html",
        ".css": "css",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c_header",
        ".rs": "rust",
        ".swift": "swift",
        ".kt": "kotlin",
    }
    for fp in root.rglob("*"):
        if fp.is_file() and fp.suffix in ext_map:
            lang = ext_map[fp.suffix]
            counts[lang] = counts.get(lang, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def build_standard_report(
    root: Path | str,
    census_summary: dict[str, Any] | None = None,
    kg_summary: dict[str, Any] | None = None,
    gaps: list[dict[str, Any]] | None = None,
    architecture: dict[str, Any] | None = None,
    capabilities: dict[str, Any] | None = None,
    persistence: dict[str, Any] | None = None,
    events: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standardized VRIP report from analysis results."""
    report = dict(EMPTY_REPORT)
    report["repository"]["root"] = str(root)
    report["repository"]["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    report["repository"]["languages"] = detect_languages(Path(root))

    if census_summary:
        report["repository"]["files"] = census_summary.get("total_files", 0)
        report["repository"]["lines"] = census_summary.get("total_lines", 0)

    if kg_summary:
        report["knowledge_graph"]["total_nodes"] = kg_summary.get("total_nodes", 0)
        report["knowledge_graph"]["total_edges"] = kg_summary.get("total_edges", 0)

    if gaps:
        report["gaps"] = list(gaps)

    if architecture:
        report["architecture"].update(architecture)

    if capabilities:
        report["capabilities"]["total_detected"] = capabilities.get("total", 0)
        report["capabilities"]["list"] = capabilities.get("list", [])

    if persistence:
        report["persistence"]["stores_detected"] = persistence.get("providers", 0)
        report["persistence"]["wired_count"] = persistence.get("wired_to_services", 0)

    if events:
        report["observability"].update(events)

    return report


def format_report_text(report: dict[str, Any]) -> str:
    """Format a standardized VRIP report as human-readable text."""
    repo = report["repository"]
    arch = report["architecture"]
    kg = report["knowledge_graph"]
    gaps = report["gaps"]
    maturity = report["maturity"]

    lines = [
        "=" * 60,
        "VRIP REPOSITORY INTELLIGENCE REPORT",
        "=" * 60,
        "",
        f"Repository: {repo['root']}",
        f"Files: {repo['files']} | Lines: {repo['lines']}",
        f"Languages: {', '.join(f'{k}={v}' for k, v in repo.get('languages', {}).items())}",
        "",
        f"Architecture:",
        f"  Modules: {arch['total_modules']} | Classes: {arch['total_classes']} | Functions: {arch['total_functions']}",
        f"  Dependencies: {arch.get('dependencies', {}).get('total_edges', 0)} edges",
        f"  Cycles: {len(arch.get('dependencies', {}).get('cycles', []))}",
        "",
        f"Knowledge Graph: {kg['total_nodes']} nodes, {kg['total_edges']} edges",
        f"Capabilities: {report['capabilities']['total_detected']} detected",
        f"Persistence: {report['persistence']['wired_count']}/{report['persistence']['stores_detected']} wired",
        f"Gaps: {len(gaps)}",
        "",
    ]

    if gaps:
        lines.append("TOP GAPS:")
        for g in gaps[:5]:
            lines.append(f"  [{g.get('priority', '?')}] {g.get('title', '?')}")
        lines.append("")

    lines.append(f"Maturity: {maturity['overall']*100:.0f}%")
    lines.append("=" * 60)
    return "\n".join(lines)
