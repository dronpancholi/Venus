# USPTCROS RBAC Permissions Matrix
**Document Link:** [RBAC Permissions Matrix](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/RBAC_PERMISSIONS_MATRIX.md)  
**References:** [Role Definition Catalog](file:///Users/dronpancholi/Developer/01_Strategic/Venus/usptcros_templates/ROLE_DEFINITION_CATALOG.md)

## 1. System Permission Mapping Matrix
| Permission Name | SuperAdmin | SecurityAdmin | Operator | ReadOnly |
|---|---|---|---|---|
| **keys:create** | Yes | Yes | No | No |
| **keys:rotate** | Yes | Yes | No | No |
| **keys:destroy** | Yes | No | No | No |
| **secrets:read** | Yes | No | Yes | No |
| **audit:read** | Yes | Yes | Yes | Yes |
| **network:update** | Yes | Yes | No | No |
| **system:reboot** | Yes | No | No | No |

## 2. Verification Check Policy
Ensure the RBAC configurations conform to the permissions mapping model:
```bash
# Verify user role mapping in deployment namespace
kubectl get rolebindings -n venus-system -o json
```
