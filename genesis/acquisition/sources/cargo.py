"""Cargo source — crates, versions, dependencies."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class CargoSource(AcquisitionSource):
    source_name = "cargo"
    entity_type = EntityType.CARGO_CRATE
    base_url = "https://crates.io/api/v1"
    interval_seconds = 43200.0
    confidence = 0.85

    def __init__(self, crates: list[str] | None = None):
        self.crates = crates or []

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": "venus-acquisition/1.0"}

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for cr in self.crates:
            rec = self.fetch_one(cr)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, crate_name: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"{self.base_url}/crates/{crate_name}"
        try:
            req = urllib.request.Request(url, headers=self._headers())
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        crate = data.get("crate") or {}
        versions = [v.get("num", "") for v in (data.get("versions") or [])]
        keywords = crate.get("keywords", [])
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"cargo:{crate_name}",
            name=crate_name,
            description=crate.get("description") or "",
            raw_data=data,
            metadata={
                "latest_version": crate.get("max_version", ""),
                "all_versions": versions,
                "downloads": crate.get("downloads", 0),
                "recent_downloads": crate.get("recent_downloads", 0),
                "homepage": crate.get("homepage", ""),
                "repository": crate.get("repository", ""),
                "documentation": crate.get("documentation", ""),
                "license": crate.get("license", ""),
                "keywords": [k.get("keyword", "") for k in keywords],
                "categories": [c.get("category", "") for c in (crate.get("categories") or [])],
                "created": crate.get("created_at", ""),
                "updated": crate.get("updated_at", ""),
            },
            confidence=self.confidence,
            tags=["package", "cargo", "rust"] + [k.get("keyword", "") for k in keywords],
            url=crate.get("homepage") or f"https://crates.io/crates/{crate_name}",
        )
