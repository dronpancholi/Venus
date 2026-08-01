"""Go source — modules, versions, metadata."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class GoSource(AcquisitionSource):
    source_name = "go"
    entity_type = EntityType.GO_MODULE
    base_url = "https://proxy.golang.org"
    interval_seconds = 43200.0
    confidence = 0.85

    def __init__(self, modules: list[str] | None = None):
        self.modules = modules or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for mod in self.modules:
            rec = self.fetch_one(mod)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, module_path: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        # Go proxy list versions
        url = f"{self.base_url}/{module_path}/@v/list"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode().strip().split("\n")
        except Exception:
            return None
        versions = [v.strip() for v in data if v.strip()]
        latest = versions[-1] if versions else ""
        # Fetch latest version info
        info_url = f"{self.base_url}/{module_path}/@v/{latest}.info"
        info_data: dict = {}
        try:
            req2 = urllib.request.Request(info_url)
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                info_data = json.loads(resp2.read().decode())
        except Exception:
            pass
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"go:{module_path}",
            name=module_path,
            description="",
            raw_data=info_data,
            metadata={
                "latest_version": latest,
                "all_versions": versions,
                "version_count": len(versions),
                "go_version": info_data.get("GoVersion", ""),
                "created": info_data.get("Time", ""),
            },
            confidence=self.confidence,
            tags=["package", "go", "golang"],
            url=f"https://pkg.go.dev/{module_path}",
        )
