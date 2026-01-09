"""
STORE/RECALL PROTOCOL - The Memory of the Soul
==============================================

SHADOW REFACTOR:
Mayavad Destroyed: "Static Data" does not exist.
Only "Protected Data" (Prahlad) exists.
"""

from typing import Protocol, Optional, Any, runtime_checkable
from vibe_core.protocols.substrate.byte import MantraByte

@runtime_checkable
class StoreRecallProtocol(Protocol):
    """
    Atomic Memory Operations.
    NOW HARDENED: Unprotected data is instantly consumed by Time.
    """

    def remember(self, key: str, value: Any, mantra: MantraByte) -> bool:
        """
        Stores data ONLY if wrapped in the Holy Name.
        The 'mantra' acts as the Encryption/Protection Shield.
        """
        ...

    def recall(self, key: str, mantra: MantraByte) -> Optional[Any]:
        """
        Retrieves data ONLY if the caller resonates with the stored shield.
        No Mantra = No Access (Amnesia).
        """
        ...
