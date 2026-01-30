"""
DEPRECATED: Use mahajana import.

LEVEL -1 BRIDGE (LOTUS/ONTOS):
    This module is a DYNAMIC PROXY.
    Position 0 (GENESIS HEAD) determines the owner at runtime.

    Currently: Position 0 = Vyasa (SYS_WAKE)

    If you change MAHAMANTRA_POSITIONS, this bridge adapts automatically.
    ZERO manual imports. ZERO hardcoded names.

ONE IMPORT:
    from vibe_core.protocols.mahajanas.<whoever-sits-at-0>.types.process_manager import ProcessManager

Or via this bridge (for backward compatibility):
    from vibe_core.process_manager import ProcessManager

This file is a BRIDGE for backward compatibility.
Will be removed in future version.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
# Position 0 determines ownership dynamically
__mahajana__ = "dynamic"  # Resolved at runtime from SSOT
__position__ = 0
__genesis__ = "0x00000000"  # GenesisByte (Position 0)

from vibe_core.mahamantra import ProcessManager

__all__ = ["ProcessManager"]

