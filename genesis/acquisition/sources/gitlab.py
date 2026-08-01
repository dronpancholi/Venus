"""GitLab source — repositories, metadata."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class GitLabSource(AcquisitionSource):
    source_name = "gitlab"
    entity_type = EntityType.GITLAB_REPO
    base_url = "https://gitlab.com/api/v4"
    interval_seconds = 43200.0
    confidence = 0.9

    def __init__(self, token: str = "", groups: list[str] | None = None):
        self.token = token
        self.groups = groups or []

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/json"}
        if self.token:
            h["PRIVATE-TOKEN"] = self.token
        return h

    def fetch(self) -> list[AcquisitionRecord]:
        import urllib.request
        import json
        records: list[AcquisitionRecord] = []
        for group in self.groups:
            url = f"{self.base_url}/groups/{group}/projects?per_page=100&include_subgroups=true"
            try:
                req = urllib.request.Request(url, headers=self._headers())
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
            except Exception:
                continue
            for proj in data:
                records.append(self._to_record(proj))
        return records

    def fetch_one(self, project_id: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"{self.base_url}/projects/{project_id}"
        try:
            req = urllib.request.Request(url, headers=self._headers())
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            return self._to_record(data)
        except Exception:
            return None

    def _to_record(self, proj: dict) -> AcquisitionRecord:
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"gitlab:{proj.get('path_with_namespace', proj['id'])}",
            name=proj.get("path_with_namespace", proj.get("name", "")),
            description=proj.get("description") or "",
            raw_data=proj,
            metadata={
                "namespace": proj.get("namespace", {}).get("name", ""),
                "visibility": proj.get("visibility", ""),
                "star_count": proj.get("star_count", 0),
                "forks_count": proj.get("forks_count", 0),
                "open_issues_count": proj.get("open_issues_count", 0),
                "default_branch": proj.get("default_branch", ""),
                "language": proj.get("programming_language", ""),
                "created": proj.get("created_at", ""),
                "last_activity": proj.get("last_activity_at", ""),
                "archived": proj.get("archived", False),
            },
            confidence=self.confidence,
            tags=["vcs", "gitlab"],
            url=proj.get("web_url", ""),
        )
