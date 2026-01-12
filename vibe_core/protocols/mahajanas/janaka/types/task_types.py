"""
OPUS-122: Canonical Task Types - Single Source of Truth.

"एकं सत्यं बहुधा वदन्ति" - "The truth is one, the wise call it by many names."

This module defines the CANONICAL task status enum for all task-related
operations across the codebase. Previously, three different TaskStatus
enums existed with drift:

  - scheduling/task.py:        PENDING, RUNNING, COMPLETED, FAILED, TIMEOUT
  - task_management/models.py: PENDING, IN_PROGRESS, COMPLETED, FAILED, BLOCKED, ARCHIVED
  - state_store.py:            pending, in_progress, completed, failed, blocked (lowercase!)

OPUS-122 unifies these into a single source of truth with:
  - Consistent UPPERCASE values
  - Superset of all states
  - Semantic aliases (RUNNING = IN_PROGRESS)

CANONICAL IMPORT:
    from vibe_core.task_types import TaskStatus

MIGRATION:
    Old: from vibe_core.scheduling.task import TaskStatus
    New: from vibe_core.task_types import TaskStatus
"""

from enum import Enum


class TaskStatus(str, Enum):
    """
    Canonical task lifecycle states (OPUS-122).

    This is the SINGLE SOURCE OF TRUTH for task status across the system.
    All task-related modules should import from here.

    States:
        PENDING: Task created but not yet started
        IN_PROGRESS: Task is currently being executed (alias: RUNNING)
        COMPLETED: Task finished successfully
        FAILED: Task encountered an error
        BLOCKED: Task waiting on dependency or external factor
        TIMEOUT: Task exceeded time limit (scheduling-specific)
        ARCHIVED: Task moved to archive (management-specific)

    Semantic Aliases:
        RUNNING: Alias for IN_PROGRESS (backward compat with scheduling)
    """

    # Core states (present in all systems)
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    # Extended states
    BLOCKED = "BLOCKED"  # task_management, state_store
    TIMEOUT = "TIMEOUT"  # scheduling
    ARCHIVED = "ARCHIVED"  # task_management

    # ==========================================================================
    # SEMANTIC ALIAS: RUNNING = IN_PROGRESS
    # ==========================================================================
    # The scheduling module used RUNNING while task_management used IN_PROGRESS.
    # They mean the same thing. We standardize on IN_PROGRESS but provide
    # RUNNING as an alias for backward compatibility.
    #
    # NOTE: Python Enum doesn't support true aliases with same value,
    # so we use a class method for compatibility checking.
    # ==========================================================================

    @classmethod
    def from_string(cls, value: str) -> "TaskStatus":
        """
        Convert string to TaskStatus with alias support.

        Handles:
            - UPPERCASE values (canonical)
            - lowercase values (state_store compat)
            - RUNNING -> IN_PROGRESS alias

        Args:
            value: String status value

        Returns:
            TaskStatus enum member

        Raises:
            ValueError: If value doesn't match any status
        """
        # Normalize to uppercase
        normalized = value.upper()

        # Handle RUNNING -> IN_PROGRESS alias
        if normalized == "RUNNING":
            return cls.IN_PROGRESS

        # Try direct match
        try:
            return cls(normalized)
        except ValueError:
            pass

        # Try by name
        try:
            return cls[normalized]
        except KeyError:
            raise ValueError(f"Invalid TaskStatus: {value}. Valid values: {[s.value for s in cls]}")

    @classmethod
    def is_active(cls, status: "TaskStatus") -> bool:
        """Check if status represents an active (non-terminal) state."""
        return status in (cls.PENDING, cls.IN_PROGRESS, cls.BLOCKED)

    @classmethod
    def is_terminal(cls, status: "TaskStatus") -> bool:
        """Check if status represents a terminal (finished) state."""
        return status in (cls.COMPLETED, cls.FAILED, cls.TIMEOUT, cls.ARCHIVED)


# =============================================================================
# BACKWARD COMPATIBILITY: Value mappings for lowercase consumers
# =============================================================================

# state_store.py used lowercase values - provide mapping
LOWERCASE_STATUS_MAP = {
    "pending": TaskStatus.PENDING,
    "in_progress": TaskStatus.IN_PROGRESS,
    "completed": TaskStatus.COMPLETED,
    "failed": TaskStatus.FAILED,
    "blocked": TaskStatus.BLOCKED,
}


def normalize_status(value: str) -> TaskStatus:
    """
    Normalize any status string to canonical TaskStatus.

    Handles all legacy formats:
        - UPPERCASE: "PENDING", "IN_PROGRESS", "RUNNING"
        - lowercase: "pending", "in_progress"
        - Mixed: "Pending", "In_Progress"

    Args:
        value: Status string in any format

    Returns:
        Canonical TaskStatus enum member
    """
    # Try lowercase map first
    if value.lower() in LOWERCASE_STATUS_MAP:
        return LOWERCASE_STATUS_MAP[value.lower()]

    # Fall back to from_string
    return TaskStatus.from_string(value)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TaskStatus",
    "normalize_status",
    "LOWERCASE_STATUS_MAP",
]
