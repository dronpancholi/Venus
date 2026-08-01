# USPTCROS Cloud Armor WAF Edge Security
**Document Link:** [Cloud Armor WAF Edge Security](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CLOUD_ARMOR_WAF_EDGE_SECURITY.md)  
**References:** [WAF Rule Enforcement Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/WAF_RULE_ENFORCEMENT_SPEC.md)

Google Cloud Armor configuration parameters for Edge security.

## 1. Rule Sets & Policies
* **Pre-configured Rule Sets:** Enable `sqli-v33-stable` and `xss-v33-stable`.
* **Rate Limiting Policies:** Dynamic IP rate-limiting set to block IPs generating over 100 HTTP connections per 10-second window.

## 2. Cloud Armor Deployment Configuration Spec
```yaml
apiVersion: compute.cnrm.cloud.google.com/v1beta1
kind: ComputeSecurityPolicy
metadata:
  name: venus-cloud-armor-policy
  namespace: venus-system
spec:
  description: "Strict Edge protection controls for Venus API gateway"
  rules:
  - action: "deny(403)"
    description: "Block identified SQL injection attempts"
    expression: "evaluatePreconfiguredExpr('sqli-v33-stable')"
    priority: 1000
  - action: "deny(403)"
    description: "Block identified XSS injection attempts"
    expression: "evaluatePreconfiguredExpr('xss-v33-stable')"
    priority: 1010
  - action: "throttle"
    description: "Limit requests per client IP address"
    expression: "true"
    priority: 2000
    rateLimitOptions:
      banDurationSec: 600
      conformAction: "allow"
      exceedAction: "deny(429)"
      rateLimitThreshold:
        count: 100
        intervalSec: 10
```
