# USPTCROS CORS HTTP Headers Matrix
**Document Link:** [CORS HTTP Headers Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CORS_HTTP_HEADERS_MATRIX.md)  
**References:** [Web Application Hardening Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/WEB_APPLICATION_HARDENING_GUIDE.md)

Cross-Origin Resource Sharing (CORS) configurations for Venus API gateways.

## 1. Dynamic Origin Mapping Rules
* Wildcard origins (`*`) are prohibited for all authenticated endpoints.
* Dynamic lookup against an approved whitelist database is mandatory.

## 2. CORS Matrix Definitions
| Origin Whitelist Pattern | Allowed Methods | Allowed Headers | Credentials | Max Age (Cache) |
|---|---|---|---|---|
| `https://*.venus.local` | GET, POST, PUT | Content-Type, Authorization | True | 86400 (24 hours) |
| `https://external-partner.com` | GET, POST | Content-Type | False | 3600 (1 hour) |

## 3. Configuration Verification Test
Ensure that requests from unapproved domains are blocked:
```bash
# Verify CORS behavior using a custom Origin header
curl -H "Origin: https://malicious.com" -I https://api.venus.local/v1/data
# Output must not return the Access-Control-Allow-Origin header.
```
