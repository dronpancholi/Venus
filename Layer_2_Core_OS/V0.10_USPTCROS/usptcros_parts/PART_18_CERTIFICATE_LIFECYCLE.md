# Project Venus USPTCROS — Part 18: Certificate Lifecycle Automation

## 1. Executive Summary
Manual certificate management is a primary source of operational outages. This module outlines the standards for automated certificate issuance, monitoring, renewal, and revocation using the ACME protocol.

## 2. Certificate Revocation and Verification Protocols
To maintain trust, Venus implements two validation mechanisms:
1. **Certificate Revocation List (CRL)**: Signed lists of serial numbers identifying revoked certificates.
2. **Online Certificate Status Protocol (OCSP)**: Real-time query to an OCSP responder checking certificate status.

Venus requires OCSP Stapling on all public servers to prevent latency overhead and user IP leakage.

---

## 3. Automated ACME Client Cert Request (Implementation Example)
The following Python script automates client certificate requests via the ACME API (using the `acme` library helper wrapper).

```python
import logging
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_key_and_csr(common_name: str, san_uri: str) -> tuple:
    # 1. Generate Private Key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    
    # 2. Build Certificate Signing Request (CSR)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, u"Project Venus"),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.UniformResourceIdentifier(san_uri),
        ]),
        critical=False
    ).sign(private_key, hashes.SHA384())
    
    # 3. Serialize outputs
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    
    logging.info(f"Successfully generated CSR for {common_name}")
    return key_pem, csr_pem
```

---

## 4. Certificate Lifecycle Checklist
- [ ] Enforce automated renewal checks once a certificate reaches 70% of its lifespan.
- [ ] Configure monitoring tools to alert on certificates expiring within 10 days.
- [ ] Verify that the server rejects any incoming connection presenting a certificate on the local CRL.
- [ ] Disable support for TLS session tickets to ensure Perfect Forward Secrecy (PFS).

---

## 5. Absolute System Links
- **Previous Chapter**: [Part 17: PKI](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_17_PKI.md)
- **Next Chapter**: [Part 19: Key Rotation](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/PART_19_KEY_ROTATION.md)
