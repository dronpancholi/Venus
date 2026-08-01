"""NuGet source — packages, versions, metadata."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class NuGetSource(AcquisitionSource):
    source_name = "nuget"
    entity_type = EntityType.NUGET_PACKAGE
    base_url = "https://api.nuget.org/v3"
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
        # NuGet V3 registration
        url = f"{self.base_url}/registration5-semver1/{package_name.lower()}/index.json"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        latest = ""
        versions: list[str] = []
        items = data.get("items") or []
        # Handle flat vs paged index
        first_item = items[0] if items else {}
        if "items" in first_item:
            for page in items:
                for entry in (page.get("items") or []):
                    v = (entry.get("catalogEntry") or {}).get("version", "")
                    if v:
                        versions.append(v)
        else:
            for entry in items:
                v = (entry.get("catalogEntry") or {}).get("version", "")
                if v:
                    versions.append(v)
        # NuGet catalog entries have package details
        catalog_url = f"{self.base_url}/catalog0/index.json"
        try:
            req2 = urllib.request.Request(catalog_url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                cat_data = json.loads(resp2.read().decode())
                pages = cat_data.get("items") or []
                if pages:
                    latest = (pages[-1].get("catalogPage") or {}).get("packageVersion", "")
        except Exception:
            pass
        if versions:
            latest = versions[-1]
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"nuget:{package_name}",
            name=package_name,
            description="",
            raw_data=data,
            metadata={
                "latest_version": latest,
                "all_versions": versions,
                "version_count": len(versions),
            },
            confidence=self.confidence,
            tags=["package", "nuget", "dotnet"],
            url=f"https://www.nuget.org/packages/{package_name}/",
        )
