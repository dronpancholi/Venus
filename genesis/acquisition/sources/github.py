"""GitHub source — repositories, metadata, language stats."""

from __future__ import annotations

import time
from typing import Any

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class GitHubSource(AcquisitionSource):
    source_name = "github"
    entity_type = EntityType.GITHUB_REPO
    base_url = "https://api.github.com"
    interval_seconds = 43200.0
    confidence = 0.9

    def __init__(self, token: str = "", orgs: list[str] | None = None):
        self.token = token
        self.orgs = orgs or []

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def fetch(self) -> list[AcquisitionRecord]:
        import urllib.request
        import json
        records: list[AcquisitionRecord] = []
        for org in self.orgs:
            url = f"{self.base_url}/orgs/{org}/repos?per_page=100&sort=updated"
            try:
                req = urllib.request.Request(url, headers=self._headers())
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
            except Exception:
                continue
            for repo in data:
                records.append(self._to_record(repo, org))
            # Handle pagination
            page = 2
            while len(data) == 100:
                try:
                    url2 = f"{self.base_url}/orgs/{org}/repos?per_page=100&sort=updated&page={page}"
                    req2 = urllib.request.Request(url2, headers=self._headers())
                    with urllib.request.urlopen(req2, timeout=30) as resp2:
                        data = json.loads(resp2.read().decode())
                    for repo in data:
                        records.append(self._to_record(repo, org))
                    page += 1
                except Exception:
                    break
        return records

    def fetch_one(self, owner_repo: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"{self.base_url}/repos/{owner_repo}"
        try:
            req = urllib.request.Request(url, headers=self._headers())
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            owner = owner_repo.split("/")[0]
            return self._to_record(data, owner)
        except Exception:
            return None

    def _to_record(self, repo: dict[str, Any], org: str) -> AcquisitionRecord:
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"github:{repo['full_name']}",
            name=repo["full_name"],
            description=repo.get("description") or "",
            raw_data=repo,
            metadata={
                "org": org,
                "language": repo.get("language", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "open_issues": repo.get("open_issues_count", 0),
                "topics": repo.get("topics", []),
                "license": (repo.get("license") or {}).get("spdx_id", ""),
                "default_branch": repo.get("default_branch", ""),
                "created": repo.get("created_at", ""),
                "updated": repo.get("updated_at", ""),
                "size_kb": repo.get("size", 0),
                "has_wiki": repo.get("has_wiki", False),
                "has_issues": repo.get("has_issues", False),
                "archived": repo.get("archived", False),
            },
            confidence=self.confidence,
            tags=["vcs", "github"] + repo.get("topics", []),
            url=repo.get("html_url", ""),
        )
