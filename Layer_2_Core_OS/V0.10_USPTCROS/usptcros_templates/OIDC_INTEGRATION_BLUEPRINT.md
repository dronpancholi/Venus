# USPTCROS OIDC Integration Blueprint
**Document Link:** [OIDC Integration Blueprint](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OIDC_INTEGRATION_BLUEPRINT.md)  
**References:** [OAuth Design Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OAUTH_DESIGN_SPECIFICATION.md)

This blueprint outlines Identity federation using OpenID Connect (OIDC) protocols.

## 1. ID Token Payload Verification
The system must validate ID tokens using the JWKS endpoint signature.

### Signature Verification Algorithm
* **Algorithm:** RS256 (RSA with SHA-256) or ES256 (ECDSA using P-256).
* **Audience Check:** `aud` claim must match the registered `client_id`.
* **Issuer Check:** `iss` claim must match the configured identity provider URL.

### ID Token Payload Schema
```json
{
  "iss": "https://identity.venus.local",
  "sub": "usr-9823498234",
  "aud": "venus-core-portal",
  "exp": 1782489600,
  "iat": 1782486000,
  "auth_time": 1782486000,
  "acr": "urn:mace:incommon:iap:silver",
  "email": "user@venus.local",
  "roles": ["operator"]
}
```

## 2. UserInfo Endpoint Mapping
Attributes fetched from the `/userinfo` endpoint must align with internal system attributes:
| Provider Claim | Target User Object Property | Data Type |
|---|---|---|
| `sub` | `externalId` | String |
| `name` | `displayName` | String |
| `email_verified` | `isEmailVerified` | Boolean |
| `zoneinfo` | `timezone` | String |
