"""
MANU - The 6th Mahajana (Law/Governance)
========================================

POSITION: 7 (DHARMA Quarter, PULSE_SYNC OpCode)

The Lawgiver. Father of mankind.
Manu-samhita - The Laws of Manu.

DERIVED FROM MAHAMANTRA:
    Position 7 -> guardian=MANU, opcode=PULSE_SYNC, quarter=DHARMA
    All properties derived from truth table. No manual wiring.

Manu establishes ORDER. Without Manu = Anarchy.
"""

from typing import ClassVar, Dict, List, Optional, Protocol, TypedDict, runtime_checkable
from dataclasses import dataclass

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode


# =============================================================================
# MANU PROTOCOL BASE - Derives from MantraPosition 7
# =============================================================================

class ManuProtocolBase(WorkerProtocol):
    """
    Manu protocol ownership - DERIVED from Mahamantra position 7.

    NO MANUAL WIRING:
        _position_index = 7 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.MANU
        opcode()    -> MantraOpCode.PULSE_SYNC
        quarter()   -> Quarter.DHARMA
        is_head()   -> False (Worker position)
        parampara_vector() -> 296 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 7  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[7]


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


class SyncResult(TypedDict):
    """Result of sync operation. WATERTIGHT - no Any!"""
    success: bool
    target: str
    synced: bool
    message: str


class NullManu(ManuProtocolBase):
    """
    The Lawless State.
    All actions permitted (for testing without governance).

    Inherits from ManuProtocolBase -> position 7 -> MANU.
    """

    def bind_context(self, context: DharmaContext) -> bool:
        return True

    def check_dharma(self, action: str, context: DharmaContext) -> ManuVerdict:
        return ManuVerdict(is_dharmic=True, reason="NullManu permits all")

    def get_ruling(self, action: str) -> Optional[str]:
        return None

    def sync(self, target: str = "all") -> SyncResult:
        """CLI: Synchronize dharmic state. WATERTIGHT."""
        return SyncResult(
            success=True,
            target=target,
            synced=True,
            message="NullManu sync complete",
        )


# Import Dharma (The Architectural Law) - Manu's PRIMARY protocol
from .dharma import (
    ProtocolLayer,
    PROTOCOL_MAP,
    get_layer,
    check_compliance,
    is_dharmic,
    LOTUS_POSITION as DHARMA_POSITION,
)

# Import Varnashrama (The Social Law) - Manu's SOCIAL protocol
from .varnashrama import (
    Varna,
    Ashrama,
    Certification,
    CERT_TO_VARNA,
    SocialPosition,
    determine_varna,
    determine_ashrama,
    create_position,
)

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "ManuProtocolBase",
    # Protocol
    "ManuProtocol",
    "NullManu",
    # Types (WATERTIGHT)
    "DharmaContext",
    "ManuVerdict",
    "SyncResult",
    # Dharma (Architectural Law)
    "ProtocolLayer",
    "PROTOCOL_MAP",
    "get_layer",
    "check_compliance",
    "is_dharmic",
    # Varnashrama (Social Law)
    "Varna",
    "Ashrama",
    "Certification",
    "CERT_TO_VARNA",
    "SocialPosition",
    "determine_varna",
    "determine_ashrama",
    "create_position",
]
