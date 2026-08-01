# PART 19 — Authentication
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

Authentication defines who you are. It is the first gate of trust in every system. This part establishes the authentication protocols, token management standards, session design, multi-factor requirements, and identity provider integration patterns for all VENUS systems.

---

## 2. Authentication Protocol Standards

### 2.1 OAuth 2.0 + OpenID Connect (OIDC) — Primary Standard
All user-facing authentication must use OAuth 2.0 + OIDC.

```
Flows by use case:
  Web App (server-side):      Authorization Code Flow
  SPA / Mobile:               Authorization Code Flow + PKCE (no client secret)
  Machine-to-Machine:         Client Credentials Flow
  Background Jobs:            Client Credentials Flow
  
NEVER use:
  Implicit Flow (deprecated, insecure)
  Password Grant (except for migration from legacy systems)
```

### 2.2 Identity Providers
| Provider | Use Case |
|---|---|
| **Auth0** | Consumer-facing, rapid deployment |
| **Keycloak** | On-premise, enterprise SSO |
| **AWS Cognito** | AWS-native workloads |
| **Google Identity Platform** | Google Workspace integration |
| **Okta / Ping Identity** | Enterprise B2B SSO |

---

## 3. Token Standards

### 3.1 JWT (JSON Web Token)
```json
Header:
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-id-for-rotation"
}

Payload:
{
  "sub": "user-uuid",
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "exp": 1700000000,
  "iat": 1699999100,
  "jti": "unique-token-id",
  "email": "user@example.com",
  "roles": ["admin", "viewer"],
  "org_id": "org-uuid"
}
```

### 3.2 Token Lifetimes
| Token Type | Lifetime | Storage |
|---|---|---|
| **Access Token** | 15 minutes | Memory (SPA), httpOnly cookie (web) |
| **Refresh Token** | 24 hours (sliding) | httpOnly, Secure, SameSite=Strict cookie |
| **ID Token** | 15 minutes | Memory only |
| **API Key** | No expiry (manual rotation) | Secrets manager |

### 3.3 Token Security Rules
- Access tokens: Never stored in localStorage (XSS risk)
- Refresh tokens: Rotation on every use (refresh token rotation)
- JWT signing: RS256 (asymmetric) for production; never HS256 with shared secrets
- Token revocation: Maintain a revocation list or short expiry + blacklist
- JTI tracking: Track JWT IDs to enable single-use enforcement

---

## 4. Session Management

### 4.1 Stateless JWT Sessions (Default)
```
Pros: Horizontally scalable, no server-side state
Cons: Cannot revoke without blacklist or short expiry

Implementation:
  - Short-lived access tokens (15 min)
  - Refresh tokens stored server-side (revocable)
  - Token refresh handled transparently by client SDK
```

### 4.2 Stateful Sessions (Redis-backed)
```
Pros: Instant revocation, full control over session data
Cons: Requires distributed session store

Implementation:
  - Session ID in httpOnly cookie
  - Session data in Redis with TTL
  - Redis cluster for HA
  - Session fixed on authentication to prevent session fixation attacks
```

---

## 5. Multi-Factor Authentication (MFA)

### 5.1 MFA Requirements
| User Type | MFA Requirement |
|---|---|
| End users (consumer) | Optional (strongly recommended) |
| Enterprise users | Mandatory |
| Admin users | Mandatory, hardware key required |
| Service accounts | Not applicable (use client credentials) |

### 5.2 Supported MFA Methods
| Method | Strength | VENUS Recommendation |
|---|---|---|
| TOTP (Authenticator App) | High | Primary recommendation |
| SMS OTP | Medium | Discouraged (SIM swap risk) |
| Hardware Key (FIDO2/WebAuthn) | Very High | Required for admin |
| Email OTP | Low | Legacy fallback only |
| Push Notification | High | Enterprise option |

---

## 6. API Key Authentication (Service-to-Service)

```
Format: {prefix}_{random_32_bytes_base64url}
Example: venus_K3mF9xP2qN8rT7vY5wL1jH4iU6cE0bA

Key Management:
  - Stored as SHA-256 hash in database (never plaintext)
  - Only shown once at creation
  - Rotatable without downtime (dual key support during rotation window)
  - Scoped to specific permissions
  - Expires: optional, recommended 90 days

Request authentication:
  Authorization: Bearer venus_K3mF9xP2qN8rT7vY5wL1jH4iU6cE0bA
  OR
  X-API-Key: venus_K3mF9xP2qN8rT7vY5wL1jH4iU6cE0bA
```

---

## 7. Authentication Attack Prevention

| Attack | Prevention |
|---|---|
| **Brute Force** | Account lockout (5 failures → 15 min lockout), CAPTCHA |
| **Credential Stuffing** | Breached password detection (HaveIBeenPwned API) |
| **Session Fixation** | Generate new session ID after authentication |
| **CSRF** | SameSite=Strict cookies, CSRF tokens for non-cookie auth |
| **Token Leakage** | Short expiry, revocation, audit logs |
| **Phishing** | FIDO2 hardware keys (phishing-resistant by design) |
| **Replay Attacks** | JTI uniqueness validation, short token expiry |

---

## 8. Authentication Observability

```
Events to log (Security SIEM):
  authentication.success     — userId, ip, device, timestamp
  authentication.failure     — reason, ip, device, timestamp
  mfa.challenge              — method, userId, timestamp
  mfa.failure                — method, userId, ip, timestamp
  token.refresh              — userId, previousJti, newJti
  token.revoked              — userId, jti, reason
  account.locked             — userId, reason, duration
  password.changed           — userId, ip, timestamp
  api_key.created/revoked    — keyId, userId, timestamp

Alerts:
  > 10 failures from same IP in 1 minute → Potential brute force
  > 5 failures for same user in 5 minutes → Account compromise attempt
  Authentication from new country → Notify user
```
