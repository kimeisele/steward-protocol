"""
OPUS-311 Sprint 3: Synapse Protocol

The Nadi (Neural Channel) for inter-agent communication.

Direct agent-to-agent messaging without going through kernel.
Enables emergent coordination and swarm behavior.

Usage:
    # Via ServiceRegistry
    synapse: SynapseProtocol = ServiceRegistry.get(SynapseProtocol) or NullSynapse()

    # Connect to another agent
    synapse.connect("herald")

    # Send message
    msg = SynapseMessage(
        sender="archivist",
        receiver="herald",
        topic="audit_complete",
        payload={"issues": 3}
    )
    synapse.send(msg)

    # Receive messages
    while msg := synapse.receive():
        process(msg)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, runtime_checkable


class MessagePriority(str, Enum):
    """Priority levels for synapse messages."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageType(str, Enum):
    """Types of synapse messages."""

    REQUEST = "request"  # Expecting response
    RESPONSE = "response"  # Reply to request
    EVENT = "event"  # Fire and forget
    BROADCAST = "broadcast"  # To all connected
    HEARTBEAT = "heartbeat"  # Keep-alive


@dataclass
class SynapseMessage:
    """A message between agents."""

    sender: str
    receiver: str  # Use "*" for broadcast
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)
    message_type: MessageType = MessageType.EVENT
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None  # For request/response pairing
    timestamp: datetime = field(default_factory=datetime.now)
    ttl_seconds: Optional[int] = None  # Time to live

    @property
    def is_broadcast(self) -> bool:
        return self.receiver == "*"

    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        from datetime import timedelta

        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)


@dataclass
class Connection:
    """A connection to another agent."""

    agent_id: str
    connected_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    messages_sent: int = 0
    messages_received: int = 0
    is_active: bool = True


@dataclass
class SynapseStats:
    """Statistics about synapse activity."""

    agent_id: str
    connections: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    broadcasts_sent: int = 0
    pending_messages: int = 0
    connected_agents: List[str] = field(default_factory=list)


@runtime_checkable
class SynapseProtocol(Protocol):
    """
    OPUS-311: Inter-agent neural messaging.

    The Nadi - "channels" through which prana (energy/messages) flows.

    Features:
    - Direct agent-to-agent messaging
    - Broadcast to all connected agents
    - Request/response pairing
    - Priority queuing
    - TTL-based message expiration
    """

    @property
    def agent_id(self) -> str:
        """Get the ID of the agent using this synapse."""
        ...

    def connect(self, agent_id: str) -> bool:
        """
        Establish connection to another agent.

        Returns True if connection successful.
        """
        ...

    def disconnect(self, agent_id: str) -> bool:
        """
        Disconnect from an agent.

        Returns True if was connected.
        """
        ...

    def is_connected(self, agent_id: str) -> bool:
        """Check if connected to an agent."""
        ...

    def get_connections(self) -> List[Connection]:
        """Get all active connections."""
        ...

    def send(self, message: SynapseMessage) -> bool:
        """
        Send a message to an agent.

        Returns True if message was queued.
        """
        ...

    def receive(self, timeout_ms: Optional[int] = None) -> Optional[SynapseMessage]:
        """
        Receive the next message from the queue.

        Args:
            timeout_ms: Optional timeout (None = non-blocking)

        Returns:
            Next message or None if queue empty/timeout
        """
        ...

    def receive_all(self) -> List[SynapseMessage]:
        """Receive all pending messages."""
        ...

    def broadcast(self, topic: str, payload: Dict[str, Any]) -> int:
        """
        Broadcast a message to all connected agents.

        Returns number of agents messaged.
        """
        ...

    def subscribe(
        self,
        topic: str,
        handler: Callable[[SynapseMessage], None],
    ) -> str:
        """
        Subscribe to messages on a topic.

        Returns subscription ID.
        """
        ...

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        ...

    def request(
        self,
        receiver: str,
        topic: str,
        payload: Dict[str, Any],
        timeout_ms: int = 5000,
    ) -> Optional[SynapseMessage]:
        """
        Send a request and wait for response.

        Args:
            receiver: Target agent
            topic: Request topic
            payload: Request data
            timeout_ms: How long to wait

        Returns:
            Response message or None if timeout
        """
        ...

    def respond(
        self,
        original: SynapseMessage,
        payload: Dict[str, Any],
    ) -> bool:
        """
        Respond to a request message.

        Uses correlation_id from original.
        """
        ...

    def get_stats(self) -> SynapseStats:
        """Get synapse statistics."""
        ...


class NullSynapse:
    """
    Arjuna Pattern: No-op synapse.

    No connections, all messages dropped.
    Use when synapse service is not available.
    """

    def __init__(self, agent_id: str = "anonymous"):
        self._agent_id = agent_id

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def connect(self, agent_id: str) -> bool:
        return False

    def disconnect(self, agent_id: str) -> bool:
        return False

    def is_connected(self, agent_id: str) -> bool:
        return False

    def get_connections(self) -> List[Connection]:
        return []

    def send(self, message: SynapseMessage) -> bool:
        return False

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
        return SynapseStats(agent_id=self._agent_id)


class LocalSynapse:
    """
    OPUS-311: Local implementation of SynapseProtocol.

    In-process messaging for single-machine deployment.
    Uses a shared message hub for routing.
    """

    # Shared message hub for all local synapses
    _hub: Dict[str, "LocalSynapse"] = {}
    _hub_lock = None  # Set on first use

    @classmethod
    def _get_lock(cls):
        if cls._hub_lock is None:
            import threading

            cls._hub_lock = threading.Lock()
        return cls._hub_lock

    def __init__(self, agent_id: str):
        from collections import deque
        from uuid import uuid4

        self._agent_id = agent_id
        self._connections: Dict[str, Connection] = {}
        self._inbox: deque = deque(maxlen=1000)
        self._subscriptions: Dict[str, Callable] = {}
        self._pending_requests: Dict[str, SynapseMessage] = {}
        self._uuid = uuid4
        self._stats = {
            "sent": 0,
            "received": 0,
            "broadcasts": 0,
        }

        # Register with hub
        with self._get_lock():
            self._hub[agent_id] = self

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def connect(self, agent_id: str) -> bool:
        if agent_id == self._agent_id:
            return False  # Can't connect to self

        if agent_id in self._connections:
            return True  # Already connected

        # Check if target exists in hub
        with self._get_lock():
            if agent_id not in self._hub:
                return False

        self._connections[agent_id] = Connection(agent_id=agent_id)
        return True

    def disconnect(self, agent_id: str) -> bool:
        if agent_id in self._connections:
            del self._connections[agent_id]
            return True
        return False

    def is_connected(self, agent_id: str) -> bool:
        return agent_id in self._connections

    def get_connections(self) -> List[Connection]:
        return list(self._connections.values())

    def send(self, message: SynapseMessage) -> bool:
        if message.is_broadcast:
            self.broadcast(message.topic, message.payload)
            return True

        # Check connection
        if not self.is_connected(message.receiver):
            return False

        # Route via hub
        with self._get_lock():
            target = self._hub.get(message.receiver)
            if target is None:
                return False

            target._deliver(message)
            self._stats["sent"] += 1
            self._connections[message.receiver].messages_sent += 1

        return True

    def _deliver(self, message: SynapseMessage) -> None:
        """Internal: Deliver a message to this synapse."""
        # Check if expired
        if message.is_expired:
            return

        # Check for response to pending request
        if message.message_type == MessageType.RESPONSE and message.correlation_id:
            if message.correlation_id in self._pending_requests:
                self._pending_requests[message.correlation_id] = message
                return

        # Check topic subscriptions
        for sub_id, handler in list(self._subscriptions.items()):
            try:
                handler(message)
            except Exception:
                pass  # Don't let handler errors break delivery

        # Add to inbox
        self._inbox.append(message)
        self._stats["received"] += 1

        # Update connection stats
        if message.sender in self._connections:
            self._connections[message.sender].messages_received += 1

    def receive(self, timeout_ms: Optional[int] = None) -> Optional[SynapseMessage]:
        if not self._inbox:
            if timeout_ms and timeout_ms > 0:
                import time

                time.sleep(timeout_ms / 1000)
            if not self._inbox:
                return None

        return self._inbox.popleft()

    def receive_all(self) -> List[SynapseMessage]:
        messages = list(self._inbox)
        self._inbox.clear()
        return messages

    def broadcast(self, topic: str, payload: Dict[str, Any]) -> int:
        message = SynapseMessage(
            sender=self._agent_id,
            receiver="*",
            topic=topic,
            payload=payload,
            message_type=MessageType.BROADCAST,
        )

        count = 0
        with self._get_lock():
            for agent_id, synapse in self._hub.items():
                if agent_id != self._agent_id and agent_id in self._connections:
                    synapse._deliver(message)
                    count += 1

        self._stats["broadcasts"] += 1
        return count

    def subscribe(
        self,
        topic: str,
        handler: Callable[[SynapseMessage], None],
    ) -> str:
        sub_id = f"{topic}_{self._uuid()}"
        self._subscriptions[sub_id] = lambda m: handler(m) if m.topic == topic else None
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            return True
        return False

    def request(
        self,
        receiver: str,
        topic: str,
        payload: Dict[str, Any],
        timeout_ms: int = 5000,
    ) -> Optional[SynapseMessage]:
        correlation_id = str(self._uuid())

        message = SynapseMessage(
            sender=self._agent_id,
            receiver=receiver,
            topic=topic,
            payload=payload,
            message_type=MessageType.REQUEST,
            correlation_id=correlation_id,
        )

        # Register pending request
        self._pending_requests[correlation_id] = None

        # Send request
        if not self.send(message):
            del self._pending_requests[correlation_id]
            return None

        # Wait for response
        import time

        start = time.time()
        while time.time() - start < timeout_ms / 1000:
            response = self._pending_requests.get(correlation_id)
            if response is not None:
                del self._pending_requests[correlation_id]
                return response
            time.sleep(0.01)

        # Timeout
        del self._pending_requests[correlation_id]
        return None

    def respond(
        self,
        original: SynapseMessage,
        payload: Dict[str, Any],
    ) -> bool:
        if not original.correlation_id:
            return False

        response = SynapseMessage(
            sender=self._agent_id,
            receiver=original.sender,
            topic=original.topic,
            payload=payload,
            message_type=MessageType.RESPONSE,
            correlation_id=original.correlation_id,
        )

        return self.send(response)

    def get_stats(self) -> SynapseStats:
        return SynapseStats(
            agent_id=self._agent_id,
            connections=len(self._connections),
            messages_sent=self._stats["sent"],
            messages_received=self._stats["received"],
            broadcasts_sent=self._stats["broadcasts"],
            pending_messages=len(self._inbox),
            connected_agents=list(self._connections.keys()),
        )

    def __del__(self):
        # Unregister from hub
        with self._get_lock():
            if self._agent_id in self._hub:
                del self._hub[self._agent_id]


def get_synapse_safe(agent_id: str = "anonymous") -> SynapseProtocol:
    """
    Get Synapse via ServiceRegistry with NullSynapse fallback.

    OPUS-311: Use this for guaranteed non-None return.
    """
    try:
        from vibe_core.di import ServiceRegistry

        synapse = ServiceRegistry.get(SynapseProtocol)
        if synapse is not None:
            return synapse
    except ImportError:
        pass

    return NullSynapse(agent_id)
