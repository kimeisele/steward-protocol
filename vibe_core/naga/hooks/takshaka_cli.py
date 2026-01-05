"""
Takshaka CLI Hook - Security Guardian

TAKSHAKA: King of serpents, known for his BITE.
Validates CLI arguments for toxic patterns (injection, traversal, etc.)

Phase: PRE_VALIDATE (runs FIRST - security before everything)

When Takshaka detects toxicity:
- Block execution immediately
- Record violation in context
- Optionally dispatch to correction (soft mode)

GAD-000: "Security is not optional, it's foundational"
"""

import logging
import re
from typing import TYPE_CHECKING, List, Optional

from vibe_core.protocols.cli_execution import (
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIHookProtocol,
    CLIHookResult,
)

if TYPE_CHECKING:
    from vibe_core.naga.services.takshaka import Takshaka

logger = logging.getLogger("TAKSHAKA_CLI")


# =============================================================================
# TOXIC PATTERNS - Command Injection Detection
# =============================================================================

# Shell injection patterns
SHELL_INJECTION_PATTERNS: List[str] = [
    r";\s*\w+",  # Command chaining
    r"\|\s*\w+",  # Pipe to command
    r"`[^`]+`",  # Backtick execution
    r"\$\([^)]+\)",  # Command substitution
    r"&&\s*\w+",  # AND chaining
    r"\|\|\s*\w+",  # OR chaining
]

# Path traversal patterns
PATH_TRAVERSAL_PATTERNS: List[str] = [
    r"\.\./",  # Parent directory
    r"\.\.\\",  # Windows parent
    r"/etc/",  # System files
    r"/proc/",  # Process info
    r"~root",  # Root home
]

# Dangerous flags
DANGEROUS_FLAGS: List[str] = [
    "--rm",  # Remove (if not expected)
    "--force",  # Force operations
    "-rf",  # Recursive force
    "--no-verify",  # Skip verification
    "--allow-insecure",  # Bypass security
]


class TakshakaCLIHook(CLIHookProtocol):
    """
    Takshaka CLI Hook - Security validation at PRE_VALIDATE phase.

    Scans all CLI arguments for toxic patterns:
    - Shell injection (;, |, `, $())
    - Path traversal (../)
    - Dangerous flags (--force, -rf)

    Modes:
    - Soft (flooding): Log and allow (observation only)
    - Hard (biting): Block execution
    """

    def __init__(
        self,
        takshaka: Optional["Takshaka"] = None,
        hard_mode: bool = True,
    ) -> None:
        """
        Initialize Takshaka CLI hook.

        Args:
            takshaka: Optional Takshaka service for advanced scanning
            hard_mode: If True, block on toxicity. If False, log only.
        """
        self._takshaka = takshaka
        self._hard_mode = hard_mode
        self._compiled_shell = [re.compile(p) for p in SHELL_INJECTION_PATTERNS]
        self._compiled_path = [re.compile(p) for p in PATH_TRAVERSAL_PATTERNS]

    @property
    def hook_id(self) -> str:
        return "takshaka"

    def on_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> CLIHookResult:
        """
        Process CLI at PRE_VALIDATE phase.

        Scans arguments for toxic patterns.
        """
        if phase != CLIExecutionPhase.PRE_VALIDATE:
            return CLIHookResult(allow=True)

        # Scan each argument
        for arg in context.args:
            # Check shell injection
            for pattern in self._compiled_shell:
                if pattern.search(arg):
                    return self._handle_toxicity(
                        context,
                        f"Shell injection pattern detected: {pattern.pattern}",
                        arg,
                    )

            # Check path traversal
            for pattern in self._compiled_path:
                if pattern.search(arg):
                    return self._handle_toxicity(
                        context,
                        f"Path traversal detected: {pattern.pattern}",
                        arg,
                    )

            # Check dangerous flags
            for flag in DANGEROUS_FLAGS:
                if arg == flag or arg.startswith(flag + "="):
                    return self._handle_toxicity(
                        context,
                        f"Dangerous flag detected: {flag}",
                        arg,
                    )

        # If Takshaka service available, use advanced scanning
        if self._takshaka:
            full_input = " ".join(context.args)
            report = self._takshaka.scan_toxicity(full_input)
            if report.blocked:
                return self._handle_toxicity(
                    context,
                    f"Takshaka blocked: {report.patterns}",
                    full_input,
                )

        # All clear
        logger.debug(f"Takshaka approved: {context.command_name} {context.args}")
        return CLIHookResult(allow=True)

    def _handle_toxicity(
        self,
        context: CLIExecutionContext,
        reason: str,
        toxic_input: str,
    ) -> CLIHookResult:
        """
        Handle detected toxicity.

        In hard mode: Block execution
        In soft mode: Log and allow (flooding)
        """
        logger.warning(f"TAKSHAKA: {reason} in '{toxic_input}'")

        if self._hard_mode:
            # BITE - block execution
            return CLIHookResult(
                allow=False,
                reason=f"Security violation: {reason}",
            )
        else:
            # FLOOD - observe only
            logger.info(f"Takshaka (soft mode): Would block '{toxic_input}'")
            return CLIHookResult(allow=True)

    def set_hard_mode(self, enabled: bool) -> None:
        """Toggle hard mode (blocking) vs soft mode (flooding)."""
        self._hard_mode = enabled
        mode = "BITING" if enabled else "FLOODING"
        logger.info(f"Takshaka mode changed to: {mode}")
