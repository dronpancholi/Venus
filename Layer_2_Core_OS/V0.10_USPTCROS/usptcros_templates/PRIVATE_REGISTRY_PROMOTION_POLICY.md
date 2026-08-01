# Private Registry Promotion Policy
**Document ID:** VENUS-USPTCROS-088
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Establishes promotion gates, testing requirements, scanning triggers, and role approvals necessary to elevate container images from staging to the private production registry.

## 2. Technical Specifications & Architecture
### Promotion Stage Mapping

| Pipeline Stage | Registry Scope | Security Controls | Allowed Action |
| --- | --- | --- | --- |
| Build Stage | `registry/staging` | Automatic Trivy Scan | No deployments allowed |
| Audit Stage | `registry/approved` | Cosign Signature + SBOM check | Deploy to Staging Cluster |
| Release Stage | `registry/production` | Policy Verification (OPA) | Deploy to Production Cluster |

## 3. Code Fragment / Implementation Details
```rego
package registry.promotion

default allow = false

# Allow promotion only if image has been scanned and has zero critical vulnerabilities
allow {
    input.scan_results.critical_count == 0
    input.scan_results.high_count == 0
    input.signature_verified == true
    input.provenance_exists == true
}
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PromotionApprovalMetadata",
  "type": "object",
  "properties": {
    "image_digest": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$"
    },
    "origin_registry": {
      "type": "string"
    },
    "destination_registry": {
      "type": "string"
    },
    "promoted_by": {
      "type": "string",
      "format": "email"
    },
    "gatekeeper_signature": {
      "type": "string"
    }
  },
  "required": [
    "image_digest",
    "origin_registry",
    "destination_registry",
    "promoted_by",
    "gatekeeper_signature"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
$$PromotionApprovalRate = \frac{ApprovedImages}{AttemptedPromotions}$$

## 6. Institutional Verification Checklist
* [ ] Run static vulnerability scanners on the staging container image.
* [ ] Verify the image is signed with the build pipeline's cryptographic key.
* [ ] Verify in-toto build provenance exists and passes signature checks.
* [ ] Verify all quality gate metrics return green states prior to OPA rule evaluation.

## 7. Cross-References
- [Code Signing Cosign Verification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CODE_SIGNING_COSIGN_VERIFICATION.md)
- [Provenance Generation Checklist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PROVENANCE_GENERATION_CHECKLIST.md)
- [Oss Ingestion Policy Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OSS_INGESTION_POLICY_STANDARD.md)
