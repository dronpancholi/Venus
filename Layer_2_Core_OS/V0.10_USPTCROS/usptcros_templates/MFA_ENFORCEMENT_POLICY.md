# USPTCROS MFA Enforcement Policy
**Document Link:** [MFA Enforcement Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/MFA_ENFORCEMENT_POLICY.md)

## 1. Mandatory MFA Requirements
Multi-Factor Authentication (MFA) is strictly required for all administrative access.

## 2. Approved Authentication Factors
1. **FIDO2 / WebAuthn Hardware Keys (Preferred):** YubiKey 5 Series or equivalent security keys.
2. **TOTP Authentication Applications:** Google Authenticator, Microsoft Authenticator. Minimum key length of 160 bits (32 base32 characters) using SHA-1/SHA-256.

## 3. Step-Up Authentication Rules
Step-up MFA verification is triggered dynamically under the following conditions:
* **Condition 1:** Accessing [Secrets Management Vault Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECRETS_MANAGEMENT_VAULT_POLICY.md).
* **Condition 2:** Modifying network configurations (e.g. firewall rules).
* **Condition 3:** Executing cryptographic key destruction protocols. See [Key Destruction Protocol](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KEY_DESTRUCTION_PROTOCOL.md).

## 4. TOTP Verification Configuration Parameter Schema
```json
{
  "totp_config": {
    "algorithm": "SHA1",
    "digits": 6,
    "period_seconds": 30,
    "skew_allowed_steps": 1
  }
}
```
