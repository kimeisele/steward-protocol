"""
VibeKernel Interface Stub

This is a stub definition of the VibeKernel interface that steward-protocol
cartridges depend on. When cartridges run in vibe-agency, they will use the
actual implementation from vibe_core.kernel.

This stub allows cartridges to be type-checked and developed standalone.

GAP-018 FIX: All kernel ABCs now re-exported from canonical source (protocols.ledger)
"""

# Re-export from canonical source (protocols module)
# This eliminates duplication while maintaining backwards compatibility
from .protocols.ledger import (
    KernelStatus,
    VibeKernel,
    VibeLedger,
    VibeScheduler,
)
from .protocols.registry import ManifestRegistry

# Re-export for backwards compatibility
__all__ = [
    "KernelStatus",
    "VibeScheduler",
    "VibeLedger",
    "VibeKernel",
    "ManifestRegistry",
]
