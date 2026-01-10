"""
MANU - The 6th Mahajana (Law/Governance)
========================================
OpCodes: bind_ctx (Bit 11), check_dharma (Bit 12)
Opulence: Aishvarya (Sovereignty)

The Lawgiver. Father of mankind.
Manu-samhita - The Laws of Manu.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Manu is the PERSON responsible for these protocols.
They are not "universal" - they are PERSONAL (owned by Manu).

OWNED PROTOCOLS:
- dharma.py - Dharma verification
- enforce.py - Law enforcement
- governance/ - Governance systems

Manu establishes ORDER. Without Manu = Anarchy.
"""

from typing import Protocol, runtime_checkable, Optional, List, Final
from dataclasses import dataclass

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP - Manu's Domain
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.MANU

OWNED_PROTOCOLS: Final[List[str]] = [
    "manu",
    "dharma",
    "enforce",
    "governance",
    "law",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.PULSE_SYNC,  # Vyuha: Q2 Worker 3 (BIND_CTX -> Shambhu, CHECK_DHARMA -> Janaka)
]


# =============================================================================
# DHARMA CONTEXT - What Manu validates
# =============================================================================

@dataclass(frozen=True)
class DharmaContext:
    """The context for dharma checking - replaces Any."""
    sovereign_id: Optional[str] = None
    action: str = ""
    resource: str = ""
    intent: str = ""


@dataclass(frozen=True)
class ManuVerdict:
    """Manu's verdict on an action."""
    is_dharmic: bool
    reason: str
    ruling: Optional[str] = None


# =============================================================================
# PROTOCOL DEFINITION
# =============================================================================

@runtime_checkable
class ManuProtocol(Protocol):
    """
    The Lawgiver Protocol.
    Any system that enforces rules/governance must implement this.

    ANTI-MAYAVAD: This is not an abstract "universal" protocol.
    MANU (the Person) owns this. He is the Lawgiver.
    """

    def bind_context(self, context: DharmaContext) -> bool:
        """
        Bind an operation to a context.
        Returns True if binding is valid.
        """
        ...

    def check_dharma(self, action: str, context: DharmaContext) -> ManuVerdict:
        """
        Check if action is dharmic (lawful) in context.
        Returns ManuVerdict with explanation.
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

    def bind_context(self, context: DharmaContext) -> bool:
        return True

    def check_dharma(self, action: str, context: DharmaContext) -> ManuVerdict:
        return ManuVerdict(is_dharmic=True, reason="NullManu permits all")

    def get_ruling(self, action: str) -> Optional[str]:
        return None


__all__ = [
    # Ownership
    "OWNER",
    "OWNED_PROTOCOLS",
    "OWNED_OPCODES",
    # Protocol
    "ManuProtocol",
    "NullManu",
    # Types
    "DharmaContext",
    "ManuVerdict",
]
