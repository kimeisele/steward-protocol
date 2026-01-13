"""
CLI Protocol - Contracts for the Fractal CLI System.

This defines the interfaces that plugins use to expose CLI commands.
GAD-000 Compliant: Handlers return structured data, not print().
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x13ec8dda"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Type


class ExecutionMode(Enum):
    """How a command should be executed."""

    OFFLINE = "offline"  # No kernel needed - file manipulation, config reads
    RPC = "rpc"  # Forward to running kernel via gateway API
    BOOT = "boot"  # Spin up ephemeral kernel, execute, shutdown
    HYBRID = "hybrid"  # Try RPC first, fallback to BOOT if kernel not running


@dataclass
class CLIArg:
    """Definition of a CLI argument."""

    name: str
    type: type  # str, int, bool, float, Path
    help: str
    required: bool = True
    default: Any = None
    choices: Optional[List[Any]] = None  # For enum-like args
    nargs: Optional[str] = None  # For list args: "+", "*", "?"

    def to_argparse_kwargs(self) -> Dict[str, Any]:
        """Convert to argparse.add_argument kwargs."""
        kwargs: Dict[str, Any] = {
            "help": self.help,
        }

        if not self.required:
            kwargs["default"] = self.default
            kwargs["required"] = False

        if self.type is bool:
            kwargs["action"] = "store_true"
        else:
            kwargs["type"] = self.type

        if self.choices:
            kwargs["choices"] = self.choices

        if self.nargs:
            kwargs["nargs"] = self.nargs

        return kwargs


@dataclass
class CLICommand:
    """
    Definition of a CLI command.

    Commands are discovered from plugin manifests and executed
    either locally (OFFLINE), via RPC (daemon mode), or by
    booting an ephemeral kernel (BOOT).
    """

    # Identity
    name: str
    namespace: Optional[str] = None  # Plugin namespace (e.g., "steward", "test")
    plugin_id: Optional[str] = None  # Plugin directory name for import resolution

    # Handler
    handler: str = ""  # Method name on plugin class
    execution_mode: ExecutionMode = ExecutionMode.HYBRID

    # Documentation
    help: str = ""
    args: List[CLIArg] = field(default_factory=list)

    # GAD-000 Compliance
    response_model: Type = Dict  # Pydantic model or dataclass for output
    renderer: Optional[str] = None  # Custom renderer method name

    # Streaming support
    supports_streaming: bool = False  # Handler is a generator?

    @property
    def full_name(self) -> str:
        """Get namespaced command name."""
        if self.namespace:
            return f"{self.namespace}:{self.name}"
        return self.name

    def to_argparse_name(self) -> str:
        """Get name for argparse subparser."""
        # Replace : with - for shell compatibility
        return self.full_name.replace(":", "-")


@dataclass
class CLIResponse:
    """
    Standard response wrapper for all CLI commands.

    GAD-000: Machine-readable by default.
    """

    success: bool
    data: Any  # The actual response_model instance
    error: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.OFFLINE
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "success": self.success,
            "data": self._serialize_data(self.data),
            "execution_mode": self.execution_mode.value,
        }
        if self.error:
            result["error"] = self.error
        if self.warnings:
            result["warnings"] = self.warnings
        return result

    def _serialize_data(self, data: Any) -> Any:
        """Serialize data to JSON-compatible format."""
        if hasattr(data, "to_dict"):
            return data.to_dict()
        if hasattr(data, "__dict__"):
            return {k: self._serialize_data(v) for k, v in data.__dict__.items()}
        if isinstance(data, (list, tuple)):
            return [self._serialize_data(item) for item in data]
        if isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}
        return data


@dataclass
class ProgressUpdate:
    """
    Progress update for streaming commands.

    Yielded by generator handlers to show progress to user.
    """

    status: Literal["starting", "running", "progress", "done", "error"]
    message: str
    percent: Optional[int] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "status": self.status,
            "message": self.message,
        }
        if self.percent is not None:
            result["percent"] = self.percent
        if self.data:
            result["data"] = self.data
        return result


# Type alias for command registry
CommandRegistry = Dict[str, CLICommand]
