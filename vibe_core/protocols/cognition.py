"""
Cognitive Protocols - Layer 1: Interfaces Only

OPUS-211: Structural Decoupling (DI.py wiring)
OPUS-309: CognitiveProtocol for Operator Input (Hot-Swap Hook)

Defines the interface for the MANAS Cognitive Kernel.
Breaking circular dependencies between Kernel and its organs.

PROMPT.md Compliance:
- "Protocol statt konkrete Klassen (Dependency Inversion)"
- "Hot-Swap-Fähigkeit – Module austauschbar ohne Neustart"
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class CognitiveKernelProtocol(ABC):
    """
    Protocol for the MANAS Cognitive Kernel.

    The central orchestrator of autonomous thought and action.
    """

    @abstractmethod
    def tick(self) -> Dict[str, Any]:
        """
        Processes a single consciousness tick.
        Updates biorhythm and checks if thinking is needed.
        """
        pass

    @abstractmethod
    def think(self, context: Optional[Dict[str, Any]] = None, force: bool = False) -> List[Any]:
        """
        Executes a thought cycle (OODA loop).
        Generates intents based on perceived state.
        """
        pass


class SystemHeartbeatProtocol(ABC):
    """
    Protocol for the System Heartbeat service.

    Orchestrates the unified breathing cycle (Snapshots + Sync).
    """

    @abstractmethod
    async def pulse(self) -> Dict[str, Any]:
        """Execute a unified system pulse."""
        pass


# =============================================================================
# OPUS-309: Operator Input Protocol (Hot-Swap Cognitive Hook)
# =============================================================================


class IntentType(Enum):
    """Type of intent detected from natural language."""

    CHAT = "chat"  # Conversational, needs LLM response
    EXECUTE = "execute"  # Action, needs syscall execution
    QUERY = "query"  # Information retrieval, needs data lookup
    ROUTE = "route"  # Delegate to specific agent/tool


@dataclass
class CognitiveResult:
    """
    Result from cognitive processing.

    GAD-000: Structured, machine-readable output.
    PROMPT.md: No hidden states - everything explicit.
    """

    intent_type: IntentType
    confidence: float  # 0.0 - 1.0

    # For CHAT intents
    response: Optional[str] = None

    # For EXECUTE intents (syscall)
    syscall_type: Optional[str] = None  # e.g., "SPAWN_COGNITION", "DISPATCH_TASK"
    syscall_params: Dict[str, Any] = field(default_factory=dict)

    # For ROUTE intents
    target: Optional[str] = None  # Agent/tool to route to

    # For QUERY intents
    query_type: Optional[str] = None
    query_result: Optional[Dict[str, Any]] = None

    # Metadata
    reasoning: Optional[str] = None  # Why this decision was made
    alternatives: List[str] = field(default_factory=list)


@dataclass
class CognitiveContext:
    """
    Context passed to cognitive processing.

    Contains everything the cognitive layer needs to make decisions.
    """

    # System state
    kernel_status: str = "unknown"
    active_agents: List[str] = field(default_factory=list)
    pending_tasks: int = 0

    # Conversation context
    previous_messages: List[Dict[str, Any]] = field(default_factory=list)
    session_id: Optional[str] = None

    # User context
    user_id: Optional[str] = None
    user_capabilities: List[str] = field(default_factory=list)

    # Available actions
    available_tools: List[str] = field(default_factory=list)
    available_circuits: List[str] = field(default_factory=list)
    available_agents: List[str] = field(default_factory=list)


@runtime_checkable
class OperatorCognitiveProtocol(Protocol):
    """
    OPUS-309: Protocol for cognitive plugins handling operator input.

    PROMPT.md: "Protocol statt konkrete Klassen"

    The Kernel doesn't know MANAS exists.
    The Kernel only knows OperatorCognitiveProtocol.
    MANAS (or any other cognitive plugin) implements this protocol.

    Usage:
        # In plugin (e.g., opus_assistant):
        class MANASCognitive:
            async def process_intent(self, intent, context):
                ...

        kernel.register_cognitive(MANASCognitive())

        # In kernel:
        result = await self._cognitive.process_intent("create an agent", ctx)
        if result.intent_type == IntentType.EXECUTE:
            self.execute_syscall(result.syscall_request)
    """

    async def process_intent(self, intent: str, context: CognitiveContext) -> CognitiveResult:
        """
        Process natural language intent.

        This is the main entry point. Takes raw user input,
        analyzes it, and returns structured result.

        Args:
            intent: Raw natural language input from operator
            context: System and conversation context

        Returns:
            CognitiveResult with intent_type and relevant data
        """
        ...

    async def generate_response(self, prompt: str, context: CognitiveContext) -> str:
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


class NullCognitive:
    """
    Null implementation of OperatorCognitiveProtocol.

    PROMPT.md: "Arjuna-Pattern - Kritische Komponente fehlt →
               Neu initialisieren statt crashen"

    Used when no cognitive plugin is registered.
    Routes everything directly to Envoy.
    """

    async def process_intent(self, intent: str, context: CognitiveContext) -> CognitiveResult:
        """Fallback: Route everything to Envoy."""
        return CognitiveResult(
            intent_type=IntentType.ROUTE,
            confidence=0.5,
            target="envoy",
            reasoning="No cognitive plugin registered, routing to Envoy",
        )

    async def generate_response(self, prompt: str, context: CognitiveContext) -> str:
        """Fallback: Cannot generate without cognitive layer."""
        return "[No cognitive layer available]"

    def get_capabilities(self) -> List[str]:
        """Null cognitive has no capabilities."""
        return []
