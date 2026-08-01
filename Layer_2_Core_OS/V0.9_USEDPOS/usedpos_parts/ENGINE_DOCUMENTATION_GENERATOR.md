# Engine: Documentation Generator

## 1. Context & Strategy

### 1.1 Purpose
The Documentation Generator Engine scans project files, source comments, schema definitions, and markdown sources to generate institutional-grade developers' portals, dynamic API references, database dictionaries, and architectural diagrams.

### 1.2 Philosophy
Documentation must never drift from reality. The generator runs as a CI hook, validating code comments, generating tables, and checking links during normal branch validation cycles.

---

## 2. Ingest Parameters & Taxonomy

### 2.1 Inputs & Outputs
*   **Inputs**: Source directories containing comments (Go doc, JSDoc), Markdown source folders, OpenAPI definitions, database schemas.
*   **Outputs**: Static HTML pages (e.g., Docusaurus/Hugo target output), structured JSON reference structures, C4 model diagrams.

### 2.2 Pipeline Flow
```
[Scan codebase files] ──► [Parse code comment annotations] ──► [Verify relative markdown links] ──► [Compile HTML portal]
```

---

## 3. Algorithmic Checks & Computations

### 3.1 Documentation Coverage Metric
The generator computes a Documentation Coverage Index ($CI_{doc}$) to flag undocumented endpoints:

$$CI_{doc} = \frac{N_{documented\_endpoints}}{N_{discovered\_endpoints}} \times 100$$

*   *Rule*: The engine throws pipeline warnings if $CI_{doc} < 100\%$ for any deployable API package.

### 3.2 Dynamic Link Auditor Algorithm
The generator verifies internal and external URIs using a directed graph crawler:
1.  **Vertex Discovery**: Extract all link elements ($[text](URI)$) from markdown.
2.  **Relative Link Verification**: Check local filesystem paths; verify target file exists at that offset.
3.  **Anchor Check**: Validate that inline section anchors (e.g. `#section-name`) match target HTML identifiers.

---

## 4. Documentation Manifest Schema
Projects must contain a configuration manifest matching this JSON structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DocumentationManifest",
  "type": "object",
  "properties": {
    "projectName": { "type": "string" },
    "sourcePaths": {
      "type": "array",
      "items": { "type": "string" }
    },
    "validateUrls": { "type": "boolean" },
    "outputDirectory": { "type": "string" }
  },
  "required": ["projectName", "sourcePaths", "validateUrls", "outputDirectory"]
}
```

---

## 5. Reusable Checklist & Exit Criteria
*   [ ] Checked that code comments are extracted correctly from all active backend languages.
*   [ ] Verified relative filesystem links (`file:///...`) resolve to valid directories or files.
*   [ ] Confirmed Mermaid syntax parsing validates cleanly.
*   [ ] Checked that all generated database tables list correct schema description fields.
*   *Exit Criteria*: Generator completes compiling static outputs with zero dead link errors and $CI_{doc} = 100\%$.
