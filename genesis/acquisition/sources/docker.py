"""Docker source — images, tags, metadata."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class DockerSource(AcquisitionSource):
    source_name = "docker"
    entity_type = EntityType.DOCKER_IMAGE
    base_url = "https://hub.docker.com/v2"
    interval_seconds = 43200.0
    confidence = 0.85

    def __init__(self, images: list[str] | None = None):
        self.images = images or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for img in self.images:
            rec = self.fetch_one(img)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, image_name: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        # Docker Hub API
        namespace = "library"
        repo = image_name
        if "/" in image_name:
            parts = image_name.split("/")
            namespace = parts[0]
            repo = "/".join(parts[1:])
        url = f"{self.base_url}/repositories/{namespace}/{repo}/tags?page_size=50"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        results = data.get("results") or []
        tags = [t.get("name", "") for t in results]
        latest_digest = results[0].get("digest", "") if results else ""
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"docker:{image_name}",
            name=image_name,
            description=f"Docker image {image_name}",
            raw_data=data,
            metadata={
                "tags": tags,
                "tag_count": data.get("count", 0),
                "latest_digest": latest_digest,
                "namespace": namespace,
                "repo": repo,
            },
            confidence=self.confidence,
            tags=["container", "docker", "image"],
            url=f"https://hub.docker.com/r/{namespace}/{repo}",
        )
