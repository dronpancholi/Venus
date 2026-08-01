# USPTCROS VPC Subnet Traffic Isolation Spec
**Document Link:** [VPC Subnet Traffic Isolation](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/VPC_SUBNET_TRAFFIC_ISOLATION.md)  
**References:** [Network Security Group Rules](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/NETWORK_SECURITY_GROUP_RULES.md)

## 1. VPC IP Subnet Layout
The system network is segmented into isolated subnets with strict routing tables.

* **Edge DMZ Subnet:** `10.240.10.0/24`. Houses public load balancers and Envoy edge proxies.
* **App Subnet:** `10.240.20.0/24`. Houses internal application runtimes. No public IP assignments allowed.
* **Secure Database Subnet:** `10.240.30.0/24`. Houses storage resources. Completely isolated.
* **Secrets & HSM Subnet:** `10.240.40.0/24`. Houses Vault and encryption interfaces.

## 2. Traffic Flow Diagram
```
[Edge Subnet: 10.240.10.0/24]
        │
(Routing Firewall)
        ▼
[App Subnet: 10.240.20.0/24]
        │
(Routing Firewall)
        ▼
[Database Subnet: 10.240.30.0/24]  ◄── (mTLS only) ──► [HSM Subnet: 10.240.40.0/24]
```
