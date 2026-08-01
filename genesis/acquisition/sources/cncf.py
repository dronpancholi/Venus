"""CNCF source — cloud native projects, maturity levels."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class CNCFSource(AcquisitionSource):
    source_name = "cncf"
    entity_type = EntityType.CNCF_PROJECT
    base_url = "https://landscape.cncf.io/api"
    interval_seconds = 86400.0
    confidence = 0.9

    def __init__(self, projects: list[str] | None = None):
        self.projects = projects or []

    def fetch(self) -> list[AcquisitionRecord]:
        import urllib.request
        import json
        records: list[AcquisitionRecord] = []
        url = "https://landscape.cncf.io/api/items"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return records
        items = data if isinstance(data, list) else data.get("items", [])
        for item in items:
            name = item.get("name", "")
            if self.projects and name not in self.projects:
                continue
            records.append(self._to_record(item))
        return records

    def fetch_one(self, project_name: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"https://landscape.cncf.io/api/items?name={project_name}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        items = data if isinstance(data, list) else data.get("items", [])
        for item in items:
            if item.get("name", "").lower() == project_name.lower():
                return self._to_record(item)
        return None

    def _to_record(self, item: dict) -> AcquisitionRecord:
        name = item.get("name", "")
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"cncf:{name.lower().replace(' ', '-')}",
            name=name,
            description=item.get("description", ""),
            raw_data=item,
            metadata={
                "maturity": item.get("maturity", ""),
                "category": item.get("category", ""),
                "homepage_url": item.get("homepage_url", ""),
                "repo_url": item.get("repo_url", ""),
                "logo": item.get("logo", ""),
                "joined": item.get("joined", ""),
                "github_stars": item.get("github_stars", 0),
                "primary_language": item.get("primary_language", ""),
                "cncf_tags": item.get("tags", []),
            },
            confidence=self.confidence,
            tags=["cncf", "cloud-native", "open-source"] + item.get("tags", []),
            url=item.get("homepage_url", ""),
        )
