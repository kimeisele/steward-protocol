"""
CHAT PROTOCOL - The Conversation Protocol
==========================================

"Every conversation is a chance for connection."

PROTOCOL-FIRST DESIGN:
This defines the CONTRACT for chat operations.
Implementations must fulfill this contract.

MANTRA MAPPING:
    Chat = IntentType.CHAT → MantraOpCode.EXTEND_CAP
    Phase: SERVE (3)
    Word: RAMA
    Mahajana: JANAKA (legacy) / PRAHLADA (vyuha)

THE GAP THIS FILLS:
    Before: ChatCommand → BaseCommand (no Mantra connection)
    After:  ChatCommand → ChatProtocol → ICliCommand → MantraOpCode

STRICT TYPING (NO ANY):
Per PROMPT.md §IV.1 - All types explicit.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0x7806582e"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol, Union, runtime_checkable

# MantraOpCode for chat
from vibe_core.mahamantra.substrate.opcode import MantraOpCode

# Cognitive types
from vibe_core.protocols.cognition import IntentType, CognitiveResult


# =============================================================================
# STRICT TYPES (NO ANY)
# =============================================================================


class ChatMode(str, Enum):
    """Mode of chat interaction."""

    DIRECT = "direct"  # Direct LLM response
    ROUTED = "routed"  # Route to Mahajana
    SYSCALL = "syscall"  # Execute syscall
    QUERY = "query"  # Query data


@dataclass(frozen=True)
class ChatMessage:
    """
    A chat message (input or output).

    Strict typing - no Any allowed.
    """

    content: str
    role: str  # "user", "assistant", "system"
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional metadata (all typed)
    session_id: Optional[str] = None
    message_id: Optional[str] = None

    # Mantra connection
    opcode: Optional[str] = None  # MantraOpCode value if routed
    mahajana: Optional[str] = None  # Mahajana if routed


@dataclass
class ChatResponse:
    """
    Response from chat operation.

    Strictly typed - no Any.
    """

    success: bool
    message: ChatMessage

    # Routing info
    mode: ChatMode = ChatMode.DIRECT
    intent_type: Optional[IntentType] = None

    # If routed through Mantra
    opcode: Optional[str] = None
    mahajana: Optional[str] = None
    confidence: float = 0.0

    # Error info (if any)
    error: Optional[str] = None
    retry_allowed: bool = True


@dataclass(frozen=True)
class ChatContext:
    """
    Context for chat operations.

    Contains session info, history, and sovereign identity.
    """

    session_id: str

    # Conversation history (typed messages)
    history: List[ChatMessage] = field(default_factory=list)

    # The 37th - Sovereign Identity
    sovereign_id: Optional[str] = None
    sovereign_signed: bool = False

    # Available capabilities
    capabilities: List[str] = field(default_factory=list)


# =============================================================================
# CHAT PROTOCOL (THE CONTRACT)
# =============================================================================


@runtime_checkable
class ChatProtocol(Protocol):
    """
    Protocol for chat operations.

    MANTRA CONNECTION:
    - opcode: EXEC_SERVICE (Position 9, Phase SERVE, Word RAMA)
    - Routes through JANAKA/PRAHLADA Mahajana

    GAD-000 COMPLIANCE:
    - Discoverability: chat.capabilities()
    - Observability: chat.status()
    - Parseability: ChatResponse.error has typed error codes
    - Composability: Can chain with other CLI commands
    - Idempotency: Same message + context = same response
    - Recoverability: Always returns ChatResponse (never throws)
    """

    # ==========================================================================
    # MANTRA PROPERTIES (ICliCommand compliance)
    # ==========================================================================

    @property
    def opcode(self) -> str:
        """MantraOpCode for chat: EXEC_SERVICE."""
        ...

    @property
    def phase(self) -> str:
        """Phase: SERVE (3)."""
        ...

    @property
    def word(self) -> str:
        """Mahamantra word: RAMA."""
        ...

    @property
    def position(self) -> int:
        """Position in Mahamantra: 9."""
        ...

    # ==========================================================================
    # CHAT OPERATIONS
    # ==========================================================================

    async def chat(self, message: str, context: ChatContext) -> ChatResponse:
        """
        Process a chat message.

        THE FLOW:
        1. Parse message → IntentType
        2. If CHAT intent → direct LLM response
        3. If other intent → route through Mantra

        Args:
            message: User's message
            context: Chat context with session and history

        Returns:
            ChatResponse (never throws)
        """
        ...

    async def chat_with_routing(self, message: str, context: ChatContext, force_routing: bool = False) -> ChatResponse:
        """
        Chat with explicit Mahajana routing.

        If force_routing=True, always route through SemanticRouter
        even for simple chat messages.
        """
        ...

    # ==========================================================================
    # GAD-000 COMPLIANCE
    # ==========================================================================

    def capabilities(self) -> List[str]:
        """
        Discoverability: What can this chat do?

        Returns list of capabilities:
        - "direct_response": Can respond to chat
        - "syscall_routing": Can route to syscalls
        - "mahajana_routing": Can route to Mahajanas
        - "context_aware": Uses conversation history
        """
        ...

    def status(self) -> Dict[str, Union[str, bool, int]]:
        """
        Observability: Current chat system status.

        Returns:
            {
                "available": bool,
                "mode": str,
                "sessions_active": int,
                "mahajana_connected": bool,
            }
        """
        ...


# =============================================================================
# CONSTANTS
# =============================================================================

# Chat's Mantra identity
CHAT_OPCODE = MantraOpCode.EXTEND_CAP
CHAT_PHASE = "SERVE"
CHAT_WORD = "RAMA"
CHAT_POSITION = 9

# Default capabilities
DEFAULT_CHAT_CAPABILITIES = [
    "direct_response",
    "syscall_routing",
    "mahajana_routing",
    "context_aware",
]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol
    "ChatProtocol",
    # Types
    "ChatMode",
    "ChatMessage",
    "ChatResponse",
    "ChatContext",
    # Constants
    "CHAT_OPCODE",
    "CHAT_PHASE",
    "CHAT_WORD",
    "CHAT_POSITION",
    "DEFAULT_CHAT_CAPABILITIES",
]
