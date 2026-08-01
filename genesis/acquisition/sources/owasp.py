"""OWASP source — security categories, projects, resources."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class OWASPSource(AcquisitionSource):
    source_name = "owasp"
    entity_type = EntityType.OWASP_CATEGORY
    base_url = "https://www.owasp.org"
    interval_seconds = 86400.0
    confidence = 0.9

    def __init__(self, projects: list[str] | None = None):
        self.projects = projects or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for proj in self.projects:
            rec = self.fetch_one(proj)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, project_name: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        # OWASP GitHub-based projects API
        url = f"https://raw.githubusercontent.com/OWASP/www-community/main/{project_name}/index.md"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                md_content = resp.read().decode()
        except Exception:
            # Fallback: try the www-project- convention
            url2 = f"https://raw.githubusercontent.com/OWASP/www-project-{project_name}/master/index.md"
            try:
                req2 = urllib.request.Request(url2)
                with urllib.request.urlopen(req2, timeout=30) as resp2:
                    md_content = resp2.read().decode()
            except Exception:
                return None
        name = project_name.replace("-", " ").title()
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"owasp:{project_name}",
            name=name,
            description=f"OWASP {name}",
            raw_data={"markdown": md_content},
            metadata={
                "project_name": project_name,
                "content_length": len(md_content),
            },
            confidence=self.confidence,
            tags=["owasp", "security"],
            url=f"https://owasp.org/www-project-{project_name}/",
        )
