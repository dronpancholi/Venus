# PART 11 — API Engineering
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## 1. Purpose

API Engineering defines the standards for designing, building, versioning, documenting, testing, securing, and evolving all APIs within the VENUS ecosystem. APIs are contracts. Breaking a contract without notice destroys trust. Every API decision must balance expressiveness, stability, and evolvability.

---

## 2. API Protocol Selection

| Protocol | When to Use |
|---|---|
| **REST** | Public APIs, CRUD-heavy services, mobile clients |
| **GraphQL** | Flexible querying, complex front-end data requirements, multi-team APIs |
| **gRPC** | Internal service-to-service communication, high throughput, streaming |
| **WebSocket** | Real-time bidirectional communication (chat, live updates) |
| **Server-Sent Events** | One-way real-time streaming (notifications, progress updates) |
| **Webhooks** | Event-driven async notifications to external systems |

---

## 3. REST API Design Standard

### 3.1 Resource Design Principles
- Resources are **nouns**, not verbs
- Collections are plural: `/users`, `/orders`, `/products`
- Relationships use hierarchical paths: `/users/{userId}/orders`
- Avoid deep nesting beyond 2 levels: prefer `/orders/{orderId}` over `/users/{userId}/orders/{orderId}/items/{itemId}`
- Actions that don't fit CRUD use sub-resources: `POST /orders/{orderId}/cancel`

### 3.2 Query Parameters Standard
```
Filtering:   GET /orders?status=pending&customerId=123
Sorting:     GET /orders?sort=createdAt:desc,amount:asc
Pagination:  GET /orders?page=2&pageSize=20
             GET /orders?cursor=eyJpZCI6MTAwfQ==&limit=20
Projection:  GET /orders?fields=id,status,total
Search:      GET /orders?q=invoice+payment
```

### 3.3 Idempotency
All non-idempotent operations (POST, PATCH) must support idempotency keys:

```
POST /payments
Idempotency-Key: {uuid}

The server stores the result for 24 hours.
Duplicate requests with same key return the original response.
```

---

## 4. API Versioning Strategy

### 4.1 Versioning Rules
- **URI versioning** for major breaking changes: `/v1/`, `/v2/`
- **Header versioning** for minor variations: `API-Version: 2024-01-15`
- Never break a versioned API without a deprecation period
- Minimum deprecation notice: **90 days**
- Maximum parallel supported versions: **2**

### 4.2 Deprecation Lifecycle
```
v1 Active → v1 Deprecated (warning headers) → v1 Sunset (404) → v1 Removed
                    ↑                               ↑
               90 days minimum             30 days notice
```

### 4.3 Deprecation Headers
```http
Deprecation: true
Sunset: Sat, 01 Jan 2025 00:00:00 GMT
Link: <https://api.example.com/v2/orders>; rel="successor-version"
```

---

## 5. API Documentation Standard

All APIs must be documented using **OpenAPI 3.1** (REST) or **SDL** (GraphQL).

### 5.1 OpenAPI Requirements
- Every endpoint documented with request/response schemas
- All error responses documented
- Authentication schemes documented
- Example requests and responses for every endpoint
- Changelog maintained in `CHANGELOG.md`
- Documentation auto-generated and published on every merge to `main`

### 5.2 Documentation Portal Requirements
- Interactive API explorer (Swagger UI or Redoc)
- Code samples in 3+ languages (TypeScript, Python, curl)
- Authentication guide
- Rate limiting documentation
- Webhook documentation with payload examples
- SDK links and installation instructions

---

## 6. API Security Standards

### 6.1 Authentication
- All API endpoints require authentication (except public health checks)
- OAuth 2.0 / OIDC for user-context APIs
- API Keys for service-to-service with HMAC signing
- JWT tokens: short expiry (15 min) with refresh tokens
- mTLS for internal service mesh communication

### 6.2 Rate Limiting
```
Default limits:
  Anonymous:     60 requests/minute
  Authenticated: 1000 requests/minute
  Premium:       10000 requests/minute

Headers returned:
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 742
  X-RateLimit-Reset: 1609459200
  Retry-After: 30 (on 429)
```

### 6.3 Input Validation
- Validate all inputs at the API boundary
- Schema validation using JSON Schema / Zod / Pydantic
- Maximum request body size enforced (default: 10MB)
- Maximum URL length enforced (default: 8KB)
- Sanitize all string inputs against injection

---

## 7. API Testing Requirements

| Test Level | Coverage Requirement |
|---|---|
| **Unit Tests** | All request validation, business logic |
| **Integration Tests** | All endpoints with real database |
| **Contract Tests** | Consumer-driven contracts (Pact) |
| **Performance Tests** | p95 < 200ms, p99 < 500ms under load |
| **Security Tests** | OWASP API Security Top 10 |

---

## 8. API Observability

Every API must emit:

```
Metrics:
  api.request.duration (histogram, by route, method, status)
  api.request.count (counter, by route, method, status)
  api.error.rate (gauge)
  api.rate_limit.hits (counter)

Logs (structured JSON):
  requestId, method, path, statusCode, duration, userId, traceId

Traces:
  OpenTelemetry spans for every request
  Downstream dependency spans
```
