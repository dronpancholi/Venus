# Code Signing and Cosign Verification Specification
**Document ID:** VENUS-USPTCROS-081
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Delineates the cryptographic validation protocols for container images and application artifacts using Sigstore Cosign to guarantee build authenticity and reject untrusted payloads.

## 2. Technical Specifications & Architecture
### Trust Root Infrastructure

| Attribute | Description | Provider |
| --- | --- | --- |
| OIDC Issuer | Authenticates the builder identity | Github Actions OIDC |
| Fulcio CA | Issues short-lived certificates | Sigstore Public Good |
| Rekor Log | Transparent ledger for signature logs | Sigstore Transparency |
| Kyverno | Admission controller checking signatures | Kubernetes Engine |

## 3. Code Fragment / Implementation Details
```bash
#!/usr/bin/env bash
set -euo pipefail

# Verify the container image using Cosign keyless signatures
IMAGE_URI="ghcr.io/venus/core-engine:latest"
OIDC_ISSUER="https://token.actions.githubusercontent.com"
SUBJECT="https://github.com/venus/core-engine/.github/workflows/release.yml@refs/heads/main"

echo "Verifying signature for image: ${IMAGE_URI}"
cosign verify \
  --certificate-identity-regexp "${SUBJECT}" \
  --certificate-oidc-issuer "${OIDC_ISSUER}" \
  "${IMAGE_URI}"
```

## 4. Verification Schema & Configurations
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-cosign-signature
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      imageSignatures:
      - imageReference: "ghcr.io/venus/*"
        attestations:
        - predicateType: cosign.sigstore.dev/attestation/v1
          entries:
          - keys:
              publicKeys: |-
                -----BEGIN PUBLIC KEY-----
                MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE7v1W9e6U4r792376179374917491
                7491749174917491749174917491749174917491749174917491749174917491
                -----END PUBLIC KEY-----
```

## 5. Mathematical Formulations & Quantitative Metrics
$$SignatureVerificationRate = \frac{ValidSignatures}{TotalDeployedContainers}$$

## 6. Institutional Verification Checklist
* [ ] Verify container image metadata and digests match original build artifacts.
* [ ] Verify signatures using keyless OIDC configurations linked to GitHub build runners.
* [ ] Configure Kubernetes admission control policies to reject unsigned or unverified container images.
* [ ] Audit signature logs in the public Rekor transparency ledger weekly.

## 7. Cross-References
- [Slsa Compliance Checklist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SLSA_COMPLIANCE_CHECKLIST.md)
- [Private Registry Promotion Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PRIVATE_REGISTRY_PROMOTION_POLICY.md)
- [Provenance Generation Checklist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PROVENANCE_GENERATION_CHECKLIST.md)
