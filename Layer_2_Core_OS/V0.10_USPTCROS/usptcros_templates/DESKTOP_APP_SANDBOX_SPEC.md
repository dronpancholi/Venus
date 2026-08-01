# USPTCROS Desktop App Sandbox Spec
**Document Link:** [Desktop App Sandbox Spec](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/DESKTOP_APP_SANDBOX_SPEC.md)

Sandboxing specifications for Project Venus desktop client builds.

## 1. Sandbox Capabilities Restrictions
Desktop clients must execute inside OS-level containers:
* **macOS:** App Sandboxing enabled with target capabilities restricted (`com.apple.security.network.client` only).
* **Windows (AppContainer):** Network access restricted to domain endpoints. Direct access to base physical volumes is denied.
* **Linux (Flatpak/Firejail):** Run using restricted filesystem namespaces (e.g. mounting user documents as read-only).

## 2. Local Database Storage Encryption
Application SQLite files must utilize SQLCipher with a PBKDF2 derived key:
```sql
-- Establish cryptographic session on local database
PRAGMA key = "ENV[LOCAL_SQLCIPHER_PASSPHRASE]";
PRAGMA cipher_page_size = 4096;
```
