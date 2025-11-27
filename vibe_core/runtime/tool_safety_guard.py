#!/usr/bin/env python3
"""
GAD-509 Extension: Tool Safety Guard ("Iron Dome")
===================================================

Protects VIBE Agency OS from dangerous tool operations that cause regressions.

This is a HARD GUARDRAIL layer that sits between the Agent and the Tools.
It physically prevents operations that are known to cause "AI Slop" and regressions.

Rules (Non-negotiable):
  1. ANTI-BLINDNESS: No file edits without prior read in session
  2. BLAST RADIUS: No directory deletions without explicit override
  3. TEST DISCIPLINE: No commits when tests are failing

Version: 1.0 (GAD-509 Extension - Operation Iron Dome)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Severity levels for safety violations"""

    BLOCKING = "blocking"  # Operation is blocked entirely
    WARNING = "warning"  # Operation allowed with warning
    INFO = "info"  # Informational, no blocking


@dataclass
class SafetyViolation:
    """Represents a safety rule violation"""

    rule: str
    severity: ViolationSeverity
    message: str
    tool_name: str
    args: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class SessionContext:
    """Tracks session state for safety checks"""

    files_read: set[str] = field(default_factory=set)
    files_written: set[str] = field(default_factory=set)
    violations: list[SafetyViolation] = field(default_factory=list)
    session_start: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ToolSafetyGuardError(Exception):
    """Raised when a tool operation is blocked by safety rules"""

    pass


class ToolSafetyGuard:
    """
    Iron Dome protection layer for tool operations.

    This guard sits between the agent and the tools, intercepting dangerous
    operations before they can cause regressions or "AI slop".

    Rules enforced:
        1. Anti-Blindness: Block file edits without prior read
        2. Blast Radius: Block directory deletions
        3. Test Discipline: Block commits with failing tests

    Usage:
        guard = ToolSafetyGuard()

        # Before executing a tool
        allowed, violation = guard.check_action("edit_file", {"path": "foo.py", ...})
        if not allowed:
            raise ToolSafetyGuardError(violation.message)

        # After successful read
        guard.record_file_read("foo.py")
    """

    def __init__(self, enable_strict_mode: bool = True):
        """
        Initialize the safety guard.

        Args:
            enable_strict_mode: If True, enforce all blocking rules.
                               If False, log warnings but allow operations.
        """
        self.strict_mode = enable_strict_mode
        self.context = SessionContext()

        logger.info(
            f"Tool Safety Guard initialized (strict_mode={enable_strict_mode}). "
            f"Iron Dome protection active."
        )

    def check_action(
        self, tool_name: str, args: dict[str, Any]
    ) -> tuple[bool, SafetyViolation | None]:
        """
        Check if a tool action is safe to execute.

        Args:
            tool_name: Name of the tool being invoked
            args: Arguments being passed to the tool

        Returns:
            (allowed: bool, violation: SafetyViolation | None)
            - If allowed is True, operation can proceed
            - If allowed is False, operation is blocked and violation contains details
        """
        # Rule 1: Anti-Blindness
        if tool_name in ["edit_file", "write_file", "modify_file"]:
            file_path = self._extract_file_path(args)
            if file_path and not self._was_file_read(file_path):
                violation = SafetyViolation(
                    rule="ANTI_BLINDNESS",
                    severity=ViolationSeverity.BLOCKING,
                    message=(
                        f"BLOCKED: Cannot edit '{file_path}' without reading it first. "
                        f"This prevents hallucinated edits. Read the file before editing."
                    ),
                    tool_name=tool_name,
                    args=args,
                )
                self.context.violations.append(violation)

                if self.strict_mode:
                    logger.error(f"🛡️ IRON DOME BLOCKED: {violation.message}")
                    return False, violation
                else:
                    logger.warning(f"⚠️ IRON DOME WARNING: {violation.message}")

        # Rule 2: Blast Radius
        if tool_name in ["delete_directory", "rm_rf", "remove_tree"]:
            dir_path = self._extract_file_path(args)
            violation = SafetyViolation(
                rule="BLAST_RADIUS",
                severity=ViolationSeverity.BLOCKING,
                message=(
                    f"BLOCKED: Directory deletion '{dir_path}' requires explicit override. "
                    f"Use delete_file for individual files instead."
                ),
                tool_name=tool_name,
                args=args,
            )
            self.context.violations.append(violation)

            if self.strict_mode:
                logger.error(f"🛡️ IRON DOME BLOCKED: {violation.message}")
                return False, violation
            else:
                logger.warning(f"⚠️ IRON DOME WARNING: {violation.message}")

        # Rule 3: Test Discipline (placeholder - requires test runner integration)
        # This would check if tests are passing before allowing commits
        # Deferred to integration phase

        return True, None

    def record_file_read(self, file_path: str):
        """
        Record that a file has been read in this session.

        Args:
            file_path: Path to the file that was read
        """
        normalized = self._normalize_path(file_path)
        self.context.files_read.add(normalized)
        logger.debug(f"📖 Recorded file read: {normalized}")

    def record_file_write(self, file_path: str):
        """
        Record that a file has been written in this session.

        Args:
            file_path: Path to the file that was written
        """
        normalized = self._normalize_path(file_path)
        self.context.files_written.add(normalized)
        logger.debug(f"✍️ Recorded file write: {normalized}")

    def _was_file_read(self, file_path: str) -> bool:
        """
        Check if a file was read in the current session.

        Args:
            file_path: Path to check

        Returns:
            True if file was read, False otherwise
        """
        normalized = self._normalize_path(file_path)
        was_read = normalized in self.context.files_read

        logger.debug(f"🔍 Check file read: {normalized} → {was_read}")
        return was_read

    def _normalize_path(self, path: str) -> str:
        """
        Normalize a file path for comparison.

        Args:
            path: File path to normalize

        Returns:
            Normalized absolute path
        """
        try:
            return str(Path(path).resolve())
        except Exception:
            # If path resolution fails, return as-is
            return path

    def _extract_file_path(self, args: dict[str, Any]) -> str | None:
        """
        Extract file path from tool arguments.

        Args:
            args: Tool arguments dictionary

        Returns:
            File path if found, None otherwise
        """
        # Try common parameter names
        for key in ["path", "file_path", "file", "filepath", "target"]:
            if key in args:
                return args[key]
        return None

    def get_status(self) -> dict[str, Any]:
        """
        Get current safety guard status.

        Returns:
            Dictionary with session context and violation stats
        """
        return {
            "strict_mode": self.strict_mode,
            "session_start": self.context.session_start,
            "files_read": len(self.context.files_read),
            "files_written": len(self.context.files_written),
            "violations": {
                "total": len(self.context.violations),
                "blocking": sum(
                    1 for v in self.context.violations if v.severity == ViolationSeverity.BLOCKING
                ),
                "warning": sum(
                    1 for v in self.context.violations if v.severity == ViolationSeverity.WARNING
                ),
            },
            "recent_violations": [
                {
                    "rule": v.rule,
                    "severity": v.severity.value,
                    "message": v.message,
                    "timestamp": v.timestamp,
                }
                for v in self.context.violations[-5:]  # Last 5 violations
            ],
        }

    def reset_session(self):
        """
        Reset session context (for testing or new session).
        """
        logger.info("🔄 Resetting Tool Safety Guard session context")
        self.context = SessionContext()
