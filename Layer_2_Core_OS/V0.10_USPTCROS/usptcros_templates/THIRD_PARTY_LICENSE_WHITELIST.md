# Third-Party License Whitelist and Approval Policy
**Document ID:** VENUS-USPTCROS-082
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Establishes policy requirements for open-source licenses permissible in Venus codebases, categorizing licenses into whitelisted, restricted, and blacklisted groups.

## 2. Technical Specifications & Architecture
### License Classification Matrix

| Category | Permissible Licenses | Action | Approval Needed |
| --- | --- | --- | --- |
| Approved (Whitelist) | MIT, Apache-2.0, BSD-3-Clause | Allowed automatically | No |
| Restricted | LGPL-2.1, EPL-2.0 | Conditional review | Architecture Board |
| Blocked (Blacklist) | GPL-3.0, AGPL-3.0, CC-BY-NC-4.0 | Reject build | Legal Counsel Only |

## 3. Code Fragment / Implementation Details
```json
{
  "license_policy": {
    "whitelist": ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"],
    "restricted": ["LGPL-2.1", "LGPL-3.0", "MPL-2.0"],
    "blacklist": ["GPL-3.0", "AGPL-3.0", "SSPL", "Commons-Clause"]
  }
}
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "LicenseConfiguration",
  "type": "object",
  "properties": {
    "allowed_licenses": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "restricted_licenses": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "blocked_licenses": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "allowed_licenses",
    "restricted_licenses",
    "blocked_licenses"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
$$ComplianceRatio = \frac{\text{WhitelistedDependencies}}{\text{TotalDependencies}} \times 100\%$$

## 6. Institutional Verification Checklist
* [ ] Scan all packages at build stage to construct a complete list of licenses.
* [ ] Verify there are no dependencies utilizing licenses that are blacklisted.
* [ ] Obtain written architecture board approval for any restricted license packages.
* [ ] Document copyright notices for all third-party components inside target builds.

## 7. Cross-References
- [Dependency Risk Report](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DEPENDENCY_RISK_REPORT.md)
- [Oss Ingestion Policy Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OSS_INGESTION_POLICY_STANDARD.md)
- [Dependency Pinning Lockfile](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DEPENDENCY_PINNING_LOCKFILE.md)
