"""PyPI source — packages, releases, metadata."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class PyPISource(AcquisitionSource):
    source_name = "pypi"
    entity_type = EntityType.PYPI_PACKAGE
    base_url = "https://pypi.org/pypi"
    interval_seconds = 43200.0
    confidence = 0.85

    def __init__(self, packages: list[str] | None = None):
        self.packages = packages or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for pkg in self.packages:
            rec = self.fetch_one(pkg)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, package_name: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"{self.base_url}/{package_name}/json"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        info = data.get("info") or {}
        latest_version = info.get("version", "")
        requires_dist = info.get("requires_dist") or []
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"pypi:{package_name}",
            name=package_name,
            description=info.get("summary") or "",
            raw_data=data,
            metadata={
                "latest_version": latest_version,
                "author": info.get("author", ""),
                "author_email": info.get("author_email", ""),
                "homepage": info.get("home_page", ""),
                "project_urls": info.get("project_urls", {}),
                "license": info.get("license", ""),
                "classifiers": info.get("classifiers", []),
                "requires_dist": requires_dist,
                "requires_python": info.get("requires_python", ""),
                "keywords": info.get("keywords", ""),
            },
            confidence=self.confidence,
            tags=["package", "pypi", "python"] + [c.split("::")[-1].strip() for c in (info.get("classifiers") or []) if "::" in c],
            url=info.get("home_page") or f"https://pypi.org/project/{package_name}/",
        )
