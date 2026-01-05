"""
NAGA Flood Registry - Automatic Service Replacement.

At boot, this module registers FLOODED versions of REBEL services
in the ServiceRegistry. When code requests a service, it gets
the NAGA-protected version automatically.

Architecture:
    Original: ServiceRegistry.get(CISyncServiceProtocol) → CISyncService
    Flooded:  ServiceRegistry.get(CISyncServiceProtocol) → FloodedCISyncService

"Das Wasser ersetzt den Stein, ohne dass der Stein es merkt."
"""

import logging
from typing import Dict, Type

logger = logging.getLogger("NAGA.FLOOD.REGISTRY")


# =============================================================================
# FLOOD MAPPING: Original → Flooded
# =============================================================================

FLOOD_MAP: Dict[str, Type] = {}


def register_flood(original_class: Type, flooded_class: Type) -> None:
    """Register a flooded replacement for an original class."""
    key = f"{original_class.__module__}.{original_class.__name__}"
    FLOOD_MAP[key] = flooded_class
    logger.debug(f"FLOOD REGISTRY: {key} → {flooded_class.__name__}")


def get_flooded(original_class: Type) -> Type:
    """Get the flooded version of a class, or original if not flooded."""
    key = f"{original_class.__module__}.{original_class.__name__}"
    return FLOOD_MAP.get(key, original_class)


def is_flooded(cls: Type) -> bool:
    """Check if a class is NAGA-flooded."""
    return getattr(cls, "_naga_flooded", False)


# =============================================================================
# AUTO-REGISTRATION AT IMPORT
# =============================================================================


def _register_all_floods() -> None:
    """Register all known flood classes."""
    try:
        from vibe_core.naga.floods.ouroboros import FloodedCISyncService
        from vibe_core.ouroboros.sync import CISyncService

        register_flood(CISyncService, FloodedCISyncService)
    except ImportError as e:
        logger.debug(f"FLOOD REGISTRY: Could not register ouroboros floods: {e}")

    # Future floods will be registered here:
    # from vibe_core.naga.floods.plugin_service import FloodedPluginService
    # register_flood(PluginService, FloodedPluginService)


# Auto-register on import
_register_all_floods()
