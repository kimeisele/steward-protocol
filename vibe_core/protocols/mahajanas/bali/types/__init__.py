"""
BALI Types - Position 10 (KARMA Quarter, ALLOC_RESOURCE)
=========================================================

BALI - The Generous Demon King.
Types for resource management and allocation.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0xefb0cf0e"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.bali.types.resource_manager import (
    ResourceManager,
)

__all__ = [
    "ResourceManager",
]
