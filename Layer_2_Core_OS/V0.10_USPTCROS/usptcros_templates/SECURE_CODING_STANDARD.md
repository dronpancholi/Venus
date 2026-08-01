# USPTCROS Secure Coding Standard
**Document Link:** [Secure Coding Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURE_CODING_STANDARD.md)

Guidelines and rules for writing secure, resilient software in Project Venus.

## 1. Memory Safety and Code Vulnerabilities
* **Avoid Buffer Overflows:** Use memory-safe languages or bound-checked arrays.
* **Strict Buffer Handling (C/C++):** Never use unsafe functions (`strcpy`, `sprintf`, `gets`). Use `strncpy`, `snprintf`, and `fgets` instead.
* **Secure Pointer Validation:** Always validate pointers against `NULL` before operations.

## 2. Input and Output Constraints
* **Sanitize Inputs:** Validate all incoming payloads against strict regex patterns. See [Input Validation & Sanitization](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/INPUT_VALIDATION_SANITIZATION.md).
* **Encode Outputs:** Prevent Cross-Site Scripting (XSS) by encoding outputs. See [Output Encoding Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OUTPUT_ENCODING_STANDARD.md).

## 3. Cryptography & Key Management
* Never hardcode secrets. Use environment-injected secret bindings.
* Use cryptographically secure pseudorandom number generators (CSPRNG). See [Secure Randomness Audit Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURE_RANDOMNESS_AUDIT_STANDARD.md).

## 4. Secure Coding Snippet (Python Validation Pattern)
```python
import re

def validate_input(user_input: str) -> bool:
    # Match alphanumeric characters only, length 1-32
    pattern = re.compile(r"^[a-zA-Z0-9]{1,32}$")
    if not pattern.match(user_input):
        raise ValueError("Invalid input format detected.")
    return True
```

## 5. Build/Compilation Hardening Flags
For C/C++ compilation, the following flags are mandatory:
```bash
gcc -fstack-protector-all -D_FORTIFY_SOURCE=2 -O2 -Wl,-z,relro,-z,now -fPIE -pie main.c -o main
```
