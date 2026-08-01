"""W3C source — web standards, specifications, recommendations."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class W3CSource(AcquisitionSource):
    source_name = "w3c"
    entity_type = EntityType.W3C_STANDARD
    base_url = "https://www.w3.org"
    interval_seconds = 86400.0
    confidence = 0.95

    def __init__(self, specs: list[str] | None = None):
        self.specs = specs or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for spec in self.specs:
            rec = self.fetch_one(spec)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, spec_shortname: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"https://www.w3.org/TR/{spec_shortname}/"
        import urllib.parse
        # Try TR API
        api_url = f"https://api.w3.org/specifications/{urllib.parse.quote(spec_shortname, safe='')}"
        try:
            req = urllib.request.Request(api_url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"w3c:{spec_shortname}",
            name=spec_shortname,
            description=data.get("title", ""),
            raw_data=data,
            metadata={
                "title": data.get("title", ""),
                "status": data.get("status", ""),
                "shortlink": data.get("shortlink", ""),
                "editor": data.get("editor", ""),
                "created": data.get("created", ""),
                "modified": data.get("modified", ""),
                "version": data.get("version", ""),
                "process_rule": data.get("process_rule", ""),
            },
            confidence=self.confidence,
            tags=["w3c", "web", "standard"],
            url=f"https://www.w3.org/TR/{spec_shortname}/",
        )
