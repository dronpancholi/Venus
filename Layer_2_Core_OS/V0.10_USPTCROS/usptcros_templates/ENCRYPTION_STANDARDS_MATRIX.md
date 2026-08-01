# USPTCROS Encryption Standards Matrix
**Document Link:** [Encryption Standards Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ENCRYPTION_STANDARDS_MATRIX.md)

Approved cryptographic standards and algorithms for Project Venus.

## 1. Approved Cryptographic Algorithms
| Usage Domain | Cryptosystem | Key Size / Curve | Mode | Additional Security Constraints |
|---|---|---|---|---|
| **Data at Rest** | AES | 256 bits | GCM | Initialization Vector (IV) must be unique. |
| **Data in Transit** | TLS | 128/256 bits | GCM / CHACHA | TLS 1.3 mandatory. Diffie-Hellman ephemeral. |
| **Digital Signatures** | ECDSA / RSA | 256 bits / 4096 | N/A | P-256/P-384 curves, RSA-PSS padding. |
| **Key Agreement** | ECDH | 384 bits | Curve P-384 | Ephemeral keys generated per-session. |
| **Password Hashing** | Argon2id | N/A | N/A | $m=65536, t=3, p=4$ parameters. |

## 2. Banned Cryptographic Operations
* **Block Cipher Modes:** ECB, CBC (unless using strict MAC verification).
* **Hash Functions:** MD5, SHA-1 (except for historical signature verification).
* **Asymmetric Keys:** RSA keys under 2048 bits.
