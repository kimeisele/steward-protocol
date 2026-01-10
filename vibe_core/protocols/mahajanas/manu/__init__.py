"""
MANU - The 6th Mahajana (Law/Governance)
========================================
OpCodes: bind_ctx (Bit 11), check_dharma (Bit 12)
Opulence: Aishvarya (Sovereignty)

The Lawgiver. Father of mankind.
Manu-samhita - The Laws of Manu.

Manu OWNS all governance protocols:
- Context Binding
- Dharma Checking
- Permission Systems
- Rule Enforcement
- Varnashrama (Social Order)

Manu establishes ORDER. Without Manu = Anarchy.
"""

from typing import Protocol, runtime_checkable, Any, Optional


@runtime_checkable
class ManuProtocol(Protocol):
    """
    The Lawgiver Protocol.
    Any system that enforces rules/governance must implement this.
    """

    def bind_context(self, context: Any) -> bool:
        """
        Bind an operation to a context.
        Returns True if binding is valid.
        """
        ...

    def check_dharma(self, action: str, context: Any) -> bool:
        """
        Check if action is dharmic (lawful) in context.
        Returns True if allowed.
        """
        ...

    def get_ruling(self, action: str) -> Optional[str]:
        """
        Get the ruling/law for an action.
        Returns None if no ruling exists.
        """
        ...


class NullManu:
    """
    The Lawless State.
    All actions permitted (for testing without governance).
    """

    def bind_context(self, context: Any) -> bool:
        return True

    def check_dharma(self, action: str, context: Any) -> bool:
        return True  # All permitted

    def get_ruling(self, action: str) -> Optional[str]:
        return None


__all__ = ["ManuProtocol", "NullManu"]
