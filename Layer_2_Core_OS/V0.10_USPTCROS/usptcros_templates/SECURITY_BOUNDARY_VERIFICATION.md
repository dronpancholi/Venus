# USPTCROS Security Boundary Verification
**Document Link:** [Security Boundary Verification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURITY_BOUNDARY_VERIFICATION.md)  
**Map Reference:** [Trust Boundary Map](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TRUST_BOUNDARY_MAP.md)

This playbook outlines methods to verify the segregation controls implemented across trust boundaries.

## 1. Network Boundary Penetration Audits
Verify that database ports are inaccessible from outside the database proxy subnet.

```bash
# Nmap scan against the database subnet to ensure isolation
nmap -p 5432 --open -Pn 10.240.10.0/24
# Output must show 0 open database ports from external namespaces.
```

## 2. Token Isolation Verification
Test that an expired or tampered token is rejected by the internal service.

```bash
# Send request with invalid token to backend service
curl -k -i -H "Authorization: Bearer invalid_token_value" https://api.venus.local/v1/data
# Expect HTTP response code: 401 Unauthorized
```

## 3. Kubernetes Network Policy Validation
Ensure that pods in Namespace `A` cannot talk to pods in Namespace `B` unless explicitly permitted.

```bash
# Execute internal ping from unapproved service pod
kubectl exec -it pod-client-a -n namespace-a -- curl --max-time 5 http://service-b.namespace-b.svc.cluster.local:8080
# Output should time out: "curl: (28) Connection timed out after 5001 milliseconds"
```
