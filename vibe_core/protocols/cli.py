"""
OPUS-307 Phase E+: CLI Protocol

GAD-000 COMPLIANCE: CLI commands must be:
1. Discoverable - registered, not hardcoded
2. Observable - introspectable via protocol
3. Parseable - structured output
4. Composable - can be combined
5. Idempotent - same input = same output

THE ANTI-GOD-OBJECT PRINCIPLE:
UnifiedCLI should NOT know about individual CLI handlers.
It discovers them via CLIRegistry (same pattern as CapabilityRegistry).

PROMPT.md Compliance:
- "Protocol statt konkrete Klassen (Dependency Inversion)"
- "Wir akzeptieren keine 'ungefähren' Lösungen"
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Type, runtime_checkable

# Import capability types for NAGA CLI hook integration
from vibe_core.protocols.cli_execution import CLIPermissionLevel


@dataclass
class CLIResult:
    """
    Structured result from CLI command execution.

    GAD-000: All outputs must be machine-readable.
    """

    success: bool
    exit_code: int = 0
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # For composability
    raw_output: str = ""


@dataclass
class CLIMeta:
    """
    Metadata for CLI command discovery.

    GAD-000: All commands must be discoverable.
    NAGA CLI Hooks: Capability declarations for Level -2 governance.
    """

    command: str  # The CLI command name (e.g., "knowledge", "standards")
    description: str
    version: str = "1.0.0"

    # Subcommands this CLI supports
    subcommands: List[str] = field(default_factory=list)

    # For categorization
    domain: str = "system"  # e.g., "knowledge", "operations", "governance"
    tags: List[str] = field(default_factory=list)

    # NAGA CLI Hook Integration (Phase 4)
    # Permission level required to execute this command
    permission_level: CLIPermissionLevel = CLIPermissionLevel.PUBLIC

    # Specific capabilities required (e.g., ["cli.naga.status", "cli.tool.execute"])
    # These are checked by CapabilityCLIHook against the caller's token
    capabilities_required: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"<CLI:{self.command}>"


@runtime_checkable
class CLIHandler(Protocol):
    """
    Protocol for CLI command handlers.

    Any class implementing this protocol can be registered
    with CLIRegistry and discovered by UnifiedCLI.

    PROMPT.md: "Protocol statt konkrete Klassen"
    """

    @property
    @abstractmethod
    def meta(self) -> CLIMeta:
        """Return CLI metadata for discovery."""
        ...

    @abstractmethod
    def run(self, args: List[str]) -> int:
        """
        Execute the CLI command.

        Args:
            args: Command-line arguments (after the command name)

        Returns:
            Exit code (0 = success)
        """
        ...


class CLIRegistry:
    """
    Central registry for CLI handlers.

    THE ANTI-GOD-OBJECT:
    Instead of hardcoding CLI handlers in UnifiedCLI,
    they register themselves here and are discovered dynamically.

    Usage:
        # In knowledge_cli.py:
        CLIRegistry.register(KnowledgeCLI)

        # In unified_cli.py:
        for handler in CLIRegistry.all():
            if command == handler.meta.command:
                return handler.run(args)
    """

    _handlers: Dict[str, Type[CLIHandler]] = {}
    _instances: Dict[str, CLIHandler] = {}

    @classmethod
    def register(cls, handler_class: Type[CLIHandler]) -> None:
        """
        Register a CLI handler class.

        The handler is instantiated lazily on first use.
        """
        # Create temporary instance to get metadata
        instance = handler_class()
        command = instance.meta.command
        cls._handlers[command] = handler_class
        cls._instances[command] = instance

    @classmethod
    def get(cls, command: str) -> Optional[CLIHandler]:
        """Get handler instance for a command."""
        if command in cls._instances:
            return cls._instances[command]
        if command in cls._handlers:
            cls._instances[command] = cls._handlers[command]()
            return cls._instances[command]
        return None

    @classmethod
    def has(cls, command: str) -> bool:
        """Check if command is registered."""
        return command in cls._handlers

    @classmethod
    def all(cls) -> List[CLIHandler]:
        """Get all registered handler instances."""
        # Ensure all handlers are instantiated
        for cmd, handler_class in cls._handlers.items():
            if cmd not in cls._instances:
                cls._instances[cmd] = handler_class()
        return list(cls._instances.values())

    @classmethod
    def commands(cls) -> List[str]:
        """List all registered command names."""
        return list(cls._handlers.keys())

    @classmethod
    def discover(cls) -> Dict[str, CLIMeta]:
        """
        Discover all registered CLIs with their metadata.

        GAD-000: Everything must be discoverable.
        """
        return {cmd: handler.meta for cmd, handler in cls._instances.items()}

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._handlers.clear()
        cls._instances.clear()


def register_cli(cls: Type[CLIHandler]) -> Type[CLIHandler]:
    """
    Decorator to register a CLI handler.

    ANANTA PATTERN: Registration = Automatic Governance

    Like water flowing into every crevice, @register_cli automatically
    wraps ALL cmd_* and _cmd_* methods with @cli_governed.

    This eliminates manual decoration and ensures:
    - No command can escape NAGA observation
    - New commands are automatically governed
    - Self-healing infrastructure (GAD-000 Principle 6)

    Usage:
        @register_cli
        class KnowledgeCLI:
            @property
            def meta(self) -> CLIMeta:
                return CLIMeta(command="knowledge", ...)

            def run(self, args: List[str]) -> int:
                ...

            def cmd_list(self, args): ...  # AUTO-GOVERNED!
            def cmd_show(self, args): ...  # AUTO-GOVERNED!
    """
    # === ANANTA: Auto-wrap all cmd_* methods with cli_governed ===
    try:
        from vibe_core.naga.services.base import cli_governed

        for name in dir(cls):
            if name.startswith(("cmd_", "_cmd_")):
                method = getattr(cls, name)
                # Only wrap if callable and not already wrapped
                if callable(method) and not hasattr(method, "__wrapped__"):
                    wrapped = cli_governed()(method)
                    setattr(cls, name, wrapped)
    except ImportError:
        # Graceful degradation if NAGA not available
        pass

    CLIRegistry.register(cls)
    return cls
