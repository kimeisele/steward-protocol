"""
CHAT NADI - User ↔ System Communication via PRANA
==================================================

"prāṇa" - The life force, the incoming breath.

PRANA NADI is the channel for User ↔ System communication.
This wraps ChatSubstrateBridge with Nadi transport.

ARCHITECTURE:
=============

    User Input
        ↓
    PranaNadi.receive() ← NadiMessage from UI/CLI
        ↓
    ChatSubstrateBridge.route() → SubstrateRoute
        ↓
    Dispatch to Mahajana via NadiOp.DELEGATE
        ↓
    Response via NadiOp.RECEIVE
        ↓
    PranaNadi.send() → Back to User

ALL CONSTANTS DERIVED FROM SEED.PY:
- Uses NadiType.PRANA (index 0)
- Message buffer from NADI_RESONANCE (72)
- Timeouts from PRANA_DURATION_MS (4000ms)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x45c5169c"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Final, List, Optional
from uuid import uuid4

# Import Nadi infrastructure
# GAD compliance + Nadi + Seed constants
from vibe_core.mahamantra import (
    NADI_RESONANCE,
    NADI_TIMEOUT_MS,
    PRANA_DURATION_MS,
    WORDS,
    GADBase,
    LocalNadi,
    NadiConnection,
    NadiMessage,
    NadiOp,
    NadiPriority,
    NadiProtocol,
    NadiType,
)

# Import ChatSubstrateBridge for routing
from vibe_core.services.chat_substrate_bridge import (
    ChatSubstrateBridge,
    SubstrateRoute,
    get_substrate_bridge,
)

logger = logging.getLogger("CHAT_NADI")


# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Chat session timeout = PRANA_DURATION_MS × WORDS = 4000 × 16 = 64000ms = 64 seconds
CHAT_SESSION_TIMEOUT_MS: Final[int] = PRANA_DURATION_MS * WORDS  # 64000ms

# Max pending chat messages = NADI_RESONANCE = 72
CHAT_MESSAGE_BUFFER: Final[int] = NADI_RESONANCE  # 72

# Verification
assert CHAT_SESSION_TIMEOUT_MS == 64000, "Session timeout = 64 seconds"
assert CHAT_MESSAGE_BUFFER == 72, "Buffer = NADI_RESONANCE"


# =============================================================================
# CHAT MESSAGE - User ↔ System
# =============================================================================


@dataclass
class ChatMessage:
    """
    A chat message between User and System.

    This is the high-level chat abstraction that gets
    converted to/from NadiMessage for transport.
    """

    message_id: str
    session_id: str
    role: str  # "user" or "assistant"
    content: str
    route: Optional[SubstrateRoute] = None  # Set after routing
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_nadi_message(self, source: str, target: str) -> NadiMessage:
        """Convert to NadiMessage for transport."""
        return NadiMessage(
            source=source,
            target=target,
            nadi_type=NadiType.PRANA,
            operation=NadiOp.SEND if self.role == "user" else NadiOp.RECEIVE,
            payload={
                "message_id": self.message_id,
                "session_id": self.session_id,
                "role": self.role,
                "content": self.content,
                "route": {
                    "position": self.route.position,
                    "mahajana": self.route.mahajana,
                    "energy": self.route.energy,
                }
                if self.route
                else None,
                "metadata": self.metadata,
            },
            priority=NadiPriority.RAJAS,
            timestamp=self.timestamp,
        )

    @classmethod
    def from_nadi_message(cls, msg: NadiMessage) -> "ChatMessage":
        """Create ChatMessage from NadiMessage."""
        payload = msg.payload
        return cls(
            message_id=payload.get("message_id", str(uuid4())),
            session_id=payload.get("session_id", "unknown"),
            role=payload.get("role", "user"),
            content=payload.get("content", ""),
            timestamp=msg.timestamp,
            metadata=payload.get("metadata", {}),
        )


# =============================================================================
# CHAT SESSION
# =============================================================================


@dataclass
class ChatSession:
    """
    A chat session tracking conversation state.
    """

    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    routes: List[SubstrateRoute] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Session expired if inactive > timeout."""
        elapsed = (datetime.now() - self.last_activity).total_seconds() * 1000
        return elapsed > CHAT_SESSION_TIMEOUT_MS

    def touch(self) -> None:
        """Update last activity."""
        self.last_activity = datetime.now()


# =============================================================================
# CHAT NADI - The PRANA Channel
# =============================================================================


class ChatNadi(GADBase):
    """
    PRANA Nadi for User ↔ System communication.

    Wraps ChatSubstrateBridge with Nadi transport.
    GAD-000 compliant.

    FLOW:
    1. User sends ChatMessage
    2. ChatNadi routes via ChatSubstrateBridge
    3. Message dispatched to Mahajana
    4. Response comes back
    5. ChatNadi sends response to User
    """

    def __init__(
        self,
        service_id: str = "chat_service",
        bridge: Optional[ChatSubstrateBridge] = None,
    ):
        super().__init__()  # Initialize GADBase

        self._service_id = service_id

        # Create PRANA Nadi for this service
        self._nadi = LocalNadi(
            endpoint_id=f"prana_{service_id}",
            nadi_type=NadiType.PRANA,
        )

        # Use provided bridge or get default
        self._bridge = bridge or get_substrate_bridge()

        # Session tracking
        self._sessions: Dict[str, ChatSession] = {}

        # Message handlers
        self._on_message: Optional[Callable[[ChatMessage], None]] = None
        self._on_route: Optional[Callable[[SubstrateRoute], None]] = None

        # Stats
        self._messages_received = 0
        self._messages_sent = 0
        self._routes_computed = 0

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def service_id(self) -> str:
        return self._service_id

    @property
    def nadi(self) -> NadiProtocol:
        """Access underlying Nadi."""
        return self._nadi

    @property
    def bridge(self) -> ChatSubstrateBridge:
        """Access routing bridge."""
        return self._bridge

    @property
    def active_sessions(self) -> int:
        """Count of active (non-expired) sessions."""
        return sum(1 for s in self._sessions.values() if not s.is_expired)

    # =========================================================================
    # GAD COMPLIANCE
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """GAD Discoverability."""
        return {
            "service": "chat_nadi",
            "mahajana": __mahajana__,
            "position": __position__,
            "genesis": __genesis__,
            "nadi_type": NadiType.PRANA.name,
            "capabilities": [
                "user_message_routing",
                "session_management",
                "mahajana_dispatch",
            ],
            "constants": {
                "session_timeout_ms": CHAT_SESSION_TIMEOUT_MS,
                "message_buffer": CHAT_MESSAGE_BUFFER,
            },
        }

    def get_state(self) -> Dict[str, object]:
        """GAD Observability."""
        return {
            "service_id": self._service_id,
            "active_sessions": self.active_sessions,
            "total_sessions": len(self._sessions),
            "messages_received": self._messages_received,
            "messages_sent": self._messages_sent,
            "routes_computed": self._routes_computed,
            "bridge_inertia": self._bridge.inertia,
            "heartbeat": self.heartbeat.get_summary(),
        }

    def detect_drift(self) -> List[str]:
        """GAD Drift Detection."""
        issues = []

        # Check for expired sessions
        expired = sum(1 for s in self._sessions.values() if s.is_expired)
        if expired > len(self._sessions) // 2:
            issues.append(f"Too many expired sessions: {expired}")

        # Check bridge health
        bridge_drifts = self._bridge.detect_drift()
        issues.extend(bridge_drifts)

        return issues

    def test_tapas(self) -> bool:
        """GAD Tapas: Resource efficiency."""
        # Prune expired sessions
        expired = [sid for sid, s in self._sessions.items() if s.is_expired]
        return len(expired) < len(self._sessions) // 2

    def test_saucam(self) -> bool:
        """GAD Saucam: Connection purity."""
        return self._nadi.nadi_type == NadiType.PRANA

    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================

    def get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(session_id=session_id)
            logger.info(f"📋 New chat session: {session_id}")

        session = self._sessions[session_id]
        session.touch()
        return session

    def close_session(self, session_id: str) -> bool:
        """Close a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"📋 Closed session: {session_id}")
            return True
        return False

    def prune_expired_sessions(self) -> int:
        """Remove expired sessions."""
        expired = [sid for sid, s in self._sessions.items() if s.is_expired]
        for sid in expired:
            del self._sessions[sid]

        if expired:
            logger.info(f"🧹 Pruned {len(expired)} expired sessions")

        return len(expired)

    # =========================================================================
    # MESSAGE HANDLING
    # =========================================================================

    def process_user_message(self, content: str, session_id: str) -> ChatMessage:
        """
        Process a user message through the substrate.

        1. Create ChatMessage
        2. Route through ChatSubstrateBridge
        3. Track in session
        4. Return routed message
        """
        # Get/create session
        session = self.get_or_create_session(session_id)

        # Create message
        message = ChatMessage(
            message_id=f"msg_{uuid4().hex[:8]}",
            session_id=session_id,
            role="user",
            content=content,
        )

        # Route through substrate
        route = self._bridge.route(content)
        message.route = route

        # Update stats
        session.message_count += 1
        session.routes.append(route)
        self._messages_received += 1
        self._routes_computed += 1

        # Trigger callback
        if self._on_route:
            self._on_route(route)

        if self._on_message:
            self._on_message(message)

        logger.info(
            f"💬 User message routed: session={session_id}, mahajana={route.mahajana}, energy={route.energy:.3f}"
        )

        return message

    def send_response(
        self,
        content: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """
        Send a response back to the user.

        Creates an assistant message and sends via Nadi.
        """
        session = self.get_or_create_session(session_id)

        message = ChatMessage(
            message_id=f"msg_{uuid4().hex[:8]}",
            session_id=session_id,
            role="assistant",
            content=content,
            metadata=metadata or {},
        )

        session.message_count += 1
        self._messages_sent += 1

        logger.info(f"💬 Response sent: session={session_id}")

        return message

    # =========================================================================
    # NADI INTEGRATION
    # =========================================================================

    def connect_to_mahajana(self, mahajana_endpoint: str) -> bool:
        """Connect to a Mahajana endpoint for dispatching."""
        return self._nadi.connect(mahajana_endpoint)

    def dispatch_to_mahajana(
        self,
        message: ChatMessage,
        mahajana_endpoint: str,
    ) -> bool:
        """
        Dispatch a routed message to the target Mahajana.

        Converts ChatMessage to NadiMessage and sends via PRANA Nadi.
        """
        if not message.route:
            logger.warning("Cannot dispatch unrouted message")
            return False

        nadi_msg = NadiMessage(
            source=self._nadi.endpoint_id,
            target=mahajana_endpoint,
            nadi_type=NadiType.PRANA,
            operation=NadiOp.DELEGATE,
            payload={
                "type": "chat_dispatch",
                "message": message.to_nadi_message(
                    self._nadi.endpoint_id,
                    mahajana_endpoint,
                ).payload,
                "route": {
                    "position": message.route.position,
                    "mahajana": message.route.mahajana,
                    "quarter": message.route.quarter,
                    "energy": message.route.energy,
                    "manifests": message.route.manifests,
                },
            },
        )

        return self._nadi.send(nadi_msg)

    def receive_from_nadi(self) -> List[ChatMessage]:
        """
        Receive pending messages from Nadi.

        Converts NadiMessages to ChatMessages.
        """
        messages = []

        for nadi_msg in self._nadi.receive_all():
            if nadi_msg.operation in (NadiOp.SEND, NadiOp.RECEIVE):
                chat_msg = ChatMessage.from_nadi_message(nadi_msg)
                messages.append(chat_msg)

                if self._on_message:
                    self._on_message(chat_msg)

        return messages

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def set_on_message(self, callback: Callable[[ChatMessage], None]) -> None:
        """Set callback for incoming messages."""
        self._on_message = callback

    def set_on_route(self, callback: Callable[[SubstrateRoute], None]) -> None:
        """Set callback for computed routes."""
        self._on_route = callback

    # =========================================================================
    # HEARTBEAT
    # =========================================================================

    def pulse(self) -> bool:
        """
        Send heartbeat and prune expired sessions.
        """
        self.prune_expired_sessions()
        self._nadi.pulse()
        self.chant()
        return True

    # =========================================================================
    # STATS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "service_id": self._service_id,
            "active_sessions": self.active_sessions,
            "total_sessions": len(self._sessions),
            "messages_received": self._messages_received,
            "messages_sent": self._messages_sent,
            "routes_computed": self._routes_computed,
            "nadi_stats": self._nadi.get_stats().__dict__,
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_chat_nadi(service_id: str = "chat_service") -> ChatNadi:
    """
    Get ChatNadi through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        Raw ChatNadi → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees all Nadi operations)
    - NAGA profiling (Chitragupta tracks message latency)
    - NAGA isolation (Kaliya handles transport errors)
    """
    from vibe_core.di import ServiceRegistry

    # Use ChatNadi type as protocol (GADBase compliant)
    existing = ServiceRegistry.get(ChatNadi)
    if existing is not None:
        return existing

    # Create new instance
    instance = ChatNadi(service_id)

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(ChatNadi, instance)
    logger.info("✅ ChatNadi registered via ServiceRegistry (WIRED + NAGA-observed)")

    return ServiceRegistry.get(ChatNadi)  # type: ignore


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "CHAT_SESSION_TIMEOUT_MS",
    "CHAT_MESSAGE_BUFFER",
    # Data structures
    "ChatMessage",
    "ChatSession",
    # Service
    "ChatNadi",
    # Factory
    "get_chat_nadi",
]
