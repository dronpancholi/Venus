# USPTCROS Service Authorization Specification
**Document Link:** [Service Authorization Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SERVICE_AUTHORIZATION_SPEC.md)

## 1. Machine-to-Machine (M2M) Access Model
Inter-service communications use OAuth 2.0 Client Credentials Grant, validated using JSON Web Key Sets (JWKS).

## 2. SPIFFE/SPIRE Identity Configuration
Workloads receive dynamic cryptographic identities in SPIFFE ID format.

```
spiffe://venus.local/ns/venus-system/sa/service-api-engine
```

## 3. JWT Audience and Scope Validation Configuration
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-auth-policy
  namespace: venus-system
spec:
  selector:
    matchLabels:
      app: service-api-engine
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/venus-system/sa/service-gateway"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/v1/secure-data*"]
```
