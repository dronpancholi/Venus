from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class ArchitectureExtractor:
    """Dimension 9: Map architectural role, layer, pattern."""

    LAYER_MAP = {
        "layer_0": 0, "layer_1": 1, "layer_2": 2, "layer_3": 3, "layer_4": 4,
        "genesis/persistence": 0,
        "genesis/di": 1,
        "genesis/events": 1,
        "genesis/compiler": 2,
        "genesis/graph": 2,
        "genesis/execution": 2,
        "genesis/metadata": 2,
        "genesis/diagnostics": 2,
        "genesis/indexer": 2,
        "genesis/plugin": 2,
        "genesis/capability": 2,
        "genesis/memory": 2,
        "genesis/package": 2,
        "genesis/project": 2,
        "genesis/certification": 2,
        "genesis/security": 2,
        "genesis/intelligence": 3,
        "genesis/digital_twin": 3,
        "digital_twin/extractors": 3,
        "digital_twin/analyzers": 3,
        "genesis/platform.py": 4,
        "genesis/tests": 0,
        "genesis/decisions": 1,
    }

    ROLE_KEYWORDS = {
        "store": "persistence_store",
        "event": "event_bus",
        "engine": "engine",
        "service": "service",
        "manager": "manager",
        "registry": "registry",
        "protocol": "protocol",
        "interface": "interface",
        "adapter": "adapter",
        "factory": "factory",
        "controller": "controller",
        "validator": "validator",
        "checker": "validator",
        "repository": "repository",
        "mapper": "mapper",
        "serializer": "serializer",
        "deserializer": "serializer",
    }

    def __init__(self, root: Path):
        self.root = root

    def run(self, twin: DigitalTwin):
        for node in twin.nodes:
            self._assign_layer(node)
            self._assign_role(node)
            self._assign_pattern(node)
            twin.add_node(node)

    def _path_segments(self, fp: str) -> list[str]:
        parts = fp.replace("\\", "/").split("/")
        segments = []
        for i in range(len(parts)):
            segments.append("/".join(parts[:i+1]))
        return segments

    def _assign_layer(self, node: TwinNode):
        fp = (node.file_path or "").lower()
        # — check full path segments first (most specific) —
        segments = self._path_segments(fp)
        for seg in reversed(segments):
            for key, layer in self.LAYER_MAP.items():
                if seg.endswith(key) or seg == key:
                    node.layer = layer
                    node.layer_name = f"L{layer}"
                    return

        # — fallback: check prefix via module structure —
        if node.module:
            parts = node.module.split(".")
            if len(parts) > 1:
                prefix = parts[1] if parts[0] == "genesis" else parts[0]
                for key, layer in self.LAYER_MAP.items():
                    if key.endswith(f"/{prefix}") or key == f"genesis/{prefix}":
                        node.layer = layer
                        node.layer_name = f"L{layer}"
                        return

        node.layer = 2
        node.layer_name = "L2"

    def _assign_role(self, node: TwinNode):
        if node.role:
            return
        label = (node.label or "").lower()
        for kw, role in self.ROLE_KEYWORDS.items():
            if kw in label:
                node.role = role
                return

    def _assign_pattern(self, node: TwinNode):
        label = (node.label or "").lower()
        if "abstract" in label or "base" in label:
            node.pattern = "template_method"
        elif "factory" in label:
            node.pattern = "factory"
        elif "singleton" in label:
            node.pattern = "singleton"
        elif "adapter" in label or "wrapper" in label:
            node.pattern = "adapter"
        elif "observer" in label or "listener" in label:
            node.pattern = "observer"
        elif "proxy" in label:
            node.pattern = "proxy"
        elif "strategy" in label:
            node.pattern = "strategy"
        elif "decorator" in label:
            node.pattern = "decorator"
        elif "command" in label:
            node.pattern = "command"
