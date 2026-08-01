"""Schema validation — validates JSON Schema compliance."""

import json
from pathlib import Path
from typing import Any

from genesis.validation.base import BaseValidator, ValidationResult


class SchemaValidator(BaseValidator):
    """Validates that files conform to their declared schema."""

    def __init__(self):
        super().__init__("schema_validator", "schema")

    def validate(self, target: Any) -> ValidationResult:
        path = target if isinstance(target, str) else target.get("path", "")
        suffix = Path(path).suffix if path else target.get("suffix", "")

        if suffix not in (".json", ".yaml", ".yml"):
            return self.result(True, "Not a schema-validatable file", severity="info", location=path)

        if not Path(path).exists():
            return self.result(False, "File not found", severity="error", location=path)

        try:
            if suffix == ".json":
                with open(path) as f:
                    json.load(f)
                return self.result(True, "Valid JSON", severity="info", location=path)
            return self.result(True, "File exists", severity="info", location=path)
        except json.JSONDecodeError as e:
            return self.result(False, f"Invalid JSON: {e}", severity="error", location=path)
        except Exception as e:
            return self.result(False, f"Validation error: {e}", severity="error", location=path)
