# Template: Deployment Topology

## 1. Document Control
*   **Project Name**: [Project Name]
*   **Topology ID**: DEP-[UUID]
*   **Target Cloud**: AWS / GCP / Azure

---

## 2. Cloud Infrastructure Architecture Map
*Provide a layout of cloud resources, subnets, and routing gates.*

```
[Route 53 DNS Router] ──► [WAF Shield] ──► [AWS Application Load Balancer]
                                                    │
                                                    ▼
                                     [Private Subnet: EC2 / Fargate]
                                                    │
                                                    ▼
                                     [Isolated Subnet: Aurora RDS DB]
```

---

## 3. Subnet Configuration Details
*   **Public Subnet**: Load balancers and WAF proxies only.
*   **Private Application Subnet**: Node API workers (no public IPs assigned).
*   **Isolated Database Subnet**: Postgres DB node access restricted to Fargate security group.

---

## 4. Continuous Integration & Deployment (CI/CD)
*   **Pipeline Tool**: GitHub Actions / GitLab CI.
*   **Deployment Method**: Blue-Green deployment with automated DNS route weighting.
*   *Validation Gate*: Post-deploy smoke test must pass 100% checks before scaling down previous version.
