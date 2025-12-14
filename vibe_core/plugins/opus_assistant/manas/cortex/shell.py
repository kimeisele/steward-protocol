"""
OPUS-041: VAK (The Voice) - ShellCortex

This is the sensory-motor interface for MANAS to execute CLI commands.

SECURITY CRITICAL:
- SAFE commands CAN auto-execute (read-only queries)
- DANGEROUS commands MUST NEVER auto-execute
- Unknown commands require explicit approval
- Output MUST always be captured (no silent execution)

"The voice must speak truth, not chaos."
"""

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MANAS.Cortex.Shell")


class CommandRisk(Enum):
    """Risk classification for CLI commands."""

    SAFE = "safe"  # Read-only, can auto-execute
    REQUIRES_APPROVAL = "requires_approval"  # Needs human approval
    FORBIDDEN = "forbidden"  # NEVER execute through cortex


@dataclass
class ShellResult:
    """Result of a shell command execution."""

    command: List[str]
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    blocked: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for memory/serialization."""
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "blocked": self.blocked,
            "error": self.error,
        }


class ShellCortex:
    """
    Safe interface for MANAS to execute CLI commands.

    Security Model:
    - SAFE commands: status, state, diff, ps, plugins, capabilities, help
    - FORBIDDEN commands: stop, boot, execute, init (require direct human action)
    - REQUIRES_APPROVAL: Everything else

    Usage:
        cortex = ShellCortex(workspace=Path("."))
        result = cortex.execute_safe(["status"])  # Auto-executes
        result = cortex.execute_with_approval(["verify", "agent"], "human_approved")
    """

    # Commands that are safe to auto-execute (read-only queries)
    SAFE_COMMANDS = frozenset(
        {
            "status",
            "state",
            "diff",
            "ps",
            "plugins",
            "capabilities",
            "help",
            "extensions",
            "lineage",
            "introspect",
        }
    )

    # Commands that are FORBIDDEN through the cortex (require direct human)
    FORBIDDEN_COMMANDS = frozenset(
        {
            "stop",
            "boot",
            "execute",
            "init",
            "install-llm",
            "install-semantic",
        }
    )

    # Default timeout in seconds
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        workspace: Optional[Path] = None,
        timeout_seconds: Optional[int] = None,
    ):
        """
        Initialize ShellCortex.

        Args:
            workspace: Working directory for command execution
            timeout_seconds: Command timeout (default: 30s)
        """
        self._workspace = workspace or Path.cwd()
        self._timeout = timeout_seconds if timeout_seconds is not None else self.DEFAULT_TIMEOUT

    def classify_risk(self, command: List[str]) -> CommandRisk:
        """
        Classify the risk level of a command.

        Args:
            command: Command as list of strings (e.g., ["status"])

        Returns:
            CommandRisk enum value
        """
        if not command:
            return CommandRisk.REQUIRES_APPROVAL

        cmd_name = command[0].lower()

        if cmd_name in self.FORBIDDEN_COMMANDS:
            return CommandRisk.FORBIDDEN

        if cmd_name in self.SAFE_COMMANDS:
            return CommandRisk.SAFE

        # Unknown commands require approval
        return CommandRisk.REQUIRES_APPROVAL

    def execute_safe(self, command: List[str]) -> ShellResult:
        """
        Execute a command only if it's classified as SAFE.

        Rejects FORBIDDEN and REQUIRES_APPROVAL commands.

        Args:
            command: Command to execute

        Returns:
            ShellResult with output or blocked status
        """
        risk = self.classify_risk(command)

        if risk == CommandRisk.FORBIDDEN:
            logger.warning(f"Blocked FORBIDDEN command: {command}")
            return ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Command is FORBIDDEN - cannot execute through cortex",
            )

        if risk == CommandRisk.REQUIRES_APPROVAL:
            logger.info(f"Blocked unapproved command: {command}")
            return ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Command requires approval - use execute_with_approval()",
            )

        # SAFE - execute it
        return self._execute(command)

    def execute_with_approval(
        self,
        command: List[str],
        approval_token: Optional[str],
    ) -> ShellResult:
        """
        Execute a command with explicit approval.

        FORBIDDEN commands are still blocked - they must be executed
        directly by a human, not through the cortex.

        Args:
            command: Command to execute
            approval_token: Approval token (must be non-empty)

        Returns:
            ShellResult with output or blocked status
        """
        # Validate approval token
        if not approval_token:
            logger.warning(f"No approval token provided for: {command}")
            return ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Approval token is required",
            )

        risk = self.classify_risk(command)

        # FORBIDDEN commands cannot be executed even with approval
        if risk == CommandRisk.FORBIDDEN:
            logger.warning(f"Blocked FORBIDDEN command even with approval: {command}")
            return ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Command is FORBIDDEN - must be executed directly by human",
            )

        # SAFE or REQUIRES_APPROVAL with valid token - execute it
        return self._execute(command)

    def _execute(self, command: List[str]) -> ShellResult:
        """
        Actually execute the command via subprocess.

        Args:
            command: Command to execute

        Returns:
            ShellResult with output
        """
        try:
            # Build the full command with steward CLI
            full_command = ["steward"] + command

            logger.debug(f"Executing: {full_command}")

            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                cwd=str(self._workspace),
            )

            return ShellResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                blocked=False,
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {self._timeout}s: {command}")
            return ShellResult(
                command=command,
                exit_code=124,  # Standard timeout exit code
                blocked=False,
                error=f"Command timed out after {self._timeout} seconds",
            )
        except FileNotFoundError:
            logger.error("steward CLI not found in PATH")
            return ShellResult(
                command=command,
                exit_code=127,  # Command not found
                blocked=False,
                error="steward CLI not found - is it installed?",
            )
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return ShellResult(
                command=command,
                exit_code=1,
                blocked=False,
                error=str(e),
            )
