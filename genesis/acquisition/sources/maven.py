"""Maven source — artifacts, metadata."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class MavenSource(AcquisitionSource):
    source_name = "maven"
    entity_type = EntityType.MAVEN_ARTIFACT
    base_url = "https://search.maven.org"
    interval_seconds = 43200.0
    confidence = 0.85

    def __init__(self, artifacts: list[str] | None = None):
        self.artifacts = artifacts or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for art in self.artifacts:
            rec = self.fetch_one(art)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, artifact_coord: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        parts = artifact_coord.split(":")
        if len(parts) < 2:
            return None
        group = parts[0].replace(".", "/")
        artifact = parts[1]
        url = f"https://search.maven.org/solrsearch/select?q=g:{group}+AND+a:{artifact}&rows=1&wt=json"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        docs = (data.get("response") or {}).get("docs") or []
        if not docs:
            return None
        doc = docs[0]
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"maven:{artifact_coord}",
            name=artifact_coord,
            description=doc.get("description", ""),
            raw_data=doc,
            metadata={
                "group_id": doc.get("g", ""),
                "artifact_id": doc.get("a", ""),
                "latest_version": doc.get("latestVersion", ""),
                "repository": doc.get("repository", ""),
                "version_count": doc.get("versionCount", 0),
                "ecosystem": doc.get("ec", ""),
                "tags": doc.get("tags", ""),
            },
            confidence=self.confidence,
            tags=["package", "maven", "java"],
            url=f"https://search.maven.org/artifact/{artifact_coord}",
        )
