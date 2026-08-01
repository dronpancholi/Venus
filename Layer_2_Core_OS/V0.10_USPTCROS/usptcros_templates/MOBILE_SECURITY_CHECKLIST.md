# USPTCROS Mobile Security Checklist
**Document Link:** [Mobile Security Checklist](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/MOBILE_SECURITY_CHECKLIST.md)

Audit controls for native mobile applications interacting with Project Venus APIs.

## 1. Certificate Pinning Enforcements
- [ ] iOS: Network connections use `NSPinningConfiguration` specifying root and intermediate public key hashes.
- [ ] Android: Network Security Configuration XML restricts trust anchors to pinned certificate keys:
```xml
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.venus.local</domain>
        <pin-set expiration="2027-06-26">
            <pin digest="SHA-256">98234hsd8f79s8dfywsudyf9s87df9s87d=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

## 2. Platform Security Configurations
- [ ] Biometric credentials must authenticate using iOS `Keychain` and Android `Keystore` backends.
- [ ] Anti-rooting / Anti-jailbreak checking is performed at application startup.
- [ ] Strict isolation of memory space (disable debugging flags in release versions).
