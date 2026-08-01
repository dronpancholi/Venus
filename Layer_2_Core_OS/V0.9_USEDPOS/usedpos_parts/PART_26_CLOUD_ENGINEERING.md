# Part 26: Cloud Engineering

## 1. Context & Strategy
Cloud Engineering under Project Venus governs the network topology, security isolation, regional replication, and runtime hosting infrastructure across cloud providers. We mandate zero-trust network boundaries, private connectivity via service endpoints, multi-region high availability architectures, and automated resource cleanup.

---

## 2. Mathematical Reliability & Networking Models

### 2.1 Multi-Region Availability Model
To defend against regional provider failures, systems must run in active-active or active-passive multi-region configurations. The joint availability ($A_{sys}$) of two independent regions, each with availability $A_{reg} = 99.9\%$, is calculated as:

$$A_{sys} = 1 - (1 - A_{reg})^2 = 1 - (1 - 0.999)^2 = 1 - 0.000001 = 99.9999\%$$

### 2.2 VPC CIDR Subnet Block Allocation Formula
Cloud VPCs allocate subnets using Classless Inter-Domain Routing (CIDR) blocks. For a given mask length $M$, the total usable host IP addresses ($N_{usable}$) is:

$$N_{usable} = 2^{32 - M} - 5$$

*(5 IP addresses are reserved by the cloud provider for network, gateway, DNS, metadata, and broadcast).*
*   For a $/24$ subnet: $2^{32-24} - 5 = 256 - 5 = 251$ usable hosts.
*   For a $/20$ subnet: $2^{32-20} - 5 = 4096 - 5 = 4091$ usable hosts.

---

## 3. Terraform Cloud Infrastructure Specifications

### 3.1 Google Cloud VPC & Private Subnet Terraform Setup
All runtime nodes must be provisioned inside private subnets without public IP addresses, routing outbound traffic through Cloud NAT.

```tf
# vpc.tf
resource "google_compute_network" "vpc" {
  name                    = "venus-vpc-prod"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "private_subnet" {
  name                     = "venus-subnet-private-us-central1"
  ip_cidr_range            = "10.0.1.0/24"
  region                   = "us-central1"
  network                  = google_compute_network.vpc.id
  private_ip_google_access = true
}

resource "google_compute_router" "router" {
  name    = "venus-router-us-central1"
  region  = "us-central1"
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "venus-nat-us-central1"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}
```

### 3.2 Private Service Connect API Schema Definition
Services connecting to internal databases must validate their VPC peering configuration via this structured schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PrivateServiceConnectionSettings",
  "type": "object",
  "properties": {
    "vpcId": { "type": "string" },
    "privateEndpointIp": {
      "type": "string",
      "format": "ipv4"
    },
    "serviceAttachmentUri": { "type": "string" }
  },
  "required": ["vpcId", "privateEndpointIp", "serviceAttachmentUri"]
}
```

---

## 4. Reusable Checklist & Exit Criteria
*   [ ] Checked that all compute instances reside in private subnets with no public IPs assigned.
*   [ ] Confirmed CIDR calculations account for projected network growth over a 3-year horizon.
*   [ ] Verified egress traffic passes exclusively through verified NAT gateways.
*   [ ] Checked that VPC firewall rules deny all traffic by default (ingress/egress), applying strict allow whitelists.
*   [ ] Confirmed regional DNS latency routing maps are validated globally.
