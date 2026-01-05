"""
Capability CLI Hook - Token Verification

NARADA CORRECTION: A UUID session_id is worthless - attacker generates new one.
The Capability Pass must be CRYPTOGRAPHICALLY BOUND to identity.

This hook verifies:
1. Token signature is valid (HMAC-SHA256)
2. Token is not expired
3. Required capabilities are granted

Phase: POST_VALIDATE (after args validated, before execution)

GAD-000 v2.0: "Notariell beglaubigt, not handgeschrieben"
"""

import logging
from typing import List, Optional

from vibe_core.protocols.cli_execution import (
    CLICapabilityToken,
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIHookProtocol,
    CLIHookResult,
    CLIPermissionLevel,
)

logger = logging.getLogger("CAPABILITY_CLI")


# =============================================================================
# CAPABILITY DEFINITIONS - Granular Permissions
# =============================================================================

# Command -> Required Capabilities mapping
COMMAND_CAPABILITIES: dict[str, List[str]] = {
    # NAGA commands
    "naga.status": ["cli.naga.status"],
    "naga.scan": ["cli.naga.scan.read"],
    "naga.chaos": ["cli.naga.chaos.run"],
    # Tool commands
    "tool.run": ["cli.tool.execute"],
    "tool.list": ["cli.public"],
    # Kernel commands
    "kernel.boot": ["cli.kernel.boot"],
    "kernel.stop": ["cli.kernel.stop"],
    # Default public
    "help": ["cli.public"],
    "version": ["cli.public"],
}

# Permission level -> minimum capabilities
PERMISSION_LEVEL_CAPS: dict[CLIPermissionLevel, List[str]] = {
    CLIPermissionLevel.PUBLIC: ["cli.public"],
    CLIPermissionLevel.AUTHENTICATED: ["cli.auth"],
    CLIPermissionLevel.PRIVILEGED: ["cli.privileged"],
    CLIPermissionLevel.KERNEL: ["cli.kernel"],
}


class CapabilityCLIHook(CLIHookProtocol):
    """
    Capability verification hook at POST_VALIDATE phase.

    Verifies capability tokens are:
    1. Cryptographically valid (signature check)
    2. Not expired
    3. Contain required capabilities for command

    Uses shared secret for HMAC verification.
    The secret should be injected from Kernel at boot.
    """

    def __init__(
        self,
        secret_key: Optional[bytes] = None,
        enforce: bool = True,
    ) -> None:
        """
        Initialize capability hook.

        Args:
            secret_key: Shared secret for HMAC verification (32+ bytes)
            enforce: If True, block invalid tokens. If False, log only.
        """
        self._secret_key = secret_key or b"dev-secret-replace-in-production"
        self._enforce = enforce

    @property
    def hook_id(self) -> str:
        return "capability"

    def on_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> CLIHookResult:
        """
        Verify capability token at POST_VALIDATE phase.
        """
        if phase != CLIExecutionPhase.POST_VALIDATE:
            return CLIHookResult(allow=True)

        token = context.capability_token

        # 1. Check token signature
        if not token.verify(self._secret_key):
            return self._handle_invalid(
                context,
                "Invalid token signature - possible forgery",
            )

        # 2. Check expiration
        if token.is_expired():
            return self._handle_invalid(
                context,
                f"Token expired at {token.expires_at}",
            )

        # 3. Get required capabilities for command
        command_key = f"{context.namespace}.{context.command_name}"
        required = self._get_required_capabilities(command_key, context.permission_level)
        context.capabilities_required = required

        # 4. Check each required capability
        for cap in required:
            if not token.has_capability(cap):
                return self._handle_invalid(
                    context,
                    f"Missing required capability: {cap}",
                )

        # All checks passed
        logger.debug(f"Capability check passed: {context.caller_id} -> {command_key}")
        return CLIHookResult(allow=True)

    def _get_required_capabilities(
        self,
        command_key: str,
        permission_level: CLIPermissionLevel,
    ) -> List[str]:
        """
        Get capabilities required for a command.

        Combines command-specific and permission-level requirements.
        """
        # Command-specific
        cmd_caps = COMMAND_CAPABILITIES.get(command_key, [])

        # Permission level minimum
        level_caps = PERMISSION_LEVEL_CAPS.get(permission_level, [])

        # Combine (deduplicated)
        all_caps = list(set(cmd_caps + level_caps))
        return all_caps if all_caps else ["cli.public"]

    def _handle_invalid(
        self,
        context: CLIExecutionContext,
        reason: str,
    ) -> CLIHookResult:
        """
        Handle invalid token.

        If enforce=True: Block execution
        If enforce=False: Log and allow (development mode)
        """
        logger.warning(f"CAPABILITY: {reason} for {context.caller_id} -> {context.command_name}")

        if self._enforce:
            return CLIHookResult(
                allow=False,
                reason=f"Capability denied: {reason}",
            )
        else:
            logger.info(f"Capability (dev mode): Would block - {reason}")
            return CLIHookResult(allow=True)

    def set_secret_key(self, key: bytes) -> None:
        """
        Set the secret key for HMAC verification.

        Should be called by Kernel at boot with production secret.
        """
        self._secret_key = key
        logger.info("Capability hook secret key updated")

    def set_enforce(self, enabled: bool) -> None:
        """Toggle enforcement mode."""
        self._enforce = enabled
        mode = "ENFORCING" if enabled else "PERMISSIVE"
        logger.info(f"Capability hook mode: {mode}")

    @staticmethod
    def register_command_capability(command_key: str, capabilities: List[str]) -> None:
        """
        Register capability requirements for a command.

        Allows dynamic capability registration from CLI handlers.
        """
        COMMAND_CAPABILITIES[command_key] = capabilities
        logger.debug(f"Registered capabilities for {command_key}: {capabilities}")
