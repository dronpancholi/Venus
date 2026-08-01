# USPTCROS Client-Side Cryptographic Hashing Standard
**Document Link:** [Client-Side Cryptographic Hashing](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/CLIENT_SIDE_CRYPTOGRAPHIC_HASHING.md)  
**References:** [Secure Coding Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURE_CODING_STANDARD.md)

## 1. Local Key Derivation Function (KDF)
To protect passwords in transit, the client application derives hashes using Argon2id before submission.

## 2. Cryptographic Salt & Iterations
* **Salt Size:** 16 Bytes (randomly generated and returned from the registration server).
* **Iterations:** 3 passes.
* **Memory Cost:** 64MB (client-side configuration constraint).

## 3. Web Cryptography API Snippet (PBKDF2 Fallback Pattern)
```javascript
async function deriveLocalHash(password, salt) {
    const enc = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        "raw", enc.encode(password), { name: "PBKDF2" }, false, ["deriveBits"]
    );
    const derivedBits = await window.crypto.subtle.deriveBits(
        { name: "PBKDF2", salt: enc.encode(salt), iterations: 100000, hash: "SHA-256" },
        keyMaterial, 256
    );
    return Array.from(new Uint8Array(derivedBits)).map(b => b.toString(16).padStart(2, '0')).join('');
}
```
