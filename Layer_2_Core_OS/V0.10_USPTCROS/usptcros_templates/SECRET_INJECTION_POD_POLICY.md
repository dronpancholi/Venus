# USPTCROS Secret Injection Pod Policy
**Document Link:** [Secret Injection Pod Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECRET_INJECTION_POD_POLICY.md)  
**References:** [Secrets Management Vault Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECRETS_MANAGEMENT_VAULT_POLICY.md)

## 1. Secrets Injection Architecture
Secrets are mounted directly as in-memory volumes (tmpfs) to prevent exposure via environment variables or logs.

## 2. Vault Agent Injector Deployment Spec
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-vault-injected
  namespace: venus-system
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "venus-app-role"
        vault.hashicorp.com/agent-inject-secret-database-config: "secret/data/production/database/config"
        # Template definition format to write secrets to files
        vault.hashicorp.com/agent-inject-template-database-config: |
          {{- with secret "secret/data/production/database/config" -}}
          username: {{ .Data.data.username }}
          password: {{ .Data.data.password }}
          {{- end -}}
    spec:
      containers:
      - name: main-runner
        image: venus/app-main:latest
```
