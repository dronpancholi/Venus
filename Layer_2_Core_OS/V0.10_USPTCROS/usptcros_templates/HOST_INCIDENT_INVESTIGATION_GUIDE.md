# Host Incident Investigation Guide
**Document ID:** VENUS-USPTCROS-131
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Outlines standard procedures to investigate suspicious processes, configurations, system modifications, and open connections on compromised host systems.

## 2. Technical Specifications & Architecture
```
[ Suspected Compromise ] -> Check active logins -> Review network connections -> Check modified system binaries -> Log findings
```

## 3. Code Fragment / Implementation Details
```bash
#!/usr/bin/env bash
# Basic host triage script inspecting critical files
set -euo pipefail

REPORT_FILE="/tmp/host_triage_report.txt"
echo "Executing host system triage..." > "${REPORT_FILE}"

echo "=== Active Logins ===" >> "${REPORT_FILE}"
who >> "${REPORT_FILE}"

echo "=== Modifed System Files (last 24 hours) ===" >> "${REPORT_FILE}"
find /usr/bin /usr/sbin -mtime -1 >> "${REPORT_FILE}"

echo "Triage report saved to: ${REPORT_FILE}"
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HostTriageSummary",
  "type": "object",
  "properties": {
    "host_identifier": {
      "type": "string"
    },
    "compromise_found": {
      "type": "boolean"
    },
    "suspicious_processes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "host_identifier",
    "compromise_found",
    "suspicious_processes"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
$$CompromiseIndicator = \frac{SuspiciousObjectsFound}{TotalObjectsReviewed}$$

## 6. Institutional Verification Checklist
* [ ] Review list of active user logins on the host.
* [ ] Verify integrity of critical system binary files.
* [ ] Examine active system connections and open ports.
* [ ] Review cron job scheduling files for persistence mechanisms.

## 7. Cross-References
- [Compromised Credentials Revocation](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/COMPROMISED_CREDENTIALS_REVOCATION.md)
- [Network Traffic Capture Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/NETWORK_TRAFFIC_CAPTURE_SPEC.md)
- [Digital Forensics Collection Runbook](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DIGITAL_FORENSICS_COLLECTION_RUNBOOK.md)
