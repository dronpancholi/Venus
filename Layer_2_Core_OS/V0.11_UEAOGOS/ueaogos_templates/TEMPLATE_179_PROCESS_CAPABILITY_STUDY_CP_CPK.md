# Process Capability Study (Cp & Cpk) Template
## Metadata
| Attribute | Value |
|---|---|
| Template ID | TEMPLATE_179 |
| Filename | TEMPLATE_179_PROCESS_CAPABILITY_STUDY_CP_CPK.md |
| Version | 1.0.0 |
| Classification | Confidential |
| Domain | Six Sigma Analytics |
| Owner | Quality Engineer |
| Strategic Framework | [V0.11_UEAOGOS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/V0.11_UEAOGOS.md) |

---

## 1. Executive Summary & Purpose
This template provides the strategic operational standard for the Process Capability Study (Cp & Cpk) Template. It is designed to satisfy the core constitutional governance principles of Project Venus.

---

## 2. Mathematical Formulations & Performance Models
Process Capability indices ($C_p$ and $C_{pk}$) are calculated as follows:
$$C_p = \frac{USL - LSL}{6\sigma}$$
$$C_{pk} = \min\left(\frac{USL - \mu}{3\sigma}, \frac{\mu - LSL}{3\sigma}\right)$$
where:
$USL$ is the Upper Specification Limit.
$LSL$ is the Lower Specification Limit.
$\mu$ is the process mean.
$\sigma$ is the process standard deviation.
For a Six Sigma process:
$$C_p \ge 2.00 \quad \text{and} \quad C_{pk} \ge 1.50$$

---

## 3. Operational Specification & Reference Table
| Parameter | Symbol | Value | Unit | Definition |
|---|---|---|---|---|
| Upper Specification Limit | $USL$ | 11.00 | mm | Max allowed size |
| Lower Specification Limit | $LSL$ | 9.00 | mm | Min allowed size |
| Process Mean | $\mu$ | 10.01 | mm | Calculated average size |
| Standard Deviation | $\sigma$ | 0.15 | mm | Process spread variation |
| **Process Capability** | **$C_p$** | **2.22** | **Ratio** | **Potential capability** |
| **Capability Index** | **$C_{pk}$**| **2.20** | **Ratio** | **Actual process capability** |

---

## 4. System Configuration & Schema Definition
```python
import numpy as np

def calculate_capability(data, usl, lsl):
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    if std == 0:
        return 0.0, 0.0
    cp = (usl - lsl) / (6 * std)
    cpk = min((usl - mean) / (3 * std), (mean - lsl) / (3 * std))
    return round(cp, 2), round(cpk, 2)

# Verify behavior
mock_data = [10.2, 10.0, 9.8, 10.1, 9.9, 10.0, 10.2, 9.9]
assert calculate_capability(mock_data, 11.0, 9.0) == (1.11, 1.11)
```

---

## 5. Institutional Execution Checklist
### 5.1 Pre-Execution Phase
- [ ] Validate that the process is in a state of statistical control using control charts. - [ ] Collect at least 30 random samples from production lines.

### 5.2 Execution Phase
- [ ] Execute the mean, standard deviation, and capability index calculations. - [ ] Document the USL and LSL values for target parameters.

### 5.3 Post-Execution Phase
- [ ] Publish capability study report to the Quality Control board. - [ ] Investigate process variance sources if $C_{pk} < 1.50$.

### 5.4 Exception / Rollback Phase
- [ ] Discard study results if data collection does not follow sampling standards. - [ ] Reschedule sampling.

---

## 6. Document & Template References
- Strategic Core Governance: [V0.11_UEAOGOS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/V0.11_UEAOGOS.md)
- Target Directory: [ueaogos_templates](file:///Users/dronpancholi/Developer/01_Strategic/Venus/Layer_2_Core_OS/V0.11_UEAOGOS/ueaogos_templates/)
