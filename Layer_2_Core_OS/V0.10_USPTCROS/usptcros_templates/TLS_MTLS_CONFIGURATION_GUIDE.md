# USPTCROS TLS/mTLS Configuration Guide
**Document Link:** [TLS/mTLS Configuration Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TLS_MTLS_CONFIGURATION_GUIDE.md)  
**References:** [SSL/TLS Cipher Enforcement](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SSL_TLS_CIPHER_ENFORCEMENT.md)

## 1. Envoy mTLS Configuration Snippet
For service mesh communications, use the following Envoy cluster tls configuration:
```yaml
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
    common_tls_context:
      tls_certificates:
      - certificate_chain: { filename: "/etc/certs/tls.crt" }
        private_key: { filename: "/etc/certs/tls.key" }
      validation_context:
        trusted_ca: { filename: "/etc/certs/ca.crt" }
        require_client_certificate: true
```

## 2. Server TLS 1.3 Configuration (Nginx)
Ensure server setups only support modern TLS:
```nginx
# Secure Nginx Configuration
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
}
```
