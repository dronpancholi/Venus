# Part 21: Secrets Management

## 1. Context & Strategy
This manual outlines the mandatory security protocols, lifecycle management, and architectural standards for secrets management under Project Venus. Hardcoded secrets, API keys, or plaintext configurations in repository structures are strictly prohibited. All secrets must be dynamically injected at runtime, encrypted at rest using industry-standard cryptographic algorithms, and audited continuously.

---

## 2. Secrets Lifecycle & Encryption Architecture

### 2.1 Envelope Encryption Model
All sensitive values must use envelope encryption. A Data Encryption Key (DEK) is generated locally to encrypt the payload, and the DEK itself is encrypted using a Key Encryption Key (KEK) managed by an external Key Management Service (KMS).

```
[Plaintext Secret] + [Generated DEK] ──(AES-256-GCM)──► [Ciphertext Payload]
                                                              ▲
[KEK (KMS/HSM Managed)] + [DEK] ──────(KMS Encrypt)──────► [Encrypted DEK]
```

### 2.2 Mathematical Model for Secret Entropy
To resist brute-force attacks, all generated secrets must meet minimum entropy requirements:

$$H = L \log_2(R)$$

Where:
*   $H$: Entropy in bits (minimum required: $128\text{ bits}$ for system credentials, $256\text{ bits}$ for cryptographic root keys).
*   $L$: Length of the generated password/secret string.
*   $R$: Size of the character pool (charset) used to generate the secret.

For a standard alphanumeric character set with special characters ($R = 94$):
$$H = L \log_2(94) \approx 6.55 \times L$$
Thus, a minimum length of $L \ge 20$ characters is required to achieve $>128\text{ bits}$ of entropy ($6.55 \times 20 = 131\text{ bits}$).

---

## 3. Storage and Integration Implementations

### 3.1 HashiCorp Vault Integration Spec
All microservices must authenticate to HashiCorp Vault using Kubernetes Service Accounts (JWT tokens) to fetch short-lived secret tokens.

```hcl
# Terraform configuration for Google Cloud KMS Keyring and Vault Auth Backend
resource "google_kms_key_ring" "vault" {
  name     = "vault-keyring"
  location = "us-central1"
  project  = "project-venus-prod"
}

resource "google_kms_crypto_key" "vault_unseal" {
  name            = "vault-unseal-key"
  key_ring        = google_kms_key_ring.vault.id
  rotation_period = "7776000s" # 90 days

  lifecycle {
    prevent_destroy = true
  }
}

resource "vault_auth_backend" "kubernetes" {
  type = "kubernetes"
  path = "kubernetes"
}
```

### 3.2 Secret Schema Definition
Every secret registered in the vault engine must conform to this schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SecretDefinition",
  "type": "object",
  "properties": {
    "secretPath": {
      "type": "string",
      "pattern": "^secret/data/[a-z0-9-]+(/[a-z0-9-]+)*$"
    },
    "rotationPeriodDays": {
      "type": "integer",
      "minimum": 1,
      "maximum": 90
    },
    "requiredKeys": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "ownerTeam": {
      "type": "string"
    }
  },
  "required": ["secretPath", "rotationPeriodDays", "requiredKeys", "ownerTeam"]
}
```

---

## 4. Operational Auditing Checklist
*   [ ] Verify that no secrets, passwords, or keys are committed to Git.
*   [ ] Confirm all services access credentials using IAM Role bindings or Kubernetes Service Accounts instead of permanent credential keys.
*   [ ] Validate that vault tokens are configured with a Time-To-Live (TTL) of $\le 1\text{ hour}$.
*   [ ] Ensure automatic secret rotation schedules are verified in Vault or GSM.
*   [ ] Audit encryption keys in KMS to confirm standard rotation periods are active.
