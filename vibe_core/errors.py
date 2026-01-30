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
__genesis__ = "0xbdf3586d"  # GenesisByte (Position 4)

from typing import Any

from vibe_core.mahamantra import (
    ErrorCode,
    StructuredError,
    ErrorCategory,
    kernel_fault,
)

__all__ = ["ErrorCode", "StructuredError", "ErrorCategory", "kernel_fault"]

