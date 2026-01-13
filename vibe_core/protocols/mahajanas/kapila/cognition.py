"""
COGNITIVE PROTOCOLS - Kapila's Analytical Domain
=================================================

Owner: KAPILA (Analysis/Sankhya)
LOTUS_POSITION: 6 (DHARMA Quarter, Worker 2)

"Lord Kapila - The Founder of Sankhya.
 His analytical philosophy leads to devotion, not dry speculation.
 The cognitive kernel THINKS through Kapila's analytical framework."

MIGRATED FROM: vibe_core.protocols.cognition (legacy location)

This module contains:
- CognitiveKernelProtocol (tick + think)
- OperatorCognitiveProtocol (process_intent + generate_response)
- Supporting types (IntentType, CognitiveResult, CognitiveContext)

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xf50dc335"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.KAPILA
LOTUS_POSITION: Final[int] = 6  # DHARMA Quarter, Worker 2
LOTUS_QUARTER: Final[str] = "dharma"


# =============================================================================
# WATERTIGHT TYPES (No Any!)
# =============================================================================


class IntentType(str, Enum):
    """Type of intent detected from natural language."""

    CHAT = "chat"          # Conversational, needs LLM response
    EXECUTE = "execute"    # Action, needs syscall execution
    QUERY = "query"        # Information retrieval, needs data lookup
    ROUTE = "route"        # Delegate to specific agent/tool


class SyscallParams(TypedDict, total=False):
    """
    WATERTIGHT syscall parameters.
    Replaces Dict[str, Any] in CognitiveResult.
    """
    agent_id: str
    target_id: str
    message: str
    task_name: str
    priority: str
    timeout_ms: int
    args_json: str  # Serialized args for complex params


class QueryResult(TypedDict, total=False):
    """
    WATERTIGHT query result.
    Replaces Dict[str, Any] in CognitiveResult.
    """
    result_type: str
    result_value: str
    result_count: int
    has_more: bool
    error_message: str


class MessageRecord(TypedDict, total=False):
    """
    WATERTIGHT message record.
    Replaces Dict[str, Any] in conversation history.
    """
    role: str         # "user", "assistant", "system"
    content: str
    timestamp: str    # ISO format
    intent_type: str  # IntentType value


class TickResult(TypedDict, total=False):
    """
    WATERTIGHT tick result.
    Replaces Dict[str, Any] in tick().
    """
    tick_id: int
    timestamp: str
    needs_thinking: bool
    biorhythm_phase: str
    events_processed: int


class ThoughtResult(TypedDict, total=False):
    """
    WATERTIGHT thought result.
    Replaces List[Any] in think().
    """
    intent_type: str
    confidence: float
    action: str
    reasoning: str


# =============================================================================
# COGNITIVE RESULT (WATERTIGHT)
# =============================================================================


@dataclass
class CognitiveResult:
    """
    Result from cognitive processing.

    GAD-000: Structured, machine-readable output.
    WATERTIGHT: No Any types!
    """

    intent_type: IntentType
    confidence: float  # 0.0 - 1.0

    # For CHAT intents
    response: Optional[str] = None

    # For EXECUTE intents (syscall) - WATERTIGHT
    syscall_type: Optional[str] = None  # e.g., "SPAWN_COGNITION", "DISPATCH_TASK"
    syscall_params: Optional[SyscallParams] = None

    # For ROUTE intents
    target: Optional[str] = None  # Agent/tool to route to

    # For QUERY intents - WATERTIGHT
    query_type: Optional[str] = None
    query_result: Optional[QueryResult] = None

    # Metadata
    reasoning: Optional[str] = None  # Why this decision was made
    alternatives: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Union[str, float, bool, None, List[str]]]:
        """Serialize to WATERTIGHT dict."""
        result: Dict[str, Union[str, float, bool, None, List[str]]] = {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
        }
        if self.response:
            result["response"] = self.response
        if self.syscall_type:
            result["syscall_type"] = self.syscall_type
        if self.target:
            result["target"] = self.target
        if self.query_type:
            result["query_type"] = self.query_type
        if self.reasoning:
            result["reasoning"] = self.reasoning
        if self.alternatives:
            result["alternatives"] = self.alternatives
        return result


# =============================================================================
# SIGNED OPERATOR INPUT (The 37th Principle)
# =============================================================================


@dataclass
class SignedOperatorInput:
    """
    GAD-000 v2.0 + CONSTITUTION v2.0: The 37th Principle.

    Every operator input MUST be signed by a sovereign entity.
    Without signature: Mayavad (dead mechanism, no WHO)
    With signature: Vaishnava (living operation, sovereign will)
    """

    message: str
    timestamp: str  # ISO 8601

    # The 37th: Sovereign Identity
    signature: Optional[str] = None  # Base64 ECDSA signature
    public_key: Optional[str] = None  # Base64 public key (for verification)
    signer_id: Optional[str] = None  # Human-readable signer identity

    # Verification result (filled by kernel)
    is_verified: bool = False
    verification_error: Optional[str] = None

    def is_signed(self) -> bool:
        """Check if this input has a signature (regardless of verification)."""
        return self.signature is not None and self.public_key is not None

    def is_sovereign(self) -> bool:
        """Check if this input has a verified sovereign signature (The 37th)."""
        return self.is_signed() and self.is_verified


# =============================================================================
# COGNITIVE CONTEXT (WATERTIGHT)
# =============================================================================


@dataclass
class CognitiveContext:
    """
    Context passed to cognitive processing.
    WATERTIGHT: No Any types!
    """

    # System state
    kernel_status: str = "unknown"
    active_agents: List[str] = field(default_factory=list)
    pending_tasks: int = 0

    # Conversation context - WATERTIGHT
    previous_messages: List[MessageRecord] = field(default_factory=list)
    session_id: Optional[str] = None

    # User context
    user_id: Optional[str] = None
    user_capabilities: List[str] = field(default_factory=list)

    # Available actions
    available_tools: List[str] = field(default_factory=list)
    available_circuits: List[str] = field(default_factory=list)
    available_agents: List[str] = field(default_factory=list)

    # GAD-000 v2.0: The 37th Principle
    signed_input: Optional[SignedOperatorInput] = None
    sovereign_verified: bool = False  # True if 37th signature is valid


# =============================================================================
# COGNITIVE KERNEL PROTOCOL
# =============================================================================


class CognitiveKernelProtocol(Protocol):
    """
    Protocol for the MANAS Cognitive Kernel.

    The central orchestrator of autonomous thought and action.
    WATERTIGHT: Returns TypedDicts, not Dict[str, Any].
    """

    def tick(self) -> TickResult:
        """
        Processes a single consciousness tick.
        Updates biorhythm and checks if thinking is needed.
        WATERTIGHT: Returns TickResult TypedDict.
        """
        ...

    def think(
        self,
        context: Optional[CognitiveContext] = None,
        force: bool = False
    ) -> List[ThoughtResult]:
        """
        Executes a thought cycle (OODA loop).
        Generates intents based on perceived state.
        WATERTIGHT: Returns List[ThoughtResult].
        """
        ...


# =============================================================================
# SYSTEM HEARTBEAT PROTOCOL
# =============================================================================


class HeartbeatResult(TypedDict, total=False):
    """WATERTIGHT heartbeat result."""
    pulse_id: int
    timestamp: str
    snapshot_taken: bool
    sync_complete: bool
    duration_ms: int
    health: str


class SystemHeartbeatProtocol(Protocol):
    """
    Protocol for the System Heartbeat service.

    Orchestrates the unified breathing cycle (Snapshots + Sync).
    WATERTIGHT: Returns TypedDict, not Dict[str, Any].
    """

    async def pulse(self) -> HeartbeatResult:
        """Execute a unified system pulse."""
        ...


# =============================================================================
# OPERATOR COGNITIVE PROTOCOL
# =============================================================================


@runtime_checkable
class OperatorCognitiveProtocol(Protocol):
    """
    Protocol for cognitive plugins handling operator input.

    KAPILA's domain: The Kernel doesn't know MANAS exists.
    The Kernel only knows OperatorCognitiveProtocol.
    MANAS (or any other cognitive plugin) implements this protocol.

    WATERTIGHT - no Any types!
    """

    async def process_intent(
        self,
        intent: str,
        context: CognitiveContext
    ) -> CognitiveResult:
        """
        Process natural language intent.

        This is the main entry point. Takes raw user input,
        analyzes it, and returns structured result.

        Args:
            intent: Raw natural language input from operator
            context: System and conversation context (WATERTIGHT)

        Returns:
            CognitiveResult with intent_type and relevant data
        """
        ...

    async def generate_response(
        self,
        prompt: str,
        context: CognitiveContext
    ) -> str:
        """
        Generate intelligent response (for CHAT intents).

        Called when intent_type is CHAT and we need
        an LLM-powered response.
        """
        ...

    def get_capabilities(self) -> List[str]:
        """
        GAD-000: Discoverability.

        Returns list of capabilities this cognitive layer provides.
        """
        ...


# =============================================================================
# NULL COGNITIVE (Arjuna Pattern)
# =============================================================================


class NullCognitive:
    """
    Null implementation of OperatorCognitiveProtocol.

    Arjuna Pattern: Critical component missing ->
    Initialize fallback instead of crash.

    Used when no cognitive plugin is registered.
    Routes everything directly to Envoy.
    """

    async def process_intent(
        self,
        intent: str,
        context: CognitiveContext
    ) -> CognitiveResult:
        """Fallback: Route everything to Envoy."""
        return CognitiveResult(
            intent_type=IntentType.ROUTE,
            confidence=0.5,
            target="envoy",
            reasoning="No cognitive plugin registered, routing to Envoy",
        )

    async def generate_response(
        self,
        prompt: str,
        context: CognitiveContext
    ) -> str:
        """Fallback: Cannot generate without cognitive layer."""
        return "[No cognitive layer available]"

    def get_capabilities(self) -> List[str]:
        """Null cognitive has no capabilities."""
        return []


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    # Types (WATERTIGHT)
    "IntentType",
    "SyscallParams",
    "QueryResult",
    "MessageRecord",
    "TickResult",
    "ThoughtResult",
    "HeartbeatResult",
    # Dataclasses
    "CognitiveResult",
    "SignedOperatorInput",
    "CognitiveContext",
    # Protocols
    "CognitiveKernelProtocol",
    "SystemHeartbeatProtocol",
    "OperatorCognitiveProtocol",
    # Null implementation
    "NullCognitive",
]
