"""RFC source — IETF RFC documents, metadata."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class RFCSource(AcquisitionSource):
    source_name = "rfc"
    entity_type = EntityType.RFC_DOCUMENT
    base_url = "https://www.rfc-editor.org/rfc"
    interval_seconds = 86400.0
    confidence = 0.95

    def __init__(self, rfc_numbers: list[int] | None = None):
        self.rfc_numbers = rfc_numbers or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for num in self.rfc_numbers:
            rec = self.fetch_one(str(num))
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, rfc_id: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        num = rfc_id.replace("rfc", "").strip()
        # RFC index API
        url = f"https://www.rfc-editor.org/rfc/index/rfc-index.json"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        # Find specific RFC
        entries = (data.get("rfc_index") or []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        for entry in entries:
            if str(entry.get("rfc_number", "")) == num:
                return AcquisitionRecord(
                    source=self.source_name,
                    entity_type=self.entity_type,
                    external_id=f"rfc:{num}",
                    name=f"RFC {num}",
                    description=entry.get("title", ""),
                    raw_data=entry,
                    metadata={
                        "rfc_number": int(num),
                        "authors": entry.get("authors", []),
                        "area": entry.get("area", ""),
                        "status": entry.get("status", ""),
                        "stream": entry.get("stream", ""),
                        "pub_date": entry.get("pub_date", ""),
                        "doi": entry.get("doi", ""),
                        "obsoletes": entry.get("obsoletes", []),
                        "obsoleted_by": entry.get("obsoleted_by", []),
                        "updates": entry.get("updates", []),
                        "updated_by": entry.get("updated_by", []),
                        "keywords": entry.get("keywords", []),
                    },
                    confidence=self.confidence,
                    tags=["rfc", "standard", "ietf"] + (entry.get("keywords") or []),
                    url=f"https://www.rfc-editor.org/rfc/rfc{num}",
                )
        return None
