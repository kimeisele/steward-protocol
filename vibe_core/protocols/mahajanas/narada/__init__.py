"""
NARADA - The 2nd Mahajana (Communication/Observation)
=====================================================

POSITION: 2 (GENESIS Quarter, ALLOC_MEM OpCode)

"Narada Muni ki Jai!" - The Cosmic Journalist

DERIVED FROM MAHAMANTRA:
    Position 2 -> guardian=NARADA, opcode=ALLOC_MEM, quarter=GENESIS
    All properties derived from truth table. No manual wiring.

Narada travels everywhere, knows everything, reports faithfully.
He does NOT act - he OBSERVES and TRANSMITS.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry


# =============================================================================
# NARADA PROTOCOL BASE - Derives from MantraPosition 2
# =============================================================================

@ProtocolRegistry.register
class NaradaProtocolBase(WorkerProtocol):
    """
    Narada protocol ownership - DERIVED from Mahamantra position 2.

    NO MANUAL WIRING:
        _position_index = 2 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.NARADA
        opcode()    -> MantraOpCode.ALLOC_MEM
        quarter()   -> Quarter.GENESIS
        is_head()   -> False (Worker position)
        parampara_vector() -> 111 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 2  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[2]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

# The union of allowed message payload types - WATERTIGHT
MessagePayload = Union[str, int, float, bool, Dict[str, str], List[str], None]


class MessageType(str, Enum):
    """Types of messages Narada can transmit."""
    EVENT = "event"           # Something happened
    NOTIFICATION = "notification"  # FYI
    REQUEST = "request"       # Asking for something
    RESPONSE = "response"     # Answering a request
    BROADCAST = "broadcast"   # To all listeners
    WHISPER = "whisper"       # To specific target
    PULSE = "pulse"           # Heartbeat sync


class Message(TypedDict, total=False):
    """
    A message structure for communication.
    WATERTIGHT - no Any!
    """
    id: str                   # Unique message ID
    type: str                 # MessageType value
    source: str               # Sender identity
    target: str               # Receiver identity (empty for broadcast)
    payload_type: str         # Python type of payload
    payload_repr: str         # String representation of payload
    timestamp: str            # ISO timestamp
    correlation_id: str       # For request/response pairing


class Observation(TypedDict, total=False):
    """
    A recorded observation.
    WATERTIGHT - no Any!
    """
    observed_at: str          # ISO timestamp
    source: str               # What was observed
    event_type: str           # Type of event
    details: str              # String description
    severity: str             # "debug", "info", "warning", "error"


class ObserverState(TypedDict, total=False):
    """
    Complete observer state for observability.
    WATERTIGHT - no Any!
    """
    observations: List[Observation]
    total_observed: int
    listeners_count: int
    messages_sent: int
    messages_received: int
    last_pulse: str           # ISO timestamp
    health: str               # "pristine", "healthy", "degraded"


class BroadcastResult(TypedDict, total=False):
    """
    Result of a broadcast operation.
    WATERTIGHT - no Any!
    """
    success: bool
    recipients_count: int
    failed_count: int
    message_id: str


class BroadcastCliResult(TypedDict):
    """Result of CLI broadcast operation. WATERTIGHT - no Any!"""
    success: bool
    message_type: str
    recipients: int
    health: str


# =============================================================================
# LISTENER TYPE (For type-safe callbacks)
# =============================================================================

# TypeVar for the observed value type
T = TypeVar("T")


class ListenerCallback(Protocol):
    """Protocol for listener callbacks - WATERTIGHT."""
    def __call__(self, message: Message) -> None:
        """Receive a message."""
        ...


# =============================================================================
# NARADA PROTOCOL (Main Communication Protocol)
# =============================================================================


@runtime_checkable
class NaradaProtocol(Protocol):
    """
    The Communication/Observer Protocol - Narada's domain.

    DERIVED: Position 2 -> NARADA, ALLOC_MEM, GENESIS
    WATERTIGHT - no Any types!

    The Three Aspects of Communication (Kirtanam):
    1. OBSERVE (spy) - Pure observation without modification
    2. TRANSMIT (broadcast) - Send to all listeners
    3. RECORD (log) - Keep history of observations
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 2 in the Mahamantra."""
        ...

    # =========================================================================
    # Observation (Spy Pattern)
    # =========================================================================

    def observe(self, source: str, event_type: str, details: str) -> bool:
        """
        Record an observation.
        WATERTIGHT: All parameters are strings.
        Returns True if recorded.
        """
        ...

    def get_observations(self, limit: int = 100) -> List[Observation]:
        """
        Get recent observations.
        WATERTIGHT: Returns List[Observation], not List[Any].
        """
        ...

    # =========================================================================
    # Communication (PULSE_SYNC OpCode)
    # =========================================================================

    def broadcast(self, message_type: MessageType, payload: MessagePayload) -> BroadcastResult:
        """
        Broadcast a message to all listeners.
        WATERTIGHT: payload is MessagePayload union, not Any.
        Returns structured BroadcastResult.
        """
        ...

    def whisper(self, target: str, message_type: MessageType, payload: MessagePayload) -> bool:
        """
        Send a message to a specific target.
        WATERTIGHT: payload is MessagePayload union, not Any.
        Returns True if delivered.
        """
        ...

    def subscribe(self, listener_id: str, callback: ListenerCallback) -> bool:
        """
        Subscribe to broadcasts.
        WATERTIGHT: callback is typed ListenerCallback.
        Returns True if subscribed.
        """
        ...

    def unsubscribe(self, listener_id: str) -> bool:
        """
        Unsubscribe from broadcasts.
        Returns True if was subscribed and now unsubscribed.
        """
        ...

    # =========================================================================
    # Pulse Synchronization
    # =========================================================================

    def pulse(self) -> str:
        """
        Send a heartbeat pulse.
        Returns the pulse timestamp (ISO format).
        """
        ...

    def get_last_pulse(self) -> Optional[str]:
        """
        Get timestamp of last pulse.
        Returns None if no pulse yet.
        """
        ...

    # =========================================================================
    # Observability
    # =========================================================================

    def get_state(self) -> ObserverState:
        """
        Get complete observer state.
        WATERTIGHT: Returns ObserverState TypedDict, not Dict[str, Any].
        """
        ...


# =============================================================================
# NULL NARADA (For testing)
# =============================================================================


class NullNarada(NaradaProtocolBase):
    """
    The Silent Witness.
    Observes nothing, reports nothing (for testing without communication).

    Inherits from NaradaProtocolBase -> position 2 -> NARADA.

    Even in Null mode:
    - returns empty observations
    - broadcasts succeed silently
    """

    def observe(self, source: str, event_type: str, details: str) -> bool:
        return True  # Accept but don't record

    def get_observations(self, limit: int = 100) -> List[Observation]:
        return []  # Nothing observed

    def broadcast(self, message_type: MessageType, payload: MessagePayload) -> BroadcastResult:
        return BroadcastResult(
            success=True,
            recipients_count=0,
            failed_count=0,
            message_id="null",
        )

    def whisper(self, target: str, message_type: MessageType, payload: MessagePayload) -> bool:
        return True  # Silently succeed

    def subscribe(self, listener_id: str, callback: ListenerCallback) -> bool:
        return True  # Accept but don't store

    def unsubscribe(self, listener_id: str) -> bool:
        return False  # Nothing to unsubscribe

    def pulse(self) -> str:
        return datetime.now().isoformat()

    def get_last_pulse(self) -> Optional[str]:
        return None

    def get_state(self) -> ObserverState:
        return ObserverState(
            observations=[],
            total_observed=0,
            listeners_count=0,
            messages_sent=0,
            messages_received=0,
            health="pristine",
        )

    def broadcast_cli(self, message: str = "pulse") -> BroadcastCliResult:
        """CLI: Broadcast a message. WATERTIGHT."""
        result = self.broadcast(MessageType.PULSE, message)
        state = self.get_state()
        return BroadcastCliResult(
            success=result.get("success", True),
            message_type="pulse",
            recipients=result.get("recipients_count", 0),
            health=state.get("health", "pristine"),
        )


# =============================================================================
# NARADA'S INSTRUCTION (For Communication)
# =============================================================================

@dataclass(frozen=True)
class KirtanamInstruction:
    """
    An instruction for communication.

    Kirtanam = Glorification/Communication (Second of the Nine Processes of Bhakti)

    This is the ATOMIC unit of communication.
    Used by NadiProtocol and AkashaProtocol.
    """
    operation: str  # "observe", "broadcast", "whisper", "subscribe", "pulse"
    source: str
    target: Optional[str] = None
    message_type: Optional[MessageType] = None
    payload: Optional[MessagePayload] = None
    sovereign_id: Optional[str] = None  # For audit trail

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, None]]:
        """Serialize for transmission."""
        result: Dict[str, Union[str, int, float, bool, None]] = {
            "operation": self.operation,
            "source": self.source,
        }
        if self.target:
            result["target"] = self.target
        if self.message_type:
            result["message_type"] = self.message_type.value
        if self.payload is not None:
            if isinstance(self.payload, (dict, list)):
                result["payload"] = str(self.payload)
                result["payload_type"] = type(self.payload).__name__
            else:
                result["payload"] = self.payload
                result["payload_type"] = type(self.payload).__name__
        if self.sovereign_id:
            result["sovereign_id"] = self.sovereign_id
        return result


# =============================================================================
# EXPORTS
# =============================================================================

# Event Bus Protocol
from vibe_core.protocols.mahajanas.narada.events import (
    EventType,
    EventData,
    Event,
    SubscriberInfo,
    EventBusStats,
    EventBusState,
    EventBusProtocol,
    EventBusOwnedProtocol,
    NullEventBus,
)

# =============================================================================
# BROADCAST - Multi-Channel Communication
# =============================================================================

from vibe_core.protocols.mahajanas.narada.broadcast import (
    DeliveryMode,
    Channel,
    Subscription,
    BroadcastHandler,
    BroadcastProtocol,
    Broadcaster,
    NullBroadcaster,
    LOTUS_POSITION as BROADCAST_POSITION,
)

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "NaradaProtocolBase",
    # State Types (WATERTIGHT)
    "MessagePayload",
    "MessageType",
    "Message",
    "Observation",
    "ObserverState",
    "BroadcastResult",
    "BroadcastCliResult",
    # Callback Protocol
    "ListenerCallback",
    # Protocol
    "NaradaProtocol",
    # Implementations
    "NullNarada",
    # Instructions
    "KirtanamInstruction",
    # Event Bus (WATERTIGHT)
    "EventType",
    "EventData",
    "Event",
    "SubscriberInfo",
    "EventBusStats",
    "EventBusState",
    "EventBusProtocol",
    "EventBusOwnedProtocol",
    "NullEventBus",
    # Broadcast (Multi-Channel)
    "DeliveryMode",
    "Channel",
    "Subscription",
    "BroadcastHandler",
    "BroadcastProtocol",
    "Broadcaster",
    "NullBroadcaster",
]
