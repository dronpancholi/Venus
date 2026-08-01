# USPTCROS Certificate Auto-Renewal Config
**Document Link:** [Certificate Auto-Renewal Config](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CERTIFICATE_AUTO_RENEWAL_CONFIG.md)  
**References:** [PKI Architecture Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PKI_ARCHITECTURE_SPEC.md)

## 1. Automated Certificate Renewal Engine
Certificates must be renewed automatically to prevent operational outages.

## 2. Cert-Manager Custom Resource Definition (CRD) Spec
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: venus-service-tls
  namespace: venus-system
spec:
  secretName: venus-service-tls-secret
  duration: 2160h # 90 days
  renewBefore: 720h # 30 days
  subject:
    organizations:
    - Project Venus Strategic Systems
  commonName: service.venus.local
  dnsNames:
  - service.venus.local
  - internal.venus.local
  issuerRef:
    name: venus-vault-issuer
    kind: ClusterIssuer
```

## 3. Post-Renewal Verification Hooks
On renewal, target pods must reload TLS configurations without service interruption.
```bash
# Force reload cert configuration on web proxies
nginx -s reload
```
