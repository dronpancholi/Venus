"""Naming validation — validates file and entity naming conventions."""

import re
from pathlib import Path
from typing import Any

from genesis.validation.base import BaseValidator, ValidationResult


class NamingValidator(BaseValidator):
    """Validates naming conventions for files and entities."""

    def __init__(self):
        super().__init__("naming_validator", "naming")
        self.patterns = {
            "schema": re.compile(r"^[A-Z][A-Z0-9_]*_SCHEMA\.json$"),
            "markdown": re.compile(r"^[A-Z][A-Z0-9_]*\.md$"),
            "python": re.compile(r"^[a-z][a-z0-9_]*\.py$"),
            "yaml": re.compile(r"^[a-z][a-z0-9_]*\.ya?ml$"),
            "dsl": re.compile(r"^[a-z][a-z0-9_]*\.venus$"),
        }

    def validate(self, target: Any) -> ValidationResult:
        name = target if isinstance(target, str) else target.get("name", "")
        path = target.get("path", "") if isinstance(target, dict) else ""

        if not name:
            return self.result(True, "No name to validate", severity="info", location=path)

        suffix = Path(name).suffix
        stem = Path(name).stem

        # Determine pattern
        pattern_map = {
            ".json": "schema" if stem.endswith("_SCHEMA") else None,
            ".md": "markdown",
            ".py": "python",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".venus": "dsl",
        }

        expected_pattern_name = pattern_map.get(suffix)
        if not expected_pattern_name:
            return self.result(True, "No naming convention for this extension", severity="info", location=path)

        pattern = self.patterns.get(expected_pattern_name)
        if pattern and not pattern.match(name):
            return self.result(
                False,
                f"File '{name}' does not match {expected_pattern_name} convention: {pattern.pattern}",
                severity="warning",
                location=path,
            )

        return self.result(True, f"Naming convention OK for {name}", severity="info", location=path)
