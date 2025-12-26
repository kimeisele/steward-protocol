"""
OPUS-311 Sprint 1: Governance Gate Protocol

The Identity Crisis must end.
No more anonymous mode for dangerous operations.

Permission check BEFORE every command execution.

Usage:
    gate = GovernanceGate()
    permission = gate.can_execute(identity, "delete_agent", context)
    if not permission.allowed:
        return CommandResult(error=f"Denied: {permission.reason}")
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Set, runtime_checkable


class PermissionLevel(Enum):
    """Permission levels for commands."""

    PUBLIC = "public"  # Anyone can execute
    AUTHENTICATED = "authenticated"  # Needs identity
    ELEVATED = "elevated"  # Needs explicit grant
    ADMIN = "admin"  # Only admins
    SYSTEM = "system"  # Only kernel/system


class DenialReason(Enum):
    """Why permission was denied."""

    ANONYMOUS = "anonymous_not_allowed"
    INSUFFICIENT_LEVEL = "insufficient_permission_level"
    COMMAND_DISABLED = "command_disabled"
    RATE_LIMITED = "rate_limited"
    CONTEXT_VIOLATION = "context_violation"
    GOVERNANCE_OVERRIDE = "governance_override"


@dataclass
class Identity:
    """
    Who is executing the command.

    Could be:
    - Human operator (via CLI)
    - Agent (via syscall)
    - System (via scheduler)
    """

    id: str  # Unique identifier
    type: str = "anonymous"  # "human", "agent", "system", "anonymous"
    roles: Set[str] = field(default_factory=set)
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_anonymous(self) -> bool:
        return self.type == "anonymous"

    @property
    def is_system(self) -> bool:
        return self.type == "system"

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles


# Singleton anonymous identity
ANONYMOUS = Identity(id="anonymous", type="anonymous")

# Singleton system identity
SYSTEM = Identity(id="system", type="system", roles={"admin", "system"})


@dataclass
class ExecutionContext:
    """Context for permission check."""

    command: str
    args: List[str] = field(default_factory=list)
    caller: str = "cli"  # "cli", "agent", "api", "scheduler"
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PermissionResult:
    """Result of permission check."""

    allowed: bool
    reason: Optional[DenialReason] = None
    message: str = ""
    required_level: Optional[PermissionLevel] = None
    actual_level: Optional[PermissionLevel] = None

    @staticmethod
    def allow() -> "PermissionResult":
        return PermissionResult(allowed=True)

    @staticmethod
    def deny(reason: DenialReason, message: str = "") -> "PermissionResult":
        return PermissionResult(allowed=False, reason=reason, message=message)


@runtime_checkable
class GovernanceGateProtocol(Protocol):
    """
    OPUS-311: Permission check before every execution.

    The last line of defense against:
    - Anonymous execution of dangerous commands
    - Privilege escalation
    - Rogue agents

    Must be called before CommandRegistry.execute().
    """

    def can_execute(
        self,
        identity: Identity,
        command: str,
        context: ExecutionContext,
    ) -> PermissionResult:
        """
        Check if identity can execute command in context.

        Returns:
            PermissionResult with allowed/denied and reason
        """
        ...

    def get_required_level(self, command: str) -> PermissionLevel:
        """Get the required permission level for a command."""
        ...

    def set_command_level(self, command: str, level: PermissionLevel) -> None:
        """Set the required permission level for a command."""
        ...

    def disable_command(self, command: str, reason: str) -> None:
        """Disable a command entirely."""
        ...

    def enable_command(self, command: str) -> None:
        """Re-enable a disabled command."""
        ...


class NullGovernanceGate:
    """
    Arjuna Pattern: Allow everything.

    WARNING: Only use in dev/test environments!
    """

    def can_execute(
        self,
        identity: Identity,
        command: str,
        context: ExecutionContext,
    ) -> PermissionResult:
        return PermissionResult.allow()

    def get_required_level(self, command: str) -> PermissionLevel:
        return PermissionLevel.PUBLIC

    def set_command_level(self, command: str, level: PermissionLevel) -> None:
        pass

    def disable_command(self, command: str, reason: str) -> None:
        pass

    def enable_command(self, command: str) -> None:
        pass


class GovernanceGate:
    """
    OPUS-311: Real implementation of GovernanceGateProtocol.

    Default behavior:
    - PUBLIC commands: Anyone can execute
    - AUTHENTICATED: Requires non-anonymous identity
    - ELEVATED: Requires explicit capability grant
    - ADMIN: Requires admin role
    - SYSTEM: Only kernel/system identity
    """

    # Commands that are dangerous and require authentication
    DANGEROUS_PATTERNS = [
        "delete",
        "destroy",
        "kill",
        "drop",
        "remove",
        "wipe",
        "purge",
        "reset",
        "narasimha",  # Kill-switch
    ]

    # Commands that are always safe
    SAFE_COMMANDS = {
        "help",
        "status",
        "version",
        "commands",
        "list",
        "show",
        "get",
        "info",
        "health",
    }

    def __init__(self):
        self._command_levels: Dict[str, PermissionLevel] = {}
        self._disabled_commands: Dict[str, str] = {}  # command -> reason
        self._setup_defaults()

    def _setup_defaults(self) -> None:
        """Setup default permission levels."""
        # Safe commands are public
        for cmd in self.SAFE_COMMANDS:
            self._command_levels[cmd] = PermissionLevel.PUBLIC

    def can_execute(
        self,
        identity: Identity,
        command: str,
        context: ExecutionContext,
    ) -> PermissionResult:
        """Check if identity can execute command."""

        # Check if command is disabled
        if command in self._disabled_commands:
            return PermissionResult.deny(
                DenialReason.COMMAND_DISABLED,
                f"Command '{command}' is disabled: {self._disabled_commands[command]}",
            )

        # Get required level
        required = self.get_required_level(command)

        # Check permission based on level
        if required == PermissionLevel.PUBLIC:
            return PermissionResult.allow()

        if required == PermissionLevel.AUTHENTICATED:
            if identity.is_anonymous:
                return PermissionResult.deny(
                    DenialReason.ANONYMOUS,
                    f"Command '{command}' requires authentication. Run 'steward auth' or set identity.",
                )
            return PermissionResult.allow()

        if required == PermissionLevel.ELEVATED:
            if identity.is_anonymous:
                return PermissionResult.deny(
                    DenialReason.ANONYMOUS,
                    f"Command '{command}' requires elevated permissions.",
                )
            # Check for explicit capability
            if command not in identity.capabilities and not identity.is_admin:
                return PermissionResult.deny(
                    DenialReason.INSUFFICIENT_LEVEL,
                    f"Command '{command}' requires explicit grant. Current capabilities: {identity.capabilities}",
                )
            return PermissionResult.allow()

        if required == PermissionLevel.ADMIN:
            if not identity.is_admin:
                return PermissionResult.deny(
                    DenialReason.INSUFFICIENT_LEVEL,
                    f"Command '{command}' requires admin role.",
                )
            return PermissionResult.allow()

        if required == PermissionLevel.SYSTEM:
            if not identity.is_system:
                return PermissionResult.deny(
                    DenialReason.INSUFFICIENT_LEVEL,
                    f"Command '{command}' is system-only.",
                )
            return PermissionResult.allow()

        # Default: deny
        return PermissionResult.deny(
            DenialReason.GOVERNANCE_OVERRIDE,
            "Unknown permission level.",
        )

    def get_required_level(self, command: str) -> PermissionLevel:
        """Get required permission level for command."""
        # Explicit level set?
        if command in self._command_levels:
            return self._command_levels[command]

        # Check for dangerous patterns
        cmd_lower = command.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in cmd_lower:
                return PermissionLevel.ELEVATED

        # Check if it's a known safe command
        base_cmd = command.split(".")[0] if "." in command else command
        if base_cmd in self.SAFE_COMMANDS:
            return PermissionLevel.PUBLIC

        # Default: authenticated
        return PermissionLevel.AUTHENTICATED

    def set_command_level(self, command: str, level: PermissionLevel) -> None:
        """Set required permission level for command."""
        self._command_levels[command] = level

    def disable_command(self, command: str, reason: str) -> None:
        """Disable a command."""
        self._disabled_commands[command] = reason

    def enable_command(self, command: str) -> None:
        """Re-enable a disabled command."""
        self._disabled_commands.pop(command, None)
