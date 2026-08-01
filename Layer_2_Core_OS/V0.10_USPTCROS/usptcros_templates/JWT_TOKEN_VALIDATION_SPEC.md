# USPTCROS JWT Token Validation Spec
**Document Link:** [JWT Token Validation Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/JWT_TOKEN_VALIDATION_SPEC.md)  
**References:** [OAuth Design Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OAUTH_DESIGN_SPECIFICATION.md)

## 1. Token Validation Pipeline
All incoming JWTs must undergo the following validation sequence before resource processing.

```
Incoming JWT ──► Split Parts ──► Verify Alg is RS256/ES256 ──► Validate Signature (JWKS) ──► Validate Claims (exp, iss, aud) ──► Grant Access
```

## 2. Validation Constraints
* **Signature Algorithm:** Must be explicitly checked. Reject `none` alg tokens.
* **Expiration (`exp`):** Current Unix time must be less than `exp` (allow maximum 60 seconds clock skew).
* **Issuer (`iss`):** Must match the configured authorization server.
* **Audience (`aud`):** Must match the internal service identification tag.

## 3. Signature Validation Snippet (Python PyJWT)
```python
import jwt

def validate_token(token: str, jwks_client) -> dict:
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    data = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience="venus-core-services",
        issuer="https://auth.venus.local"
    )
    return data
```
