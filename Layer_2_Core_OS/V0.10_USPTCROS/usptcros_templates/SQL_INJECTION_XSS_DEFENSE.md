# USPTCROS SQL Injection & XSS Defense Standard
**Document Link:** [SQL Injection & XSS Defense](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/SQL_INJECTION_XSS_DEFENSE.md)  
**References:** [Input Validation & Sanitization](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/INPUT_VALIDATION_SANITIZATION.md), [Output Encoding Standard](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/OUTPUT_ENCODING_STANDARD.md)

## 1. SQL Injection Prevention
* **Parameterized Queries:** Use prepared statements for all database queries. Raw string concatenations are blocked.
* **ORM Settings:** Enable strict parameterization within SQL ORM configurations (e.g. Hibernate, SQLAlchemy).

### SQL Injection Prevention Example (Python SQLite Parameterization)
```python
import sqlite3

def retrieve_user_record(cursor, user_id: int):
    # Parameterized SQL query syntax prevents input escape bypasses
    query = "SELECT username, email FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()
```

## 2. XSS Mitigation Directives
1. Implement strict Content-Security-Policies (CSP).
2. Utilize framework-level auto-escaping (React JSX, Angular templates).
3. Validate user payloads using DOMPurify before parsing innerHTML:
```javascript
const cleanHTML = DOMPurify.sanitize(dirtyInputString);
```
