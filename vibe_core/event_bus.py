"""
DEPRECATED: Use mahajana import.

LEVEL -1 BRIDGE (LOTUS/ONTOS):
    This module is a DYNAMIC PROXY.
    Position 2 (NARADA - Communication/Events) determines the owner at runtime.

    Currently: Position 2 = Narada (ALLOC_MEM, Event Bus)

    If you change MAHAMANTRA_POSITIONS, this bridge adapts automatically.
    ZERO manual imports. ZERO hardcoded names.

ONE IMPORT:
    from vibe_core.protocols.mahajanas.<whoever-sits-at-2>.types.event_bus import EventBus

Or via mahamantra:
    from vibe_core.mahamantra import mahamantra
    EventBus = mahamantra.genesis.<whoever>.EventBus

Or via this bridge (for backward compatibility):
    from vibe_core.event_bus import EventBus

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
# Position 2 determines ownership dynamically
__mahajana__ = "dynamic"  # Resolved at runtime from SSOT
__position__ = 2
__genesis__ = "0x000000aa"  # GenesisByte (Position 2)

from typing import Any

from vibe_core.mahamantra.substrate.registry import GuardianRegistry

# =============================================================================
# DYNAMIC DISPATCH - The Lotus Level
# =============================================================================


def __getattr__(name: str) -> Any:
    """
    Dynamic attribute lookup from registry.

    Position 2 (NARADA, ALLOC_MEM) determines the owner.
    The SSOT (MAHAMANTRA_POSITIONS) determines who sits there.

    Currently: Position 2 = Narada

    Args:
        name: Attribute name to load

    Returns:
        The requested type/class from the position's types module

    Raises:
        AttributeError: If attribute not found
    """
    # Load from position 2's types module
    attr = GuardianRegistry.load_type(position=2, type_name=name)

    if attr is not None:
        return attr

    # Fallback: Try loading entire types module and get any attribute
    types_module = GuardianRegistry.load_module(index=2, component="types")
    if types_module is not None:
        try:
            return getattr(types_module, name)
        except AttributeError:
            pass

    # Not found
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# =============================================================================
# __all__ for explicit exports (optional, for IDE support)
# =============================================================================

# Note: These are loaded dynamically via __getattr__ from GuardianRegistry
# Explicitly listing them here helps IDEs with auto-completion
# ruff: noqa: F822 (names loaded dynamically via __getattr__)
__all__ = [
    "EventBus",
    "EventType",
    "VibeEvent",
    "Event",
    "EventBusProtocol",
]
