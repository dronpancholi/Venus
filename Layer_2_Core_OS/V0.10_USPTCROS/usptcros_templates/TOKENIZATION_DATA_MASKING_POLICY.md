# USPTCROS Tokenization & Data Masking Policy
**Document Link:** [Tokenization & Data Masking Policy](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/TOKENIZATION_DATA_MASKING_POLICY.md)  
**References:** [Data Classification Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DATA_CLASSIFICATION_MATRIX.md)

## 1. Data Tokenization Patterns
Tokenization replaces sensitive records with randomly generated non-sensitive markers (tokens) using Format-Preserving Encryption (FPE).

## 2. Masking Architectures
* **Static Masking:** Applied to database tables when copying records from production to staging networks.
* **Dynamic Masking:** Evaluated at runtime based on the caller's role mapping. See [ABAC Policy Rules Schema](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ABAC_POLICY_RULES_SCHEMA.md).

## 3. Formatting Standards
| Field Name | Input Format | Masking Pattern | Output Format |
|---|---|---|---|
| Tax Identifier | `999-99-9999` | Retain last 4 characters | `XXX-XX-9999` |
| Primary Account Num | `16 Digits` | Retain first 6 and last 4 | `4111-11XX-XXXX-1111` |
| Email Addresses | `user@corp.com` | Obfuscate user component | `u***r@corp.com` |
