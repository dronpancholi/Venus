# USPTCROS Web Application Hardening Guide
**Document Link:** [Web Application Hardening Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/WEB_APPLICATION_HARDENING_GUIDE.md)  
**References:** [CORS HTTP Headers Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CORS_HTTP_HEADERS_MATRIX.md)

## 1. Mandatory HTTP Response Headers
Every HTTP response issued by system portals must carry the following headers:

| Header Name | Mandatory Value | Security Objective |
|---|---|---|
| `Content-Security-Policy` | `default-src 'self'; object-src 'none'; frame-ancestors 'none';` | Prevent XSS and Clickjacking |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Force TLS connection usage |
| `X-Frame-Options` | `DENY` | Clickjacking prevention |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME-sniffing exploits |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Protect sensitive URL parameters |

## 2. Hardened Cookie Directives
Cookies holding authentication tokens must use:
```http
Set-Cookie: session_token=token_value; Secure; HttpOnly; SameSite=Strict; Path=/
```
