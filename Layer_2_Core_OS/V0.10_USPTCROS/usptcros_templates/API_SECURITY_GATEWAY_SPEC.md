# USPTCROS API Security Gateway Spec
**Document Link:** [API Security Gateway Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/API_SECURITY_GATEWAY_SPEC.md)  
**References:** [Rate Limiter & IP Whitelist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/RATE_LIMITER_IP_WHITELIST.md), [WAF Rule Enforcement Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/WAF_RULE_ENFORCEMENT_SPEC.md)

## 1. Edge Protection Features
The API gateway acts as the single point of entry, enforcing edge isolation controls.
* **Payload Size Constraint:** Requests with bodies exceeding 10MB must be rejected.
* **TLS Requirements:** Minimum TLS 1.3. Older versions must be dropped.
* **Header Stripping:** Strip diagnostic headers (`X-Powered-By`, `Server`, `X-AspNet-Version`).

## 2. Gateway Security Configuration (Envoy Filter Spec)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: request-size-limiter
  namespace: venus-system
spec:
  workloadSelector:
    labels:
      istio: ingressgateway
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: GATEWAY
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.buffer
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.buffer.v3.Buffer
          max_request_bytes: 10485760 # 10MB Limit
```
