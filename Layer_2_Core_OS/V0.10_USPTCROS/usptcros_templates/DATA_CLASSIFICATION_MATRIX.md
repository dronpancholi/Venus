# USPTCROS Data Classification Matrix
**Document Link:** [Data Classification Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DATA_CLASSIFICATION_MATRIX.md)

Detailed mapping of system data fields to compliance classes and security requirements.

## 1. Data Classification Tiers
| Classification Level | Definition | Examples |
|---|---|---|
| **L3 - Restricted** | Critical impact if exposed. Highly regulated data. | Root private keys, HSM credentials, passwords. |
| **L2 - Confidential** | Serious impact if exposed. Regulated data. | PII (Email, Phone), financial records, audit logs. |
| **L1 - Internal** | Minor internal disruption. Not for public. | Source code, internal design specs, network topologies. |
| **L0 - Public** | No impact. Intentionally open. | Public API documentation, open-source code libraries. |

## 2. Controls Mapping Matrix
| Control Target | L3 - Restricted | L2 - Confidential | L1 - Internal | L0 - Public |
|---|---|---|---|---|
| **Encryption at Rest** | AES-GCM-256 + HSM Key | AES-GCM-256 | AES-256 | Optional |
| **Encryption in Transit** | TLS 1.3 (mTLS) | TLS 1.2 / 1.3 | TLS 1.2 | HTTP/HTTPS |
| **Masking / Tokenization** | Full Tokenization | Structural Masking | Not required | Not required |
| **Access Control** | Admin Roles (MFA) | Department Roles (MFA)| Internal SSO | Open |
| **Retention Policy** | 7 Years | 3 Years | 1 Year | Unrestricted |

## 3. Structural Masking Logic for Logs
```json
{
  "PII_Masking_Rule": {
    "targetField": "email",
    "regexMatch": "^(?i)(.)(.*)(@.*)$",
    "replacePattern": "$1****$3"
  }
}
```
