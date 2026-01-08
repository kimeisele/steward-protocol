"""
JAGANNATH PROTOCOL - The Lord of the Universe (Layer 1).

"Ratha Yatra" - Der Wagen rollt.

Jagannath ist der ultimative User der Autobahn.
Er ist 'Acintya' (Unbegreiflich) und 'Sovereign' (Unabhängig).

FUNKTION:
Er bewegt große Datenmengen (Universen/State) durch das System.
Er hält sich nicht an 'Timeouts'. Er kommt an, wenn er ankommt.
"""

from dataclasses import dataclass
from typing import Any, List, Protocol, runtime_checkable

from .autobahn import AutobahnProtocol, Lane, VajraPacket
from .types import SovereignContext, TranscendentalQuality


@dataclass
class RathaYatra:
    """Der Wagen (Container für Massiv-State)."""

    deity: "JagannathDeity"
    devotees: List[str]  # Liste der Subscriber
    offerings: List[Any]  # Data Payload


class JagannathDeity:
    """
    Die Gottheit.
    Hat Quality 60 (Vishnu-Tattva) + 4 (Krishna-Tattva) = 64.
    """

    def __init__(self):
        self.quality = TranscendentalQuality.SOURCE_OF_INCARNATIONS


@runtime_checkable
class JagannathProtocol(Protocol):
    """
    Das Interface für die Prozession.
    """

    def mount_chariot(self, state: Any) -> RathaYatra: ...

    def start_procession(self, autobahn: AutobahnProtocol) -> None: ...


# =============================================================================
# THE TEMPLE IMPLEMENTATION
# =============================================================================


class PuriTemple:
    def __init__(self, context: SovereignContext):
        self.context = context
        self.lord = JagannathDeity()

    def start_procession(self, autobahn: AutobahnProtocol):
        """
        Startet den Ratha Yatra auf der Autobahn.
        """
        # 1. Der Wagen wird gebaut
        chariot = RathaYatra(deity=self.lord, devotees=[], offerings=[])

        # 2. Das Paket wird geschnürt
        packet = VajraPacket(
            id="RATHA_001",
            payload=self.lord,  # Der Herr selbst ist der Payload
            context=self.context,
            lane=Lane.SATTVA,  # Immer Überholspur
        )

        # 3. Transport
        # Da es Jagannath ist, wird die Autobahn '_clear_road' aufrufen.
        autobahn.transport(packet)
