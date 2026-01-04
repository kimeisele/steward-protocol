"""
OPUS-041: VAK (The Voice) - ShellCortex
OPUS-058: PRATYAHARA - Core Integration

This is the sensory-motor interface for MANAS to execute CLI commands.

SECURITY CRITICAL:
- SAFE commands CAN auto-execute (read-only queries)
- DANGEROUS commands MUST NEVER auto-execute
- Unknown commands require explicit approval
- Output MUST always be captured (no silent execution)

OPUS-058 PRATYAHARA: All commands are now:
- Recorded to the core ledger (VAJRA binding)
- Reported to Narasimha if FORBIDDEN (threat detection)
- Tracked for audit trail

"The voice must speak truth, not chaos."
"""

import hashlib
import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

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

        # ⚡ PRATYAHARA: Core kernel reference for ledger binding
        self._vibe_kernel: Optional["KernelProtocol"] = None

    # =========================================================================
    # ⚡ PRATYAHARA: KERNEL INTEGRATION (OPUS-058)
    # =========================================================================

    def inject_kernel(self, kernel: "KernelProtocol") -> None:
        """
        Inject the core VibeKernel for ledger and Narasimha access.

        OPUS-058 PRATYAHARA: Every shell command MUST be recorded.
        Without kernel injection, ShellCortex operates in "shadow mode".

        Args:
            kernel: The RealVibeKernel instance
        """
        self._vibe_kernel = kernel
        logger.info("⚡ PRATYAHARA: ShellCortex bound to core kernel")

    def _record_to_ledger(
        self,
        event_type: str,
        command: List[str],
        result: Optional["ShellResult"] = None,
    ) -> Optional[str]:
        """
        Record a shell command event to the core ledger.

        OPUS-058 PRATYAHARA: Audit trail for all shell actions.

        Args:
            event_type: Type of event (SHELL_EXECUTING, SHELL_COMPLETED, etc.)
            command: The command being executed
            result: Optional result after execution

        Returns:
            Event ID if recorded, None if no kernel available
        """
        if not self._vibe_kernel:
            logger.debug("⚠️ PRATYAHARA: No kernel - shell command not ledgered (shadow mode)")
            return None

        # Build command hash for integrity
        cmd_str = " ".join(command)
        cmd_hash = hashlib.sha256(cmd_str.encode()).hexdigest()[:16]

        details = {
            "command": command,
            "command_hash": cmd_hash,
            "workspace": str(self._workspace),
            "risk": self.classify_risk(command).value,
        }

        if result:
            details.update(
                {
                    "exit_code": result.exit_code,
                    "blocked": result.blocked,
                    "error": result.error,
                    "stdout_length": len(result.stdout) if result.stdout else 0,
                    "stderr_length": len(result.stderr) if result.stderr else 0,
                }
            )

        try:
            event_id = self._vibe_kernel.ledger.record_event(
                event_type=event_type,
                agent_id="shell_cortex",
                details=details,
            )
            logger.debug(f"⚡ PRATYAHARA: {event_type} recorded → {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"⚡ PRATYAHARA: Failed to record {event_type}: {e}")
            return None

    def _report_to_narasimha(self, command: List[str], reason: str) -> None:
        """
        Report a FORBIDDEN command attempt to Narasimha.

        OPUS-058 PRATYAHARA: FORBIDDEN commands are threat indicators.

        Args:
            command: The forbidden command
            reason: Why this is a threat
        """
        if not self._vibe_kernel:
            return

        try:
            from vibe_core.narasimha import ThreatIndicator, ThreatLevel, get_narasimha

            narasimha = get_narasimha()
            indicator = ThreatIndicator(
                indicator_type="shell_forbidden_attempt",
                agent_id="shell_cortex",
                severity=ThreatLevel.ORANGE,  # Serious but not RED (needs context)
                description=f"Attempted FORBIDDEN shell command: {' '.join(command)}",
                evidence={"command": command, "reason": reason},
                timestamp=__import__("time").time(),
            )
            narasimha.register_threat(indicator)
            logger.warning(f"🦁 NARASIMHA: Threat registered for FORBIDDEN command: {command}")
        except Exception as e:
            logger.error(f"Failed to report to Narasimha: {e}")

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

        OPUS-058 PRATYAHARA: All executions are recorded to ledger.
        Rejects FORBIDDEN and REQUIRES_APPROVAL commands.

        Args:
            command: Command to execute

        Returns:
            ShellResult with output or blocked status
        """
        risk = self.classify_risk(command)

        if risk == CommandRisk.FORBIDDEN:
            logger.warning(f"Blocked FORBIDDEN command: {command}")
            # ⚡ PRATYAHARA: Report to Narasimha
            self._report_to_narasimha(command, "Attempted via execute_safe()")
            result = ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Command is FORBIDDEN - cannot execute through cortex",
            )
            # ⚡ PRATYAHARA: Record blocked attempt
            self._record_to_ledger("SHELL_BLOCKED", command, result)
            return result

        if risk == CommandRisk.REQUIRES_APPROVAL:
            logger.info(f"Blocked unapproved command: {command}")
            result = ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Command requires approval - use execute_with_approval()",
            )
            # ⚡ PRATYAHARA: Record blocked attempt
            self._record_to_ledger("SHELL_BLOCKED", command, result)
            return result

        # SAFE - execute it
        return self._execute(command)

    def execute_with_approval(
        self,
        command: List[str],
        approval_token: Optional[str],
    ) -> ShellResult:
        """
        Execute a command with explicit approval.

        OPUS-058 PRATYAHARA: All executions are recorded to ledger.
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
            result = ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Approval token is required",
            )
            # ⚡ PRATYAHARA: Record blocked attempt
            self._record_to_ledger("SHELL_BLOCKED", command, result)
            return result

        risk = self.classify_risk(command)

        # FORBIDDEN commands cannot be executed even with approval
        if risk == CommandRisk.FORBIDDEN:
            logger.warning(f"Blocked FORBIDDEN command even with approval: {command}")
            # ⚡ PRATYAHARA: Report to Narasimha (escalated - they tried with approval)
            self._report_to_narasimha(command, f"Attempted with approval token: {approval_token[:8]}...")
            result = ShellResult(
                command=command,
                exit_code=1,
                blocked=True,
                error="Command is FORBIDDEN - must be executed directly by human",
            )
            # ⚡ PRATYAHARA: Record blocked attempt
            self._record_to_ledger("SHELL_BLOCKED", command, result)
            return result

        # SAFE or REQUIRES_APPROVAL with valid token - execute it
        return self._execute(command, approval_token=approval_token)

    def _execute(self, command: List[str], approval_token: Optional[str] = None) -> ShellResult:
        """
        Actually execute the command via subprocess.

        OPUS-058 PRATYAHARA: All executions are recorded to ledger.

        Args:
            command: Command to execute
            approval_token: Optional approval token (for audit trail)

        Returns:
            ShellResult with output
        """
        # ⚡ PRATYAHARA: Record EXECUTING to ledger BEFORE execution
        self._record_to_ledger("SHELL_EXECUTING", command)

        try:
            # Build the full command with steward CLI
            full_command = ["steward"] + command

            logger.debug(f"Executing: {full_command}")

            proc_result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                cwd=str(self._workspace),
            )

            result = ShellResult(
                command=command,
                exit_code=proc_result.returncode,
                stdout=proc_result.stdout,
                stderr=proc_result.stderr,
                blocked=False,
            )

            # ⚡ PRATYAHARA: Record COMPLETED to ledger AFTER execution
            event_type = "SHELL_COMPLETED" if proc_result.returncode == 0 else "SHELL_FAILED"
            self._record_to_ledger(event_type, command, result)

            return result

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {self._timeout}s: {command}")
            result = ShellResult(
                command=command,
                exit_code=124,  # Standard timeout exit code
                blocked=False,
                error=f"Command timed out after {self._timeout} seconds",
            )
            # ⚡ PRATYAHARA: Record timeout
            self._record_to_ledger("SHELL_TIMEOUT", command, result)
            return result
        except FileNotFoundError:
            logger.error("steward CLI not found in PATH")
            result = ShellResult(
                command=command,
                exit_code=127,  # Command not found
                blocked=False,
                error="steward CLI not found - is it installed?",
            )
            # ⚡ PRATYAHARA: Record error
            self._record_to_ledger("SHELL_ERROR", command, result)
            return result
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            result = ShellResult(
                command=command,
                exit_code=1,
                blocked=False,
                error=str(e),
            )
            # ⚡ PRATYAHARA: Record error
            self._record_to_ledger("SHELL_ERROR", command, result)
            return result
