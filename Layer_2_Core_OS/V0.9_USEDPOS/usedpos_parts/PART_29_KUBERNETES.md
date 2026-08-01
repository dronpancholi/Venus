# Part 29: Kubernetes

## 1. Context & Strategy
Kubernetes under Project Venus governs the container orchestration layer. This manual defines the operational structures, scaling equations, service topologies, and cluster security parameters. All deployment manifests must explicitly request resource limits, configure liveness/readiness checks, establish disruption tolerances, and support auto-scaling behaviors.

---

## 2. Orchestration scaling & Resource Models

### 2.1 Horizontal Pod Autoscaler (HPA) Formula
Kubernetes HPAs calculate the desired replica count ($N_{des}$) using the ratio of current metric values to target metric values:

$$N_{des} = \lceil N_{curr} \times \frac{\text{Metric}_{curr}}{\text{Metric}_{target}} \rceil$$

*   *Example*: If a service has $N_{curr} = 3$ replicas, a target CPU utilization of $60\%$, and the average CPU utilization is currently measured at $80\%$, the desired replicas will be:
    $$N_{des} = \lceil 3 \times \frac{80}{60} \rceil = \lceil 4.0 \rceil = 4\text{ replicas}$$

### 2.2 Pod Disruption Budget (PDB) & Availability Calculation
To guarantee services remain available during cluster maintenance operations, PDB limits are calculated based on the maximum allowed concurrent unavailable pods ($U_{max}$):

$$U_{max} = N_{replicas} - N_{min\_available}$$

For high-availability services:
*   Maintain $N_{min\_available} \ge 2$ or $N_{min\_available} \ge 50\%$.

---

## 3. Kubernetes Deployment Blueprint

### 3.1 Service Deployment & Auto-scaling Configuration
All backend services must be deployed with explicit resource limits, probes, services, and HPAs.

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: venus-payment-service
  namespace: venus-prod
  labels:
    app: venus-payment-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: venus-payment-service
  template:
    metadata:
      labels:
        app: venus-payment-service
    spec:
      containers:
      - name: app
        image: gcr.io/project-venus-prod/payment-service:v1.2.0
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1024Mi"
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: venus-payment-service-hpa
  namespace: venus-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: venus-payment-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: venus-payment-service-pdb
  namespace: venus-prod
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: venus-payment-service
```

### 3.2 Helm Values Integration Schema
Custom Helm charts must validate their core schema parameters using this JSON template structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HelmChartValuesSchema",
  "type": "object",
  "properties": {
    "replicaCount": { "type": "integer", "minimum": 1 },
    "image": {
      "type": "object",
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" },
        "pullPolicy": { "type": "string" }
      },
      "required": ["repository", "tag", "pullPolicy"]
    }
  },
  "required": ["replicaCount", "image"]
}
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that all pods have explicit CPU and memory request/limit specifications.
*   [ ] Confirmed liveness and readiness probes target validated health check endpoints.
*   [ ] Verified that a Pod Disruption Budget (PDB) is deployed alongside the HPA.
*   [ ] Checked that configurations do not mount writeable host directories directly to container nodes.
*   [ ] Confirmed that ingress configs run with active TLS terminates and SSL redirects.
