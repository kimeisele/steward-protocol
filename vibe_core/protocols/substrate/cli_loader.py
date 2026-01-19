"""
CLI LOADER PROTOCOL - Substrate-Level CLI Discovery
====================================================

Layer -1: SUBSTRATE (shared foundation)

"yad yad acarati sresthas tat tad evetaro janah"
"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

PURPOSE:
    Universal CLI loader protocol for command discovery.
    Used by multiple consumers:
    - UnifiedCLI (main entry point)
    - CommandRegistry (aggregation)
    - Any system that needs CLI commands

DESIGN:
    - NO HARDCODED PATHS - config injected via protocol
    - Manifest-based discovery (YAML/JSON)
    - Watertight types - no Any
    - Protocol-first - interface before implementation

USAGE:
    from vibe_core.protocols.substrate.cli_loader import (
        CLILoaderProtocol,
        CLILoaderConfig,
        DiscoveredCommand,
    )

    class MyLoaderImpl(CLILoaderProtocol):
        def discover(self) -> List[DiscoveredCommand]:
            ...

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xe701edcd"  # GenesisByte: parampara % 37 == 0

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    TypedDict,
    runtime_checkable,
)


# =============================================================================
# WATERTIGHT TYPES
# =============================================================================


class ExecutionMode(str, Enum):
    """How a command should be executed."""

    OFFLINE = "offline"  # No kernel needed
    RPC = "rpc"  # Forward to running kernel
    BOOT = "boot"  # Spin up ephemeral kernel
    HYBRID = "hybrid"  # Try RPC, fallback BOOT


class CommandArgument(TypedDict, total=False):
    """Definition of a CLI argument. WATERTIGHT."""

    name: str  # Argument name (e.g., "--target")
    type: str  # Type name: "str", "int", "bool", "float", "path"
    help: str  # Help text
    required: bool  # Is required?
    default: str  # Default value (as string)
    choices: List[str]  # Valid choices
    flag: bool  # Is a boolean flag?


class DiscoveredCommand(TypedDict, total=False):
    """A discovered CLI command. WATERTIGHT."""

    name: str  # Command name
    namespace: str  # Namespace (e.g., "mahamantra")
    full_name: str  # Full name (namespace:name)
    handler: str  # Handler path (module:function)
    help: str  # Help text
    execution_mode: str  # ExecutionMode value
    arguments: List[CommandArgument]  # Command arguments
    source_manifest: str  # Path to manifest file
    source_module: str  # Module that provides this
    discovered_at: str  # ISO timestamp


class CLILoaderConfig(TypedDict, total=False):
    """
    Configuration for CLI loading. WATERTIGHT.

    Injected via protocol - NO HARDCODING.
    """

    scan_paths: List[str]  # Paths to scan for manifests
    manifest_patterns: List[str]  # Patterns: ["cli.yaml", "manifest.yaml"]
    exclude_patterns: List[str]  # Patterns to skip
    namespace_from_folder: bool  # Derive namespace from folder name
    recursive: bool  # Scan recursively
    max_depth: int  # Max recursion depth (0 = unlimited)


class LoaderProgress(TypedDict, total=False):
    """Progress during loading. WATERTIGHT."""

    paths_total: int
    paths_scanned: int
    commands_found: int
    current_path: str
    percent_complete: float
    started_at: str
    updated_at: str


class LoaderResult(TypedDict, total=False):
    """Result of a load operation. WATERTIGHT."""

    config: CLILoaderConfig
    paths_scanned: int
    commands_found: int
    commands_skipped: int
    commands_error: int
    by_namespace: Dict[str, int]  # Count per namespace
    by_mode: Dict[str, int]  # Count per execution mode
    commands: List[DiscoveredCommand]
    errors: List[str]
    started_at: str
    completed_at: str
    duration_seconds: float


# =============================================================================
# DEFAULT CONFIG
# =============================================================================


def get_default_config() -> CLILoaderConfig:
    """
    Get default CLI loader configuration.

    IMPORTANT: This is a FALLBACK. Proper config should come
    from Shuka/Phoenix config system.
    """
    return CLILoaderConfig(
        scan_paths=[
            # Core modules that can have CLI
            "vibe_core/mahamantra",
            "vibe_core/plugins",
            "vibe_core/cartridges",
            "vibe_core/naga",
            "vibe_core/shuddhi",
            "vibe_core/phoenix",
            "vibe_core/services",
        ],
        manifest_patterns=[
            "cli.yaml",
            "cli.json",
            "manifest.yaml",
            "manifest.json",
        ],
        exclude_patterns=[
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "test_",
            "_test.py",
            "tests/",
        ],
        namespace_from_folder=True,
        recursive=True,
        max_depth=3,
    )


# =============================================================================
# MANIFEST PARSING
# =============================================================================


def parse_manifest(
    manifest_path: Path,
    namespace: str,
) -> List[DiscoveredCommand]:
    """
    Parse CLI commands from a manifest file.

    Supports YAML and JSON formats.

    Args:
        manifest_path: Path to manifest file
        namespace: Default namespace for commands

    Returns:
        List of discovered commands
    """
    import json
    import yaml

    content = manifest_path.read_text()

    # Parse based on extension
    if manifest_path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(content)
    else:
        data = json.loads(content)

    if not data:
        return []

    commands: List[DiscoveredCommand] = []

    # Support both "cli:" section and "commands:" directly
    cli_section = data.get("cli", data)
    cmd_list = cli_section.get("commands", [])

    # Get namespace from manifest or folder
    manifest_namespace = cli_section.get("namespace", namespace)

    for cmd_data in cmd_list:
        if not isinstance(cmd_data, dict):
            continue

        name = cmd_data.get("name", "")
        if not name:
            continue

        # Parse arguments
        arguments: List[CommandArgument] = []
        for arg_data in cmd_data.get("options", cmd_data.get("args", [])):
            if isinstance(arg_data, dict):
                arguments.append(
                    CommandArgument(
                        name=arg_data.get("name", ""),
                        type=arg_data.get("type", "str"),
                        help=arg_data.get("help", ""),
                        required=arg_data.get("required", False),
                        default=str(arg_data.get("default", "")),
                        choices=arg_data.get("choices", []),
                        flag=arg_data.get("flag", False),
                    )
                )

        full_name = f"{manifest_namespace}:{name}" if manifest_namespace else name

        commands.append(
            DiscoveredCommand(
                name=name,
                namespace=manifest_namespace,
                full_name=full_name,
                handler=cmd_data.get("handler", ""),
                help=cmd_data.get("help", ""),
                execution_mode=cmd_data.get("execution_mode", ExecutionMode.HYBRID.value),
                arguments=arguments,
                source_manifest=str(manifest_path),
                source_module=str(manifest_path.parent),
                discovered_at=datetime.now().isoformat(),
            )
        )

    return commands


# =============================================================================
# CLI LOADER PROTOCOL
# =============================================================================


@runtime_checkable
class CLILoaderProtocol(Protocol):
    """
    Universal CLI loading protocol.

    Layer -1 SUBSTRATE - used by multiple consumers.

    Consumers:
        - UnifiedCLI
        - CommandRegistry
        - Any CLI system

    WATERTIGHT - no Any types!
    """

    # =========================================================================
    # Configuration
    # =========================================================================

    def get_config(self) -> CLILoaderConfig:
        """
        Get current loader configuration.

        Should come from Shuka/Phoenix config, not hardcoded.
        """
        ...

    def set_config(self, config: CLILoaderConfig) -> None:
        """Set loader configuration."""
        ...

    # =========================================================================
    # Discovery
    # =========================================================================

    def discover(self, path: Optional[str] = None) -> LoaderResult:
        """
        Discover CLI commands from manifests.

        Args:
            path: Path to scan (uses config.scan_paths if None)

        Returns:
            LoaderResult with all findings
        """
        ...

    def discover_path(self, path: str) -> List[DiscoveredCommand]:
        """
        Discover commands from a single path.

        Args:
            path: Path to scan for manifests

        Returns:
            List of discovered commands
        """
        ...

    def iter_commands(
        self,
        path: Optional[str] = None,
    ) -> Iterator[DiscoveredCommand]:
        """
        Iterate over commands lazily.

        For large codebases where loading all at once is too much.
        """
        ...

    # =========================================================================
    # Queries
    # =========================================================================

    def get_by_namespace(self, namespace: str) -> List[DiscoveredCommand]:
        """Get all commands in a namespace."""
        ...

    def get_by_mode(self, mode: str) -> List[DiscoveredCommand]:
        """Get all commands with execution mode."""
        ...

    def get_command(self, full_name: str) -> Optional[DiscoveredCommand]:
        """Get a specific command by full name."""
        ...

    # =========================================================================
    # Progress (for long discoveries)
    # =========================================================================

    def get_progress(self) -> Optional[LoaderProgress]:
        """Get current discovery progress (if discovering)."""
        ...

    def on_progress(
        self,
        callback: Callable[[LoaderProgress], None],
    ) -> None:
        """Register progress callback."""
        ...


# =============================================================================
# NULL LOADER (For testing)
# =============================================================================


class NullCLILoader:
    """
    Null implementation for testing.
    Returns empty results.
    """

    def __init__(self) -> None:
        self._config = get_default_config()
        self._progress: Optional[LoaderProgress] = None
        self._callbacks: List[Callable[[LoaderProgress], None]] = []

    def get_config(self) -> CLILoaderConfig:
        return self._config

    def set_config(self, config: CLILoaderConfig) -> None:
        self._config = config

    def discover(self, path: Optional[str] = None) -> LoaderResult:
        return LoaderResult(
            config=self._config,
            paths_scanned=0,
            commands_found=0,
            commands_skipped=0,
            commands_error=0,
            by_namespace={},
            by_mode={},
            commands=[],
            errors=[],
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            duration_seconds=0.0,
        )

    def discover_path(self, path: str) -> List[DiscoveredCommand]:
        return []

    def iter_commands(
        self,
        path: Optional[str] = None,
    ) -> Iterator[DiscoveredCommand]:
        return iter([])

    def get_by_namespace(self, namespace: str) -> List[DiscoveredCommand]:
        return []

    def get_by_mode(self, mode: str) -> List[DiscoveredCommand]:
        return []

    def get_command(self, full_name: str) -> Optional[DiscoveredCommand]:
        return None

    def get_progress(self) -> Optional[LoaderProgress]:
        return self._progress

    def on_progress(
        self,
        callback: Callable[[LoaderProgress], None],
    ) -> None:
        self._callbacks.append(callback)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ExecutionMode",
    # Types (WATERTIGHT)
    "CommandArgument",
    "DiscoveredCommand",
    "CLILoaderConfig",
    "LoaderProgress",
    "LoaderResult",
    # Functions
    "get_default_config",
    "parse_manifest",
    # Protocol
    "CLILoaderProtocol",
    # Null Implementation
    "NullCLILoader",
]
