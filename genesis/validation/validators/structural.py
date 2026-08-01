"""Structural validation — validates file structure, required fields, references."""

import json
from pathlib import Path
from typing import Any

from genesis.validation.base import BaseValidator, ValidationResult


class StructuralValidator(BaseValidator):
    """Validates structural integrity of artifacts."""

    def __init__(self):
        super().__init__("structural_validator", "quality")

    def validate(self, target: Any) -> ValidationResult:
        path = target if isinstance(target, str) else target.get("path", "")

        if not path or not Path(path).exists():
            return self.result(True, "No file to validate structurally", severity="info")

        p = Path(path)
        if p.suffix == ".json":
            return self._validate_json(p)
        elif p.suffix == ".md":
            return self._validate_markdown(p)
        else:
            return self.result(True, "No structural validation for this type", severity="info", location=path)

    def _validate_json(self, path: Path) -> ValidationResult:
        try:
            data = json.loads(path.read_text())
            checks = []
            if isinstance(data, dict):
                if not data.get("$schema") and not data.get("id"):
                    checks.append("missing $schema or id field")
                if len(json.dumps(data, default=str)) < 10:
                    checks.append("content appears empty or minimal")
            return self.result(
                len(checks) == 0,
                "; ".join(checks) if checks else "JSON structure OK",
                severity="warning" if checks else "info",
                location=str(path),
            )
        except Exception as e:
            return self.result(False, f"JSON structural error: {e}", severity="error", location=str(path))

    def _validate_markdown(self, path: Path) -> ValidationResult:
        try:
            content = path.read_text()
            checks = []
            if len(content.strip()) < 50:
                checks.append("file is very short (< 50 chars)")
            if not content.startswith("# "):
                checks.append("missing H1 heading")
            if content.count("TODO") > 3:
                checks.append(f"contains {content.count('TODO')} TODO markers")
            if content.count("{{") > 5:
                checks.append("contains unrendered template placeholders")
            return self.result(
                len(checks) == 0,
                "; ".join(checks) if checks else "Markdown structure OK",
                severity="warning" if checks else "info",
                location=str(path),
            )
        except Exception as e:
            return self.result(False, f"Markdown structural error: {e}", severity="error", location=str(path))
