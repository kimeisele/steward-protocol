"""
CLI Loader - Protocol-Based CLI Discovery
==========================================

VEDA-4 Pattern:
  SHABDA   → Scan paths from CLILoaderConfig (NO HARDCODING)
  ARTHA    → Parse CLI section from manifests
  PRATYAYA → Validate command definitions
  KARMA    → Build command registry

SUBSTRATE INTEGRATION:
  Implements CLILoaderProtocol from protocols/substrate/cli_loader.py
  Config-driven via CLILoaderConfig - NO DEFAULT_PLUGIN_PATHS hardcoding!

SELF-MANIFESTING:
  Modules bring their own cli.yaml (e.g., mahamantra/cli.yaml)
  The truth is IN the module, not in the router.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x16d5c44f"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional

import yaml

from .protocol import CLIArg, CLICommand, CommandRegistry, ExecutionMode

# === SUBSTRATE PROTOCOL ===
from vibe_core.protocols.substrate.cli_loader import (
    CLILoaderConfig,
    CLILoaderProtocol,
    CommandArgument,
    DiscoveredCommand,
    LoaderProgress,
    LoaderResult,
    get_default_config as get_substrate_config,
    parse_manifest as substrate_parse_manifest,
)

logger = logging.getLogger("CLI_LOADER")


class CLILoaderError(Exception):
    """Error during CLI command discovery."""

    pass


class CLICollisionError(CLILoaderError):
    """Two plugins define the same command name."""

    pass


# =============================================================================
# CLI LOADER - Implements CLILoaderProtocol
# =============================================================================


class CLILoader:
    """
    Protocol-based CLI command discovery.

    IMPLEMENTS: CLILoaderProtocol (SUBSTRATE)

    NO HARDCODED PATHS - uses CLILoaderConfig from substrate.
    Scans all configured paths for:
      - cli.yaml (module root)
      - manifest.yaml (plugin subdirs)
      - cli.json / manifest.json

    SELF-MANIFESTING:
      Modules like mahamantra/ bring their own cli.yaml.
      The loader discovers them automatically.
    """

    def __init__(self, config: Optional[CLILoaderConfig] = None) -> None:
        """
        Initialize CLI Loader with config.

        Args:
            config: CLILoaderConfig (optional - uses substrate default)
        """
        self._config = config or get_substrate_config()
        self._cache: Optional[CommandRegistry] = None
        self._cache_mtimes: Dict[str, float] = {}
        self._progress: Optional[LoaderProgress] = None
        self._callbacks: List[Callable[[LoaderProgress], None]] = []
        self._discovered_commands: List[DiscoveredCommand] = []

    # =========================================================================
    # CLILoaderProtocol Implementation
    # =========================================================================

    def get_config(self) -> CLILoaderConfig:
        """Get current loader configuration."""
        return self._config

    def set_config(self, config: CLILoaderConfig) -> None:
        """Set loader configuration (clears cache)."""
        self._config = config
        self.clear_cache()

    def discover(self, path: Optional[str] = None) -> LoaderResult:
        """
        Discover CLI commands from manifests.

        Uses config.scan_paths if path not specified.
        """
        start_time = datetime.now()
        self._discovered_commands = []
        errors: List[str] = []

        # Get paths to scan
        if path:
            scan_paths = [path]
        else:
            scan_paths = self._config.get("scan_paths", [])

        paths_scanned = 0
        commands_found = 0
        commands_skipped = 0
        commands_error = 0
        by_namespace: Dict[str, int] = {}
        by_mode: Dict[str, int] = {}

        for scan_path in scan_paths:
            base_path = Path(scan_path)
            if not base_path.exists():
                logger.debug(f"Scan path does not exist: {base_path}")
                continue

            paths_scanned += 1

            # Get manifest patterns from config
            patterns = self._config.get("manifest_patterns", ["cli.yaml", "manifest.yaml"])

            for pattern in patterns:
                # Check root level (e.g., mahamantra/cli.yaml)
                root_manifest = base_path / pattern
                if root_manifest.exists():
                    try:
                        namespace = base_path.name
                        commands = substrate_parse_manifest(root_manifest, namespace)
                        for cmd in commands:
                            self._discovered_commands.append(cmd)
                            commands_found += 1
                            ns = cmd.get("namespace", "")
                            by_namespace[ns] = by_namespace.get(ns, 0) + 1
                            mode = cmd.get("execution_mode", "hybrid")
                            by_mode[mode] = by_mode.get(mode, 0) + 1
                    except Exception as e:
                        errors.append(f"{root_manifest}: {e}")
                        commands_error += 1

                # Check subdirectories (e.g., plugins/*/manifest.yaml)
                for manifest_path in base_path.glob(f"*/{pattern}"):
                    try:
                        namespace = manifest_path.parent.name
                        commands = substrate_parse_manifest(manifest_path, namespace)
                        for cmd in commands:
                            self._discovered_commands.append(cmd)
                            commands_found += 1
                            ns = cmd.get("namespace", "")
                            by_namespace[ns] = by_namespace.get(ns, 0) + 1
                            mode = cmd.get("execution_mode", "hybrid")
                            by_mode[mode] = by_mode.get(mode, 0) + 1
                    except Exception as e:
                        errors.append(f"{manifest_path}: {e}")
                        commands_error += 1

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return LoaderResult(
            config=self._config,
            paths_scanned=paths_scanned,
            commands_found=commands_found,
            commands_skipped=commands_skipped,
            commands_error=commands_error,
            by_namespace=by_namespace,
            by_mode=by_mode,
            commands=self._discovered_commands,
            errors=errors,
            started_at=start_time.isoformat(),
            completed_at=end_time.isoformat(),
            duration_seconds=duration,
        )

    def discover_path(self, path: str) -> List[DiscoveredCommand]:
        """Discover commands from a single path."""
        result = self.discover(path)
        return result.get("commands", [])

    def iter_commands(
        self,
        path: Optional[str] = None,
    ) -> Iterator[DiscoveredCommand]:
        """Iterate over commands lazily."""
        result = self.discover(path)
        for cmd in result.get("commands", []):
            yield cmd

    def get_by_namespace(self, namespace: str) -> List[DiscoveredCommand]:
        """Get all commands in a namespace."""
        if not self._discovered_commands:
            self.discover()
        return [cmd for cmd in self._discovered_commands if cmd.get("namespace") == namespace]

    def get_by_mode(self, mode: str) -> List[DiscoveredCommand]:
        """Get all commands with execution mode."""
        if not self._discovered_commands:
            self.discover()
        return [cmd for cmd in self._discovered_commands if cmd.get("execution_mode") == mode]

    def get_command(self, full_name: str) -> Optional[DiscoveredCommand]:
        """Get a specific command by full name."""
        if not self._discovered_commands:
            self.discover()
        for cmd in self._discovered_commands:
            if cmd.get("full_name") == full_name:
                return cmd
        return None

    def get_progress(self) -> Optional[LoaderProgress]:
        """Get current discovery progress."""
        return self._progress

    def on_progress(
        self,
        callback: Callable[[LoaderProgress], None],
    ) -> None:
        """Register progress callback."""
        self._callbacks.append(callback)

    # =========================================================================
    # Legacy API (Backward Compatibility)
    # =========================================================================

    @classmethod
    def discover_commands(
        cls,
        plugin_paths: Optional[List[Path]] = None,
        force_refresh: bool = False,
    ) -> CommandRegistry:
        """
        LEGACY API - Discover all CLI commands from plugin manifests.

        For backward compatibility with existing code.
        Uses new protocol-based implementation internally.
        """
        # Create instance with config
        config = get_substrate_config()
        if plugin_paths:
            config["scan_paths"] = [str(p) for p in plugin_paths]

        loader = cls(config)

        if not force_refresh and cls._class_cache is not None:
            if not cls._class_cache_stale():
                return cls._class_cache

        # Discover using protocol
        result = loader.discover()

        # Convert to legacy CommandRegistry format
        commands: CommandRegistry = {}
        for discovered in result.get("commands", []):
            cmd = cls._convert_to_cli_command(discovered)
            if cmd.full_name in commands:
                logger.warning(f"Command collision: {cmd.full_name}")
            commands[cmd.full_name] = cmd

        # Update class-level cache
        cls._class_cache = commands
        cls._update_class_cache_mtimes(config.get("scan_paths", []))

        logger.info(f"CLI Loader: Discovered {len(commands)} commands")
        return commands

    @classmethod
    def _convert_to_cli_command(cls, discovered: DiscoveredCommand) -> CLICommand:
        """Convert DiscoveredCommand to legacy CLICommand."""
        # Parse args
        args: List[CLIArg] = []
        for arg_data in discovered.get("arguments", []):
            # FOLDER_IS_WIRING: flag: true in yaml means type=bool
            is_flag = arg_data.get("flag", False)
            arg_type = bool if is_flag else cls._parse_type(arg_data.get("type", "str"))

            arg = CLIArg(
                name=arg_data.get("name", ""),
                type=arg_type,
                help=arg_data.get("help", ""),
                required=arg_data.get("required", False),
                default=arg_data.get("default", False if is_flag else None),
                choices=arg_data.get("choices"),
            )
            args.append(arg)

        # Parse execution mode
        mode_str = discovered.get("execution_mode", "hybrid").upper()
        try:
            execution_mode = ExecutionMode[mode_str]
        except KeyError:
            execution_mode = ExecutionMode.HYBRID

        return CLICommand(
            name=discovered.get("name", ""),
            namespace=discovered.get("namespace"),
            plugin_id=discovered.get("source_module", ""),
            handler=discovered.get("handler", ""),
            execution_mode=execution_mode,
            help=discovered.get("help", ""),
            args=args,
        )

    @classmethod
    def _parse_type(cls, type_str: str) -> type:
        """Parse type string to Python type."""
        type_map = {
            "str": str,
            "string": str,
            "int": int,
            "integer": int,
            "float": float,
            "bool": bool,
            "boolean": bool,
            "path": Path,
        }
        return type_map.get(type_str.lower(), str)

    # Class-level cache for legacy API
    _class_cache: Optional[CommandRegistry] = None
    _class_cache_mtimes: Dict[str, float] = {}

    @classmethod
    def _class_cache_stale(cls) -> bool:
        """Check if any manifest files have changed since cache."""
        for path_str, cached_mtime in cls._class_cache_mtimes.items():
            path = Path(path_str)
            if path.exists() and path.stat().st_mtime > cached_mtime:
                return True
        return False

    @classmethod
    def _update_class_cache_mtimes(cls, paths: List[str]) -> None:
        """Update cached modification times."""
        cls._class_cache_mtimes = {}
        config = get_substrate_config()
        patterns = config.get("manifest_patterns", ["cli.yaml", "manifest.yaml"])

        for path_str in paths:
            base_path = Path(path_str)
            if not base_path.exists():
                continue

            # Check root level
            for pattern in patterns:
                root_manifest = base_path / pattern
                if root_manifest.exists():
                    cls._class_cache_mtimes[str(root_manifest)] = root_manifest.stat().st_mtime

            # Check subdirectories
            for pattern in patterns:
                for manifest_path in base_path.glob(f"*/{pattern}"):
                    cls._class_cache_mtimes[str(manifest_path)] = manifest_path.stat().st_mtime

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached commands."""
        cls._class_cache = None
        cls._class_cache_mtimes = {}

    @classmethod
    def get_commands_for_plugin(cls, plugin_id: str) -> List[CLICommand]:
        """Get all commands registered by a specific plugin."""
        commands = cls.discover_commands()
        return [cmd for cmd in commands.values() if cmd.namespace == plugin_id]

    @classmethod
    def get_namespaces(cls) -> List[str]:
        """Get all registered namespaces."""
        commands = cls.discover_commands()
        namespaces = set()
        for cmd in commands.values():
            if cmd.namespace:
                namespaces.add(cmd.namespace)
        return sorted(namespaces)


# =============================================================================
# MODULE-LEVEL SINGLETON (For easy access)
# =============================================================================

_default_loader: Optional[CLILoader] = None


def get_loader(config: Optional[CLILoaderConfig] = None) -> CLILoader:
    """Get the default CLI loader (singleton)."""
    global _default_loader
    if _default_loader is None or config is not None:
        _default_loader = CLILoader(config)
    return _default_loader
