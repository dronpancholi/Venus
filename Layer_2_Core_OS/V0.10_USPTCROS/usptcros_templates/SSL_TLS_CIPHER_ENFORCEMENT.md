# USPTCROS SSL/TLS Cipher Enforcement Standard
**Document Link:** [SSL/TLS Cipher Enforcement](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SSL_TLS_CIPHER_ENFORCEMENT.md)  
**References:** [TLS/mTLS Configuration Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TLS_MTLS_CONFIGURATION_GUIDE.md)

## 1. Approved TLS Cipher Suites
Only Forward Secrecy ciphers with Authenticated Encryption (AEAD) are allowed:
* `TLS_AES_256_GCM_SHA384` (TLS 1.3 only)
* `TLS_CHACHA20_POLY1305_SHA256` (TLS 1.3 only)
* `ECDHE-ECDSA-AES256-GCM-SHA384` (TLS 1.2 fallback)
* `ECDHE-RSA-AES256-GCM-SHA384` (TLS 1.2 fallback)

## 2. Auditing and Scanning Procedures
System administrators must run validation scans against external ports monthly:
```bash
# Audit cipher suites on the external gateway interface
testssl.sh --standard gateway.venus.local:443
# Scan output must report no Medium/High/Critical TLS vulnerabilities.
```
