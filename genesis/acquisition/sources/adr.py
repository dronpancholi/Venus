"""ADR source — Architecture Decision Records from repositories."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class ADRSource(AcquisitionSource):
    source_name = "adr"
    entity_type = EntityType.ADR_DOCUMENT
    base_url = ""
    interval_seconds = 86400.0
    confidence = 0.85

    def __init__(self, adr_urls: list[str] | None = None):
        self.adr_urls = adr_urls or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for url in self.adr_urls:
            rec = self._fetch_url(url)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, adr_url: str) -> AcquisitionRecord | None:
        return self._fetch_url(adr_url)

    def _fetch_url(self, adr_url: str) -> AcquisitionRecord | None:
        import urllib.request
        url = adr_url
        if not url.startswith("http"):
            url = f"https://raw.githubusercontent.com/{url}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read().decode()
        except Exception:
            return None
        name = url.split("/")[-1].replace(".md", "")
        # Extract title from markdown
        title = name
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        # Extract status
        status = ""
        for line in content.split("\n"):
            lower = line.lower().strip()
            for s in ["accepted", "proposed", "deprecated", "superseded", "draft", "rejected"]:
                if lower.startswith(f"* status: {s}") or lower.startswith(f"- status: {s}"):
                    status = s
                    break
            if status:
                break
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=f"adr:{name.lower().replace(' ', '-')}",
            name=name,
            description=f"Architecture Decision Record: {title}",
            raw_data={"markdown": content},
            metadata={
                "title": title,
                "status": status,
                "source_url": adr_url,
                "content_length": len(content),
            },
            confidence=self.confidence,
            tags=["adr", "architecture", "decision"],
            url=adr_url,
        )
