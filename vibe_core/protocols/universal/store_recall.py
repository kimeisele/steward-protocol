"""
STORE/RECALL PROTOCOL - The Memory of the Soul
==============================================

SHADOW REFACTOR (Phase 27):
- Mayavad Destroyed: 'Any' replaced with 'ProtectedMemory'.
- Mantra Binding: Explicit requirement.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x69b231c4"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, Optional, List, Dict, runtime_checkable
from vibe_core.protocols.substrate.byte import MantraByte
from .types import ProtectedMemory, SovereignContext


@runtime_checkable
class StoreRecallProtocol(Protocol):
    """
    Atomic Memory Operations.
    HARDENED: Only defined, protected memories can be stored.
    """

    def remember(self, key: str, memory: ProtectedMemory, mantra: MantraByte, context: SovereignContext) -> bool:
        """
        Stores data ONLY if it is a valid ProtectedMemory envelope.
        The 'mantra' must resonate with the 'memory.mantra_hash'.
        """
        ...

    def store(self, key: str, value: object, context: SovereignContext) -> bool:
        """Legacy store (Any-based)."""
        ...

    def recall(self, key: str, mantra: MantraByte, context: SovereignContext) -> Optional[ProtectedMemory]:
        """
        Retrieves data ONLY if the caller's mantra resonates with the stored shield.
        Returns the Envelope, not raw Any.
        """
        ...

    def forget(self, key: str, context: SovereignContext) -> bool:
        """Erase a memory from the field."""
        ...

    def list_keys(self, pattern: str = "*", context: SovereignContext = None) -> List[str]:
        """List keys in the field matching pattern."""
        ...

    def get_memory_stats(self, context: SovereignContext = None) -> Dict[str, object]:
        """Return memory usage and performance metrics."""
        ...
