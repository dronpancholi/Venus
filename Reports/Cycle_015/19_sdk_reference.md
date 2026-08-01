# Cycle 015 — SDK Reference

> Note: The SDK is still aspirational. This reference documents the intended API surface for plugin/extension developers.

## Core SDK Package (`genesis/sdk/`)

Until the SDK package is extracted, the primary integration point is `FabricKernel.instance()`.

```python
from genesis.fabric.kernel import FabricKernel

kernel = FabricKernel.instance()
```

## Plugin SDK

```python
from genesis.sdk import GenesisPlugin
from genesis.sdk.types import PluginManifest, PluginHook

@GenesisPlugin(
    name="my-plugin",
    version="0.1.0",
    description="My Genesis plugin",
)
class MyPlugin:
    def on_boot(self, kernel):
        """Called during kernel boot."""
        pass

    def on_event(self, event):
        """Called for every event."""
        pass

    def on_shutdown(self):
        """Called during kernel shutdown."""
        pass
```

`genesis/sdk/` should contain:
- `__init__.py` — GenesisPlugin base class, create_plugin()
- `types.py` — PluginManifest, PluginHook, PluginConfig
- `api.py` — GenesisAPI client (HTTP + WS) for external plugins

## Intent SDK

For building custom intents (autonomous agents):

```python
from genesis.sdk import GenesisIntent
from genesis.sdk.types import IntentSpec

class MyIntent(GenesisIntent):
    spec = IntentSpec(
        name="my_intent",
        description="Does something useful",
        required_capabilities=["reasoning"],
    )

    async def execute(self, context):
        # context.kernel — FabricKernel instance
        # context.memory — UniversalMemorySystem
        # context.ai — AIRouter
        return {"result": "done"}
```

## SDK Generation

Generate `genesis/sdk/` from canonical implementations:
1. Extract public API surface of FabricKernel
2. Extract PluginManifest → GenesisPlugin decorator
3. Extract IntentSpec → GenesisIntent base class
4. Add GenesisAPI client for remote access
5. Publish as PyPI package `genesis-sdk`
