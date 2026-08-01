# USPTCROS Trust Boundary Checklist
**Document Link:** [Trust Boundary Checklist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TRUST_BOUNDARY_CHECKLIST.md)  
**Map Reference:** [Trust Boundary Map](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TRUST_BOUNDARY_MAP.md)

## 1. API Edge Gateway Verification
- [ ] TLS 1.3 is enforced with forward secrecy ciphers only.
- [ ] Egress traffic from the gateway is constrained to specific target namespaces.
- [ ] IP Rate limiting is active and configured to block bursts exceeding 100 req/sec.

## 2. Internal Microservice Isolation
- [ ] All inter-service communications enforce mTLS via service mesh.
- [ ] Access is validated using scoped JWT tokens.
- [ ] Network namespaces are isolated; default egress rules block non-whitelisted traffic.

## 3. Cryptographic Boundary Audits
- [ ] System secrets are loaded dynamically into memory and never written to persistent disk.
- [ ] HSM access keys are rotated at the policy intervals.
- [ ] Database credentials are short-lived (max duration: 3600 seconds).

## 4. Verification Command Script
```bash
# Verify TLS cipher settings on target gateway
openssl s_client -connect gateway.venus.local:443 -tls1_3
```
