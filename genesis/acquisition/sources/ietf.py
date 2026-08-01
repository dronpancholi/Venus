"""IETF source — standards, drafts, working groups."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class IETFSource(AcquisitionSource):
    source_name = "ietf"
    entity_type = EntityType.IETF_STANDARD
    base_url = "https://datatracker.ietf.org/api/v1"
    interval_seconds = 86400.0
    confidence = 0.95

    def __init__(self, documents: list[str] | None = None):
        self.documents = documents or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for doc in self.documents:
            rec = self.fetch_one(doc)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, doc_id: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"{self.base_url}/doc/document/{doc_id}/"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        doc = data if isinstance(data, dict) else {}
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"ietf:{doc_id}",
            name=doc_id,
            description=doc.get("abstract", ""),
            raw_data=doc,
            metadata={
                "type": doc.get("type", ""),
                "stream": doc.get("stream", ""),
                "status": doc.get("status", ""),
                "wg": doc.get("group", {}).get("acronym", "") if doc.get("group") else "",
                "authors": doc.get("authors", []),
                "pages": doc.get("pages", 0),
                "created": doc.get("time", ""),
                "revisions": doc.get("rev", ""),
                "keywords": doc.get("keywords", []),
            },
            confidence=self.confidence,
            tags=["ietf", "standard"] + doc.get("keywords", []),
            url=f"https://datatracker.ietf.org/doc/{doc_id}/",
        )
