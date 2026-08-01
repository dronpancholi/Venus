"""
VRIP Phase 1 — Semantic Extraction

Reads every artifact and extracts structured knowledge:
classes, capabilities, events, interfaces, protocols, algorithms, state machines.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .kgraph import KnowledgeGraph


class SemanticExtractor:
    """Phase 1: Extract semantic entities from all source files."""

    def __init__(self, root: Path):
        self.root = root

    def run(self, kg: KnowledgeGraph):
        for path in sorted(self.root.rglob("*.py")):
            if "__pycache__" in str(path):
                continue
            rel = str(path.relative_to(self.root))
            try:
                tree = ast.parse(path.read_text())
                self._extract_module(kg, rel, tree)
            except SyntaxError:
                pass

        # Extract from markdown specs
        for path in sorted(self.root.rglob("*.md")):
            if "__pycache__" in str(path) or not path.is_file():
                continue
            rel = str(path.relative_to(self.root))
            self._extract_markdown(kg, rel, path.read_text())

    def _extract_module(self, kg: KnowledgeGraph, rel: str, tree: ast.AST):
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
                kind = "protocol" if "Protocol" in bases else "interface" if "ABC" in bases else "class"
                kg.add_node(kind, f"{rel}::{node.name}", label=node.name, module=rel, bases=bases)
                kg.add_edge(f"{rel}::{node.name}", rel, "defined_in")
            elif isinstance(node, ast.FunctionDef):
                kg.add_node("function", f"{rel}::{node.name}", label=node.name, module=rel)
                kg.add_edge(f"{rel}::{node.name}", rel, "defined_in")

    def _extract_markdown(self, kg: KnowledgeGraph, rel: str, content: str):
        # Extract normative statements (>> NORMATIVE: ...)
        for i, line in enumerate(content.splitlines()):
            if ">> NORMATIVE:" in line:
                req_id = f"norm:{rel}:{i+1}"
                text = line.split(">> NORMATIVE:")[-1].strip()
                kg.add_node("normative", req_id, label=text[:80], source=rel, line=i+1, text=text)
                kg.add_edge(req_id, rel, "defined_in")

        # Extract ADRs
        if rel.startswith("decisions/") or "ADR" in rel:
            title_match = re.search(r"^#\s+(ADR-\d+.*)", content, re.MULTILINE)
            if title_match:
                adr_id = title_match.group(1).split(":")[0].strip()
                kg.add_node("adr", adr_id, label=title_match.group(1), source=rel)
                kg.add_edge(adr_id, rel, "defined_in")

        # Extract section headers as architecture concepts
        for match in re.finditer(r"^##\s+(.+)", content, re.MULTILINE):
            section = match.group(1).strip()
            if any(kw in section.lower() for kw in ["architecture", "capability", "specification", "storage", "persistence"]):
                node_id = f"section:{rel}:{section}"
                kg.add_node("arch_concept", node_id, label=section, source=rel)
                kg.add_edge(node_id, rel, "defined_in")

    def summary(self, kg: KnowledgeGraph) -> dict[str, Any]:
        return kg.count_by_kind()
