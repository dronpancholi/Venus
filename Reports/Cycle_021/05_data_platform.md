# Engineering Data Platform (M178)

**File:** `genesis/data/__init__.py`
**Tests:** 9

Standardizes every internal model with descriptors, versioning, validation, and migration.

### API
```python
from genesis.data import ModelRegistry, ModelDescriptor, ModelCategory

registry = ModelRegistry()
registry.register(ModelDescriptor(
    name="architecture.decision",
    category=ModelCategory.KNOWLEDGE,
    version="2.0.0",
    required_fields=["id", "title", "status"],
    validation_rules={"confidence": "positive"},
    migrate_from={"1.0.0": "migrate_v1_to_v2"},
))

# Validate any payload
errors = registry.validate("architecture.decision", data)

# Versioned payloads
vp = VersionedPayload(model="architecture.decision", version="2.0.0", data={})
upgraded = registry.upgrade(vp)
```
