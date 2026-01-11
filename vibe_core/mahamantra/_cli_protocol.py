"""
CLI EXECUTION PROTOCOL - GAD-000 Compliant
==========================================

"Can an AI successfully operate your system without human intervention?"
— GAD-000 Turing Test

This module defines the PROTOCOL for CLI execution.
NO print() statements. STRUCTURED output only.

GAD-000 COMPLIANCE CHECKLIST:
1. Discoverability  - CLICapability describes what CLI can do
2. Observability    - CLIState exposes current state
3. Parseability     - CLIError has codes + context
4. Composability    - CLIOutput can be chained
5. Idempotency      - CLIResult includes retry info
6. Recoverability   - CLIHealth for self-healing
+ 37th (Identity)   - CLIContext has signature

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import (
    Callable,
    ClassVar,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)


# =============================================================================
# ERROR CODES (Parseability - GAD-000)
# =============================================================================

class CLIErrorCode(IntEnum):
    """
    Machine-readable error codes.

    GAD-000: "Can AI distinguish transient vs permanent failures?"

    Ranges:
        0       = Success
        1-99    = User errors (retryable with different input)
        100-199 = System errors (transient, retryable)
        200-299 = Permission errors (requires escalation)
        300-399 = State errors (requires recovery)
        400+    = Fatal errors (not retryable)
    """
    # Success
    SUCCESS = 0

    # User errors (1-99)
    INVALID_ARGUMENT = 1
    MISSING_ARGUMENT = 2
    UNKNOWN_COMMAND = 3
    INVALID_FORMAT = 4

    # System errors (100-199) - Transient, retryable
    TIMEOUT = 100
    SERVICE_UNAVAILABLE = 101
    RESOURCE_BUSY = 102
    RATE_LIMITED = 103

    # Permission errors (200-299) - Requires escalation
    UNAUTHORIZED = 200
    FORBIDDEN = 201
    SIGNATURE_REQUIRED = 202
    SIGNATURE_INVALID = 203

    # State errors (300-399) - Requires recovery
    STATE_CORRUPTED = 300
    STATE_DRIFT = 301
    INCONSISTENT_STATE = 302

    # Fatal errors (400+) - Not retryable
    INTERNAL_ERROR = 400
    NOT_IMPLEMENTED = 401
    FATAL = 500

    @property
    def is_retryable(self) -> bool:
        """Can AI safely retry this operation?"""
        return self.value < 200 or (100 <= self.value < 200)

    @property
    def is_transient(self) -> bool:
        """Is this a transient error?"""
        return 100 <= self.value < 200

    @property
    def requires_escalation(self) -> bool:
        """Does this require human/sovereign intervention?"""
        return 200 <= self.value < 300

    @property
    def requires_recovery(self) -> bool:
        """Does this require OUROBOROS recovery?"""
        return 300 <= self.value < 400


# =============================================================================
# OUTPUT TYPES (Composability - GAD-000)
# =============================================================================

class OutputFormat(str, Enum):
    """Output format for composability."""
    JSON = "json"           # Machine-readable (default)
    TABLE = "table"         # Structured table
    LINES = "lines"         # Line-separated values
    STREAM = "stream"       # Streaming output


@dataclass
class CLIOutputItem:
    """
    Single output item.

    GAD-000: Output of one feeds input of next.
    """
    key: str
    value: Union[str, int, float, bool, None]
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class CLIOutput:
    """
    Structured CLI output.

    GAD-000: "Does output match input schemas of dependent tools?"

    NO print() - this is DATA that can be:
    - Serialized to JSON
    - Piped to next command
    - Parsed by AI
    - Stored in logs
    """
    items: List[CLIOutputItem] = field(default_factory=list)
    format: OutputFormat = OutputFormat.JSON

    # For table output
    columns: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)

    # For streaming
    stream_complete: bool = True

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, List[Dict[str, str]]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "format": self.format.value,
            "items": [
                {"key": i.key, "value": i.value, "metadata": i.metadata}
                for i in self.items
            ],
            "columns": self.columns,
            "rows": self.rows,
            "stream_complete": self.stream_complete,
        }

    def add(self, key: str, value: Union[str, int, float, bool, None], **metadata: str) -> "CLIOutput":
        """Add an item (fluent API for composability)."""
        self.items.append(CLIOutputItem(key=key, value=value, metadata=metadata))
        return self

    def add_row(self, *values: str) -> "CLIOutput":
        """Add a table row."""
        self.rows.append(list(values))
        return self


# =============================================================================
# ERROR TYPE (Parseability - GAD-000)
# =============================================================================

@dataclass
class CLIError:
    """
    Structured error with context.

    GAD-000: "Are errors machine-readable (error codes + context)?"

    Includes:
    - Error code (machine-readable)
    - Message (human-readable)
    - Context (what was being attempted)
    - Recovery hints (how AI can fix it)
    """
    code: CLIErrorCode
    message: str
    context: Dict[str, str] = field(default_factory=dict)
    recovery_hints: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Union[str, int, List[str], Dict[str, str]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "code": self.code.value,
            "code_name": self.code.name,
            "message": self.message,
            "context": self.context,
            "recovery_hints": self.recovery_hints,
            "retryable": self.code.is_retryable,
            "transient": self.code.is_transient,
            "requires_escalation": self.code.requires_escalation,
            "requires_recovery": self.code.requires_recovery,
            "timestamp": self.timestamp,
        }


# =============================================================================
# RESULT TYPE (Idempotency - GAD-000)
# =============================================================================

@dataclass
class CLIResult:
    """
    Structured CLI result.

    GAD-000: "Can AI safely retry this operation?"

    Includes:
    - Success/failure status
    - Output data (for chaining)
    - Error (if failed)
    - Idempotency info (safe to retry?)
    """
    success: bool
    exit_code: int
    output: CLIOutput = field(default_factory=CLIOutput)
    error: Optional[CLIError] = None

    # Idempotency info
    idempotent: bool = True              # Safe to retry?
    retry_after_ms: Optional[int] = None  # Wait before retry
    operation_id: Optional[str] = None    # For deduplication

    # Timing
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Union[str, int, bool, None, Dict[str, str]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "output": self.output.to_dict(),
            "error": self.error.to_dict() if self.error else None,
            "idempotent": self.idempotent,
            "retry_after_ms": self.retry_after_ms,
            "operation_id": self.operation_id,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }

    @classmethod
    def ok(cls, output: Optional[CLIOutput] = None, **kwargs: Union[str, int, float, bool]) -> "CLIResult":
        """Create successful result."""
        out = output or CLIOutput()
        for k, v in kwargs.items():
            out.add(k, v)
        return cls(success=True, exit_code=0, output=out)

    @classmethod
    def fail(cls, code: CLIErrorCode, message: str, **context: str) -> "CLIResult":
        """Create failed result."""
        return cls(
            success=False,
            exit_code=code.value,
            error=CLIError(code=code, message=message, context=context),
        )


# =============================================================================
# CAPABILITY (Discoverability - GAD-000)
# =============================================================================

@dataclass
class CLIParameter:
    """
    CLI parameter description.

    GAD-000: Machine-readable parameter schema.
    """
    name: str
    param_type: str  # "string", "integer", "boolean", "float"
    required: bool = False
    default: Optional[Union[str, int, bool, float]] = None
    description: str = ""
    choices: List[str] = field(default_factory=list)


@dataclass
class CLICapability:
    """
    CLI capability description.

    GAD-000: "Can an AI discover this tool exists?"

    This is NOT a man page. This is MACHINE-READABLE metadata.
    """
    name: str                           # Command name
    purpose: str                        # What it does (1 sentence)
    parameters: List[CLIParameter] = field(default_factory=list)
    returns_success: str = ""           # What success looks like
    returns_failure: str = ""           # What failure looks like
    examples: List[str] = field(default_factory=list)

    # Routing info
    mahajana_position: int = -1         # Which mahajana handles this
    keywords: List[str] = field(default_factory=list)

    # Idempotency
    idempotent: bool = True
    side_effects: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Union[str, int, bool, List[str], List[Dict[str, str]]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "purpose": self.purpose,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.param_type,
                    "required": p.required,
                    "default": p.default,
                    "description": p.description,
                    "choices": p.choices,
                }
                for p in self.parameters
            ],
            "returns_success": self.returns_success,
            "returns_failure": self.returns_failure,
            "examples": self.examples,
            "mahajana_position": self.mahajana_position,
            "keywords": self.keywords,
            "idempotent": self.idempotent,
            "side_effects": self.side_effects,
        }


# =============================================================================
# STATE (Observability - GAD-000)
# =============================================================================

@dataclass
class CLIState:
    """
    Observable CLI state.

    GAD-000: "Can an AI see the current state?"
    """
    ready: bool = True
    busy: bool = False
    last_command: Optional[str] = None
    last_result: Optional[CLIResult] = None
    pending_operations: int = 0

    # Health
    healthy: bool = True
    degraded: bool = False
    error_count: int = 0

    def to_dict(self) -> Dict[str, Union[str, int, bool, None, Dict[str, str]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ready": self.ready,
            "busy": self.busy,
            "last_command": self.last_command,
            "last_result": self.last_result.to_dict() if self.last_result else None,
            "pending_operations": self.pending_operations,
            "healthy": self.healthy,
            "degraded": self.degraded,
            "error_count": self.error_count,
        }


# =============================================================================
# HEALTH (Recoverability - GAD-000)
# =============================================================================

@dataclass
class CLIHealth:
    """
    CLI health for self-healing (OUROBOROS).

    GAD-000: "Can the system heal itself?"
    """
    healthy: bool = True
    drift_detected: bool = False
    violations: List[str] = field(default_factory=list)
    recovery_actions: List[str] = field(default_factory=list)
    last_check: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Union[str, bool, List[str]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "healthy": self.healthy,
            "drift_detected": self.drift_detected,
            "violations": self.violations,
            "recovery_actions": self.recovery_actions,
            "last_check": self.last_check,
        }


# =============================================================================
# CONTEXT (37th - Identity)
# =============================================================================

@dataclass
class CLIContext:
    """
    CLI execution context with identity.

    GAD-000 37th: "All operations must be signed by sovereign."
    """
    # Identity (The 37th)
    caller_id: str = "anonymous"
    signature: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Execution context
    command: str = ""
    args: List[str] = field(default_factory=list)

    # Routing info
    mahajana_position: Optional[int] = None

    @property
    def is_signed(self) -> bool:
        """Is this operation signed by a sovereign?"""
        return self.signature is not None

    def to_dict(self) -> Dict[str, Union[str, int, bool, None, List[str]]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "caller_id": self.caller_id,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "command": self.command,
            "args": self.args,
            "mahajana_position": self.mahajana_position,
            "is_signed": self.is_signed,
        }


# =============================================================================
# THE PROTOCOL (GAD-000 Compliant)
# =============================================================================

@runtime_checkable
class CLIExecutable(Protocol):
    """
    Protocol for CLI execution.

    GAD-000: "Can an AI successfully operate your system?"

    Every mahajana that wants CLI capabilities MUST implement this.
    NO print() statements. Structured data only.
    """

    # =========================================================================
    # DISCOVERABILITY
    # =========================================================================

    @classmethod
    def get_capabilities(cls) -> List[CLICapability]:
        """
        Return machine-readable capability descriptions.

        GAD-000: "Can an AI discover this tool exists?"
        """
        ...

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute(self, context: CLIContext) -> CLIResult:
        """
        Execute CLI command.

        GAD-000: AI operates on behalf of human.

        Args:
            context: Execution context with identity

        Returns:
            Structured result (NO print!)
        """
        ...

    # =========================================================================
    # OBSERVABILITY
    # =========================================================================

    def get_state(self) -> CLIState:
        """
        Return current state.

        GAD-000: "Can an AI see the current state?"
        """
        ...

    # =========================================================================
    # RECOVERABILITY
    # =========================================================================

    def check_health(self) -> CLIHealth:
        """
        Check health for self-healing.

        GAD-000: "Can the system heal itself?"
        """
        ...


# =============================================================================
# BASE IMPLEMENTATION
# =============================================================================

class CLIExecutableBase(ABC):
    """
    Base class for CLI executables.

    Provides default implementations for:
    - State tracking
    - Health checking
    - Common error handling
    """

    def __init__(self) -> None:
        self._state = CLIState()
        self._health = CLIHealth()

    # =========================================================================
    # ABSTRACT - Must implement
    # =========================================================================

    @classmethod
    @abstractmethod
    def get_capabilities(cls) -> List[CLICapability]:
        """Return capabilities - MUST implement."""
        ...

    @abstractmethod
    def _execute_impl(self, context: CLIContext) -> CLIResult:
        """Execute implementation - MUST implement."""
        ...

    # =========================================================================
    # CONCRETE - Default implementations
    # =========================================================================

    def execute(self, context: CLIContext) -> CLIResult:
        """Execute with state tracking."""
        import time

        start = time.time()
        self._state.busy = True
        self._state.last_command = context.command

        try:
            result = self._execute_impl(context)
        except Exception as e:
            result = CLIResult.fail(
                CLIErrorCode.INTERNAL_ERROR,
                str(e),
                command=context.command,
            )
            self._state.error_count += 1
        finally:
            self._state.busy = False
            result.duration_ms = int((time.time() - start) * 1000)

        self._state.last_result = result
        return result

    def get_state(self) -> CLIState:
        """Return current state."""
        return self._state

    def check_health(self) -> CLIHealth:
        """Check health - override for custom checks."""
        self._health.healthy = self._state.error_count < 10
        self._health.last_check = datetime.now().isoformat()
        return self._health


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Error codes
    "CLIErrorCode",
    # Output types
    "OutputFormat",
    "CLIOutputItem",
    "CLIOutput",
    # Error type
    "CLIError",
    # Result type
    "CLIResult",
    # Capability (Discoverability)
    "CLIParameter",
    "CLICapability",
    # State (Observability)
    "CLIState",
    # Health (Recoverability)
    "CLIHealth",
    # Context (37th - Identity)
    "CLIContext",
    # The Protocol
    "CLIExecutable",
    # Base implementation
    "CLIExecutableBase",
]
