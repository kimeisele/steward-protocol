"""
OPUS-310: Command Protocol - Universal Execution Layer

Every command in the system implements this protocol.
No exceptions. No special cases.

YANTRA (CommandProtocol) + MANTRA (CLI) = SIDDHI (Universal Execution)

Usage:
    class ChatCommand:
        name = "chat"
        description = "Chat with the cognitive layer"

        async def execute(self, args, context):
            return CommandResult(success=True, output="Hello!")

    registry.register(ChatCommand())
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class ParameterType(Enum):
    """Supported parameter types."""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FLOAT = "float"
    OBJECT = "object"
    ARRAY = "array"


@dataclass
class ParameterSpec:
    """Specification for a command parameter."""

    name: str
    param_type: ParameterType = ParameterType.STRING
    required: bool = False
    default: Optional[Any] = None
    description: str = ""


@dataclass
class CommandContext:
    """
    Context passed to command execution.

    Contains everything a command needs to execute.
    """

    kernel: Optional[Any] = None  # The kernel instance
    session_id: Optional[str] = None
    caller: str = "cli"  # "cli", "agent", "api"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandResult:
    """
    Result from command execution.

    Structured output for consistent handling.
    """

    success: bool
    output: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    exit_code: int = 0

    def __post_init__(self):
        if not self.success and self.exit_code == 0:
            self.exit_code = 1


@dataclass
class CommandInfo:
    """
    Metadata about a command for discovery.

    Used by MANAS to understand available capabilities.
    """

    name: str
    description: str
    parameters: List[ParameterSpec]
    source: str  # "core", "plugin:opus_assistant", "cartridge:civic"
    tags: List[str] = field(default_factory=list)


@runtime_checkable
class CommandProtocol(Protocol):
    """
    OPUS-310: Universal Command Interface.

    Every command implements this. No exceptions.

    The fractal property:
    - Core commands implement this
    - Plugin commands implement this
    - Cartridge commands implement this
    - Holon commands implement this

    Same interface, same power, everywhere.
    """

    @property
    def name(self) -> str:
        """
        Unique command name.

        Examples: 'chat', 'boot', 'civic.bank', 'my-agent.deploy'
        """
        ...

    @property
    def description(self) -> str:
        """Human-readable description for help and discovery."""
        ...

    @property
    def parameters(self) -> List[ParameterSpec]:
        """Parameter specifications for validation and help."""
        ...

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """
        Execute the command.

        Args:
            args: Command arguments (already parsed from CLI)
            context: Execution context (kernel, session, caller)

        Returns:
            CommandResult with success/failure and output
        """
        ...

    def validate(self, args: List[str]) -> List[str]:
        """
        Validate arguments before execution.

        Returns:
            List of validation errors (empty if valid)
        """
        ...


class BaseCommand:
    """
    Base implementation of CommandProtocol.

    Provides default implementations for common patterns.
    Inherit from this for convenience.
    """

    name: str = "unnamed"
    description: str = "No description"
    _parameters: List[ParameterSpec] = []
    source: str = "core"
    tags: List[str] = []

    @property
    def parameters(self) -> List[ParameterSpec]:
        return self._parameters

    def validate(self, args: List[str]) -> List[str]:
        """Default validation: check required parameters."""
        errors = []
        required_params = [p for p in self.parameters if p.required]

        for i, param in enumerate(required_params):
            if i >= len(args) or not args[i]:
                errors.append(f"Missing required parameter: {param.name}")

        return errors

    @abstractmethod
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Subclasses must implement this."""
        pass

    def get_info(self) -> CommandInfo:
        """Get command metadata for discovery."""
        return CommandInfo(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            source=self.source,
            tags=self.tags,
        )
