"""
OPUS-310: Command Registry - Single Source of Truth

All commands are registered here. All discovery happens here.
No more 5 parallel systems.

Usage:
    # At boot:
    registry = CommandRegistry.get_instance()
    registry.scan_manifests()

    # Register a command:
    registry.register(ChatCommand())

    # Execute:
    result = await registry.execute("chat", ["hello"], context)

    # Discovery (for MANAS):
    commands = registry.list_commands()
    commands = registry.search("agent")
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandInfo,
    CommandProtocol,
    CommandResult,
    ParameterSpec,
    ParameterType,
)

logger = logging.getLogger("COMMAND.REGISTRY")


@dataclass
class ManifestCommandSpec:
    """Command specification from a manifest file."""

    name: str
    description: str = ""
    protocol: Optional[str] = None
    method: Optional[str] = None
    handler: Optional[str] = None  # Legacy format: "cmd_opus_status"
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    source: str = "manifest"


class ManifestCommand(BaseCommand):
    """
    Command created from manifest specification.

    Routes to protocol method or callable.
    """

    def __init__(
        self,
        spec: ManifestCommandSpec,
        executor: Optional[Callable] = None,
    ):
        self.name = spec.name
        self.description = spec.description
        self.source = spec.source
        self._spec = spec
        self._executor = executor

        # Parse parameters from spec
        self._parameters = []
        for p in spec.parameters:
            self._parameters.append(
                ParameterSpec(
                    name=p.get("name", "arg"),
                    param_type=ParameterType(p.get("type", "string")),
                    required=p.get("required", False),
                    default=p.get("default"),
                    description=p.get("description", ""),
                )
            )

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute via injected executor or fail gracefully."""
        if self._executor:
            try:
                result = await self._executor(args, context)
                if isinstance(result, CommandResult):
                    return result
                return CommandResult(success=True, output=str(result))
            except Exception as e:
                logger.error(f"Command {self.name} failed: {e}")
                return CommandResult(success=False, error=str(e))

        return CommandResult(
            success=False,
            error=f"Command '{self.name}' has no executor (protocol: {self._spec.protocol})",
        )


class CommandRegistry:
    """
    OPUS-310: The One Registry to Rule Them All.

    Single source of truth for ALL commands in the system.

    Scans:
    - ManifestRegistry for 'commands' sections
    - Programmatic registrations

    Provides:
    - get(name) → CommandProtocol
    - list() → List[CommandInfo]
    - search(query) → List[CommandInfo]
    - execute(name, args, context) → CommandResult
    """

    _instance: Optional["CommandRegistry"] = None

    def __init__(self):
        self._commands: Dict[str, CommandProtocol] = {}
        self._pending_wiring: Dict[str, ManifestCommandSpec] = {}
        self._scanned = False

    @classmethod
    def get_instance(cls) -> "CommandRegistry":
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def register(self, command: CommandProtocol, replace: bool = False) -> bool:
        """
        Register a command.

        Args:
            command: Command implementing CommandProtocol
            replace: If True, replace existing command

        Returns:
            True if registered, False if name conflict
        """
        name = command.name

        if name in self._commands and not replace:
            logger.warning(f"Command '{name}' already registered (use replace=True to override)")
            return False

        self._commands[name] = command
        logger.debug(f"Registered command: {name}")

        # Clear pending wiring if we have an implementation now
        if name in self._pending_wiring:
            del self._pending_wiring[name]

        return True

    def register_class(self, command_class: Type[BaseCommand]) -> bool:
        """Register a command class (instantiates it)."""
        return self.register(command_class())

    def scan_manifests(self) -> int:
        """
        Scan ManifestRegistry for commands.

        Extracts 'commands' section from each manifest.
        Commands without executors go to pending_wiring.

        Returns:
            Number of commands discovered
        """
        if self._scanned:
            return len(self._commands)

        try:
            from vibe_core.loaders.manifest_registry import ManifestRegistry

            # Ensure ManifestRegistry is scanned
            ManifestRegistry.scan_all()

            count = 0

            # Scan plugins
            for entry in ManifestRegistry.get_by_type("plugin"):
                count += self._extract_commands(entry.manifest, f"plugin:{entry.id}")

            # Scan cartridges
            for entry in ManifestRegistry.get_by_type("cartridge"):
                count += self._extract_commands(entry.manifest, f"cartridge:{entry.id}")

            self._scanned = True
            logger.info(f"[COMMAND.REGISTRY] Discovered {count} commands from manifests")

            return count

        except ImportError as e:
            logger.warning(f"ManifestRegistry not available: {e}")
            return 0

    def _extract_commands(self, manifest: Dict[str, Any], source: str) -> int:
        """
        Extract commands from a manifest.

        Supports two formats:
        1. New format: top-level "commands" array
        2. Legacy format: "cli.commands" with namespace

        Both are converted to CommandProtocol implementations.
        """
        count = 0

        # Format 1: Top-level "commands" array (new OPUS-310 format)
        commands = manifest.get("commands", [])
        for cmd_spec in commands:
            if self._register_command_spec(cmd_spec, source):
                count += 1

        # Format 2: "cli.commands" with namespace (existing format)
        cli_section = manifest.get("cli", {})
        if cli_section and "commands" in cli_section:
            namespace = cli_section.get("namespace", "")
            for cmd_spec in cli_section.get("commands", []):
                # Prefix with namespace if present
                if namespace and "name" in cmd_spec:
                    cmd_spec = dict(cmd_spec)  # Copy to avoid mutation
                    cmd_spec["name"] = f"{namespace}.{cmd_spec['name']}"
                if self._register_command_spec(cmd_spec, source, cli_section):
                    count += 1

        return count

    def _register_command_spec(
        self,
        cmd_spec: Dict[str, Any],
        source: str,
        cli_section: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register a single command specification."""
        if not isinstance(cmd_spec, dict):
            return False

        name = cmd_spec.get("name")
        if not name:
            return False

        # Already registered? Skip
        if name in self._commands:
            return False

        # Convert args to parameters format
        parameters = []
        for arg in cmd_spec.get("args", cmd_spec.get("parameters", [])):
            if isinstance(arg, dict):
                parameters.append(
                    {
                        "name": arg.get("name", "arg"),
                        "type": arg.get("type", "string"),
                        "required": arg.get("required", False),
                        "default": arg.get("default"),
                        "description": arg.get("help", arg.get("description", "")),
                    }
                )

        spec = ManifestCommandSpec(
            name=name,
            description=cmd_spec.get("help", cmd_spec.get("description", "")),
            protocol=cmd_spec.get("protocol"),
            method=cmd_spec.get("method"),
            handler=cmd_spec.get("handler"),  # Legacy format uses handler
            parameters=parameters,
            source=source,
        )

        # Create command without executor (pending wiring)
        command = ManifestCommand(spec)
        self._commands[name] = command
        self._pending_wiring[name] = spec

        return True

    def wire_command(
        self,
        name: str,
        executor: Callable,
    ) -> bool:
        """
        Wire an executor to a pending command.

        Called by protocols when they want to provide implementation.
        """
        if name not in self._commands:
            logger.warning(f"Cannot wire '{name}': not registered")
            return False

        cmd = self._commands[name]
        if isinstance(cmd, ManifestCommand):
            cmd._executor = executor
            if name in self._pending_wiring:
                del self._pending_wiring[name]
            logger.debug(f"Wired executor for: {name}")
            return True

        return False

    def wire_from_plugins(self, plugins: Any) -> int:
        """
        Wire pending commands to their handlers in loaded plugins.

        Looks for 'handler' in pending specs and finds the method
        in the corresponding plugin.

        Args:
            plugins: List or Dict of plugins

        Returns:
            Number of commands wired
        """
        # Convert list to dict by plugin id
        if isinstance(plugins, list):
            plugins_dict: Dict[str, Any] = {}
            for p in plugins:
                # Try various ways to get plugin id
                plugin_id = getattr(p, "id", None)
                if not plugin_id:
                    plugin_id = getattr(p, "plugin_id", None)
                if not plugin_id:
                    # Try to extract from class name (e.g., OpusAssistantPlugin -> opus_assistant)
                    class_name = type(p).__name__
                    if class_name.endswith("Plugin"):
                        # Convert CamelCase to snake_case
                        import re

                        plugin_id = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name[:-6]).lower()
                if plugin_id:
                    plugins_dict[plugin_id] = p
            plugins = plugins_dict

        wired = 0

        for name, spec in list(self._pending_wiring.items()):
            if not spec.handler:
                continue

            # Extract plugin id from source (e.g., "plugin:opus_assistant")
            source_parts = spec.source.split(":")
            if len(source_parts) != 2 or source_parts[0] != "plugin":
                continue

            plugin_id = source_parts[1]
            plugin = plugins.get(plugin_id)

            if not plugin:
                continue

            # Find handler method on plugin
            handler_method = getattr(plugin, spec.handler, None)
            if handler_method and callable(handler_method):
                # Create async wrapper if needed
                async def make_executor(method, cmd_name):
                    async def executor(args: List[str], context: CommandContext) -> CommandResult:
                        try:
                            # Call the handler - most are sync
                            import asyncio

                            if asyncio.iscoroutinefunction(method):
                                result = await method(args)
                            else:
                                result = method(args)

                            # Convert to CommandResult
                            if isinstance(result, CommandResult):
                                return result
                            elif isinstance(result, int):
                                return CommandResult(
                                    success=result == 0,
                                    exit_code=result,
                                )
                            elif isinstance(result, str):
                                return CommandResult(success=True, output=result)
                            else:
                                return CommandResult(success=True, output=str(result))
                        except Exception as e:
                            return CommandResult(success=False, error=str(e))

                    return executor

                # Wire it
                import asyncio

                executor = (
                    asyncio.get_event_loop().run_until_complete(make_executor(handler_method, name))
                    if False
                    else self._create_executor(handler_method)
                )

                if self.wire_command(name, executor):
                    wired += 1
                    logger.debug(f"Wired {name} -> {plugin_id}.{spec.handler}")

        if wired:
            logger.info(f"[COMMAND.REGISTRY] Wired {wired} commands from plugins")

        return wired

    def _create_executor(self, method: Callable) -> Callable:
        """Create an async executor wrapper for a handler method."""
        import asyncio

        async def executor(args: List[str], context: CommandContext) -> CommandResult:
            try:
                if asyncio.iscoroutinefunction(method):
                    result = await method(args)
                else:
                    result = method(args)

                if isinstance(result, CommandResult):
                    return result
                elif isinstance(result, int):
                    return CommandResult(success=result == 0, exit_code=result)
                elif isinstance(result, str):
                    return CommandResult(success=True, output=result)
                else:
                    return CommandResult(success=True, output=str(result) if result else "OK")
            except Exception as e:
                return CommandResult(success=False, error=str(e))

        return executor

    def get(self, name: str) -> Optional[CommandProtocol]:
        """Get command by name."""
        return self._commands.get(name)

    def has(self, name: str) -> bool:
        """Check if command exists."""
        return name in self._commands

    def list_commands(self) -> List[CommandInfo]:
        """
        List all registered commands.

        For MANAS to discover capabilities.
        """
        result = []
        for cmd in self._commands.values():
            if hasattr(cmd, "get_info"):
                result.append(cmd.get_info())
            else:
                # Fallback for non-BaseCommand implementations
                result.append(
                    CommandInfo(
                        name=cmd.name,
                        description=cmd.description if hasattr(cmd, "description") else "",
                        parameters=cmd.parameters if hasattr(cmd, "parameters") else [],
                        source="unknown",
                    )
                )
        return result

    def search(self, query: str) -> List[CommandInfo]:
        """
        Search commands by name or description.

        For MANAS to find relevant commands.
        """
        query = query.lower()
        results = []

        for cmd in self._commands.values():
            name = cmd.name.lower()
            desc = (cmd.description if hasattr(cmd, "description") else "").lower()

            if query in name or query in desc:
                if hasattr(cmd, "get_info"):
                    results.append(cmd.get_info())

        return results

    async def execute(
        self,
        name: str,
        args: List[str],
        context: Optional[CommandContext] = None,
    ) -> CommandResult:
        """
        Execute a command by name.

        The universal execution entry point.
        """
        cmd = self.get(name)
        if not cmd:
            return CommandResult(
                success=False,
                error=f"Command not found: {name}",
                exit_code=127,
            )

        context = context or CommandContext()

        # Validate
        errors = cmd.validate(args)
        if errors:
            return CommandResult(
                success=False,
                error=f"Validation failed: {'; '.join(errors)}",
                exit_code=2,
            )

        # Execute
        try:
            return await cmd.execute(args, context)
        except Exception as e:
            logger.exception(f"Command '{name}' raised exception")
            return CommandResult(
                success=False,
                error=f"Execution failed: {e}",
                exit_code=1,
            )

    def get_pending_wiring(self) -> Dict[str, ManifestCommandSpec]:
        """Get commands that need executors wired."""
        return dict(self._pending_wiring)

    def stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        by_source: Dict[str, int] = {}
        for cmd in self._commands.values():
            source = getattr(cmd, "source", "unknown")
            by_source[source] = by_source.get(source, 0) + 1

        return {
            "total": len(self._commands),
            "pending_wiring": len(self._pending_wiring),
            "by_source": by_source,
            "scanned": self._scanned,
        }

    def register_core_commands(self) -> int:
        """
        Register the core OPUS-310 commands.

        Called during boot to ensure base commands are available.
        """
        from vibe_core.cli.commands import (
            BootCommand,
            ChatCommand,
            CommandsCommand,
            StatusCommand,
        )

        count = 0
        for cmd_class in [ChatCommand, BootCommand, StatusCommand, CommandsCommand]:
            if self.register(cmd_class()):
                count += 1

        logger.info(f"[COMMAND.REGISTRY] Registered {count} core commands")
        return count
