# Helm Chart Values Template
**Document ID:** VENUS-STD-083
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Purpose
This document provides a template of default configurations for the deployment of Helm charts in the Project Venus cluster system.

## 2. Configuration Values Template (`values.yaml`)
```yaml
# Default values for venus-application-chart.
replicaCount: 3

image:
  repository: gcr.io/project-venus/application
  pullPolicy: IfNotPresent
  # Overrides the image tag whose default is the chart appVersion.
  tag: "v1.0.0"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: "venus-application-sa"

podAnnotations: {}

podSecurityContext:
  fsGroup: 1001

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1001
  runAsGroup: 1001

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: "nginx"
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: api.venus.org
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: venus-api-tls-secret
      hosts:
        - api.venus.org

resources:
  limits:
    cpu: 1000m
    memory: 1024Mi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 60
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}
```

## 3. Cross-References
- [Kubernetes Deployment Manifest](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_DEPLOYMENT_MANIFEST.md)
- [Kubernetes Ingress Route Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_INGRESS_ROUTE_SPEC.md)
