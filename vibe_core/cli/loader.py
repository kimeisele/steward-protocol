"""
CLI Loader - Discovers CLI commands from plugin manifests.

VEDA-4 Pattern:
  SHABDA   → Scan plugin directories for manifest.yaml/.json
  ARTHA    → Parse CLI section from manifests
  PRATYAYA → Validate command definitions
  KARMA    → Build command registry
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .protocol import CLIArg, CLICommand, CommandRegistry, ExecutionMode

logger = logging.getLogger("CLI_LOADER")


class CLILoaderError(Exception):
    """Error during CLI command discovery."""

    pass


class CLICollisionError(CLILoaderError):
    """Two plugins define the same command name."""

    pass


class CLILoader:
    """
    Discovers CLI commands from plugin manifests.

    Scans vibe_core/plugins/*/manifest.yaml for cli: sections.
    """

    # Default scan paths for plugin manifests
    DEFAULT_PLUGIN_PATHS = [
        Path("vibe_core/plugins"),
    ]

    # Cache for discovered commands
    _cache: Optional[CommandRegistry] = None
    _cache_mtimes: Dict[str, float] = {}

    @classmethod
    def discover_commands(
        cls,
        plugin_paths: Optional[List[Path]] = None,
        force_refresh: bool = False,
    ) -> CommandRegistry:
        """
        Discover all CLI commands from plugin manifests.

        Args:
            plugin_paths: Override default scan paths
            force_refresh: Bypass cache

        Returns:
            Dict mapping command full_name to CLICommand
        """
        if not force_refresh and cls._cache is not None:
            if not cls._cache_stale():
                return cls._cache

        paths = plugin_paths or cls.DEFAULT_PLUGIN_PATHS
        commands: CommandRegistry = {}

        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                logger.debug(f"Plugin path does not exist: {base_path}")
                continue

            # Scan for manifest files (both YAML and JSON)
            manifest_patterns = ["*/manifest.yaml", "*/manifest.json"]
            for pattern in manifest_patterns:
                for manifest_path in base_path.glob(pattern):
                    try:
                        plugin_commands = cls._load_plugin_commands(manifest_path)
                        for cmd in plugin_commands:
                            if cmd.full_name in commands:
                                raise CLICollisionError(
                                    f"Command '{cmd.full_name}' already registered. Use namespace to disambiguate."
                                )
                            commands[cmd.full_name] = cmd
                            logger.debug(f"Registered command: {cmd.full_name}")
                    except Exception as e:
                        logger.warning(f"Failed to load CLI from {manifest_path}: {e}")

        # Update cache
        cls._cache = commands
        cls._update_cache_mtimes(paths)

        logger.info(f"CLI Loader: Discovered {len(commands)} commands")
        return commands

    @classmethod
    def _load_plugin_commands(cls, manifest_path: Path) -> List[CLICommand]:
        """Load CLI commands from a single plugin manifest (YAML or JSON)."""
        commands: List[CLICommand] = []

        with open(manifest_path) as f:
            if manifest_path.suffix == ".json":
                manifest = json.load(f)
            else:
                manifest = yaml.safe_load(f)

        if not manifest or "cli" not in manifest:
            return commands

        cli_section = manifest["cli"]
        namespace = cli_section.get("namespace")
        plugin_id = manifest.get("plugin_id", manifest_path.parent.name)

        for cmd_def in cli_section.get("commands", []):
            cmd = cls._parse_command(cmd_def, namespace, plugin_id)
            commands.append(cmd)

        return commands

    @classmethod
    def _parse_command(
        cls,
        cmd_def: Dict[str, Any],
        namespace: Optional[str],
        plugin_id: str,
    ) -> CLICommand:
        """Parse a command definition from manifest."""
        # Parse args
        args: List[CLIArg] = []
        for arg_def in cmd_def.get("args", []):
            arg = CLIArg(
                name=arg_def["name"],
                type=cls._parse_type(arg_def.get("type", "str")),
                help=arg_def.get("help", ""),
                required=arg_def.get("required", True),
                default=arg_def.get("default"),
                choices=arg_def.get("choices"),
                nargs=arg_def.get("nargs"),
            )
            args.append(arg)

        # Parse execution mode
        mode_str = cmd_def.get("execution_mode", "hybrid").upper()
        try:
            execution_mode = ExecutionMode[mode_str]
        except KeyError:
            execution_mode = ExecutionMode.HYBRID

        return CLICommand(
            name=cmd_def["name"],
            namespace=namespace,
            plugin_id=plugin_id,
            handler=cmd_def.get("handler", f"cmd_{cmd_def['name']}"),
            execution_mode=execution_mode,
            help=cmd_def.get("help", ""),
            args=args,
            renderer=cmd_def.get("renderer"),
            supports_streaming=cmd_def.get("streaming", False),
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

    @classmethod
    def _cache_stale(cls) -> bool:
        """Check if any manifest files have changed since cache."""
        for path_str, cached_mtime in cls._cache_mtimes.items():
            path = Path(path_str)
            if path.exists() and path.stat().st_mtime > cached_mtime:
                return True
        return False

    @classmethod
    def _update_cache_mtimes(cls, paths: List[Path]) -> None:
        """Update cached modification times."""
        cls._cache_mtimes = {}
        for base_path in paths:
            base_path = Path(base_path)
            if not base_path.exists():
                continue
            for pattern in ["*/manifest.yaml", "*/manifest.json"]:
                for manifest_path in base_path.glob(pattern):
                    cls._cache_mtimes[str(manifest_path)] = manifest_path.stat().st_mtime

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached commands."""
        cls._cache = None
        cls._cache_mtimes = {}

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
