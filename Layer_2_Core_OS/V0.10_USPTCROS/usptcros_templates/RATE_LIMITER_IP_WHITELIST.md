# USPTCROS Rate Limiter & IP Whitelist
**Document Link:** [Rate Limiter & IP Whitelist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/RATE_LIMITER_IP_WHITELIST.md)  
**References:** [API Security Gateway Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/API_SECURITY_GATEWAY_SPEC.md)

## 1. Rate Limiting System Config
The rate limiting engine employs a Token Bucket algorithm managed in a Redis backend.

## 2. Configuration Settings
* **Default Limit:** 100 requests per IP address per minute.
* **Burst allowance:** 150 requests.
* **IP Whitelist Bypass:** Private IP addresses (`10.0.0.0/8`, `172.16.0.0/12`) bypass the rate limiting checks when communicating internally.

## 3. Limiter Configuration YAML
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: ip-rate-limiter
  namespace: venus-system
spec:
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
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          stat_prefix: http_local_rate_limiter
          token_bucket:
            max_tokens: 150
            tokens_per_fill: 100
            fill_interval: 60s
          filter_enabled:
            runtime_key: local_rate_limit_enabled
            default_value:
              numerator: 100
              denominator: HUNDRED
```
