"""
DEPRECATED: Use mahajana import.

LEVEL -1 BRIDGE (LOTUS/ONTOS):
    This module is a DYNAMIC PROXY.
    Position 4 (DHARMA HEAD) determines the owner at runtime.

    Currently: Position 4 = Prithu (ASSERT_TRUTH)

    If you change MAHAMANTRA_POSITIONS, this bridge adapts automatically.
    ZERO manual imports. ZERO hardcoded names.

ONE IMPORT:
    from vibe_core.protocols.mahajanas.<whoever-sits-at-4>.types.errors import ErrorCode, StructuredError

Or via this bridge (for backward compatibility):
    from vibe_core.errors import ErrorCode, StructuredError

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
# Position 4 determines ownership dynamically
__mahajana__ = "dynamic"  # Resolved at runtime from SSOT
__position__ = 4
__genesis__ = "0x94644443"  # GenesisByte (Position 4)

from typing import Any

from vibe_core.mahamantra.substrate.registry import GuardianRegistry

# =============================================================================
# DYNAMIC DISPATCH - The Lotus Level
# =============================================================================


def __getattr__(name: str) -> Any:
    """
    Dynamic attribute lookup from registry.

    Position 4 (DHARMA HEAD, ASSERT_TRUTH) determines the owner.
    The SSOT (MAHAMANTRA_POSITIONS) determines who sits there.

    Currently: Position 4 = Prithu

    Args:
        name: Attribute name to load

    Returns:
        The requested type/class from the position's types module

    Raises:
        AttributeError: If attribute not found
    """
    # Load from position 4's types module
    attr = GuardianRegistry.load_type(position=4, type_name=name)

    if attr is not None:
        return attr

    # Fallback: Try loading entire types module and get any attribute
    types_module = GuardianRegistry.load_module(index=4, component="types")
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

__all__ = ["ErrorCode", "StructuredError", "ErrorCategory", "kernel_fault"]  # noqa: F822
