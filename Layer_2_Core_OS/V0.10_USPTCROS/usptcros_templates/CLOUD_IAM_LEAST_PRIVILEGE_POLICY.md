# USPTCROS Cloud IAM Least Privilege Policy
**Document Link:** [Cloud IAM Least Privilege Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CLOUD_IAM_LEAST_PRIVILEGE_POLICY.md)  
**References:** [Role Definition Catalog](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ROLE_DEFINITION_CATALOG.md)

## 1. Service Account Isolation Policies
* Every workload microservice runs under a dedicated, unique Service Account.
* Generic service accounts (like default compute engine accounts) are disabled.
* Authenticating to cloud resources must utilize Workload Identity Federation (binding K8s ServiceAccounts to Cloud IAM ServiceAccounts).

## 2. Workload Identity Binding Policy Configuration
```yaml
apiVersion: iam.cnrm.cloud.google.com/v1beta1
kind: IAMPolicyMember
metadata:
  name: workload-identity-binding
  namespace: venus-system
spec:
  member: serviceAccount:project-venus-prod.svc.id.goog[venus-system/service-api-engine]
  role: roles/iam.serviceAccountTokenCreator
  resourceRef:
    apiVersion: iam.cnrm.cloud.google.com/v1beta1
    kind: IAMServiceAccount
    name: sa-venus-backend-runner
```
