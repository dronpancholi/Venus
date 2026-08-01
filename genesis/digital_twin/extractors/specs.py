from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class SpecsExtractor:
    """Dimension 10: Map specification references and ADR traceability."""

    NORM_PATTERN = re.compile(r">>\s*NORMATIVE\s*:\s*(.*)")
    ADR_PATTERN = re.compile(r"ADR-\d+")
    SPEC_REF_PATTERN = re.compile(r"(VPS|Part)\s+[XIV]+\b|VPS\s+\d+\.\d+")

    def __init__(self, root: Path):
        self.root = root

    def run(self, twin: DigitalTwin):
        for path in sorted(self.root.rglob("*.md")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(self.root))
            try:
                text = path.read_text()
            except (UnicodeDecodeError, OSError):
                continue

            for i, line in enumerate(text.splitlines()):
                nm = self.NORM_PATTERN.search(line)
                if nm:
                    nid = f"norm:{rel}:{i+1}"
                    req_node = TwinNode(
                        id=nid, kind="normative", label=nm.group(1).strip()[:80],
                        file_path=rel, first_line=i+1,
                    )
                    req_node.purpose = nm.group(1).strip()
                    twin.add_node(req_node)
                    twin.add_edge(nid, rel, "defined_in")

            # — detect ADR nodes —
            for match in self.ADR_PATTERN.finditer(text):
                adr_id = match.group(0)
                if not twin.get_node(adr_id):
                    title_match = re.search(
                        rf"#\s+{re.escape(adr_id)}[:\s]+(.+)", text, re.MULTILINE
                    )
                    label = title_match.group(1)[:80] if title_match else adr_id
                    adr_node = TwinNode(
                        id=adr_id, kind="adr", label=label,
                        file_path=rel, purpose=f"Architecture Decision Record: {adr_id}",
                    )
                    twin.add_node(adr_node)
                    twin.add_edge(adr_id, rel, "defined_in")

            adrs = self.ADR_PATTERN.findall(text)
            spec_refs = self.SPEC_REF_PATTERN.findall(text)

            file_node = twin.get_node(rel)
            if file_node and (adrs or spec_refs):
                file_node.adr_refs = list(set(file_node.adr_refs + adrs))
                file_node.spec_refs = list(set(file_node.spec_refs + spec_refs))
                twin.add_node(file_node)

    def link_nodes_to_specs(self, twin: DigitalTwin):
        # — keyword-based mapping from class patterns to spec topics —
        keyword_map: dict[str, list[str]] = {
            "compiler": ["compilation", "compiler", "compile", "parser", "ast", "uir", "pass", "generator", "pipeline"],
            "store": ["store", "storage", "persist", "sqlite", "checkpoint", "artifact"],
            "event": ["event", "bus", "publish", "subscribe", "emit", "observation"],
            "engine": ["engine", "execution", "runtime", "schedule", "task"],
            "service": ["service", "extension", "plugin", "module"],
            "registry": ["discovery", "register", "registry", "resolution"],
            "protocol": ["interface", "contract", "protocol", "abstraction"],
            "capability": ["capability", "feature", "extension", "activation"],
            "security": ["security", "sandbox", "permission", "trust", "audit"],
            "certification": ["certification", "certify", "verif"],
            "graph": ["graph", "topology", "relationship", "edge", "node"],
            "metadata": ["metadata", "identity", "type", "version"],
            "diagnostics": ["diagnostic", "observation", "observability", "monitor"],
            "memory": ["memory", "transient", "in-memory"],
            "validator": ["validation", "validator", "verify", "check", "constraint"],
            "repository": ["graph", "repository", "index"],
            "project": ["project", "package", "manager"],
            "platform": ["platform", "runtime", "venus", "implementation"],
        }

        for node in twin.find_nodes(kind="class"):
            label = (node.label or "").lower()
            name_words = set()
            for part in label.split("_"):
                for word in (
                    [part] + [part[i:i+3] for i in range(len(part)-2)]
                ):
                    if len(word) >= 4:
                        name_words.add(word)

            for keyword, spec_keywords in keyword_map.items():
                if keyword in label:
                    for spec_node in twin.find_nodes(kind="normative"):
                        spec_text = (spec_node.purpose or "").lower()
                        if any(sk in spec_text for sk in spec_keywords):
                            if spec_node.id not in node.spec_refs:
                                node.spec_refs.append(spec_node.id)
                                twin.add_edge(node.id, spec_node.id, "implements")
