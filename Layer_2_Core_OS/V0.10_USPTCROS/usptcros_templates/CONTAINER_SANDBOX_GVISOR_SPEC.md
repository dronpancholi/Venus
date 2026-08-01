# USPTCROS Container Sandbox gVisor Spec
**Document Link:** [Container Sandbox gVisor Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CONTAINER_SANDBOX_GVISOR_SPEC.md)  
**References:** [Kubernetes Hardening Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KUBERNETES_HARDENING_GUIDE.md)

## 1. gVisor Runtime Class Definition
To mitigate container-breakout vectors, high-risk untrusted workloads execute inside a gVisor sandbox.

```
  ┌────────────────────────────────────────────────────────┐
  │                 Kubernetes Pod (Workload)              │
  └───────────────────────────┬────────────────────────────┘
                              │
                    (Restricted System Calls)
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                   gVisor Sentry Core                   │
  │     (User-space kernel intercepts system interactions) │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                      Host Kernel                       │
  └────────────────────────────────────────────────────────┘
```

## 2. RuntimeClass Configuration Spec
```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
```

## 3. Workload Deployment Spec Binding
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: untrusted-api-service
  namespace: venus-system
spec:
  template:
    spec:
      runtimeClassName: gvisor
      containers:
      - name: api-runner
        image: venus/untrusted-api:latest
```
