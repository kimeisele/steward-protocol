"""
NAGA Federation Protocol - The Three Working Together

Data Flow:
    External → Takshaka (verify) → Vasuki (deserialize) → Sesha (record)
    Sesha (read) → Vasuki (serialize) → Takshaka (sign) → External

This is the unified interface for the NAGA layer.
"""

from typing import TYPE_CHECKING, Dict, Optional, Protocol, runtime_checkable

from vibe_core.protocols.naga.types import NagaStatus, NagaType

if TYPE_CHECKING:
    from vibe_core.protocols.naga.sesha import ImportResult, SeshaProtocol
    from vibe_core.protocols.naga.takshaka import TakshakaProtocol
    from vibe_core.protocols.naga.vasuki import NodeAddress, SendResult, VasukiProtocol


@runtime_checkable
class NagaFederationProtocol(Protocol):
    """
    The three NAGAs working together.

    Data Flow:
        External → Takshaka (verify) → Vasuki (deserialize) → Sesha (record)
        Sesha (read) → Vasuki (serialize) → Takshaka (sign) → External

    This is the unified interface for the NAGA layer.
    """

    @property
    def sesha(self) -> "SeshaProtocol":
        """Access Sesha (Data/Ledger)."""
        ...

    @property
    def vasuki(self) -> "VasukiProtocol":
        """Access Vasuki (Network/Serialization)."""
        ...

    @property
    def takshaka(self) -> "TakshakaProtocol":
        """Access Takshaka (Security)."""
        ...

    def receive_external(self, raw: bytes, source: str) -> Optional[Dict[str, object]]:
        """
        Process incoming external data through the full NAGA pipeline.

        Flow: Takshaka (verify) → Vasuki (deserialize) → Sesha (record)

        Args:
            raw: Raw bytes from network
            source: Source identifier (IP, node_id, etc.)

        Returns:
            Deserialized event if valid, None if rejected
        """
        ...

    def send_external(self, event: Dict[str, object], target: "NodeAddress") -> "SendResult":
        """
        Send event to external node through the full NAGA pipeline.

        Flow: Sesha (record) → Vasuki (serialize) → Takshaka (sign) → send

        Args:
            event: Event to send
            target: Destination node

        Returns:
            SendResult
        """
        ...

    def sync_with_peer(self, peer: "NodeAddress") -> "ImportResult":
        """
        Synchronize ledger with a peer node.

        Uses Sesha's gossip protocol with Vasuki for transport
        and Takshaka for verification.
        """
        ...

    def get_status(self) -> Dict[NagaType, NagaStatus]:
        """Get status of all three NAGAs."""
        ...
