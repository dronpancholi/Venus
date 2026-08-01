"""npm source — packages, versions, dependencies."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class NPMSource(AcquisitionSource):
    source_name = "npm"
    entity_type = EntityType.NPM_PACKAGE
    base_url = "https://registry.npmjs.org"
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
        url = f"{self.base_url}/{package_name}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        latest = (data.get("dist-tags") or {}).get("latest", "")
        versions = data.get("versions") or {}
        latest_data = versions.get(latest) or {}
        deps = latest_data.get("dependencies") or {}
        dev_deps = latest_data.get("devDependencies") or {}
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"npm:{package_name}",
            name=package_name,
            description=data.get("description") or "",
            raw_data=data,
            metadata={
                "latest_version": latest,
                "all_versions": list(versions.keys()),
                "dependencies": deps,
                "dev_dependencies": dev_deps,
                "maintainers": data.get("maintainers", []),
                "homepage": latest_data.get("homepage", ""),
                "repository": latest_data.get("repository", ""),
                "license": latest_data.get("license", ""),
                "keywords": data.get("keywords", []),
                "author": latest_data.get("author", {}),
            },
            confidence=self.confidence,
            tags=["package", "npm", "javascript"] + (data.get("keywords") or []),
            url=latest_data.get("homepage") or f"https://www.npmjs.com/package/{package_name}",
        )
