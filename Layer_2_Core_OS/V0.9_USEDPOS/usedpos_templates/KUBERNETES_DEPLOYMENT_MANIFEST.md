# Kubernetes Deployment Manifest
**Document ID:** VENUS-STD-080
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Purpose
This document specifies a production-grade Kubernetes Deployment and Service manifest configuration template, highlighting security parameters and health probes.

## 2. Manifest Template (`deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: venus-core-service
  namespace: venus-prod
  labels:
    app.kubernetes.io/name: venus-core-service
    app.kubernetes.io/part-of: project-venus
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: venus-core-service
  template:
    metadata:
      labels:
        app: venus-core-service
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001
      containers:
        - name: application
          image: gcr.io/project-venus/core-service:v1.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1024Mi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          env:
            - name: NODE_ENV
              value: "production"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: venus-db-secrets
                  key: database-password
          startupProbe:
            httpGet:
              path: /healthz/startup
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 6
          livenessProbe:
            httpGet:
              path: /healthz/liveness
              port: http
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /healthz/readiness
              port: http
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 2
---
apiVersion: v1
kind: Service
metadata:
  name: venus-core-service-svc
  namespace: venus-prod
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
  selector:
    app: venus-core-service
```

## 3. Cross-References
- [Kubernetes Ingress Route Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_INGRESS_ROUTE_SPEC.md)
- [Kubernetes Autoscaling HPA Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/KUBERNETES_AUTOSCALING_HPA_SPEC.md)
