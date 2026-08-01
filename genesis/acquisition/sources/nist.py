"""NIST source — frameworks, standards, special publications."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class NISTSource(AcquisitionSource):
    source_name = "nist"
    entity_type = EntityType.NIST_FRAMEWORK
    base_url = "https://www.nist.gov"
    interval_seconds = 86400.0
    confidence = 0.95

    def __init__(self, publications: list[str] | None = None):
        self.publications = publications or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for pub in self.publications:
            rec = self.fetch_one(pub)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, pub_id: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"https://services.nist.gov/rest/publication/v1/publication?id={pub_id}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        results = data if isinstance(data, list) else data.get("results", [data])
        if not results:
            return None
        result = results[0] if isinstance(results, list) else results
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"nist:{pub_id}",
            name=result.get("title", pub_id),
            description=result.get("abstract", ""),
            raw_data=result,
            metadata={
                "publication_id": pub_id,
                "authors": result.get("authors", []),
                "published_date": result.get("publishedDate", ""),
                "revision_date": result.get("revisionDate", ""),
                "doi": result.get("doi", ""),
                "series": result.get("series", ""),
                "keywords": result.get("keywords", []),
            },
            confidence=self.confidence,
            tags=["nist", "standard", "framework"] + (result.get("keywords") or []),
            url=f"https://www.nist.gov/publications/{pub_id}",
        )
