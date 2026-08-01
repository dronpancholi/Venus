# USPTCROS Kubernetes Pod Security Standards
**Document Link:** [Kubernetes Pod Security Standards](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KUBERNETES_POD_SECURITY_STANDARDS.md)  
**References:** [Kubernetes Hardening Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KUBERNETES_HARDENING_GUIDE.md)

## 1. Pod Security Admission Control
Enforce the "Restricted" Pod Security Standard across all system namespaces.

## 2. Namespace Admission Configuration Spec
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: venus-system
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## 3. Mandatory Pod Manifest Constraints
* `runAsNonRoot: true` must be specified in the securityContext.
* `allowPrivilegeEscalation: false` must be set.
* ReadOnly root filesystem must be enforced (`readOnlyRootFilesystem: true`).
* Capabilities must block all system overrides (drop `ALL`).
