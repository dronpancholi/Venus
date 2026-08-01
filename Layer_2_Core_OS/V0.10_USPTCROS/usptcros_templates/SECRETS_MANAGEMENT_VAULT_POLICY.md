# USPTCROS Secrets Management Vault Policy
**Document Link:** [Secrets Management Vault Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECRETS_MANAGEMENT_VAULT_POLICY.md)  
**References:** [Key Rotation Lifecycle Plan](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KEY_ROTATION_LIFECYCLE_PLAN.md)

## 1. Vault Authentication Baselines
No user accounts are granted permanent authorization tokens. Access is managed through Identity-bound AppRoles or OIDC federation.

## 2. Secret Engine Scopes
* **Path `/secret/data/production/*`:** restricted to Production Application Service Roles.
* **Path `/transit/*`:** interface path for cryptographic tokenization. See [Tokenization & Data Masking Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TOKENIZATION_DATA_MASKING_POLICY.md).

## 3. Access Policy Configuration (HCL Format)
```hcl
# Access control policy for production applications
path "secret/data/production/database/*" {
  capabilities = ["read"]
}

path "transit/encrypt/venus-key" {
  capabilities = ["update"]
}

path "transit/decrypt/venus-key" {
  capabilities = ["update"]
}
```
