# Kubernetes Ingress Route Specification
**Document ID:** VENUS-STD-081
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This specification details the configuration standards for external ingress traffic routing, TLS termination, and host path mapping within the Project Venus Kubernetes environments.

## 2. Ingress Manifest Template (`ingress.yaml`)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: venus-ingress-router
  namespace: venus-prod
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
    - hosts:
        - api.venus.org
      secretName: venus-api-tls-secret
  rules:
    - host: api.venus.org
      http:
        paths:
          - path: /v1/orders
            pathType: Prefix
            backend:
              service:
                name: venus-order-service-svc
                port:
                  number: 80
          - path: /v1/auth
            pathType: Prefix
            backend:
              service:
                name: venus-auth-service-svc
                port:
                  number: 80
```

## 3. Configuration Standards
1. **Force TLS:** All endpoints must redirect HTTP traffic to HTTPS (port 443).
2. **Wildcard Routing:** Wildcard hosts (`*.venus.org`) are prohibited. Each sub-domain must be explicitly mapped in the ingress manifests.
3. **Session Affinity:** Ingress-level sticky sessions must not be enabled. Session persistence should be managed out-of-band using token mechanisms.

## 4. Cross-References
- [Kubernetes Deployment Manifest](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_DEPLOYMENT_MANIFEST.md)
- [CDN SSL Termination Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/CDN_SSL_TERMINATION_SPEC.md)
