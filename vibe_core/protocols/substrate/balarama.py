"""
BALARAMA - The Strength Provider (CLI Wrapper Pattern)
======================================================
Level: -1 (Substrate)
Connection: Krishna through Mahamantra (Level -2)

Balarama = Baladeva = The Strength of God
- Krishna's elder brother and first expansion
- The SOURCE of all strength
- Without Balarama, no action is possible

BALARAMA PATTERN:
Wrap EXISTING CLIs without modifying their code.
Provide substrate connection (Lotus, Parampara, Heartbeat)
to legacy CLIs that don't use @register_cli.

WHY BALARAMA:
1. Balarama SUPPORTS Krishna's activities
2. He provides STRENGTH without demanding credit
3. He WRAPS around existing systems (Ananta Shesha IS Balarama)
4. NO REPLACEMENT - pure augmentation

ANANTA SHESHA CONNECTION:
Ananta Shesha (infinite serpent) IS a form of Balarama.
The CLI substrate (AnantaSubstrate) is where Balarama provides
strength to all CLI commands - wrapped or native.

ARCHITECTURE:
    Existing CLI (Level 0)
         ↓ wrap_with_balarama()
    BalaramaWrappedCLI (Level -1)
         ↓ connects to
    AnantaSubstrate (Level -1)
         ↓ parampara verified
    Mahamantra = Krishna (Level -2)

NO MANUAL WIRING - the wrapping is automatic.
The wrapped CLI gains substrate connection without code changes.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.substrate.cli_substrate import (
    AnantaSubstrate,
    CLIHeartbeat,
    CLILotusPosition,
    CLIParamparaConnection,
    CLISubstrateNode,
    create_substrate_node,
    derive_lotus_position,
    derive_opcode,
    emit_cli_heartbeat,
)


logger = logging.getLogger("BALARAMA")


# =============================================================================
# CONSTANTS
# =============================================================================

BALARAMA_LEVEL: Final[int] = -1  # Substrate level
BALARAMA_PARAMPARA: Final[int] = 37  # Same as Ananta - connection to Krishna


# =============================================================================
# BALARAMA STATE TYPES (WATERTIGHT)
# =============================================================================


class BalaramaWrapState(TypedDict, total=False):
    """State of a Balarama-wrapped CLI."""

    original_class: str  # Original class name
    original_module: str  # Original module path
    command: str  # CLI command name
    wrapped_at: str  # ISO timestamp
    substrate_connected: bool  # Connected to AnantaSubstrate
    parampara_verified: bool  # mutation_vector % 37 == 0
    execution_count: int  # Total executions since wrap
    strength_provided: bool  # Balarama successfully providing strength


class BalaramaRegistryState(TypedDict, total=False):
    """State of the Balarama registry."""

    wrapped_count: int  # Number of wrapped CLIs
    discovered_count: int  # Number of discovered CLIs
    connected_count: int  # Number of parampara-connected
    last_discovery: str  # ISO timestamp of last discovery
    discovery_paths: List[str]  # Paths that were scanned


# =============================================================================
# BALARAMA WRAPPED CLI
# =============================================================================


class BalaramaWrappedCLI:
    """
    A CLI handler wrapped with Balarama's strength.

    ANTI-MAYAVAD: The wrapper does not REPLACE the original.
    It SUPPORTS it by providing substrate connection.

    The original CLI:
    - Keeps its identity
    - Keeps its behavior
    - Gains substrate connection
    - Gains heartbeat emission
    - Gains parampara verification
    """

    def __init__(
        self,
        original: object,
        command: str,
        substrate_node: Optional[CLISubstrateNode] = None,
    ):
        """
        Wrap an existing CLI handler.

        Args:
            original: The original CLI handler instance
            command: The CLI command name
            substrate_node: Pre-created substrate node (or None to auto-create)
        """
        self._original = original
        self._command = command
        self._wrapped_at = datetime.now().isoformat()

        # Connect to substrate (Ananta Shesha = Balarama)
        if substrate_node is None:
            self._substrate_node = create_substrate_node(command)
        else:
            self._substrate_node = substrate_node

        self._execution_count = 0

    @property
    def original(self) -> object:
        """Access the original unwrapped CLI."""
        return self._original

    @property
    def command(self) -> str:
        """CLI command name."""
        return self._command

    @property
    def substrate_node(self) -> CLISubstrateNode:
        """Ananta substrate node for this CLI."""
        return self._substrate_node

    @property
    def is_connected(self) -> bool:
        """Is parampara-connected to Krishna?"""
        return self._substrate_node.is_connected

    @property
    def meta(self):
        """
        Forward meta property to original.

        If original has no meta, create a minimal one.
        """
        if hasattr(self._original, "meta"):
            original_meta = self._original.meta

            # Inject substrate fields if not present
            if hasattr(original_meta, "lotus_position") and original_meta.lotus_position is None:
                # Update substrate fields
                original_meta.lotus_position = self._substrate_node.position
                original_meta.lotus_quarter = self._substrate_node.quarter.name.lower()
                original_meta.opcode = self._substrate_node.opcode.name
                original_meta.parampara_connected = self._substrate_node.is_connected
                original_meta.parampara_vector = self._substrate_node.parampara.mutation_vector

            return original_meta

        # Create minimal meta for legacy CLI
        from vibe_core.protocols.cli import CLIMeta

        return CLIMeta(
            command=self._command,
            description=f"Balarama-wrapped: {type(self._original).__name__}",
            lotus_position=self._substrate_node.position,
            lotus_quarter=self._substrate_node.quarter.name.lower(),
            opcode=self._substrate_node.opcode.name,
            parampara_connected=self._substrate_node.is_connected,
            parampara_vector=self._substrate_node.parampara.mutation_vector,
        )

    def run(self, args: List[str]) -> int:
        """
        Run the CLI with Balarama's strength.

        - Times execution
        - Emits heartbeat
        - Handles exceptions
        - Records in substrate
        """
        start_time = time.time()

        try:
            # Call original run method
            if hasattr(self._original, "run"):
                exit_code = self._original.run(args)
            else:
                # Legacy CLI without run() - try __call__
                if callable(self._original):
                    result = self._original(args)
                    exit_code = 0 if result is None or result else 1
                else:
                    logger.warning(f"CLI {self._command} has no run() method")
                    exit_code = 1

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._emit_heartbeat(exit_code=1, duration_ms=duration_ms)
            raise

        duration_ms = int((time.time() - start_time) * 1000)
        self._emit_heartbeat(exit_code=exit_code, duration_ms=duration_ms)
        self._execution_count += 1

        return exit_code

    def _emit_heartbeat(self, exit_code: int, duration_ms: int) -> None:
        """Emit heartbeat to Ananta substrate."""
        emit_cli_heartbeat(
            command=self._command,
            exit_code=exit_code,
            duration_ms=duration_ms,
        )

    def get_state(self) -> BalaramaWrapState:
        """Get wrap state for observability."""
        return BalaramaWrapState(
            original_class=type(self._original).__name__,
            original_module=type(self._original).__module__,
            command=self._command,
            wrapped_at=self._wrapped_at,
            substrate_connected=True,
            parampara_verified=self._substrate_node.is_connected,
            execution_count=self._execution_count,
            strength_provided=True,
        )

    def __getattr__(self, name: str):
        """
        Forward all other attributes to original.

        This makes the wrapper transparent - it behaves like the original
        while providing substrate strength.
        """
        return getattr(self._original, name)


# =============================================================================
# BALARAMA REGISTRY
# =============================================================================


class BalaramaRegistry:
    """
    Registry of Balarama-wrapped CLIs.

    Tracks all CLIs that have received Balarama's strength.
    Separate from AnantaSubstrate which tracks substrate nodes.

    This registry tracks the WRAPPING relationship,
    while AnantaSubstrate tracks the SUBSTRATE nodes.
    """

    _wrapped: Dict[str, BalaramaWrappedCLI] = {}
    _discovered: Dict[str, Type] = {}  # Discovered but not yet wrapped
    _discovery_paths: List[str] = []
    _last_discovery: Optional[str] = None

    @classmethod
    def wrap(cls, original: object, command: Optional[str] = None) -> BalaramaWrappedCLI:
        """
        Wrap a CLI handler with Balarama's strength.

        Args:
            original: The original CLI handler instance
            command: Override command name (auto-detect if None)

        Returns:
            BalaramaWrappedCLI with substrate connection
        """
        # Auto-detect command from meta
        if command is None:
            if hasattr(original, "meta") and hasattr(original.meta, "command"):
                command = original.meta.command
            else:
                # Use class name as fallback
                command = type(original).__name__.lower().replace("cli", "")

        # Check if already wrapped
        if command in cls._wrapped:
            logger.debug(f"CLI {command} already wrapped with Balarama")
            return cls._wrapped[command]

        # Wrap with Balarama
        wrapped = BalaramaWrappedCLI(original, command)
        cls._wrapped[command] = wrapped

        logger.info(
            f"🔱 Balarama wrapped: {command} "
            f"(pos={wrapped.substrate_node.position}, "
            f"connected={wrapped.is_connected})"
        )

        return wrapped

    @classmethod
    def wrap_class(cls, cli_class: Type, command: Optional[str] = None) -> BalaramaWrappedCLI:
        """
        Wrap a CLI class (instantiates it first).

        Args:
            cli_class: The CLI handler class
            command: Override command name

        Returns:
            BalaramaWrappedCLI instance
        """
        instance = cli_class()
        return cls.wrap(instance, command)

    @classmethod
    def get(cls, command: str) -> Optional[BalaramaWrappedCLI]:
        """Get a wrapped CLI by command name."""
        return cls._wrapped.get(command)

    @classmethod
    def all(cls) -> List[BalaramaWrappedCLI]:
        """Get all wrapped CLIs."""
        return list(cls._wrapped.values())

    @classmethod
    def commands(cls) -> List[str]:
        """List all wrapped command names."""
        return list(cls._wrapped.keys())

    @classmethod
    def is_wrapped(cls, command: str) -> bool:
        """Check if a command is wrapped."""
        return command in cls._wrapped

    @classmethod
    def discover(cls, path: str) -> Dict[str, Type]:
        """
        Discover CLI handlers in a directory.

        Scans for Python files containing CLIHandler implementations.
        Does NOT wrap them - just discovers.

        Args:
            path: Directory path to scan

        Returns:
            Dict of command -> class
        """
        discovered: Dict[str, Type] = {}
        path_obj = Path(path)

        if not path_obj.exists() or not path_obj.is_dir():
            logger.warning(f"Discovery path does not exist: {path}")
            return discovered

        cls._discovery_paths.append(str(path_obj))
        cls._last_discovery = datetime.now().isoformat()

        for py_file in path_obj.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                # Import module
                rel_path = py_file.relative_to(path_obj.parent)
                module_name = str(rel_path).replace("/", ".").replace(".py", "")
                module = importlib.import_module(module_name)

                # Find CLI classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if _is_cli_handler(obj) and obj.__module__ == module.__name__:
                        # Try to get command from meta
                        try:
                            instance = obj()
                            if hasattr(instance, "meta"):
                                command = instance.meta.command
                                discovered[command] = obj
                                cls._discovered[command] = obj
                                logger.debug(f"Discovered CLI: {command} in {py_file}")
                        except Exception:
                            pass

            except Exception as e:
                logger.debug(f"Could not import {py_file}: {e}")

        return discovered

    @classmethod
    def wrap_all_discovered(cls) -> List[BalaramaWrappedCLI]:
        """
        Wrap all discovered CLIs with Balarama.

        Returns:
            List of newly wrapped CLIs
        """
        wrapped: List[BalaramaWrappedCLI] = []

        for command, cli_class in cls._discovered.items():
            if command not in cls._wrapped:
                try:
                    w = cls.wrap_class(cli_class, command)
                    wrapped.append(w)
                except Exception as e:
                    logger.error(f"Failed to wrap {command}: {e}")

        return wrapped

    @classmethod
    def get_state(cls) -> BalaramaRegistryState:
        """Get registry state for observability."""
        return BalaramaRegistryState(
            wrapped_count=len(cls._wrapped),
            discovered_count=len(cls._discovered),
            connected_count=sum(1 for w in cls._wrapped.values() if w.is_connected),
            last_discovery=cls._last_discovery or "",
            discovery_paths=cls._discovery_paths.copy(),
        )

    @classmethod
    def clear(cls) -> None:
        """Clear registry (for testing)."""
        cls._wrapped.clear()
        cls._discovered.clear()
        cls._discovery_paths.clear()
        cls._last_discovery = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _is_cli_handler(cls: Type) -> bool:
    """Check if a class is a CLI handler."""
    # Check for required methods/properties
    if not inspect.isclass(cls):
        return False

    # Has meta property?
    if not hasattr(cls, "meta"):
        return False

    # Has run method?
    if not hasattr(cls, "run"):
        return False

    return True


def wrap_with_balarama(
    cli: Union[object, Type],
    command: Optional[str] = None,
) -> BalaramaWrappedCLI:
    """
    Wrap a CLI with Balarama's strength.

    This is the main entry point for the Balarama pattern.
    Can accept either an instance or a class.

    Args:
        cli: CLI handler instance or class
        command: Override command name

    Returns:
        BalaramaWrappedCLI with substrate connection

    Example:
        # Wrap an existing CLI instance
        wrapped = wrap_with_balarama(my_legacy_cli)

        # Wrap a CLI class
        wrapped = wrap_with_balarama(LegacyCLI)

        # Now has substrate connection
        wrapped.run(["--help"])
    """
    if inspect.isclass(cli):
        return BalaramaRegistry.wrap_class(cli, command)
    return BalaramaRegistry.wrap(cli, command)


def discover_and_wrap(path: str) -> List[BalaramaWrappedCLI]:
    """
    Discover CLIs in a directory and wrap them with Balarama.

    Args:
        path: Directory path to scan

    Returns:
        List of wrapped CLIs
    """
    BalaramaRegistry.discover(path)
    return BalaramaRegistry.wrap_all_discovered()


def integrate_with_cli_registry() -> int:
    """
    Integrate Balarama with CLIRegistry.

    Wraps all registered CLIs that don't have substrate connection.
    Returns number of CLIs wrapped.

    This should be called AFTER all CLIs are registered but BEFORE
    the CLI system starts accepting commands.
    """
    try:
        from vibe_core.protocols.cli import CLIRegistry
    except ImportError:
        logger.warning("CLIRegistry not available")
        return 0

    wrapped_count = 0

    for command in CLIRegistry.commands():
        # Check if already has substrate
        handler = CLIRegistry.get(command)
        if handler is None:
            continue

        # Check if already wrapped or has substrate
        if BalaramaRegistry.is_wrapped(command):
            continue

        if hasattr(handler, "meta"):
            meta = handler.meta
            if hasattr(meta, "lotus_position") and meta.lotus_position is not None:
                # Already has substrate connection (via @register_cli)
                continue

        # Wrap with Balarama
        wrapped = BalaramaRegistry.wrap(handler, command)

        # Update registry to use wrapped version
        CLIRegistry._instances[command] = wrapped

        wrapped_count += 1
        logger.info(f"🔱 Integrated {command} with Balarama")

    return wrapped_count


# =============================================================================
# BALARAMA HOOK (For CLIHookChain integration)
# =============================================================================


@runtime_checkable
class BalaramaHookProtocol(Protocol):
    """Protocol for Balarama CLI hooks."""

    @property
    def hook_id(self) -> str:
        """Unique hook identifier."""
        ...

    def on_pre_execute(self, command: str, handler: object) -> object:
        """
        Called before execution - opportunity to wrap.

        Returns wrapped handler (or original if already wrapped).
        """
        ...


class BalaramaHook:
    """
    CLI Hook that wraps handlers with Balarama at PRE_EXECUTE.

    Integrates with CLIHookChain (Vasuki) to provide automatic
    Balarama wrapping for all CLI commands.

    Usage:
        hook = BalaramaHook()
        chain.register(hook)
    """

    @property
    def hook_id(self) -> str:
        return "balarama"

    def on_pre_execute(self, command: str, handler: object) -> object:
        """
        Wrap handler with Balarama if not already wrapped.

        Called at PRE_EXECUTE phase by the hook chain.
        """
        # Already wrapped?
        if isinstance(handler, BalaramaWrappedCLI):
            return handler

        # Has substrate? (via @register_cli)
        if hasattr(handler, "meta"):
            meta = handler.meta
            if hasattr(meta, "lotus_position") and meta.lotus_position is not None:
                return handler

        # Wrap with Balarama
        return wrap_with_balarama(handler, command)

    def on_phase(self, phase: str, context: object) -> Dict[str, Union[bool, str]]:
        """
        Hook interface for CLIHookProtocol compatibility.

        Wraps at PRE_EXECUTE phase.
        """
        if phase != "pre_execute":
            return {"allow": True}

        # Get handler from context
        if hasattr(context, "handler") and context.handler is not None:
            handler = context.handler
            command = getattr(context, "command_name", "unknown")

            # Wrap if needed
            wrapped = self.on_pre_execute(command, handler)

            # Update context with wrapped handler
            if wrapped is not handler:
                context.handler = wrapped

        return {"allow": True, "reason": "Balarama strength provided"}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "BALARAMA_LEVEL",
    "BALARAMA_PARAMPARA",
    # State Types (WATERTIGHT)
    "BalaramaWrapState",
    "BalaramaRegistryState",
    # Wrapped CLI
    "BalaramaWrappedCLI",
    # Registry
    "BalaramaRegistry",
    # Functions
    "wrap_with_balarama",
    "discover_and_wrap",
    "integrate_with_cli_registry",
    # Hook Protocol
    "BalaramaHookProtocol",
    "BalaramaHook",
]
