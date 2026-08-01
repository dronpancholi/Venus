# USPTCROS Network Security Group Rules
**Document Link:** [Network Security Group Rules](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/NETWORK_SECURITY_GROUP_RULES.md)  
**References:** [VPC Subnet Traffic Isolation](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/VPC_SUBNET_TRAFFIC_ISOLATION.md)

## 1. Firewall Rule Definitions
All network boundaries must implement default-deny policies.

## 2. Ingress Security Group Rules
| Rule Priority | Description | Protocol | Source Range | Target Port | Action |
|---|---|---|---|---|---|
| 100 | Allow HTTPS Edge Traffic | TCP | `0.0.0.0/0` | 443 | ALLOW |
| 110 | Allow Internal mTLS APIs | TCP | `10.240.10.0/24` | 8443 | ALLOW |
| 120 | Allow Vault API Queries | TCP | `10.240.20.0/24` | 8200 | ALLOW |
| 999 | Block All Remaining Traffic | Any | `0.0.0.0/0` | Any | DENY |

## 3. Egress Security Group Rules
| Rule Priority | Description | Protocol | Destination Range | Target Port | Action |
|---|---|---|---|---|---|
| 100 | Allow Outbound DNS Resolves | UDP/TCP | `10.0.0.2` | 53 | ALLOW |
| 110 | Allow Outbound DB Proxy | TCP | `10.240.30.0/24` | 5432 | ALLOW |
| 999 | Block All Remaining Traffic | Any | `0.0.0.0/0` | Any | DENY |
