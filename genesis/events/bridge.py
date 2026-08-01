from __future__ import annotations

from typing import Any

from genesis.fabric.events import EngineeringEvent, EventRouter as FabricEventRouter
from genesis.events.bus import EventBus
from genesis.events.unified import UnifiedEventBus


def bridge_fabric_router(unified: UnifiedEventBus, router: FabricEventRouter):
    """Bridge the Fabric EventRouter into the UnifiedEventBus."""
    unified.bridge_bus(router)

    original_emit = router.emit

    def bridged_emit(event: EngineeringEvent) -> int:
        delivered = original_emit(event)
        unified.emit(event)
        return delivered

    router.emit = bridged_emit


def bridge_legacy_bus(unified: UnifiedEventBus, bus: EventBus):
    """Bridge the legacy EventBus into the UnifiedEventBus."""
    unified.bridge_bus(bus)

    original_emit = bus.emit

    def bridged_emit(event_type: str, data: dict[str, Any] | None = None):
        original_emit(event_type, data)
        event = EngineeringEvent(
            type=event_type,
            payload=data or {},
            origin="legacy_bus",
        )
        unified.emit(event)

    bus.emit = bridged_emit


def bridge_all():
    """Bridge all available event systems into the UnifiedEventBus."""
    unified = UnifiedEventBus.instance()

    from genesis.fabric.kernel import FabricKernel
    kernel = FabricKernel.instance()

    bridge_fabric_router(unified, kernel._event_router)

    try:
        from genesis.events.bus import EventBus as LegacyBus
        if hasattr(kernel, '_legacy_bus') and kernel._legacy_bus:
            bridge_legacy_bus(unified, kernel._legacy_bus)
    except Exception:
        pass

    return unified
