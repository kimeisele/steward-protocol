"""
vibe_core/errors.py

GAD-000 Compliant Error System.

This module provides machine-parseable errors for AI-native operation.
All errors must be structured so an AI operator can:
1. Parse the error code
2. Determine if retry is safe
3. Take corrective action

See: docs/architecture/OPUS/006-GAD000-COMPLIANCE-AUDIT.md
"""
from vibe_core.mahamantra.protocols._seed import (QUARTERS)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = QUARTERS
__genesis__ = "0xf9a40bd3"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class ErrorCategory(Enum):
    """Error categories for AI decision-making."""

    TRANSIENT = "transient"  # Retry is safe
    PERMANENT = "permanent"  # Do not retry
    SYSTEM = "system"  # Escalate to operator


class ErrorCode(Enum):
    """
    Machine-readable error codes.

    Naming convention: E{category}{sequence}_{description}
    - E1xxx: Transient (retry safe)
    - E2xxx: Permanent (do not retry)
    - E3xxx: System (escalate)
    """

    # Transient errors (retry safe)
    E1001_AGENT_BUSY = "E1001"
    E1002_TIMEOUT = "E1002"
    E1003_RATE_LIMITED = "E1003"
    E1004_RESOURCE_UNAVAILABLE = "E1004"
    E1005_NETWORK_ERROR = "E1005"

    # Permanent errors (do not retry)
    E2001_INVALID_CIRCUIT = "E2001"
    E2002_AGENT_NOT_FOUND = "E2002"
    E2003_CAPABILITY_DENIED = "E2003"
    E2004_INVALID_PAYLOAD = "E2004"
    E2005_TASK_NOT_FOUND = "E2005"
    E2006_CIRCUIT_NOT_FOUND = "E2006"
    E2007_VALIDATION_FAILED = "E2007"
    E2008_INVALID_STATE = "E2008"

    # System errors (escalate)
    E3001_KERNEL_FAULT = "E3001"
    E3002_LEDGER_CORRUPT = "E3002"
    E3003_BOOT_FAILED = "E3003"
    E3004_PLUGIN_FAILED = "E3004"
    E3005_INTERNAL_ERROR = "E3005"


# Map error codes to categories
ERROR_CATEGORIES: Dict[ErrorCode, ErrorCategory] = {
    # Transient
    ErrorCode.E1001_AGENT_BUSY: ErrorCategory.TRANSIENT,
    ErrorCode.E1002_TIMEOUT: ErrorCategory.TRANSIENT,
    ErrorCode.E1003_RATE_LIMITED: ErrorCategory.TRANSIENT,
    ErrorCode.E1004_RESOURCE_UNAVAILABLE: ErrorCategory.TRANSIENT,
    ErrorCode.E1005_NETWORK_ERROR: ErrorCategory.TRANSIENT,
    # Permanent
    ErrorCode.E2001_INVALID_CIRCUIT: ErrorCategory.PERMANENT,
    ErrorCode.E2002_AGENT_NOT_FOUND: ErrorCategory.PERMANENT,
    ErrorCode.E2003_CAPABILITY_DENIED: ErrorCategory.PERMANENT,
    ErrorCode.E2004_INVALID_PAYLOAD: ErrorCategory.PERMANENT,
    ErrorCode.E2005_TASK_NOT_FOUND: ErrorCategory.PERMANENT,
    ErrorCode.E2006_CIRCUIT_NOT_FOUND: ErrorCategory.PERMANENT,
    ErrorCode.E2007_VALIDATION_FAILED: ErrorCategory.PERMANENT,
    ErrorCode.E2008_INVALID_STATE: ErrorCategory.PERMANENT,
    # System
    ErrorCode.E3001_KERNEL_FAULT: ErrorCategory.SYSTEM,
    ErrorCode.E3002_LEDGER_CORRUPT: ErrorCategory.SYSTEM,
    ErrorCode.E3003_BOOT_FAILED: ErrorCategory.SYSTEM,
    ErrorCode.E3004_PLUGIN_FAILED: ErrorCategory.SYSTEM,
    ErrorCode.E3005_INTERNAL_ERROR: ErrorCategory.SYSTEM,
}


@dataclass
class StructuredError(Exception):
    """
    GAD-000 Test 3: Machine-parseable error.

    This is a proper Exception subclass that can be raised and caught.
    All errors in the system should eventually migrate to this format.

    Usage:
        raise StructuredError(
            code=ErrorCode.E2002_AGENT_NOT_FOUND,
            message="Agent 'herald' not registered",
            context={"agent_id": "herald"},
        )

    AI can then:
        try:
            result = await kernel.execute(task)
        except StructuredError as e:
            if e.retry_safe:
                await asyncio.sleep(1)
                result = await kernel.execute(task)  # Retry
            else:
                logger.error(f"Permanent error: {e.code}")
    """

    code: ErrorCode
    message: str
    context: Dict[str, object] = field(default_factory=dict)
    suggested_action: Optional[str] = None

    def __post_init__(self):
        # Initialize Exception with the message
        super().__init__(self.message)

    @property
    def retry_safe(self) -> bool:
        """AI can safely retry this operation."""
        category = ERROR_CATEGORIES.get(self.code, ErrorCategory.PERMANENT)
        return category == ErrorCategory.TRANSIENT

    @property
    def category(self) -> ErrorCategory:
        """Get error category."""
        return ERROR_CATEGORIES.get(self.code, ErrorCategory.PERMANENT)

    def to_dict(self) -> Dict[str, object]:
        """
        Convert to machine-readable dict.

        This is the format AI operators will parse.
        """
        return {
            "error_code": self.code.value,
            "error_name": self.code.name,
            "category": self.category.value,
            "message": self.message,
            "context": self.context,
            "retry_safe": self.retry_safe,
            "suggested_action": self.suggested_action,
        }

    def __str__(self) -> str:
        """Human-readable string (for logs)."""
        return f"[{self.code.value}] {self.message}"

    def __repr__(self) -> str:
        """Debug representation."""
        return f"StructuredError(code={self.code.name}, message={self.message!r})"


# Convenience factory functions for common errors


def agent_not_found(agent_id: str) -> StructuredError:
    """Create agent not found error."""
    return StructuredError(
        code=ErrorCode.E2002_AGENT_NOT_FOUND,
        message=f"Agent '{agent_id}' not registered",
        context={"agent_id": agent_id},
        suggested_action="Register the agent before use",
    )


def agent_busy(agent_id: str, current_task: Optional[str] = None) -> StructuredError:
    """Create agent busy error (retry safe)."""
    return StructuredError(
        code=ErrorCode.E1001_AGENT_BUSY,
        message=f"Agent '{agent_id}' is processing another task",
        context={"agent_id": agent_id, "current_task": current_task},
        suggested_action="Wait 1 second and retry",
    )


def circuit_not_found(circuit_id: str) -> StructuredError:
    """Create circuit not found error."""
    return StructuredError(
        code=ErrorCode.E2006_CIRCUIT_NOT_FOUND,
        message=f"Circuit '{circuit_id}' not found",
        context={"circuit_id": circuit_id},
        suggested_action="Check available circuits with kernel.get_capabilities()",
    )


def capability_denied(agent_id: str, capability: str, reason: Optional[str] = None) -> StructuredError:
    """Create capability denied error."""
    return StructuredError(
        code=ErrorCode.E2003_CAPABILITY_DENIED,
        message=f"Agent '{agent_id}' denied capability '{capability}'",
        context={"agent_id": agent_id, "capability": capability, "reason": reason},
        suggested_action="Request capability through governance system",
    )


def validation_failed(field: str, reason: str) -> StructuredError:
    """Create validation failed error."""
    return StructuredError(
        code=ErrorCode.E2007_VALIDATION_FAILED,
        message=f"Validation failed for '{field}': {reason}",
        context={"field": field, "reason": reason},
        suggested_action="Check input format and constraints",
    )


def timeout_error(operation: str, timeout_seconds: float) -> StructuredError:
    """Create timeout error (retry safe)."""
    return StructuredError(
        code=ErrorCode.E1002_TIMEOUT,
        message=f"Operation '{operation}' timed out after {timeout_seconds}s",
        context={"operation": operation, "timeout_seconds": timeout_seconds},
        suggested_action="Retry with longer timeout or simplify request",
    )


def kernel_fault(operation: str, details: str) -> StructuredError:
    """Create kernel fault error (escalate)."""
    return StructuredError(
        code=ErrorCode.E3001_KERNEL_FAULT,
        message=f"Kernel fault during '{operation}': {details}",
        context={"operation": operation, "details": details},
        suggested_action="Escalate to human operator",
    )
