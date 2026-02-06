"""
SYNAPSE PROTOCOL (DEPRECATED) → Use vibe_core.mahamantra.substrate.nadi
=========================================================================

⚠️  DEPRECATION NOTICE ⚠️
This module is DEPRECATED and will be removed in a future version.
Use vibe_core.mahamantra.substrate.nadi instead.

Migration Guide:
    OLD:
        from vibe_core.protocols.synapse import SynapseProtocol, LocalSynapse
        synapse = LocalSynapse("my_agent")
        synapse.send(SynapseMessage(...))

    NEW:
        from vibe_core.mahamantra.substrate.nadi import NadiProtocol, LocalNadi, NadiType
        nadi = LocalNadi("my_agent", NadiType.APANA)
        nadi.send(NadiMessage(...))

The new Nadi protocol is SSOT-compliant and derives all constants from NADI_RESONANCE (72).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x460bbe68"  # GenesisByte: parampara % 37 == 0

import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

# =============================================================================
# IMPORT FROM NEW NADI PROTOCOL (THE FUTURE)
# =============================================================================
from vibe_core.mahamantra.substrate.nadi import (
    LocalNadi as _LocalNadi,
)
from vibe_core.mahamantra.substrate.nadi import (
    NadiConnection,
    NadiMessage,
    NadiOp,
    NadiPriority,
    NadiProtocol,
    NadiStats,
    NadiType,
    get_nadi,
)
from vibe_core.mahamantra.substrate.nadi import (
    NullNadi as _NullNadi,
)

import logging
logger = logging.getLogger(__name__)


def _deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue deprecation warning."""
    warnings.warn(
        f"{old_name} is deprecated. Use {new_name} from vibe_core.mahamantra.substrate.nadi instead.",
        DeprecationWarning,
        stacklevel=3,
    )


# =============================================================================
# LEGACY ENUMS (map to Nadi equivalents)
# =============================================================================


class MessagePriority(str, Enum):
    """
    DEPRECATED: Use NadiPriority instead.

    Priority levels for synapse messages.
    """

    LOW = "low"  # → NadiPriority.TAMAS
    NORMAL = "normal"  # → NadiPriority.RAJAS
    HIGH = "high"  # → NadiPriority.SATTVA
    CRITICAL = "critical"  # → NadiPriority.SUDDHA


# Mapping from old to new
_PRIORITY_MAP = {
    MessagePriority.LOW: NadiPriority.TAMAS,
    MessagePriority.NORMAL: NadiPriority.RAJAS,
    MessagePriority.HIGH: NadiPriority.SATTVA,
    MessagePriority.CRITICAL: NadiPriority.SUDDHA,
}

_PRIORITY_REVERSE = {v: k for k, v in _PRIORITY_MAP.items()}


class MessageType(str, Enum):
    """
    DEPRECATED: Use NadiOp instead.

    Types of synapse messages.
    """

    REQUEST = "request"  # → NadiOp.REQUEST
    RESPONSE = "response"  # → NadiOp.RECEIVE
    EVENT = "event"  # → NadiOp.SEND
    BROADCAST = "broadcast"  # → NadiOp.SEND (with target="*")
    HEARTBEAT = "heartbeat"  # → NadiOp.VALIDATE


# Mapping from old to new
_TYPE_MAP = {
    MessageType.REQUEST: NadiOp.REQUEST,
    MessageType.RESPONSE: NadiOp.RECEIVE,
    MessageType.EVENT: NadiOp.SEND,
    MessageType.BROADCAST: NadiOp.SEND,
    MessageType.HEARTBEAT: NadiOp.VALIDATE,
}


# =============================================================================
# LEGACY DATA STRUCTURES
# =============================================================================


@dataclass
class SynapseMessage:
    """
    DEPRECATED: Use NadiMessage instead.

    A message between agents.
    """

    sender: str
    receiver: str  # Use "*" for broadcast
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)
    message_type: MessageType = MessageType.EVENT
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    ttl_seconds: Optional[int] = None

    @property
    def is_broadcast(self) -> bool:
        return self.receiver == "*"

    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)

    def to_nadi_message(self) -> NadiMessage:
        """Convert to NadiMessage."""
        return NadiMessage(
            source=self.sender,
            target=self.receiver,
            nadi_type=NadiType.APANA,  # Agent-to-agent
            operation=_TYPE_MAP.get(self.message_type, NadiOp.SEND),
            payload={"topic": self.topic, **self.payload},
            priority=_PRIORITY_MAP.get(self.priority, NadiPriority.RAJAS),
            correlation_id=self.correlation_id,
            timestamp=self.timestamp,
            ttl_ms=(self.ttl_seconds * 1000) if self.ttl_seconds else 0,
        )

    @classmethod
    def from_nadi_message(cls, msg: NadiMessage) -> "SynapseMessage":
        """Convert from NadiMessage."""
        payload = msg.payload.copy()
        topic = payload.pop("topic", "unknown")

        # Reverse map operation to message type
        msg_type = MessageType.EVENT
        for old_type, new_op in _TYPE_MAP.items():
            if new_op == msg.operation:
                msg_type = old_type
                break

        return cls(
            sender=msg.source,
            receiver=msg.target,
            topic=topic,
            payload=payload,
            message_type=msg_type,
            priority=_PRIORITY_REVERSE.get(msg.priority, MessagePriority.NORMAL),
            correlation_id=msg.correlation_id,
            timestamp=msg.timestamp,
            ttl_seconds=(msg.ttl_ms // 1000) if msg.ttl_ms > 0 else None,
        )


@dataclass
class Connection:
    """
    DEPRECATED: Use NadiConnection instead.

    A connection to another agent.
    """

    agent_id: str
    connected_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    messages_sent: int = 0
    messages_received: int = 0
    is_active: bool = True


@dataclass
class SynapseStats:
    """
    DEPRECATED: Use NadiStats instead.

    Statistics about synapse activity.
    """

    agent_id: str
    connections: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    broadcasts_sent: int = 0
    pending_messages: int = 0
    connected_agents: List[str] = field(default_factory=list)


# =============================================================================
# LEGACY PROTOCOL (interface)
# =============================================================================


@runtime_checkable
class SynapseProtocol(Protocol):
    """
    DEPRECATED: Use NadiProtocol instead.

    OPUS-311: Inter-agent neural messaging.
    """

    @property
    def agent_id(self) -> str: ...

    def connect(self, agent_id: str) -> bool: ...

    def disconnect(self, agent_id: str) -> bool: ...

    def is_connected(self, agent_id: str) -> bool: ...

    def get_connections(self) -> List[Connection]: ...

    def send(self, message: SynapseMessage) -> bool: ...

    def receive(self, timeout_ms: Optional[int] = None) -> Optional[SynapseMessage]: ...

    def receive_all(self) -> List[SynapseMessage]: ...

    def broadcast(self, topic: str, payload: Dict[str, Any]) -> int: ...

    def subscribe(
        self,
        topic: str,
        handler: Callable[[SynapseMessage], None],
    ) -> str: ...

    def unsubscribe(self, subscription_id: str) -> bool: ...

    def request(
        self,
        receiver: str,
        topic: str,
        payload: Dict[str, Any],
        timeout_ms: int = 5000,
    ) -> Optional[SynapseMessage]: ...

    def respond(
        self,
        original: SynapseMessage,
        payload: Dict[str, Any],
    ) -> bool: ...

    def get_stats(self) -> SynapseStats: ...


# =============================================================================
# LEGACY IMPLEMENTATIONS (wrappers around Nadi)
# =============================================================================


class NullSynapse:
    """
    DEPRECATED: Use NullNadi instead.

    Arjuna Pattern: No-op synapse.
    """

    def __init__(self, agent_id: str = "anonymous"):
        _deprecation_warning("NullSynapse", "NullNadi")
        self._nadi = _NullNadi(agent_id, NadiType.APANA)

    @property
    def agent_id(self) -> str:
        return self._nadi.endpoint_id

    def connect(self, agent_id: str) -> bool:
        return self._nadi.connect(agent_id)

    def disconnect(self, agent_id: str) -> bool:
        return self._nadi.disconnect(agent_id)

    def is_connected(self, agent_id: str) -> bool:
        return self._nadi.is_connected(agent_id)

    def get_connections(self) -> List[Connection]:
        return []

    def send(self, message: SynapseMessage) -> bool:
        return self._nadi.send(message.to_nadi_message())

    def receive(self, timeout_ms: Optional[int] = None) -> Optional[SynapseMessage]:
        return None

    def receive_all(self) -> List[SynapseMessage]:
        return []

    def broadcast(self, topic: str, payload: Dict[str, Any]) -> int:
        return 0

    def subscribe(
        self,
        topic: str,
        handler: Callable[[SynapseMessage], None],
    ) -> str:
        return "null-subscription"

    def unsubscribe(self, subscription_id: str) -> bool:
        return False

    def request(
        self,
        receiver: str,
        topic: str,
        payload: Dict[str, Any],
        timeout_ms: int = 5000,
    ) -> Optional[SynapseMessage]:
        return None

    def respond(
        self,
        original: SynapseMessage,
        payload: Dict[str, Any],
    ) -> bool:
        return False

    def get_stats(self) -> SynapseStats:
        return SynapseStats(agent_id=self.agent_id)


class LocalSynapse:
    """
    DEPRECATED: Use LocalNadi instead.

    OPUS-311: Local implementation of SynapseProtocol.
    Now wraps LocalNadi for SSOT compliance.
    """

    def __init__(self, agent_id: str):
        _deprecation_warning("LocalSynapse", "LocalNadi")
        self._nadi = _LocalNadi(agent_id, NadiType.APANA)

    @property
    def agent_id(self) -> str:
        return self._nadi.endpoint_id

    def connect(self, agent_id: str) -> bool:
        return self._nadi.connect(agent_id)

    def disconnect(self, agent_id: str) -> bool:
        return self._nadi.disconnect(agent_id)

    def is_connected(self, agent_id: str) -> bool:
        return self._nadi.is_connected(agent_id)

    def get_connections(self) -> List[Connection]:
        nadi_conns = self._nadi.get_connections()
        return [
            Connection(
                agent_id=c.target,
                connected_at=c.established_at,
                last_heartbeat=c.last_activity,
                messages_sent=c.messages_sent,
                messages_received=c.messages_received,
                is_active=c.is_active,
            )
            for c in nadi_conns
        ]

    def send(self, message: SynapseMessage) -> bool:
        return self._nadi.send(message.to_nadi_message())

    def receive(self, timeout_ms: Optional[int] = None) -> Optional[SynapseMessage]:
        nadi_msg = self._nadi.receive(timeout_ms)
        if nadi_msg is None:
            return None
        return SynapseMessage.from_nadi_message(nadi_msg)

    def receive_all(self) -> List[SynapseMessage]:
        return [SynapseMessage.from_nadi_message(m) for m in self._nadi.receive_all()]

    def broadcast(self, topic: str, payload: Dict[str, Any]) -> int:
        return self._nadi.broadcast(NadiOp.SEND, {"topic": topic, **payload})

    def subscribe(
        self,
        topic: str,
        handler: Callable[[SynapseMessage], None],
    ) -> str:
        def wrapped(msg: NadiMessage):
            if msg.payload.get("topic") == topic:
                handler(SynapseMessage.from_nadi_message(msg))

        return self._nadi.subscribe(NadiOp.SEND, wrapped)

    def unsubscribe(self, subscription_id: str) -> bool:
        return self._nadi.unsubscribe(subscription_id)

    def request(
        self,
        receiver: str,
        topic: str,
        payload: Dict[str, Any],
        timeout_ms: int = 5000,
    ) -> Optional[SynapseMessage]:
        response = self._nadi.request(
            receiver,
            NadiOp.REQUEST,
            {"topic": topic, **payload},
            timeout_ms,
        )
        if response is None:
            return None
        return SynapseMessage.from_nadi_message(response)

    def respond(
        self,
        original: SynapseMessage,
        payload: Dict[str, Any],
    ) -> bool:
        nadi_original = original.to_nadi_message()
        return self._nadi.respond(nadi_original, payload)

    def get_stats(self) -> SynapseStats:
        nadi_stats = self._nadi.get_stats()
        return SynapseStats(
            agent_id=nadi_stats.endpoint_id,
            connections=nadi_stats.connections,
            messages_sent=nadi_stats.messages_sent,
            messages_received=nadi_stats.messages_received,
            broadcasts_sent=0,  # Not tracked in Nadi
            pending_messages=nadi_stats.messages_pending,
            connected_agents=nadi_stats.connected_endpoints,
        )


def get_synapse_safe(agent_id: str = "anonymous") -> SynapseProtocol:
    """
    DEPRECATED: Use get_nadi() instead.

    Get Synapse via ServiceRegistry with NullSynapse fallback.
    """
    _deprecation_warning("get_synapse_safe", "get_nadi")
    try:
        from vibe_core.di import ServiceRegistry

        synapse = ServiceRegistry.get(SynapseProtocol)
        if synapse is not None:
            return synapse
    except ImportError as _exc:
        logger.exception("Unexpected error: %s", _exc)

    return NullSynapse(agent_id)


# =============================================================================
# EXPORTS - Backward compatible
# =============================================================================

__all__ = [
    # Legacy (deprecated)
    "MessagePriority",
    "MessageType",
    "SynapseMessage",
    "Connection",
    "SynapseStats",
    "SynapseProtocol",
    "NullSynapse",
    "LocalSynapse",
    "get_synapse_safe",
    # New (preferred)
    "NadiProtocol",
    "NadiMessage",
    "NadiConnection",
    "NadiStats",
    "NadiType",
    "NadiOp",
    "NadiPriority",
    "get_nadi",
]
