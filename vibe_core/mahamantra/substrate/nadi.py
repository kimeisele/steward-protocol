"""
NADI - Universal Cognitive Connection Protocol (नाडी)
======================================================

"prāṇasya nāḍī saṁcāraḥ" - "Prana flows through the Nadis."

NADI (नाडी) = Channel, Conduit, Tube
The pathways through which prana (life force/energy/messages) flows.

DERIVED FROM SEED.PY - NO HARDCODING:
- NADI_RESONANCE = 72 = JIVA_CYCLE / SHARANAGATI = 432 / 6
- 300 Nadi cycles per day (COSMIC_FRAME / 72 = 21600 / 72)
- PRANA_DURATION_MS = 4000ms (the breath interval)
- TICK_INTERVAL_MS = 250ms (the quantum of time)

CONNECTION TYPES (Universal - not just Agent-to-Agent):
1. USER ↔ SYSTEM    (Chat/UI)
2. AGENT ↔ AGENT    (Synapse - legacy path)
3. AGENT ↔ MAHAJANA (Routing/Dispatch)
4. SERVICE ↔ SERVICE (Internal IPC)
5. KERNEL ↔ SHADOW   (TaskKernel integration)

The 9 NADI OPERATIONS map to NavaBhakti:
1. SRAVANAM (Hearing)     → RECEIVE
2. KIRTANAM (Chanting)    → SEND
3. SMARANAM (Remembering) → CACHE
4. PADA_SEVANAM (Serving) → PROCESS
5. ARCANAM (Worshiping)   → VALIDATE
6. VANDANAM (Praying)     → REQUEST
7. DASYAM (Servitude)     → DELEGATE
8. SAKHYAM (Friendship)   → CONNECT
9. ATMA_NIVEDANAM (Surrender) → COMMIT
"""
from vibe_core.mahamantra.protocols._seed import (GITA_CHAPTERS, HALVES, KSETRAJNA, PANCHA, QUARTERS, TRINITY)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = KSETRAJNA
__genesis__ = "0x646fe98f"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum, StrEnum
from typing import Any, Callable, Dict, Final, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._gad import GADBase

# =============================================================================
# IMPORT FROM SEED (SSOT - THE LAW)
# =============================================================================
from vibe_core.mahamantra.substrate.seed import (
    COSMIC_FRAME,  # 21600 - Daily resolution
    MALA,  # 108 - Full cycle
    NADI_RESONANCE,  # 72 - The channel frequency
    NAVA,  # 9 - The operations count
    PRANA_DURATION_MS,  # 4000 - Breath interval
    SHARANAGATI,  # 6 - Connection integrity
    TICK_INTERVAL_MS,  # 250 - Time quantum
    NavaBhakti,  # The 9 processes
)

# =============================================================================
# DERIVED CONSTANTS - All from NADI_RESONANCE (72)
# =============================================================================

# Channel capacity = NADI_RESONANCE (72 concurrent connections)
NADI_CAPACITY: Final[int] = NADI_RESONANCE  # 72

# Message buffer = NADI_RESONANCE × 2 (144 pending messages)
NADI_BUFFER_SIZE: Final[int] = NADI_RESONANCE * HALVES  # 144

# Heartbeat interval = TICK_INTERVAL_MS × NADI_RESONANCE / 18
# = 250 × 72 / 18 = 250 × 4 = 1000ms = 1 second
NADI_HEARTBEAT_MS: Final[int] = (TICK_INTERVAL_MS * NADI_RESONANCE) // GITA_CHAPTERS  # 1000ms

# Connection timeout = PRANA_DURATION_MS × SHARANAGATI
# = 4000 × 6 = 24000ms = 24 seconds (one Kshetra of time)
NADI_TIMEOUT_MS: Final[int] = PRANA_DURATION_MS * SHARANAGATI  # 24000ms

# Daily cycles = COSMIC_FRAME / NADI_RESONANCE = 21600 / 72 = 300
NADI_DAILY_CYCLES: Final[int] = COSMIC_FRAME // NADI_RESONANCE  # 300

# Full mala cycle = MALA messages before rotation = 108
NADI_MALA_CYCLE: Final[int] = MALA  # 108

# Verification: All derived from 72
assert NADI_CAPACITY == 72, "Capacity must be NADI_RESONANCE"
assert NADI_BUFFER_SIZE == 144, "Buffer = 72 × 2 = 144"
assert NADI_HEARTBEAT_MS == 1000, "Heartbeat = 1 second"
assert NADI_TIMEOUT_MS == 24000, "Timeout = 24 seconds"
assert NADI_DAILY_CYCLES == 300, "300 Nadi cycles per day"


# =============================================================================
# NADI TYPES - The 5 Connection Categories (Pancha)
# =============================================================================


class NadiType(IntEnum):
    """
    The 5 types of Nadi connections.

    Maps to the 5 Pranas (Pancha Prana):
    - PRANA    = User ↔ System (breath = life force = user input)
    - APANA    = Agent ↔ Agent (downward = peer-to-peer)
    - VYANA    = Service ↔ Service (pervasive = infrastructure)
    - UDANA    = Agent ↔ Mahajana (upward = escalation/routing)
    - SAMANA   = Kernel ↔ Shadow (balancing = task distribution)
    """

    PRANA = 0  # User ↔ System (Chat/UI)
    APANA = KSETRAJNA  # Agent ↔ Agent (Synapse compatibility)
    VYANA = HALVES  # Service ↔ Service (IPC)
    UDANA = TRINITY  # Agent ↔ Mahajana (Routing)
    SAMANA = QUARTERS  # Kernel ↔ Shadow (TaskKernel)


NADI_TYPE_NAMES: Final[Tuple[str, ...]] = (
    "prana",  # User connection
    "apana",  # Agent connection
    "vyana",  # Service connection
    "udana",  # Mahajana routing
    "samana",  # Kernel dispatch
)

assert len(NadiType) == PANCHA, "Pancha Nadi types"


# =============================================================================
# NADI OPERATIONS - The 9 Actions (Navadha)
# =============================================================================


class NadiOp(StrEnum):
    """
    The 9 Nadi operations mapped from NavaBhakti.

    Each operation has a corresponding devotional process.
    """

    RECEIVE = "receive"  # SRAVANAM - Hearing
    SEND = "send"  # KIRTANAM - Chanting
    CACHE = "cache"  # SMARANAM - Remembering
    PROCESS = "process"  # PADA_SEVANAM - Serving
    VALIDATE = "validate"  # ARCANAM - Worshiping
    REQUEST = "request"  # VANDANAM - Praying
    DELEGATE = "delegate"  # DASYAM - Servitude
    CONNECT = "connect"  # SAKHYAM - Friendship
    COMMIT = "commit"  # ATMA_NIVEDANAM - Surrender


# Map NadiOp to NavaBhakti
NADI_OP_TO_BHAKTI: Final[Dict[NadiOp, NavaBhakti]] = {
    NadiOp.RECEIVE: NavaBhakti.SRAVANAM,
    NadiOp.SEND: NavaBhakti.KIRTANAM,
    NadiOp.CACHE: NavaBhakti.SMARANAM,
    NadiOp.PROCESS: NavaBhakti.PADA_SEVANAM,
    NadiOp.VALIDATE: NavaBhakti.ARCANAM,
    NadiOp.REQUEST: NavaBhakti.VANDANAM,
    NadiOp.DELEGATE: NavaBhakti.DASYAM,
    NadiOp.CONNECT: NavaBhakti.SAKHYAM,
    NadiOp.COMMIT: NavaBhakti.ATMA_NIVEDANAM,
}

assert len(NadiOp) == NAVA, f"Navadha: 9 operations, got {len(NadiOp)}"


# =============================================================================
# NADI PRIORITY - Message Urgency (Guna-based)
# =============================================================================


class NadiPriority(IntEnum):
    """
    Priority levels based on Gunas.

    - TAMAS (0)  = Background, can wait
    - RAJAS (1)  = Normal, active processing
    - SATTVA (2) = Important, should process soon
    - SUDDHA (3) = Pure/Critical, immediate processing
    """

    TAMAS = 0  # Background
    RAJAS = KSETRAJNA  # Normal
    SATTVA = HALVES  # Important
    SUDDHA = TRINITY  # Critical


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class NadiMessage:
    """
    A message flowing through a Nadi channel.

    The prana (energy) that flows through the nadi (channel).
    """

    source: str  # Sender ID
    target: str  # Receiver ID ("*" = broadcast)
    nadi_type: NadiType  # Type of connection
    operation: NadiOp  # What operation
    payload: Dict[str, object] = field(default_factory=dict)
    priority: NadiPriority = NadiPriority.RAJAS
    correlation_id: Optional[str] = None  # For request/response
    timestamp: datetime = field(default_factory=datetime.now)
    ttl_ms: int = NADI_TIMEOUT_MS  # Default 24 seconds

    @property
    def is_broadcast(self) -> bool:
        return self.target == "*"

    @property
    def is_expired(self) -> bool:
        if self.ttl_ms <= 0:
            return False
        return datetime.now() > self.timestamp + timedelta(milliseconds=self.ttl_ms)

    @property
    def bhakti(self) -> NavaBhakti:
        """The devotional process this operation represents."""
        return NADI_OP_TO_BHAKTI[self.operation]


@dataclass
class NadiConnection:
    """
    A connection between two endpoints.

    The actual nadi (channel) through which prana flows.
    """

    connection_id: str
    source: str
    target: str
    nadi_type: NadiType
    established_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    messages_sent: int = 0
    messages_received: int = 0
    is_active: bool = True

    @property
    def age_ms(self) -> int:
        """Time since connection was established."""
        return int((datetime.now() - self.established_at).total_seconds() * 1000)

    @property
    def idle_ms(self) -> int:
        """Time since last activity."""
        return int((datetime.now() - self.last_activity).total_seconds() * 1000)

    @property
    def is_stale(self) -> bool:
        """Connection is stale if idle > timeout."""
        return self.idle_ms > NADI_TIMEOUT_MS


@dataclass
class NadiStats:
    """Statistics for a Nadi endpoint."""

    endpoint_id: str
    nadi_type: NadiType
    connections: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    messages_pending: int = 0
    connected_endpoints: List[str] = field(default_factory=list)

    # Derived metrics
    @property
    def resonance_ratio(self) -> float:
        """How close to NADI_RESONANCE (72) are we?"""
        if self.connections == 0:
            return 0.0
        return min(1.0, self.connections / NADI_RESONANCE)

    @property
    def mala_progress(self) -> float:
        """Progress through current mala cycle (108 messages)."""
        total = self.messages_sent + self.messages_received
        return (total % NADI_MALA_CYCLE) / NADI_MALA_CYCLE


# =============================================================================
# NADI PROTOCOL - The Interface
# =============================================================================


@runtime_checkable
class NadiProtocol(Protocol):
    """
    Universal Nadi Protocol - The cognitive connection interface.

    Implements all 9 operations (Navadha) for any connection type (Pancha).
    """

    @property
    def endpoint_id(self) -> str:
        """This endpoint's identifier."""
        ...

    @property
    def nadi_type(self) -> NadiType:
        """The type of Nadi this endpoint represents."""
        ...

    # SAKHYAM (CONNECT) - Establish/break connections
    def connect(self, target: str) -> bool:
        """Establish connection to target. Returns True if successful."""
        ...

    def disconnect(self, target: str) -> bool:
        """Disconnect from target. Returns True if was connected."""
        ...

    def is_connected(self, target: str) -> bool:
        """Check if connected to target."""
        ...

    def get_connections(self) -> List[NadiConnection]:
        """Get all active connections."""
        ...

    # KIRTANAM (SEND) - Outbound messages
    def send(self, message: NadiMessage) -> bool:
        """Send a message. Returns True if queued."""
        ...

    def broadcast(self, operation: NadiOp, payload: Dict[str, object]) -> int:
        """Broadcast to all connections. Returns count sent."""
        ...

    # SRAVANAM (RECEIVE) - Inbound messages
    def receive(self, timeout_ms: Optional[int] = None) -> Optional[NadiMessage]:
        """Receive next message. None if empty/timeout."""
        ...

    def receive_all(self) -> List[NadiMessage]:
        """Receive all pending messages."""
        ...

    # VANDANAM (REQUEST) - Request/response pattern
    def request(
        self,
        target: str,
        operation: NadiOp,
        payload: Dict[str, object],
        timeout_ms: int = NADI_TIMEOUT_MS,
    ) -> Optional[NadiMessage]:
        """Send request and wait for response."""
        ...

    def respond(
        self,
        original: NadiMessage,
        payload: Dict[str, object],
    ) -> bool:
        """Respond to a request."""
        ...

    # DASYAM (DELEGATE) - Subscription pattern
    def subscribe(
        self,
        operation: NadiOp,
        handler: Callable[[NadiMessage], None],
    ) -> str:
        """Subscribe to operation. Returns subscription ID."""
        ...

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe. Returns True if was subscribed."""
        ...

    # ARCANAM (VALIDATE) - Health check
    def pulse(self) -> bool:
        """Send heartbeat pulse, returns True if healthy."""
        ...

    def get_stats(self) -> NadiStats:
        """Get endpoint statistics."""
        ...


# =============================================================================
# NULL NADI - Arjuna Pattern (No-op fallback)
# =============================================================================


class NullNadi:
    """
    Arjuna Pattern: No-op Nadi.

    All operations are safe but do nothing.
    Use when Nadi service is unavailable.
    """

    def __init__(
        self,
        endpoint_id: str = "null",
        nadi_type: NadiType = NadiType.PRANA,
    ):
        self._endpoint_id = endpoint_id
        self._nadi_type = nadi_type

    @property
    def endpoint_id(self) -> str:
        return self._endpoint_id

    @property
    def nadi_type(self) -> NadiType:
        return self._nadi_type

    def connect(self, target: str) -> bool:
        return False

    def disconnect(self, target: str) -> bool:
        return False

    def is_connected(self, target: str) -> bool:
        return False

    def get_connections(self) -> List[NadiConnection]:
        return []

    def send(self, message: NadiMessage) -> bool:
        return False

    def broadcast(self, operation: NadiOp, payload: Dict[str, object]) -> int:
        return 0

    def receive(self, timeout_ms: Optional[int] = None) -> Optional[NadiMessage]:
        return None

    def receive_all(self) -> List[NadiMessage]:
        return []

    def request(
        self,
        target: str,
        operation: NadiOp,
        payload: Dict[str, object],
        timeout_ms: int = NADI_TIMEOUT_MS,
    ) -> Optional[NadiMessage]:
        return None

    def respond(self, original: NadiMessage, payload: Dict[str, object]) -> bool:
        return False

    def subscribe(
        self,
        operation: NadiOp,
        handler: Callable[[NadiMessage], None],
    ) -> str:
        return "null-subscription"

    def unsubscribe(self, subscription_id: str) -> bool:
        return False

    def pulse(self) -> bool:
        return True  # Null is always "healthy"

    def get_stats(self) -> NadiStats:
        return NadiStats(
            endpoint_id=self._endpoint_id,
            nadi_type=self._nadi_type,
        )


# =============================================================================
# LOCAL NADI - In-process implementation (GAD-compliant)
# =============================================================================


class LocalNadi(GADBase):
    """
    Local Nadi implementation with GAD-000 compliance.

    In-process messaging using shared hub.
    Thread-safe with proper locking.
    """

    # Shared hub for all local Nadis
    _hub: Dict[str, "LocalNadi"] = {}
    _hub_lock = None

    @classmethod
    def _get_lock(cls):
        if cls._hub_lock is None:
            import threading

            cls._hub_lock = threading.Lock()
        return cls._hub_lock

    def __init__(
        self,
        endpoint_id: str,
        nadi_type: NadiType = NadiType.PRANA,
    ):
        super().__init__()  # Initialize GADBase (MantraHeartbeat)

        from collections import deque
        from uuid import uuid4

        self._endpoint_id = endpoint_id
        self._nadi_type = nadi_type
        self._connections: Dict[str, NadiConnection] = {}
        self._inbox: deque = deque(maxlen=NADI_BUFFER_SIZE)
        self._subscriptions: Dict[str, Tuple[NadiOp, Callable]] = {}
        self._pending_requests: Dict[str, Optional[NadiMessage]] = {}
        self._uuid = uuid4
        self._stats = {"sent": 0, "received": 0}

        # Register with hub
        with self._get_lock():
            self._hub[endpoint_id] = self

    @property
    def endpoint_id(self) -> str:
        return self._endpoint_id

    @property
    def nadi_type(self) -> NadiType:
        return self._nadi_type

    # =========================================================================
    # GAD COMPLIANCE METHODS
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """GAD Discoverability: What am I?"""
        return {
            "service": "local_nadi",
            "mahajana": __mahajana__,
            "position": __position__,
            "genesis": __genesis__,
            "nadi_type": self._nadi_type.name,
            "capabilities": [op.value for op in NadiOp],
            "constants": {
                "capacity": NADI_CAPACITY,
                "buffer_size": NADI_BUFFER_SIZE,
                "heartbeat_ms": NADI_HEARTBEAT_MS,
                "timeout_ms": NADI_TIMEOUT_MS,
            },
        }

    def get_state(self) -> Dict[str, object]:
        """GAD Observability: What is my state?"""
        return {
            "endpoint_id": self._endpoint_id,
            "nadi_type": self._nadi_type.name,
            "connections": len(self._connections),
            "pending_messages": len(self._inbox),
            "subscriptions": len(self._subscriptions),
            "stats": self._stats.copy(),
            "heartbeat": self.heartbeat.get_summary(),
        }

    def detect_drift(self) -> List[str]:
        """GAD: Detect any configuration drift."""
        issues = []

        # Check connection count against capacity
        if len(self._connections) > NADI_CAPACITY:
            issues.append(f"Connections ({len(self._connections)}) exceed NADI_CAPACITY ({NADI_CAPACITY})")

        # Check for stale connections
        stale_count = sum(KSETRAJNA for c in self._connections.values() if c.is_stale)
        if stale_count > 0:
            issues.append(f"{stale_count} stale connections detected")

        # Check inbox overflow
        if len(self._inbox) >= NADI_BUFFER_SIZE:
            issues.append(f"Inbox at capacity ({NADI_BUFFER_SIZE})")

        return issues

    def test_tapas(self) -> bool:
        """GAD Tapas: Test resource efficiency."""
        # Check we're not wasting resources on stale connections
        stale = sum(KSETRAJNA for c in self._connections.values() if c.is_stale)
        return stale <= len(self._connections) // HALVES

    def test_saucam(self) -> bool:
        """GAD Saucam: Test connection purity."""
        # Check all connections are properly typed
        for conn in self._connections.values():
            if conn.nadi_type != self._nadi_type:
                return False
        return True

    # =========================================================================
    # SAKHYAM (CONNECT) - Connection management
    # =========================================================================

    def connect(self, target: str) -> bool:
        if target == self._endpoint_id:
            return False

        if target in self._connections:
            return True

        if len(self._connections) >= NADI_CAPACITY:
            return False

        with self._get_lock():
            if target not in self._hub:
                return False

        conn_id = f"{self._endpoint_id}→{target}"
        self._connections[target] = NadiConnection(
            connection_id=conn_id,
            source=self._endpoint_id,
            target=target,
            nadi_type=self._nadi_type,
        )
        return True

    def disconnect(self, target: str) -> bool:
        if target in self._connections:
            del self._connections[target]
            return True
        return False

    def is_connected(self, target: str) -> bool:
        return target in self._connections

    def get_connections(self) -> List[NadiConnection]:
        return list(self._connections.values())

    # =========================================================================
    # KIRTANAM (SEND) - Outbound
    # =========================================================================

    def send(self, message: NadiMessage) -> bool:
        if message.is_broadcast:
            self.broadcast(message.operation, message.payload)
            return True

        if not self.is_connected(message.target):
            return False

        with self._get_lock():
            target_nadi = self._hub.get(message.target)
            if target_nadi is None:
                return False

            target_nadi._deliver(message)
            self._stats["sent"] += KSETRAJNA
            self._connections[message.target].messages_sent += KSETRAJNA
            self._connections[message.target].last_activity = datetime.now()

        return True

    def broadcast(self, operation: NadiOp, payload: Dict[str, object]) -> int:
        message = NadiMessage(
            source=self._endpoint_id,
            target="*",
            nadi_type=self._nadi_type,
            operation=operation,
            payload=payload,
        )

        count = 0
        with self._get_lock():
            for target_id in list(self._connections.keys()):
                target_nadi = self._hub.get(target_id)
                if target_nadi:
                    target_nadi._deliver(message)
                    count += KSETRAJNA

        self._stats["sent"] += count
        return count

    def _deliver(self, message: NadiMessage) -> None:
        """Internal: Deliver message to this endpoint."""
        if message.is_expired:
            return

        # Check for response to pending request
        if message.correlation_id and message.operation == NadiOp.RECEIVE:
            if message.correlation_id in self._pending_requests:
                self._pending_requests[message.correlation_id] = message
                return

        # Fire subscriptions
        for sub_id, (op, handler) in list(self._subscriptions.items()):
            if message.operation == op:
                try:
                    handler(message)
                except Exception as _exc:
                    logger.exception("Unexpected error: %s", _exc)

        # Queue in inbox
        self._inbox.append(message)
        self._stats["received"] += KSETRAJNA

        # Update connection stats
        if message.source in self._connections:
            self._connections[message.source].messages_received += KSETRAJNA
            self._connections[message.source].last_activity = datetime.now()

    # =========================================================================
    # SRAVANAM (RECEIVE) - Inbound
    # =========================================================================

    def receive(self, timeout_ms: Optional[int] = None) -> Optional[NadiMessage]:
        if not self._inbox:
            if timeout_ms and timeout_ms > 0:
                import time

                time.sleep(timeout_ms / 1000)
            if not self._inbox:
                return None
        return self._inbox.popleft()

    def receive_all(self) -> List[NadiMessage]:
        messages = list(self._inbox)
        self._inbox.clear()
        return messages

    # =========================================================================
    # VANDANAM (REQUEST) - Request/Response
    # =========================================================================

    def request(
        self,
        target: str,
        operation: NadiOp,
        payload: Dict[str, object],
        timeout_ms: int = NADI_TIMEOUT_MS,
    ) -> Optional[NadiMessage]:
        correlation_id = str(self._uuid())

        message = NadiMessage(
            source=self._endpoint_id,
            target=target,
            nadi_type=self._nadi_type,
            operation=operation,
            payload=payload,
            correlation_id=correlation_id,
        )

        self._pending_requests[correlation_id] = None

        if not self.send(message):
            del self._pending_requests[correlation_id]
            return None

        import time

        start = time.time()
        while time.time() - start < timeout_ms / 1000:
            response = self._pending_requests.get(correlation_id)
            if response is not None:
                del self._pending_requests[correlation_id]
                return response
            time.sleep(0.01)

        del self._pending_requests[correlation_id]
        return None

    def respond(self, original: NadiMessage, payload: Dict[str, object]) -> bool:
        if not original.correlation_id:
            return False

        response = NadiMessage(
            source=self._endpoint_id,
            target=original.source,
            nadi_type=self._nadi_type,
            operation=NadiOp.RECEIVE,
            payload=payload,
            correlation_id=original.correlation_id,
        )
        return self.send(response)

    # =========================================================================
    # DASYAM (DELEGATE) - Subscriptions
    # =========================================================================

    def subscribe(
        self,
        operation: NadiOp,
        handler: Callable[[NadiMessage], None],
    ) -> str:
        sub_id = f"{operation.value}_{self._uuid()}"
        self._subscriptions[sub_id] = (operation, handler)
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            return True
        return False

    # =========================================================================
    # ARCANAM (VALIDATE) - Health
    # =========================================================================
    # ARCANAM (VALIDATE) - Health
    # =========================================================================

    def pulse(self) -> bool:
        """Send heartbeat pulse, prune stale connections."""
        # Prune stale connections
        stale = [t for t, c in self._connections.items() if c.is_stale]
        for target in stale:
            self.disconnect(target)

        # Also chant to keep GADBase heartbeat alive
        self.chant()
        return True

    def get_stats(self) -> NadiStats:
        return NadiStats(
            endpoint_id=self._endpoint_id,
            nadi_type=self._nadi_type,
            connections=len(self._connections),
            messages_sent=self._stats["sent"],
            messages_received=self._stats["received"],
            messages_pending=len(self._inbox),
            connected_endpoints=list(self._connections.keys()),
        )

    def __del__(self):
        with self._get_lock():
            if self._endpoint_id in self._hub:
                del self._hub[self._endpoint_id]


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_nadi(
    endpoint_id: str,
    nadi_type: NadiType = NadiType.PRANA,
    fallback_to_null: bool = True,
) -> NadiProtocol:
    """
    Get a Nadi instance.

    Args:
        endpoint_id: Unique identifier for this endpoint
        nadi_type: Type of Nadi connection
        fallback_to_null: If True, return NullNadi on failure

    Returns:
        NadiProtocol implementation (LocalNadi or NullNadi)
    """
    try:
        return LocalNadi(endpoint_id, nadi_type)
    except Exception:
        if fallback_to_null:
            return NullNadi(endpoint_id, nadi_type)
        raise


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "NADI_CAPACITY",
    "NADI_BUFFER_SIZE",
    "NADI_HEARTBEAT_MS",
    "NADI_TIMEOUT_MS",
    "NADI_DAILY_CYCLES",
    "NADI_MALA_CYCLE",
    # Enums
    "NadiType",
    "NADI_TYPE_NAMES",
    "NadiOp",
    "NADI_OP_TO_BHAKTI",
    "NadiPriority",
    # Data structures
    "NadiMessage",
    "NadiConnection",
    "NadiStats",
    # Protocol
    "NadiProtocol",
    # Implementations
    "NullNadi",
    "LocalNadi",
    # Factory
    "get_nadi",
]
