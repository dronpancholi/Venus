# ENGINE — Kubernetes Generator
## V0.9 USEDPOS | Universal Software Engineering, Delivery & Production Operating System

---

## Purpose
Generates complete, production-grade Kubernetes manifests for any service. Applies resource management, auto-scaling, health probes, security contexts, network policies, and all VENUS deployment standards automatically.

---

## Input Requirements
```
Required:
  - Service name and container image reference
  - Resource requirements (CPU, memory baseline)
  - Environment variables and secrets list
  - Port configuration
  - Health check endpoint paths
  - Scaling requirements (min/max replicas, target CPU)

Optional:
  - Persistent volume requirements
  - Ingress requirements
  - Service mesh annotations (Istio/Linkerd)
  - Custom HPA metrics
  - Node affinity requirements
```

---

## Generated Manifests

### Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: {service-name}
  labels:
    team: {team-name}
    environment: {env}
```

### Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service-name}
  namespace: {service-name}
spec:
  replicas: {min-replicas}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app: {service-name}
  template:
    metadata:
      labels:
        app: {service-name}
        version: "{image-tag}"
    spec:
      serviceAccountName: {service-name}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
        - name: {service-name}
          image: {image}:{tag}
          ports:
            - containerPort: {port}
          resources:
            requests:
              cpu: "{cpu-request}"
              memory: "{memory-request}"
            limits:
              cpu: "{cpu-limit}"
              memory: "{memory-limit}"
          readinessProbe:
            httpGet:
              path: /health/ready
              port: {port}
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: {port}
            initialDelaySeconds: 30
            periodSeconds: 10
          startupProbe:
            httpGet:
              path: /health/startup
              port: {port}
            failureThreshold: 30
            periodSeconds: 10
          envFrom:
            - secretRef:
                name: {service-name}-secrets
          env:
            - name: NODE_ENV
              value: "{environment}"
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]
```

### Horizontal Pod Autoscaler
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {service-name}
  namespace: {service-name}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {service-name}
  minReplicas: {min}
  maxReplicas: {max}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 75
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
        - type: Percent
          value: 50
          periodSeconds: 30
```

### Network Policy
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {service-name}-network-policy
  namespace: {service-name}
spec:
  podSelector:
    matchLabels:
      app: {service-name}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: {port}
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: database
    - to:
        - namespaceSelector:
            matchLabels:
              name: cache
```

### Pod Disruption Budget
```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {service-name}-pdb
  namespace: {service-name}
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: {service-name}
```

---

## Security Defaults Applied
- Non-root container execution
- Read-only root filesystem where possible
- Drop all capabilities, add only required
- Resource limits always set (no unbounded containers)
- Network policies restrict ingress and egress
- Service accounts with minimal RBAC
