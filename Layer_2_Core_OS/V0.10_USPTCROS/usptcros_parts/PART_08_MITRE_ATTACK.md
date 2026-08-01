# Project Venus USPTCROS — Part 08: MITRE ATT&CK Mapping

## 1. Executive Summary
Project Venus aligns its logging, detection engineering, and incident response frameworks to the MITRE ATT&CK framework. This ensures comprehensive coverage across cloud environments, containers, and AI agent workloads.

## 2. Key TTPs & Detections (Cloud & Containers)
The following matrix highlights the critical MITRE ATT&CK techniques monitored by USPTCROS:

| Phase | Technique ID | Technique Name | Venus Detection Mechanism |
| :--- | :--- | :--- | :--- |
| Privilege Escalation | T1611 | Escape to Host | Monitoring syscalls via eBPF (auditd/Falco) |
| Credential Access | T1528 | Steal Application Token | Monitoring access to IMDS metadata services |
| Command and Control | T1071 | Application Layer Protocol | Analyzing unexpected HTTPS/DNS query patterns |
| Lateral Movement | T1021 | Remote Services | Tracking SSH/gRPC calls across container namespaces |

---

## 3. Sigma Detection Rule Structure (Example)
The following Sigma rule validates and alerts on attempts to escape from a container environment by mounting the host namespace or sensitive filesystem paths.

```yaml
title: Container Breakout Attempt via Sensitive Mounts
id: 5b6c31fa-e945-4202-b0b3-95be24869c9b
status: experimental
description: Detects mounting of host directories (/var/run/docker.sock, /, /etc) within non-privileged containers.
logsource:
    category: container_creation
    product: kubernetes
detection:
    selection:
        volume_mounts:
            - '/var/run/docker.sock'
            - '/host'
            - '/var/run/containerd/containerd.sock'
    condition: selection
falsepositives:
    - Administrative maintenance scripts (must be explicitly whitelisted by service account ID).
level: critical
```

---

## 4. Mitigation Audit Checklist
- [ ] Ensure all containers do not run in privileged mode (`securityContext.privileged: false`).
- [ ] Configure egress network policies to block access to the cloud metadata endpoint (`169.254.169.254`).
- [ ] Implement runtime threat detection rules for unauthorized processes starting inside container limits.
- [ ] Review system logs in BigQuery weekly to identify anomalous credential lookups.

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 07: Kill Chains](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_07_KILL_CHAINS.md)
- **Next Chapter**: [Part 09: Identity Engineering](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_09_IDENTITY_ENGINEERING.md)
