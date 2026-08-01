# USPTCROS Input Validation & Sanitization Standard
**Document Link:** [Input Validation & Sanitization](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/INPUT_VALIDATION_SANITIZATION.md)  
**References:** [Secure Coding Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SECURE_CODING_STANDARD.md)

## 1. Input Validation Architecture
All user inputs must be validated at the application boundary using a strict whitelisting methodology.

## 2. Standard Validation Expressions
* **Email:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
* **UUID:** `^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`
* **IP Address:** `^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$`

## 3. Server-side Validation Snippet (NodeJS express-validator)
```javascript
const { body, validationResult } = require('express-validator');

app.post('/v1/user', [
  body('email').isEmail().normalizeEmail(),
  body('age').isInt({ min: 18, max: 120 }),
  body('username').matches(/^[a-zA-Z0-9_]{3,20}$/)
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  // Proceed with safe request processing
});
```
