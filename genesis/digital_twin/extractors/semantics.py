from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class SemanticsExtractor:
    """Dimension 2: Extract docstrings, purpose, and semantic tags."""

    def __init__(self, root: Path):
        self.root = root

    def run(self, twin: DigitalTwin):
        for node in twin.nodes:
            if node.kind not in ("class", "function", "method", "file"):
                continue
            if node.docstring:
                self._enrich_from_docstring(node)
            if node.kind == "file":
                self._infer_purpose(node)
            if node.label:
                self._infer_tags(node)

    def _enrich_from_docstring(self, node: TwinNode):
        ds = (node.docstring or "").lower()
        if not node.purpose:
            first_line = (node.docstring or "").split("\n")[0].strip()[:100]
            node.purpose = first_line

        for kw in ("store", "repository", "database", "persist"):
            if kw in ds:
                node.tags.append("persistence")
                break
        for kw in ("event", "publish", "subscribe", "emit"):
            if kw in ds:
                node.tags.append("event-driven")
                break
        for kw in ("service", "engine", "manager", "registry"):
            if kw in ds:
                node.tags.append("service")
                break
        for kw in ("protocol", "interface", "abstract", "contract"):
            if kw in ds:
                node.tags.append("contract")
                break
        for kw in ("test", "spec", "verify", "assert"):
            if kw in ds:
                node.tags.append("test")
                break

    def _infer_purpose(self, node: TwinNode):
        name = (node.label or "").lower()
        if "store" in name:
            node.purpose = f"Persistence store: {node.label}"
            node.tags.append("persistence")
        elif "event" in name or "bus" in name:
            node.purpose = f"Event system: {node.label}"
            node.tags.append("event-driven")
        elif "engine" in name:
            node.purpose = f"Engine: {node.label}"
            node.tags.append("service")
        elif "service" in name:
            node.purpose = f"Service: {node.label}"
            node.tags.append("service")

    def _infer_tags(self, node: TwinNode):
        name = node.label.lower()
        kw_map = {
            "store": "persistence",
            "event": "event-driven",
            "engine": "service",
            "service": "service",
            "manager": "service",
            "test": "test",
            "protocol": "contract",
            "interface": "contract",
            "abstract": "contract",
            "factory": "creational",
            "adapter": "structural",
            "observer": "behavioral",
            "singleton": "creational",
        }
        for kw, tag in kw_map.items():
            if kw in name:
                if tag not in node.tags:
                    node.tags.append(tag)
