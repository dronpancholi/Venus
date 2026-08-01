from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class SyntaxExtractor:
    """Dimension 1: Extract syntax trees for every Python file."""

    def __init__(self, root: Path):
        self.root = root

    def run(self, twin: DigitalTwin):
        for path in sorted(self.root.rglob("*.py")):
            if "__pycache__" in str(path) or not path.is_file():
                continue
            rel = str(path.relative_to(self.root))
            try:
                text = path.read_text()
                tree = ast.parse(text)
            except (SyntaxError, UnicodeDecodeError):
                continue

            # — file node —
            file_node = twin.get_node(rel) or TwinNode(id=rel, kind="file", label=path.name)
            file_node.file_path = rel
            file_node.module = rel.replace("/", ".").replace(".py", "")
            file_node.source_text = text[:5000]
            file_node.first_line = 1
            file_node.last_line = len(text.splitlines())
            twin.add_node(file_node)

            # — module-level classes/functions —
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    self._add_class(twin, rel, node, text)
                elif isinstance(node, ast.FunctionDef):
                    self._add_function(twin, rel, node, text)

    def _add_class(self, twin: DigitalTwin, rel: str, node: ast.ClassDef, text: str):
        nid = f"{rel}::{node.name}"
        cls_node = TwinNode(
            id=nid,
            kind="class",
            label=node.name,
            module=rel.replace("/", ".").replace(".py", ""),
            file_path=rel,
            first_line=node.lineno or 0,
            last_line=getattr(node, "end_lineno", node.lineno or 0),
        )
        cls_node.source_text = self._extract_source(text, node)
        cls_node.ast_json = {"lineno": node.lineno, "col_offset": node.col_offset}
        twin.add_node(cls_node)
        twin.add_edge(nid, rel, "defined_in")

        # — methods —
        for item in ast.iter_child_nodes(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                mid = f"{nid}::{item.name}"
                mnode = TwinNode(
                    id=mid,
                    kind="method",
                    label=item.name,
                    module=cls_node.module,
                    file_path=rel,
                    first_line=item.lineno or 0,
                    last_line=getattr(item, "end_lineno", item.lineno or 0),
                )
                doc = ast.get_docstring(item)
                if doc:
                    mnode.docstring = doc[:200]
                mnode.source_text = self._extract_source(text, item)
                twin.add_node(mnode)
                twin.add_edge(mid, nid, "member_of")

    def _add_function(self, twin: DigitalTwin, rel: str, node: ast.FunctionDef, text: str):
        nid = f"{rel}::{node.name}"
        fn_node = TwinNode(
            id=nid,
            kind="function",
            label=node.name,
            module=rel.replace("/", ".").replace(".py", ""),
            file_path=rel,
            first_line=node.lineno or 0,
            last_line=getattr(node, "end_lineno", node.lineno or 0),
        )
        doc = ast.get_docstring(node)
        if doc:
            fn_node.docstring = doc[:200]
        fn_node.source_text = self._extract_source(text, node)
        twin.add_node(fn_node)
        twin.add_edge(nid, rel, "defined_in")

    def _extract_source(self, text: str, node: ast.AST) -> str | None:
        try:
            lines = text.splitlines()
            start = (node.lineno or 1) - 1
            end = getattr(node, "end_lineno", start + 1) or (start + 1)
            return "\n".join(lines[start:end])
        except Exception:
            return None
