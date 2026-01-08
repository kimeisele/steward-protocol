"""
AUTOBAHN PROTOCOL - The Transgalactic Infrastructure.

"High Speed. Zero Friction. Anti-Mayavad."

This protocol abstracts 'Transport' beyond mere HTTP/RPC.
It defines the 'Lanes' of consciousness for the Juggernaut (Jagannath).

LANES:
- SATTVA (Fast Lane): High Priority, Fully Signed, Verified. (The Jagannath Chariot).
- RAJAS (Middle Lane): Action-oriented, standard traffic.
- TAMAS (Slow Lane): Logging, cleanup, shadow work.

CONCEPTS:
- PACKET: The sealed container of intent.
- VEHICLE: The carrier (Jagannath, Ananta).
- TÜV: The Gatekeeper (Validation).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Protocol, TypeVar, runtime_checkable

T_Packet = TypeVar("T_Packet")  # The Payload
T_Result = TypeVar("T_Result")  # The Outcome


class Lane(str, Enum):
    """
    The 3 Lanes of the Vedic Autobahn.
    """

    SATTVA = "SATTVA"  # Goodness, Clarity, Speed (Priority 1)
    RAJAS = "RAJAS"  # Passion, Action, Movement (Priority 2)
    TAMAS = "TAMAS"  # Ignorance, Inertia, Storage (Priority 3)


@dataclass
class Packet:
    """
    The Sealed Container on the Autobahn.
    Everything must be encapsulated here. No loose wires.
    """

    id: str  # Unique ID
    lane: Lane  # The Lane assignment
    payload: Any  # The Content (T_Packet)
    signature: str  # The 37th Seal (Sovereign Signature)
    headers: Dict[str, str]  # Meta-data (Routing info)


@runtime_checkable
class IAutobahn(Protocol):
    """
    The Interface of the Infrastructure.
    """

    def open_lane(self, lane: Lane) -> bool:
        """
        Opens a specific lane for traffic.
        Returns: Success.
        """
        ...

    def transport(self, packet: Packet) -> T_Result:
        """
        Transports a packet to its destination.

        TÜV CHECK:
        - If signature is missing -> INCINERATE (Raise Error).
        - If lane is SATTVA -> Priority execution.
        """
        ...

    def traffic_status(self) -> Dict[str, Any]:
        """
        Returns the current flow state (Prana flow).
        """
        ...
