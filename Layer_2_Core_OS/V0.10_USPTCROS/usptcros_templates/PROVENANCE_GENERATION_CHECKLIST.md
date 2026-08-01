# Provenance Generation and Attestation Checklist
**Document ID:** VENUS-USPTCROS-086
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Defines parameters for generating signed attestations detailing the source, builder, and environment used to compile software artifacts, aligning with the SLSA v1.0 standard.

## 2. Technical Specifications & Architecture
### Provenance Structure

| Element | Description | Validation Target |
| --- | --- | --- |
| subject | Unique identifier of the generated artifact | sha256 name |
| buildDefinition | Build parameters, repository path, config entrypoint | Github repository commit hash |
| runDetails | Execution timestamp and isolated runner ID | Runner signature |

## 3. Code Fragment / Implementation Details
```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "subject": [
    {
      "name": "ghcr.io/venus/core-engine",
      "digest": {
        "sha256": "4d161a4c98fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
      }
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v1.0",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://github.com/Attestations/GitHubActionsWorkflow@v1",
      "externalParameters": {
        "repository": "https://github.com/venus/core-engine",
        "ref": "refs/heads/main"
      }
    }
  }
}
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AttestationMetadata",
  "type": "object",
  "properties": {
    "statement_type": {
      "type": "string",
      "enum": [
        "https://in-toto.io/Statement/v0.1"
      ]
    },
    "predicate_type": {
      "type": "string",
      "enum": [
        "https://slsa.dev/provenance/v1.0"
      ]
    },
    "signer_identity": {
      "type": "string"
    }
  },
  "required": [
    "statement_type",
    "predicate_type",
    "signer_identity"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
$$AttestationRate = \frac{Signed\_Provenance\_Records}{Published\_Release\_Artifacts}$$

## 6. Institutional Verification Checklist
* [ ] Generate in-toto provenance templates automatically at the end of build pipeline steps.
* [ ] Verify build provenance is cryptographically bound to the artifact digest.
* [ ] Store generated build provenance files alongside container images in the registry.
* [ ] Verify provenance artifacts using Sigstore validation engines.

## 7. Cross-References
- [Slsa Compliance Checklist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SLSA_COMPLIANCE_CHECKLIST.md)
- [Code Signing Cosign Verification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CODE_SIGNING_COSIGN_VERIFICATION.md)
- [Private Registry Promotion Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PRIVATE_REGISTRY_PROMOTION_POLICY.md)
