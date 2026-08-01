# Marketplace Foundation (M183)

**File:** `genesis/marketplace/__init__.py`
**Tests:** 11

Defines the architecture for application distribution: manifests, dependencies, capabilities, permissions, versioning, signatures, updates.

### AppManifest
```python
from genesis.marketplace import AppManifest, MarketplacePackage, MarketplaceRegistry

manifest = AppManifest(
    name="studio",
    version="1.0.0",
    entry_point="genesis.studio.backend",
    dependencies=[{"name": "fabric", "version": ">=1.0"}],
    capabilities=["project:view", "ai:chat"],
    permissions=["read:engineering", "emit:events"],
)

# Validate
errors = manifest.validate()

# Package for distribution
pkg = MarketplacePackage(manifest=manifest)
registry = MarketplaceRegistry()
registry.register(pkg)

# Discovery
registry.search("studio")
registry.check_dependencies("studio")
update = registry.find_updates("studio", "0.9.0")
```
