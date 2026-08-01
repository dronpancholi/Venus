# USPTCROS Attack Surface Mapping Spec
**Document Link:** [Attack Surface Mapping Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ATTACK_SURFACE_MAPPING_SPEC.md)

Specification for analyzing, tracking, and minimizing the system attack surface.

## 1. Attack Surface Categories
* **Network Attack Surface:** Exposed network interfaces, DNS endpoints, and firewall rules.
* **Software Attack Surface:** Active APIs, listening ports, libraries, and binary entry points.
* **Administrative Attack Surface:** Remote terminal accesses (SSH, Kubeconfig), admin portals, and web consoles.

## 2. Attack Surface Index (ASI) Calculation
The system calculates an ASI to measure vulnerability exposure:
$$ASI = (E_{ep} \times W_{ep}) + (P_{open} \times W_{port}) + (V_{cvss} \times W_{vuln})$$

Where:
* $E_{ep}$: Number of public endpoints (Weight $W_{ep} = 5.0$)
* $P_{open}$: Number of open internal ports (Weight $W_{port} = 2.0$)
* $V_{cvss}$: Sum of CVSS scores of active CVEs (Weight $W_{vuln} = 10.0$)

## 3. Inventory & Verification Command
To map the active port listening configurations, execute:
```bash
# Verify listening sockets on target host
ss -tulpn | grep -i listen
```
