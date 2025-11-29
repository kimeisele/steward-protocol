"""
OPERATOR PROTOCOL - Strictly Typed Universal Operator Interface

PHOENIX VIMANA UNIFIED BOOT PLAN - Section 4: Strict Typing Protocol

This module defines the HARD PROTOCOL for operator communication.
NO loose `dict[str, Any]`. Everything is typed.

This is TCP/IP for Agents - the protocol must be hard-defined.

Models:
- SystemContext: What the operator SEES (system state)
- Intent: What the operator WANTS (decision/action)
- OperatorResponse: What the system RETURNS (result)

Protocol:
- OperatorSocket: The interface all operators implement

Usage:
    from vibe_core.protocols.operator_protocol import (
        SystemContext, Intent, OperatorSocket
    )

    class MyOperator(OperatorSocket):
        async def receive_context(self, context: SystemContext) -> None:
            ...
        async def provide_intent(self) -> Intent:
            ...
        def is_available(self) -> bool:
            ...
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Protocol, runtime_checkable
from uuid import uuid4

from pydantic import BaseModel, Field

# =============================================================================
# ENUMS - Strict categorization
# =============================================================================


class IntentType(str, Enum):
    """Types of operator intents - determines routing path"""

    COMMAND = "command"  # Direct command execution
    QUERY = "query"  # Information retrieval
    DELEGATION = "delegation"  # Delegate to agent
    CONTROL = "control"  # System control (shutdown, status, etc.)
    REFLEX = "reflex"  # Automatic response (no operator needed)


class OperatorType(str, Enum):
    """Types of operators in the system"""

    HUMAN = "human"  # Human via terminal/web
    CLAUDE_CODE = "claude_code"  # Claude Code CLI
    LLM_API = "llm_api"  # Remote LLM (OpenAI, Anthropic, etc.)
    LOCAL_LLM = "local_llm"  # Local LLM (ollama, etc.)
    DEGRADED = "degraded"  # Fallback (no intelligence)


class KernelStatusType(str, Enum):
    """Kernel status states"""

    BOOTING = "booting"
    READY = "ready"
    DEGRADED = "degraded"
    SHUTDOWN = "shutdown"


class PriorityLevel(str, Enum):
    """Priority levels for intents"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# PYDANTIC MODELS - Strictly Typed Data Structures
# =============================================================================


class GitState(BaseModel):
    """Git repository state - extracted for clarity"""

    branch: Optional[str] = None
    uncommitted_count: int = 0
    behind_count: int = 0
    is_clean: bool = True

    class Config:
        frozen = True


class TaskState(BaseModel):
    """Current task state"""

    task_id: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Literal["pending", "running", "completed", "failed"] = "pending"

    class Config:
        frozen = True


class SystemContext(BaseModel):
    """
    The complete system state passed to operators.

    This is what the operator SEES before making a decision.
    Strictly typed - no loose dictionaries.
    """

    # Core Identity
    boot_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # System State
    kernel_status: KernelStatusType = KernelStatusType.BOOTING
    agents_registered: int = 0
    agents_healthy: int = 0

    # Sarga Boot State
    sarga_phase: Optional[str] = None  # Current Sarga element (shabda, akasha, etc.)
    sarga_complete: bool = False

    # Git State (for code-aware operators)
    git: GitState = Field(default_factory=GitState)

    # Current Task State
    current_task: Optional[TaskState] = None

    # Operator Awareness
    operator_type: OperatorType = OperatorType.HUMAN
    degradation_level: int = Field(default=0, ge=0)  # 0 = full, higher = more degraded

    # Message History (last N for context)
    recent_messages: list[str] = Field(default_factory=list)

    # Capabilities (from KernelOracle)
    available_tools: list[str] = Field(default_factory=list)
    available_agents: list[str] = Field(default_factory=list)

    class Config:
        frozen = False  # Allow updates during boot


class Intent(BaseModel):
    """
    The decision from an operator.

    This is what the operator WANTS to happen.
    Strictly typed - parseable, verifiable, composable.
    """

    # Core Intent
    intent_type: IntentType
    raw_input: str = Field(..., description="Original input from operator")

    # Parsed Intent
    target_agent: Optional[str] = Field(None, description="Agent to handle this")
    target_tool: Optional[str] = Field(None, description="Tool to invoke")
    parameters: dict[str, str] = Field(default_factory=dict)  # String params only

    # Metadata
    intent_id: str = Field(default_factory=lambda: str(uuid4()))
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_operator: OperatorType = OperatorType.HUMAN
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Control Flags
    requires_confirmation: bool = False
    is_destructive: bool = False
    priority: PriorityLevel = PriorityLevel.NORMAL

    class Config:
        frozen = True  # Intents are immutable once created


class OperatorResponse(BaseModel):
    """
    Response back to the operator after processing intent.
    """

    # Core Response
    success: bool
    message: str
    intent_id: str = Field(..., description="ID of the intent this responds to")

    # Data (typed string values only)
    data: dict[str, str] = Field(default_factory=dict)

    # Next State
    next_context: Optional[SystemContext] = None

    # Suggestions for operator
    suggested_actions: list[str] = Field(default_factory=list)

    # Timing
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        frozen = True


# =============================================================================
# PROTOCOL - The Universal Operator Socket
# =============================================================================


@runtime_checkable
class OperatorSocket(Protocol):
    """
    The Universal Socket for Operator Intelligence.

    Any entity that can provide decisions implements this.
    The system doesn't know or care WHO is deciding.

    This is the TCP/IP of Agent City - the protocol stays the same,
    regardless of who's on the other end.
    """

    async def receive_context(self, context: SystemContext) -> None:
        """
        Receive the current system state.

        For Human: Render as markdown in terminal/web
        For Claude: Inject as system prompt
        For LLM: Send as API context
        For Local: Pass as string

        Args:
            context: Strictly typed system state
        """
        ...

    async def provide_intent(self) -> Intent:
        """
        Provide the next action/decision.

        For Human: Read from stdin/form
        For Claude: Parse response
        For LLM: Parse API response
        For Local: Parse output

        Returns:
            Strictly typed intent
        """
        ...

    def is_available(self) -> bool:
        """
        Check if this operator is currently available.

        Used for graceful degradation - if operator isn't available,
        fall back to next in priority chain.
        """
        ...

    def get_operator_type(self) -> OperatorType:
        """Return the type of this operator."""
        ...


# =============================================================================
# FACTORY HELPERS
# =============================================================================


def create_system_context(
    kernel_status: KernelStatusType = KernelStatusType.BOOTING,
    agents_registered: int = 0,
    git_branch: Optional[str] = None,
    git_uncommitted: int = 0,
    sarga_phase: Optional[str] = None,
) -> SystemContext:
    """Factory function to create SystemContext with common defaults."""
    return SystemContext(
        kernel_status=kernel_status,
        agents_registered=agents_registered,
        git=GitState(
            branch=git_branch,
            uncommitted_count=git_uncommitted,
            is_clean=git_uncommitted == 0,
        ),
        sarga_phase=sarga_phase,
    )


def create_intent(
    intent_type: IntentType,
    raw_input: str,
    target_agent: Optional[str] = None,
    target_tool: Optional[str] = None,
    source_operator: OperatorType = OperatorType.HUMAN,
) -> Intent:
    """Factory function to create Intent with common defaults."""
    return Intent(
        intent_type=intent_type,
        raw_input=raw_input,
        target_agent=target_agent,
        target_tool=target_tool,
        source_operator=source_operator,
    )


def create_response(
    success: bool,
    message: str,
    intent_id: str,
    data: Optional[dict[str, str]] = None,
    suggested_actions: Optional[list[str]] = None,
) -> OperatorResponse:
    """Factory function to create OperatorResponse with common defaults."""
    return OperatorResponse(
        success=success,
        message=message,
        intent_id=intent_id,
        data=data or {},
        suggested_actions=suggested_actions or [],
    )


__all__ = [
    # Enums
    "IntentType",
    "OperatorType",
    "KernelStatusType",
    "PriorityLevel",
    # Models
    "GitState",
    "TaskState",
    "SystemContext",
    "Intent",
    "OperatorResponse",
    # Protocol
    "OperatorSocket",
    # Factories
    "create_system_context",
    "create_intent",
    "create_response",
]
