# Cloud Networking VPC Blueprint
**Document ID:** VENUS-STD-084
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview
This network blueprint outlines the architecture of the Virtual Private Cloud (VPC) for hosting Project Venus infrastructure, separating network segments to maintain security boundaries.

## 2. IP Allocation and Subnet Map
The VPC uses the `10.100.0.0/16` CIDR block, distributed as follows:

| Subnet Name | CIDR Block | Accessibility | Purpose |
| :--- | :--- | :--- | :--- |
| **Public Subnet A** | `10.100.1.0/24` | Internet-facing | NAT Gateways, Ingress load balancers. |
| **Public Subnet B** | `10.100.2.0/24` | Internet-facing | NAT Gateways, Ingress load balancers. |
| **Private App Subnet A** | `10.100.10.0/22`| Private routing | Application services, cluster worker nodes. |
| **Private App Subnet B** | `10.100.14.0/22`| Private routing | Application services, cluster worker nodes. |
| **Private Data Subnet A** | `10.100.20.0/24`| Direct internal only| Database engines (PostgreSQL, Redis nodes). |
| **Private Data Subnet B** | `10.100.21.0/24`| Direct internal only| Database engines (PostgreSQL, Redis nodes). |

## 3. Network Architecture Diagram
```text
+---------------------------------------------------------------------------------+
|                                 VPC (10.100.0.0/16)                             |
|                                                                                 |
|   +------------------------------------+   +------------------------------------+
|   |    Public Subnet A (10.100.1.0/24) |   |    Public Subnet B (10.100.2.0/24) |
|   |    [ NAT-GW-A ]   [ ALB-A ]        |   |    [ NAT-GW-B ]   [ ALB-B ]        |
|   +------------------+-----------------+   +------------------+-----------------+
|                      |                                        |
|                      v                                        v
|   +------------------+-----------------+   +------------------+-----------------+
|   |  Private App Subnet A (10.100.10/22)|  |  Private App Subnet B (10.100.14/22)|
|   |  [ Kubernetes Pod Node Group A ]   |   |  [ Kubernetes Pod Node Group B ]   |
|   +------------------+-----------------+   +------------------+-----------------+
|                      |                                        |
|                      v                                        v
|   +------------------+-----------------+   +------------------+-----------------+
|   |  Private Data Subnet A (10.100.20/24)  |  Private Data Subnet B (10.100.21/24)  |
|   |  [ PostgreSQL Master Instance ]    |   |  [ PostgreSQL Read Replica ]       |
|   +------------------------------------+   +------------------------------------+
+---------------------------------------------------------------------------------+
```

## 4. Security Group / Firewalls Policy Rules
1. **Public Ingress:** Allow inbound traffic on port 443 only from CDN edge IP addresses.
2. **App Ingress:** Allow inbound traffic from Public Subnet IPs only.
3. **Data Ingress:** Block all internet routing. Only allow inbound traffic on port 5432 (Postgres) and 6379 (Redis) from Private App Subnet IPs.

## 5. Cross-References
- [Terraform Module Blueprint](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/TERRAFORM_MODULE_BLUEPRINT.md)
- [IAM Roles and Policies Specification](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usedpos_templates/IAM_ROLES_POLICIES_SPEC.md)
