# USPTCROS Capability Engine: SBOM Generator
## Version: 0.10 | Classification: Institutional Security Standard | Status: Mandated Gateway

---

## 1. Operational Purpose & Scope
Compiles a complete Software Bill of Materials (SBOM) listing all application files, dependencies, build tools, and container details, cryptographically signing the manifest.

### 1.1 Input Interfaces & Data Sources
- **Input Source**: Application codebase file catalog.
- **Input Source**: Dependency Auditor scanner output files.
- **Input Source**: Container layers and builder tool metadata.

### 1.2 Output Interfaces & Artifacts
- **Output Artifact**: SPDX or CycloneDX standard JSON and XML SBOM reports.
- **Output Artifact**: Cryptographic signature file verifying SBOM authenticity.
- **Output Artifact**: Signed build provenance metadata catalog.

### 1.3 Integration & Automation Triggers
- Executed in the packaging phase of the build pipeline.
- Attaches signed SBOMs directly to output container image metadata.
- Publishes signed SBOM to long-term artifact security repositories.

---

## 2. Mathematical Verification Model
### 2.1 Metric/Score Formula
$$S_{Integrity} = \frac{Signed\_Components}{Total\_Components} \times 100$$

### 2.2 Variable Definitions
- $Signed\_Components$: Count of components with valid cryptographic origin signatures.
- $Total\_Components$: Total count of dependencies and tools registered in the SBOM.

### 2.3 Calculation Steps & Evaluation Thresholds
1. Map all direct and indirect application dependencies.
2. Extract origin signatures and hashing metadata for every package.
3. Compile CycloneDX JSON structure representing the complete dependency trees.
4. Sign the completed CycloneDX document using organization build key.

---

## 3. Configuration & Output JSON Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SbomConfig",
  "type": "object",
  "properties": {
    "format": {
      "type": "string",
      "enum": [
        "SPDX",
        "CycloneDX"
      ]
    },
    "signingKeyUri": {
      "type": "string"
    },
    "outputLocation": {
      "type": "string"
    }
  },
  "required": [
    "format",
    "signingKeyUri",
    "outputLocation"
  ]
}
```

---

## 4. Operational Verification Checklist
- [ ] **Pre-Execution Checks**:
  - [ ] Verify accessibility of the build system's code signing private key.
  - [ ] Confirm dependency audit outputs are available and verified.
- [ ] **Execution & Scan Verification**:
  - [ ] Generate CycloneDX schema document representing the package topology.
  - [ ] Perform SHA-256 hash validation of all downloaded modules and libraries.
- [ ] **Post-Execution & Mitigation Gates**:
  - [ ] Sign the SBOM document using cosign toolset.
  - [ ] Upload signed SBOM to the container registry alongside the image tag.
- [ ] **Exception Handling & Emergency Rollback**:
  - [ ] Remove invalid, unsigned SBOM files from temporary staging areas.
  - [ ] Fail the pipeline run to prevent release of undocumented software.

---

## 5. Navigation & Reference Matrix
- **Related Engines**:
  - [ENGINE_DEPENDENCY_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_DEPENDENCY_AUDITOR.md)
  - [ENGINE_SUPPLY_CHAIN_AUDITOR.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_SUPPLY_CHAIN_AUDITOR.md)
  - [ENGINE_SLSA_COMPLIANCE_ENGINE.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_parts/ENGINE_SLSA_COMPLIANCE_ENGINE.md)
- **Output Templates**:
  - [SECURE_CODING_STANDARD.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURE_CODING_STANDARD.md)
