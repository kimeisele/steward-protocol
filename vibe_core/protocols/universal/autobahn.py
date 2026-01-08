"""
AUTOBAHN PROTOCOL - The Transgalactic Infrastructure (HARDENED).

ADR-001: VAJRA-AUTOBAHN
"High Speed. Zero Friction. Anti-Mayavad."

ENGINEERING GOAL: "Mantra byte = Reality".
Only signed, typed reality may travel.

LANES:
- SATTVA (Fast Lane): High Priority, Fully Signed, Verified (Jagannath Chariot).
- RAJAS (Middle Lane): Action-oriented, standard traffic.
- TAMAS (Slow Lane): Logging, cleanup, shadow work.

ANTI-MAYAVAD PRINCIPLES:
- NO `Any` types in VajraPacket (use Watertight bound).
- TÜV service is INJECTED, not imported (dependency inversion).
- Every packet has a MantraSeal (cryptographic proof of intent).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, Generic, Protocol, TypeVar, runtime_checkable

# TYPE_CHECKING import - Not Mayavad, only for type hints
if TYPE_CHECKING:
    from vibe_core.protocols.naga.tuv import TÜVProtocol

    from .watertight import Watertight

# =============================================================================
# LANE ENUMERATION
# =============================================================================


class Lane(str, Enum):
    """The 3 Lanes of the Vedic Autobahn."""

    SATTVA = "SATTVA"  # Goodness, Clarity, Speed (Priority 1)
    RAJAS = "RAJAS"  # Passion, Action, Movement (Priority 2)
    TAMAS = "TAMAS"  # Ignorance, Inertia, Storage (Priority 3)


# =============================================================================
# MANTRA SEAL - The 37th Siegel (DNA Injection)
# =============================================================================


@dataclass
class MantraSeal:
    """
    Das 37. Siegel. Die DNA-Injektion.

    Every packet must carry this cryptographic proof of intent.
    Without the seal, the packet is void (Mayavad).
    """

    signer_id: str  # Who signed? (Sovereign ID)
    signature: str  # Cryptographic proof (Ed25519/ECDSA)
    timestamp: datetime  # The beat (Kala) - when was it signed
    intent_hash: str  # SHA256 of payload content (Satyam)

    def is_valid(self) -> bool:
        """Basic seal validity check (not cryptographic verification)."""
        return bool(self.signer_id and self.signature and self.intent_hash)


# =============================================================================
# VAJRA PACKET - The Indestructible Vehicle
# =============================================================================

# Genetic Material: Payload must be Watertight (no Any allowed)
T_Payload = TypeVar("T_Payload", bound="Watertight")


@dataclass
class VajraPacket(Generic[T_Payload]):
    """
    Das unzerstörbare Fahrzeug (Juggernaut).

    It transports not 'data', but 'proven reality' (Capabilities/Truth).
    The verify() method is Living Software - the packet tests itself.
    """

    id: str  # Unique packet ID
    lane: Lane  # The Lane assignment
    payload: T_Payload  # MUST implement Watertight!
    seal: MantraSeal  # MUST be signed!

    def verify(self) -> bool:
        """
        Living Software: Self-test.

        1. Checks MantraSeal validity.
        2. Checks payload Watertight seal.

        Returns:
            True if packet is valid, False if Mayavad detected.
        """
        # 1. Check MantraSeal
        if not self.seal.is_valid():
            return False

        # 2. Check Watertight seal on payload
        if hasattr(self.payload, "verify_seal"):
            if not self.payload.verify_seal():
                return False

        return True


# =============================================================================
# TRANSPORT RESULT
# =============================================================================


@dataclass
class TransportResult:
    """Result of a transport operation."""

    success: bool
    packet_id: str
    lane: Lane
    message: str = ""
    quarantine_reason: str = ""


# =============================================================================
# IAUTOBAHN PROTOCOL (Interface)
# =============================================================================


@runtime_checkable
class IAutobahn(Protocol):
    """
    The Interface of the Hardened Infrastructure.

    Implementations MUST inject TÜV service (not import directly).
    """

    def open_lane(self, lane: Lane) -> bool:
        """
        Opens a specific lane for traffic.

        Returns:
            True if lane opened successfully.
        """
        ...

    def transport(self, packet: VajraPacket[T_Payload]) -> TransportResult:
        """
        Transports a VajraPacket to its destination.

        TÜV CHECK (Naga Interception):
        1. Verify MantraSeal (Identity).
        2. Verify Watertight seal (Structure).
        3. Check signer karma via TÜV badge.

        Returns:
            TransportResult with success status.
        """
        ...

    def traffic_status(self) -> Dict[str, int]:
        """
        Returns the current flow state (Prana flow).

        Returns:
            Dict with lane names and packet counts.
        """
        ...


# =============================================================================
# LEGACY PACKET (TAMAS - Deprecated)
# =============================================================================

# NOTE: This is kept for backward compatibility.
# New code should use VajraPacket exclusively.

# Removed `Packet` with `payload: Any` - that was Mayavad.
# If legacy code needs untyped packets, they go to TAMAS lane.


# =============================================================================
# MAYAVAD ERROR
# =============================================================================


class MayavadError(Exception):
    """
    Raised when untyped chaos is detected.

    The packet contains `Any` or failed Watertight verification.
    """

    pass
