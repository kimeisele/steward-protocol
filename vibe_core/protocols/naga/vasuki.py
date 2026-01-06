"""
VASUKI Protocol - Der Transformator (Network/Serialization)

Vasuki - König der Schlangen, Grenze zwischen Welten.
PROMPT.md: "Memory is not Network."

Responsibilities:
- Serialize events for network (churn_out)
- Deserialize events from network (churn_in)
- Sign before sending
- Validate schema on receive
- Maintain internal/external boundary

Integration:
- Registers as handler for DriftSource.CONFIG
- Detects config drift between nodes
- Heals by propagating correct config
"""

from dataclasses import dataclass
from enum import Enum
from typing import AsyncIterator, List, Optional, Protocol, runtime_checkable

from vibe_core.protocols.correction import (
    CorrectionHandler,
    HealingResult,
    HealingStatus,
    HealingStrategy,
    UnifiedDriftReport,
)
from vibe_core.protocols.naga.types import EventDict, NagaStatus, NagaType


@dataclass
class SignedEnvelope:
    """
    A signed, serialized payload ready for network transfer.

    Vasuki produces these when "churning out" (serializing).
    Vasuki consumes these when "churning in" (deserializing).
    """

    payload: bytes  # MsgPack/Protobuf serialized
    signature: bytes  # ECDSA signature
    sender_key: str  # PEM public key
    timestamp: float  # Unix timestamp
    content_type: str = "msgpack"  # Serialization format

    def to_bytes(self) -> bytes:
        """Serialize the entire envelope for wire transfer."""
        import msgpack

        return msgpack.packb(
            {
                "payload": self.payload,
                "signature": self.signature,
                "sender_key": self.sender_key,
                "timestamp": self.timestamp,
                "content_type": self.content_type,
            }
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "SignedEnvelope":
        """Deserialize from wire format."""
        import msgpack

        d = msgpack.unpackb(data)
        return cls(
            payload=d["payload"],
            signature=d["signature"],
            sender_key=d["sender_key"],
            timestamp=d["timestamp"],
            content_type=d.get("content_type", "msgpack"),
        )


class SendStatus(str, Enum):
    """Result of sending via Vasuki."""

    SENT = "sent"
    QUEUED = "queued"
    FAILED = "failed"
    BLOCKED = "blocked"  # Takshaka rejected


@dataclass
class SendResult:
    """Result of a Vasuki send operation."""

    status: SendStatus
    envelope_hash: str = ""
    message: str = ""
    retry_after: Optional[float] = None


@dataclass
class NodeAddress:
    """Address of a peer node."""

    host: str
    port: int
    public_key: Optional[str] = None
    node_id: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


@runtime_checkable
class VasukiProtocol(Protocol):
    """
    Vasuki - König der Schlangen, Grenze zwischen Welten.

    PROMPT.md: "Memory is not Network."

    Responsibilities:
    - Serialize events for network (churn_out)
    - Deserialize events from network (churn_in)
    - Sign before sending
    - Validate schema on receive
    - Maintain internal/external boundary

    Integration:
    - Registers as handler for DriftSource.CONFIG
    - Detects config drift between nodes
    - Heals by propagating correct config

    Usage:
        vasuki = ServiceRegistry.get(VasukiProtocol)
        envelope = vasuki.churn_out(event)
        result = vasuki.send(peer_address, envelope)
    """

    # === Serialization (Das Quirlen) ===

    def churn_out(self, event: EventDict) -> SignedEnvelope:
        """
        Transform internal event → signed wire-ready envelope.

        The "churning" metaphor from Samudra Manthan:
        Raw Python dict becomes transportable nectar.

        Args:
            event: Internal event dict

        Returns:
            SignedEnvelope ready for network
        """
        ...

    def churn_in(self, envelope: SignedEnvelope) -> EventDict:
        """
        Transform wire envelope → internal event.

        NOTE: Takshaka must verify BEFORE calling this!
        This method trusts the envelope is authentic.

        Args:
            envelope: Verified SignedEnvelope

        Returns:
            Internal event dict
        """
        ...

    # === Network Operations ===

    async def send(self, target: NodeAddress, envelope: SignedEnvelope) -> SendResult:
        """
        Send envelope to a peer node.

        Args:
            target: Destination node
            envelope: Signed payload

        Returns:
            SendResult with status
        """
        ...

    async def receive(self) -> AsyncIterator[SignedEnvelope]:
        """
        Receive envelopes from the network.

        Yields:
            SignedEnvelopes as they arrive
        """
        ...

    # === Boundary Enforcement ===

    def is_internal(self, event: EventDict) -> bool:
        """Check if event should stay internal (not sent to network)."""
        ...

    def get_peers(self) -> List[NodeAddress]:
        """Get known peer nodes."""
        ...

    # === CorrectionHandler Interface ===

    def as_handler(self) -> CorrectionHandler:
        """Get this NAGA as a CorrectionHandler for DriftSource.CONFIG."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullVasuki:
    """No-op Vasuki for when network is unavailable."""

    def churn_out(self, event: EventDict) -> SignedEnvelope:
        return SignedEnvelope(payload=b"", signature=b"", sender_key="", timestamp=0)

    def churn_in(self, envelope: SignedEnvelope) -> EventDict:
        return EventDict(event_type="null", agent_id="null", timestamp="0", details={})

    async def send(self, target: NodeAddress, envelope: SignedEnvelope) -> SendResult:
        return SendResult(status=SendStatus.FAILED, message="Vasuki not available")

    async def receive(self) -> AsyncIterator[SignedEnvelope]:
        return
        yield  # Make it a generator

    def is_internal(self, event: EventDict) -> bool:
        return True

    def get_peers(self) -> List[NodeAddress]:
        return []

    def as_handler(self) -> CorrectionHandler:
        def handler(drift: UnifiedDriftReport, strategy: HealingStrategy) -> HealingResult:
            return HealingResult(
                drift_id=drift.id,
                status=HealingStatus.SKIPPED,
                handler_id="null_vasuki",
                message="Vasuki not available",
            )

        return handler

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.VASUKI, healthy=False, message="Not initialized")