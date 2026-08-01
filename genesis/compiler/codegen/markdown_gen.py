"""Markdown code generator — produces documentation from UIR."""

from pathlib import Path
from typing import Any

from genesis.compiler.codegen.base import CodeGenerator
from genesis.core.uir import CompilationUnit


class MarkdownGenerator(CodeGenerator):
    """Generates Markdown documentation from a CompilationUnit."""

    def __init__(self):
        super().__init__("markdown_generator", "markdown")

    def generate(self, cu: CompilationUnit, output_dir: str | Path) -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []

        # Generate overview document
        overview = self._generate_overview(cu)
        overview_path = output_dir / "OVERVIEW.md"
        overview_path.write_text(overview)
        generated.append(overview_path)

        # Generate node catalog
        catalog = self._generate_node_catalog(cu)
        catalog_path = output_dir / "UIR_CATALOG.md"
        catalog_path.write_text(catalog)
        generated.append(catalog_path)

        return generated

    def _generate_overview(self, cu: CompilationUnit) -> str:
        lines = [
            f"# Compilation Overview",
            f"",
            f"**Source**: {cu.source_path}",
            f"**Format**: {cu.source_format}",
            f"**Compiled**: {cu.compiled_at}",
            f"**Passes**: {', '.join(cu.passes_applied) or 'none'}",
            f"",
            f"## Graphs",
            f"",
        ]
        for gname, graph in cu.all_graphs().items():
            lines.append(f"- **{gname}**: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        lines.append("")
        lines.append("## Dependency Order")
        order = cu.dependencies.resolve_order()
        for item in order[:20]:
            label = cu.ast.nodes.get(item)
            lines.append(f"- {item} ({label.label if label else 'unknown'})")
        if len(order) > 20:
            lines.append(f"- ... and {len(order) - 20} more")
        return "\n".join(lines)

    def _generate_node_catalog(self, cu: CompilationUnit) -> str:
        lines = ["# UIR Node Catalog", "", "| Node ID | Semantic Type | Label |", "|---------|--------------|-------|"]
        for nid, node in sorted(cu.ast.nodes.items()):
            lines.append(f"| {nid[:40]} | {node.semantic_type} | {node.label[:50]} |")
        lines.append("")
        lines.append(f"**Total nodes**: {len(cu.ast.nodes)}")
        return "\n".join(lines)
