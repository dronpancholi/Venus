from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class TestsExtractor:
    """Dimension 11: Map tests to production nodes."""

    TEST_PREFIX = "test_"
    TEST_CLASS_PREFIX = "Test"

    def __init__(self, root: Path):
        self.root = root

    def run(self, twin: DigitalTwin):
        test_files = []
        for path in sorted(self.root.rglob("test_*.py")):
            if "__pycache__" in str(path) or not path.is_file():
                continue
            test_files.append(path)

        for path in test_files:
            rel = str(path.relative_to(self.root))
            try:
                text = path.read_text()
                tree = ast.parse(text)
            except (SyntaxError, UnicodeDecodeError):
                continue

            test_funcs = []
            test_classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith(self.TEST_PREFIX):
                    test_funcs.append(node.name)
                elif isinstance(node, ast.ClassDef) and node.name.startswith(self.TEST_CLASS_PREFIX):
                    test_classes.append(node.name)
                    for item in ast.walk(node):
                        if isinstance(item, ast.FunctionDef) and item.name.startswith(self.TEST_PREFIX):
                            test_funcs.append(f"{node.name}.{item.name}")

            # — link to tested production nodes —
            import_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_names.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        import_names.add(alias.name)

            for imp in import_names:
                target_mod = imp.replace(".", "/")
                for prod_node in twin.find_nodes(kind="class"):
                    if prod_node.module and (prod_node.module == imp or prod_node.module.endswith(f".{imp}")):
                        prod_node.test_file = rel
                        prod_node.test_count += len(test_funcs)
                        twin.add_edge(prod_node.id, rel, "tested_by")

                for prod_node in twin.find_nodes(kind="file"):
                    if prod_node.module and (prod_node.module == imp or prod_node.module.endswith(f".{imp}")):
                        prod_node.test_file = rel
                        prod_node.test_count += len(test_funcs)
                        twin.add_edge(prod_node.id, rel, "tested_by")

            # — add test file node —
            test_node = twin.get_node(rel) or TwinNode(id=rel, kind="test_file", label=path.name, file_path=rel)
            test_node.test_count = len(test_funcs)
            twin.add_node(test_node)
