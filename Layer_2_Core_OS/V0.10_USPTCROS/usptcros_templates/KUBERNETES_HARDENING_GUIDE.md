# USPTCROS Kubernetes Hardening Guide
**Document Link:** [Kubernetes Hardening Guide](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KUBERNETES_HARDENING_GUIDE.md)  
**References:** [Kubernetes Network Policy Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KUBERNETES_NETWORK_POLICY_SPEC.md), [Kubernetes Pod Security Standards](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KUBERNETES_POD_SECURITY_STANDARDS.md)

## 1. API Server Security Baseline
* **Disable Anonymous Auth:** The `--anonymous-auth=false` flag must be set on the API server.
* **Node Authorization:** Enable `--authorization-mode=Node,RBAC` to isolate node permissions.
* **Secure ETCD Data Store:** Etcd communications must use mTLS. ETCD storage volumes must be encrypted.

## 2. ETCD Encryption Configuration YAML
Save encryption settings to `/etc/kubernetes/encryption-config.yaml` to encrypt Secrets at rest:
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: "ENV[ETCD_ENCRYPTION_KEY_BASE64]"
      - identity: {}
```
