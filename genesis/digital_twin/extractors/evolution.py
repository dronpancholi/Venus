from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class EvolutionExtractor:
    """Dimension 12: Extract evolution history via git."""

    def __init__(self, root: Path):
        self.root = root

    def _git(self, *args: str) -> list[str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.root)] + list(args),
                capture_output=True, text=True, timeout=10,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except Exception:
            return []

    def run(self, twin: DigitalTwin):
        if not (self.root / ".git").exists():
            return

        tracked = self._git("ls-files")
        file_map = {str(Path(f)) for f in tracked}

        for node in twin.find_nodes(kind="file"):
            fp = node.file_path or ""
            if fp not in file_map:
                continue

            log = self._git("log", "--oneline", "--follow", "--", fp)
            if log:
                change_count = len(log)
                node.change_frequency = change_count
                for entry in log[:5]:
                    parts = entry.split(" ", 1)
                    node.version_history.append({
                        "hash": parts[0],
                        "message": parts[1] if len(parts) > 1 else "",
                    })
                twin.add_node(node)
