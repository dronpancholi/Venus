# USPTCROS Kubernetes Network Policy Spec
**Document Link:** [Kubernetes Network Policy Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/KUBERNETES_NETWORK_POLICY_SPEC.md)  
**References:** [VPC Subnet Traffic Isolation](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/VPC_SUBNET_TRAFFIC_ISOLATION.md)

## 1. Network Namespace Isolation Rule Sets
Implement zero-trust network segregation between Pod namespaces.

## 2. Database Subnet Ingress Policy YAML
Ensure only App Pods can initiate connections to the database on port 5432:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-db-access-from-app
  namespace: venus-database
spec:
  podSelector:
    matchLabels:
      app: database-server
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: venus-system
      podSelector:
        matchLabels:
          app: core-api-runner
    ports:
    - protocol: TCP
      port: 5432
```
