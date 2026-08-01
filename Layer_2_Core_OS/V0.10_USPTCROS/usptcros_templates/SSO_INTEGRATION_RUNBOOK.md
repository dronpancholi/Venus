# USPTCROS SSO Integration Runbook
**Document Link:** [SSO Integration Runbook](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SSO_INTEGRATION_RUNBOOK.md)

## 1. SSO Setup Checklist
Step-by-step procedures for configuring Identity Provider (IdP) integration.

- [ ] Create application in IdP console (SAML 2.0 or OIDC).
- [ ] Export IdP Metadata XML file.
- [ ] Configure Assertions Consumer Service (ACS) URL to: `https://auth.venus.local/saml/acs`.
- [ ] Map NameID format to `urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress`.
- [ ] Validate signing and encryption requirements. SAML assertions must be signed.

## 2. Verification Assertions Audit
Use the command line to verify that metadata endpoint returns expected signed configuration structures:
```bash
# Verify OIDC openid-configuration metadata
curl -s -k https://auth.venus.local/.well-known/openid-configuration | jq .
```

## 3. Identity Provider Fallback Plan
If the primary SSO provider goes offline, emergency access is constrained to local breakglass users stored securely inside HSM-backed partitions. Refer to [Privileged Access Management Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PRIVILEGED_ACCESS_MANAGEMENT_SPEC.md).
