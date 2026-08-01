# Template: API Architecture

## 1. Document Control
*   **Project Name**: [Project Name]
*   **API ID**: API-[UUID]
*   **Date**: [Date]

---

## 2. API Architectural Pattern
*Select and justify the primary API pattern (REST, GraphQL, gRPC).*

*   **Selected Pattern**: REST (JSON) over HTTP/1.1 for public interfaces; gRPC for internal worker communication.
*   **Justification**: REST provides standard client compatibility, while gRPC minimizes network latency overhead between internal nodes.

---

## 3. Public API Specification (OpenAPI Skeletons)
```yaml
openapi: 3.0.0
info:
  title: Venus Core API
  version: 1.0.0
paths:
  /v1/sessions:
    post:
      summary: Create session token
      responses:
        '200':
          description: Successful execution
```

---

## 4. Global API Policies
*   **Rate Limiting**: Max 100 requests per minute per IP address.
*   **Authentication**: Bearer JWT token in Authorization header.
*   **Response Compression**: gzip / brotli enabled for payloads > 1KB.
