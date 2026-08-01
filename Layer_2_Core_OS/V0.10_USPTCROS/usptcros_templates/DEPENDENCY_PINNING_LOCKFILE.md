# Dependency Pinning and Lockfile Integrity Specification
**Document ID:** VENUS-USPTCROS-089
**Version:** 1.0.0
**Status:** Approved
**Effective Date:** 2026-06-26

## 1. Overview & Objective
Specifies security controls for pinning package versions and locking transitive dependencies to prevent software supply chain injection attacks and build runtime drift.

## 2. Technical Specifications & Architecture
```
[ Package Config (requirements.in) ] -> Run pip-compile -> [ Lockfile (requirements.txt) ] with sha256 checksums
```

## 3. Code Fragment / Implementation Details
```python
#!/usr/bin/env python3
# Check for lockfile checksum drift
import sys
import hashlib

def verify_lockfile_checksums(lockfile_path, expected_checksum_map):
    errors = 0
    with open(lockfile_path, "r") as f:
        for line in f:
            if "sha256:" in line:
                parts = line.strip().split()
                # Simple parser example for requirement line: pkg==1.0 --hash=sha256:abcd...
                package_name = parts[0]
                hash_val = [p for p in parts if p.startswith("--hash=sha256:")][0].split(":")[1]
                if package_name in expected_checksum_map:
                    if expected_checksum_map[package_name] != hash_val:
                        print(f"ERROR: Checksum mismatch for {package_name}!")
                        errors += 1
    return errors == 0

if __name__ == "__main__":
    ref_map = {"cryptography": "b2f6ef3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852"}
    sys.exit(0 if verify_lockfile_checksums("requirements.txt", ref_map) else 1)
```

## 4. Verification Schema & Configurations
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "LockfileIntegrityManifest",
  "type": "object",
  "properties": {
    "lockfile_format": {
      "type": "string"
    },
    "packages": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "version": {
            "type": "string"
          },
          "sha256": {
            "type": "string",
            "pattern": "^[a-f0-9]{64}$"
          }
        },
        "required": [
          "version",
          "sha256"
        ]
      }
    }
  },
  "required": [
    "lockfile_format",
    "packages"
  ]
}
```

## 5. Mathematical Formulations & Quantitative Metrics
$$PinningRatio = \frac{PinnedDependencyCount}{TotalDependencyCount} \times 100\%$$

## 6. Institutional Verification Checklist
* [ ] Pin all dependency versions exactly within project package configuration files.
* [ ] Commit lockfiles containing verified package digest hashes into source control.
* [ ] Block builds if package integrity check failures are encountered.
* [ ] Run lockfile analysis on all pipeline build phases to verify consistency.

## 7. Cross-References
- [Dependency Risk Report](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DEPENDENCY_RISK_REPORT.md)
- [Oss Ingestion Policy Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OSS_INGESTION_POLICY_STANDARD.md)
- [Secure Pr Verification Plan](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURE_PR_VERIFICATION_PLAN.md)
