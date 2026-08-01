# USPTCROS Output Encoding Standard
**Document Link:** [Output Encoding Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OUTPUT_ENCODING_STANDARD.md)  
**References:** [Input Validation & Sanitization](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/INPUT_VALIDATION_SANITIZATION.md)

## 1. Output Encoding Rules
Output encoding prevents Cross-Site Scripting (XSS) by rendering raw payloads as non-executable variables in target contexts.

## 2. Context-Specific Encoding Requirements
* **HTML Body Context:** Encode `<` to `&lt;`, `>` to `&gt;`, `&` to `&amp;`, `"` to `&quot;`, `'` to `&#x27;`.
* **HTML Attribute Context:** Use alphanumeric encoding (`&#xHH;` format).
* **JavaScript Context:** Use Unicode escapes (`\uXXXX` format) for all non-alphanumeric characters.
* **URL Parameters:** Percent-encode dynamic parameters (RFC 3986).

## 3. Reference Implementation (Python Context Encoding)
```python
import html

def safe_render_html(user_payload: str) -> str:
    # Perform strict HTML entity escaping
    return html.escape(user_payload, quote=True)
```
