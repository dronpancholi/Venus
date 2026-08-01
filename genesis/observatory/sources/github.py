"""
GitHub source integration for the Observatory.

Supports:
  - Fetching repository metadata via GitHub API
  - Extracting trending repos
  - Cloning via RepositoryMiner
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any


class GitHubSource:
    """GitHub repository source."""

    API_BASE = "https://api.github.com"

    def __init__(self, token: str = ""):
        self.token = token

    def repo_info(self, owner: str, repo: str) -> dict[str, Any]:
        """Get repository metadata from GitHub API."""
        url = f"{self.API_BASE}/repos/{owner}/{repo}"
        data = self._get(url)
        return {
            "name": data.get("full_name", f"{owner}/{repo}"),
            "description": data.get("description", ""),
            "language": data.get("language", ""),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "topics": data.get("topics", []),
            "updated_at": data.get("updated_at", ""),
            "default_branch": data.get("default_branch", "main"),
            "size": data.get("size", 0),
        }

    def trending(self, since: str = "weekly", count: int = 10) -> list[dict[str, Any]]:
        """Fetch trending repositories."""
        url = f"{self.API_BASE}/search/repositories?q=stars:>5000+created:>2024-01-01&sort=stars&order=desc&per_page={min(count, 100)}"
        data = self._get(url)
        repos = []
        for item in data.get("items", [])[:count]:
            repos.append({
                "owner": item["owner"]["login"],
                "repo": item["name"],
                "full_name": item["full_name"],
                "stars": item["stargazers_count"],
                "description": item.get("description", ""),
                "language": item.get("language", ""),
            })
        return repos

    def _get(self, url: str) -> dict[str, Any]:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 403:
                return {"items": []}
            raise
