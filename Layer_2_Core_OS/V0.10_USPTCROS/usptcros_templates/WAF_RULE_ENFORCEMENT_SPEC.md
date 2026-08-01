# USPTCROS WAF Rule Enforcement Spec
**Document Link:** [WAF Rule Enforcement Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/WAF_RULE_ENFORCEMENT_SPEC.md)  
**References:** [API Security Gateway Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/API_SECURITY_GATEWAY_SPEC.md)

ModSecurity and Cloud Armor Web Application Firewall (WAF) rule sets.

## 1. OWASP ModSecurity Core Rule Set (CRS) Configurations
* **Anomaly Scoring Threshold:** Set block threshold to 5 (Strict).
* **Paranoia Level:** Level 2 (Enhanced filtering of SQLi/XSS/LFI/RFI patterns).

## 2. Custom Block Rules (SQL Injection and Directory Traversal)
```apache
# Block directory traversal attempts
SecRule REQUEST_URI "@contains .." "id:10001,phase:2,deny,status:403,log,msg:'Directory traversal attempt blocked'"

# Block typical SQL injection payloads
SecRule REQUEST_COOKIES|REQUEST_COOKIES_NAMES|REQUEST_HEADERS|REQUEST_URI|REQUEST_BODY "@rx (select|insert|update|delete|drop|union|alter)"     "id:10002,phase:2,deny,status:403,log,msg:'SQL injection attempt blocked'"
```
