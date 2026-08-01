from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class EventsExtractor:
    """Dimension 8: Detect event emissions and subscriptions."""

    EMIT_PATTERNS = [
        "emit", "publish", "post_event", "raise_event", "fire",
    ]
    SUBSCRIBE_PATTERNS = [
        "subscribe", "on_event", "listen", "register_handler", "connect",
    ]

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

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._check_event_class(twin, rel, node)
                elif isinstance(node, ast.FunctionDef):
                    self._check_event_function(twin, rel, node)

    def _check_event_class(self, twin: DigitalTwin, rel: str, node: ast.ClassDef):
        nid = f"{rel}::{node.name}"
        cls_node = twin.get_node(nid) or TwinNode(id=nid, kind="class", label=node.name, file_path=rel)

        for item in ast.walk(node):
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
                name = item.func.attr
                if name in self.EMIT_PATTERNS:
                    args = [a for a in item.args if isinstance(a, ast.Constant)]
                    for a in args:
                        if isinstance(a.value, str) and a.value not in cls_node.event_emissions:
                            cls_node.event_emissions.append(a.value)
                if name in self.SUBSCRIBE_PATTERNS:
                    args = [a for a in item.args if isinstance(a, ast.Constant)]
                    for a in args:
                        if isinstance(a.value, str) and a.value not in cls_node.event_subscriptions:
                            cls_node.event_subscriptions.append(a.value)

        if cls_node.event_emissions or cls_node.event_subscriptions:
            cls_node.tags.append("event-driven")
            twin.add_node(cls_node)

    def _check_event_function(self, twin: DigitalTwin, rel: str, node: ast.FunctionDef):
        nid = f"{rel}::{node.name}"
        fn_node = twin.get_node(nid) or TwinNode(id=nid, kind="function", label=node.name, file_path=rel)

        for item in ast.walk(node):
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
                name = item.func.attr
                if name in self.EMIT_PATTERNS:
                    args = [a for a in item.args if isinstance(a, ast.Constant)]
                    for a in args:
                        if isinstance(a.value, str) and a.value not in fn_node.event_emissions:
                            fn_node.event_emissions.append(a.value)
                if name in self.SUBSCRIBE_PATTERNS:
                    args = [a for a in item.args if isinstance(a, ast.Constant)]
                    for a in args:
                        if isinstance(a.value, str) and a.value not in fn_node.event_subscriptions:
                            fn_node.event_subscriptions.append(a.value)

        if fn_node.event_emissions or fn_node.event_subscriptions:
            fn_node.tags.append("event-driven")
            twin.add_node(fn_node)
