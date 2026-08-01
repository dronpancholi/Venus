# Secrets Management Vault Policy
**Document ID:** VENUS-STD-086
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This policy defines the lifecycle, storage, rotation, and access parameters of sensitive configurations (passwords, tokens, GPG keys) using HashiCorp Vault.

## 2. Vault Policy Template (`app-reader.hcl`)
This policy defines the access limitations for the application container context:

```hcl
# Read database passwords and certificates
path "secret/data/production/database/*" {
  capabilities = ["read"]
}

# Allow application to authenticate and verify tokens
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Explicitly deny write or delete capabilities to application runtime
path "secret/data/production/database/*" {
  capabilities = ["deny"]
  allowed_parameters = ["delete", "put", "patch"]
}
```

## 3. Secret Rotation Lifecycle
1. **Dynamic Database Credentials:** Database tokens are leased with a Max Time To Live (TTL) of 24 hours. The application must renew leases periodically.
2. **Third-Party API Tokens:** rotated automatically every 90 days.
3. **Emergency Rotation:** If a token is detected in plain text logs, the security team triggers the revocation runbook:
   ```bash
   vault lease revoke -prefix secret/data/production/
   ```

## 4. Cross-References
- [IAM Roles and Policies Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/IAM_ROLES_POLICIES_SPEC.md)
- [Security Penetration Testing Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/SECURITY_PENETRATION_TEST_SPEC.md)
