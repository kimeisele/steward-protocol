"""
DEPRECATED: Use mahajana import.

LEVEL -1 BRIDGE (LOTUS/ONTOS):
    This module is a DYNAMIC PROXY.
    Position 0 (GENESIS HEAD) determines the owner at runtime.

    Currently: Position 0 = Vyasa (SYS_WAKE)

    If you change MAHAMANTRA_POSITIONS, this bridge adapts automatically.
    ZERO manual imports. ZERO hardcoded names.

ONE IMPORT:
    from vibe_core.protocols.mahajanas.<whoever-sits-at-0>.types.boot_mode import BootMode

Or via mahamantra:
    from vibe_core.mahamantra import mahamantra
    BootMode = mahamantra.genesis.<whoever>.BootMode

Or via this bridge (for backward compatibility):
    from vibe_core.boot_mode import BootMode

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
# Position 0 determines ownership dynamically
__mahajana__ = "dynamic"  # Resolved at runtime from SSOT
__position__ = 0
__genesis__ = "0x00000000"  # GenesisByte (Position 0)

from typing import Any

from vibe_core.mahamantra.substrate.registry import MahajanaRegistry

# =============================================================================
# DYNAMIC DISPATCH - The Lotus Level
# =============================================================================


def __getattr__(name: str) -> Any:
    """
    Dynamic attribute lookup from registry.

    Position 0 (GENESIS HEAD, SYS_WAKE) determines the owner.
    The SSOT (MAHAMANTRA_POSITIONS) determines who sits there.

    Currently: Position 0 = Vyasa

    Args:
        name: Attribute name to load

    Returns:
        The requested type/class from the position's types module

    Raises:
        AttributeError: If attribute not found
    """
    # Load from position 0's types module
    attr = MahajanaRegistry.load_type(position=0, type_name=name)

    if attr is not None:
        return attr

    # Fallback: Try loading entire types module and get any attribute
    types_module = MahajanaRegistry.load_module(index=0, component="types")
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

__all__ = ["BootMode"]
