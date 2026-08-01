# Training Data Privacy Matrix
**Document ID:** VENUS-USPTCROS-098
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Establishes guidelines and classification matrices for scanning, scrubbing, hashing, and anonymizing datasets used to train or fine-tune models.

## 2. Technical Specifications & Architecture
### Data Classification and Masking

| Category | Attributes | Processing Rule | Verification Method |
| --- | --- | --- | --- |
| Personal Identifiers | Name, SSN, Passport | Hashing / Drop | Regular Expression scan |
| Network Identifiers | IP, MAC address | Anonymization | Netmask check |
| Commercial Records | Credit card, Transactions | Dynamic Masking | Luhn algorithm check |

## 3. Code Fragment / Implementation Details
```python
import re

def scrub_pii_from_dataset(raw_text: str) -> str:
    # Basic regex patterns for PII detection
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
    
    scrubbed = re.sub(email_pattern, "[EMAIL_REDACTED]", raw_text)
    scrubbed = re.sub(ssn_pattern, "[SSN_REDACTED]", scrubbed)
    return scrubbed

if __name__ == "__main__":
    sample = "Please contact me at developer@venus.io, ssn is 000-12-3456."
    print(scrub_pii_from_dataset(sample))
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PrivacyMatrixConfig",
  "type": "object",
  "properties": {
    "enable_pii_scrubbing": {
      "type": "boolean"
    },
    "anonymization_algorithm": {
      "type": "string",
      "enum": [
        "SHA-256",
        "AES-256",
        "redaction"
      ]
    },
    "target_fields": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "enable_pii_scrubbing",
    "anonymization_algorithm",
    "target_fields"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
$$ScrubbingSuccessRate = \frac{RemovedPIIFields}{TotalIdentifiedPIIFields} \times 100\%$$

## 6. Institutional Verification Checklist
* [ ] Scan datasets to identify PII records before starting model training.
* [ ] Verify scrubbing patterns are applied to all fields containing personal data.
* [ ] Perform verification runs to ensure data fields do not leak in plain text.
* [ ] Audit dataset storage access parameters.

## 7. Cross-References
- [Model Theft Exfiltration Plan](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/MODEL_THEFT_EXFILTRATION_PLAN.md)
- [Pii Inventory Data Flow Map](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PII_INVENTORY_DATA_FLOW_MAP.md)
- [Privacy Impact Assessment](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/PRIVACY_IMPACT_ASSESSMENT.md)
