"""CVE source — vulnerability records, CVSS scores."""

from __future__ import annotations

from genesis.acquisition import AcquisitionRecord, AcquisitionSource
from genesis.metamodel.entity import EntityType


class CVESource(AcquisitionSource):
    source_name = "cve"
    entity_type = EntityType.CVE_RECORD
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    interval_seconds = 21600.0
    confidence = 0.95

    def __init__(self, cve_ids: list[str] | None = None):
        self.cve_ids = cve_ids or []

    def fetch(self) -> list[AcquisitionRecord]:
        records: list[AcquisitionRecord] = []
        for cve_id in self.cve_ids:
            rec = self.fetch_one(cve_id)
            if rec:
                records.append(rec)
        return records

    def fetch_one(self, cve_id: str) -> AcquisitionRecord | None:
        import urllib.request
        import json
        url = f"{self.base_url}?cveId={cve_id}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            return None
        vulnerabilities = (data.get("vulnerabilities") or [])
        if not vulnerabilities:
            return None
        vuln = vulnerabilities[0].get("cve") or {}
        metrics = vuln.get("metrics") or {}
        cvss_v31 = metrics.get("cvssMetricV31") or []
        cvss_data = cvss_v31[0].get("cvssData") if cvss_v31 else {}
        descriptions = vuln.get("descriptions") or []
        desc_text = ""
        for d in descriptions:
            if d.get("lang") == "en":
                desc_text = d.get("value", "")
                break
        if not desc_text and descriptions:
            desc_text = descriptions[0].get("value", "")
        return AcquisitionRecord(
            source=self.source_name,
            entity_type=self.entity_type,
            external_id=cve_id,
            name=cve_id,
            description=desc_text,
            raw_data=vuln,
            metadata={
                "source_identifier": vuln.get("sourceIdentifier", ""),
                "published": vuln.get("published", ""),
                "last_modified": vuln.get("lastModified", ""),
                "vuln_status": vuln.get("vulnStatus", ""),
                "cvss_score": cvss_data.get("baseScore", 0.0),
                "cvss_severity": cvss_data.get("baseSeverity", ""),
                "cvss_vector": cvss_data.get("vectorString", ""),
                "attack_vector": cvss_data.get("attackVector", ""),
                "attack_complexity": cvss_data.get("attackComplexity", ""),
                "privileges_required": cvss_data.get("privilegesRequired", ""),
                "user_interaction": cvss_data.get("userInteraction", ""),
                "scope": cvss_data.get("scope", ""),
                "confidentiality": cvss_data.get("confidentialityImpact", ""),
                "integrity": cvss_data.get("integrityImpact", ""),
                "availability": cvss_data.get("availabilityImpact", ""),
                "weaknesses": [w.get("description", [{}])[0].get("value", "") for w in (vuln.get("weaknesses") or [])],
                "references": [r.get("url", "") for r in (vuln.get("references") or [])],
            },
            confidence=self.confidence,
            tags=["cve", "vulnerability", "security"],
            url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
        )
