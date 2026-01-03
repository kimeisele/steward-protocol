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


class CartridgeToolCommand(BaseCommand):
    """Command wrapping a cartridge tool (lazy-loaded)."""

    def __init__(self, spec: ManifestCommandSpec, cartridge_id: str, tool_id: str):
        self.name = spec.name
        self.description = spec.description
        self.source = spec.source
        self._cartridge_id = cartridge_id
        self._tool_id = tool_id
        self._tool = None
        self._parameters = []
        self.tags = ["cartridge", "tool"]

    def _ensure_tool(self):
        """Lazy-load the tool."""
        if self._tool is None:
            from vibe_core.cartridge_service import CartridgeService

            service = CartridgeService.get_instance()
            self._tool = service.load_tool(self._cartridge_id, self._tool_id)
        return self._tool

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute the cartridge tool."""
        tool = self._ensure_tool()
        if not tool:
            return CommandResult(
                success=False,
                error=f"Failed to load tool: {self._cartridge_id}.{self._tool_id}",
            )

        try:
            # Build parameters from args
            params = {"args": args}
            if context.kernel:
                params["kernel"] = context.kernel

            # Tools have execute() method
            if hasattr(tool, "execute"):
                result = await tool.execute(params) if hasattr(tool.execute, "__await__") else tool.execute(params)
                if hasattr(result, "output"):
                    return CommandResult(success=result.success, output=str(result.output))
                return CommandResult(success=True, output=str(result))
            else:
                return CommandResult(success=False, error="Tool has no execute method")
        except Exception as e:
            return CommandResult(success=False, error=str(e))


class ToolRegistryCommand(BaseCommand):
    """Command wrapping a ToolRegistry tool."""

    def __init__(self, spec: ManifestCommandSpec, tool_name: str):
        self.name = spec.name
        self.description = spec.description
        self.source = spec.source
        self._tool_name = tool_name
        self._parameters = []
        self.tags = ["tool"]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute via ToolRegistry."""
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.tools.tool_protocol import ToolCall
            from vibe_core.tools.tool_registry import ToolRegistry as TR

            registry = ServiceRegistry.get(TR)
            if not registry:
                return CommandResult(success=False, error="ToolRegistry not available")

            # Build ToolCall
            call = ToolCall(
                tool_name=self._tool_name,
                parameters={"args": args},
            )

            result = registry.execute(call)
            return CommandResult(
                success=result.success,
                output=result.output if hasattr(result, "output") else str(result),
                error=result.error if hasattr(result, "error") else None,
            )
        except Exception as e:
            return CommandResult(success=False, error=str(e))


class CircuitCommand(BaseCommand):
    """Command wrapping a circuit execution."""

    def __init__(self, spec: ManifestCommandSpec, circuit_id: str):
        self.name = spec.name
        self.description = spec.description
        self.source = spec.source
        self._circuit_id = circuit_id
        self._parameters = []
        self.tags = ["circuit"]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute via ExecutorSingularity."""
        try:
            from vibe_core.cartridges.system.envoy.executor_singularity import (
                create_executor_singularity,
            )

            executor = create_executor_singularity(context.kernel)

            # Build input variables from args
            input_vars = {"args": args, "raw_input": " ".join(args)}

            result = await executor.execute(self._circuit_id, input_vars)

            return CommandResult(
                success=result.success if hasattr(result, "success") else True,
                output=str(result.output) if hasattr(result, "output") else str(result),
                data=result.output if hasattr(result, "output") else None,
            )
        except Exception as e:
            return CommandResult(success=False, error=str(e))


class CLIHandlerCommand(BaseCommand):
    """Command wrapping a CLIRegistry handler."""

    def __init__(self, spec: ManifestCommandSpec, handler: Any):
        self.name = spec.name
        self.description = spec.description
        self.source = spec.source
        self._handler = handler
        self._parameters = []
        self.tags = ["cli"]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute via CLIHandler.run()."""
        try:
            exit_code = self._handler.run(args)
            return CommandResult(
                success=exit_code == 0,
                exit_code=exit_code,
            )
        except Exception as e:
            return CommandResult(success=False, error=str(e))


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
        self._aliases: Dict[str, str] = {}  # OPUS-311: alias -> target command
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

    def register_alias(
        self,
        alias: str,
        target: str,
        source: str = "learning",
    ) -> bool:
        """
        OPUS-311 Sprint 4: Register an alias for a command.

        Used by LearningLoop to auto-register frequently used shortcuts.

        Args:
            alias: The alias name (e.g., "agents")
            target: The target command (e.g., "list_agents")
            source: Where this alias came from (e.g., "learning", "manifest")

        Returns:
            True if registered, False if conflict
        """
        # Don't override existing commands
        if alias in self._commands:
            logger.debug(f"Cannot create alias '{alias}': command exists")
            return False

        # Don't override existing aliases (unless same target)
        if alias in self._aliases and self._aliases[alias] != target:
            logger.debug(f"Alias '{alias}' already points to '{self._aliases[alias]}'")
            return False

        # Target must exist
        if target not in self._commands:
            logger.debug(f"Cannot create alias '{alias}': target '{target}' not found")
            return False

        self._aliases[alias] = target
        self._save_aliases()  # OPUS-311: Persist to disk
        logger.info(f"[COMMAND.REGISTRY] Registered alias: {alias} → {target} (source: {source})")
        return True

    def resolve_alias(self, name: str) -> str:
        """
        OPUS-311: Resolve an alias to its target command.

        Returns the original name if not an alias.
        """
        return self._aliases.get(name, name)

    def get_aliases(self) -> Dict[str, str]:
        """Get all registered aliases."""
        return dict(self._aliases)

    def remove_alias(self, alias: str) -> bool:
        """Remove an alias."""
        if alias in self._aliases:
            del self._aliases[alias]
            self._save_aliases()  # OPUS-311: Persist removal
            return True
        return False

    # =========================================================================
    # OPUS-311 Sprint 4: Alias Persistence
    # =========================================================================

    ALIAS_STATE_FILE = ".vibe/state/aliases.json"

    def _get_alias_path(self) -> Path:
        """Get the path to the alias state file."""
        # Try workspace first, fall back to cwd
        workspace = Path.cwd()
        return workspace / self.ALIAS_STATE_FILE

    def _save_aliases(self) -> bool:
        """
        OPUS-311: Persist aliases to .vibe/state/aliases.json.

        Called automatically after register_alias() and remove_alias().

        Returns:
            True if saved successfully
        """
        import json

        alias_path = self._get_alias_path()

        try:
            # Ensure directory exists
            alias_path.parent.mkdir(parents=True, exist_ok=True)

            # Build state
            state = {
                "version": 1,
                "aliases": self._aliases,
                "metadata": {
                    "count": len(self._aliases),
                    "updated_at": __import__("datetime").datetime.now().isoformat(),
                },
            }

            # Write atomically
            temp_path = alias_path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(state, f, indent=2)
            temp_path.replace(alias_path)

            logger.debug(f"Saved {len(self._aliases)} aliases to {alias_path}")
            return True

        except Exception as e:
            logger.warning(f"Failed to save aliases: {e}")
            return False

    def load_aliases(self) -> int:
        """
        OPUS-311: Load aliases from .vibe/state/aliases.json.

        Called during boot to restore learned aliases.

        Returns:
            Number of aliases loaded
        """
        import json

        alias_path = self._get_alias_path()

        if not alias_path.exists():
            logger.debug(f"No alias state file at {alias_path}")
            return 0

        try:
            with open(alias_path) as f:
                state = json.load(f)

            aliases = state.get("aliases", {})
            loaded = 0

            for alias, target in aliases.items():
                # Only load if target command exists
                if target in self._commands:
                    self._aliases[alias] = target
                    loaded += 1
                else:
                    logger.debug(f"Skipping alias '{alias}' → '{target}' (target not found)")

            if loaded:
                logger.info(f"[COMMAND.REGISTRY] Loaded {loaded} aliases from {alias_path}")

            return loaded

        except Exception as e:
            logger.warning(f"Failed to load aliases: {e}")
            return 0

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

            logger.info(f"[COMMAND.REGISTRY] Discovered {count} commands from manifests")

            return count

        except ImportError as e:
            logger.warning(f"ManifestRegistry not available: {e}")
            return 0

    def scan_all(self) -> Dict[str, int]:
        """
        OPUS-310: Scan ALL execution systems.

        The One Scan to Rule Them All.
        No manual wiring - everything discovered declaratively.

        Returns:
            Dict with counts per system
        """
        results = {
            "core": self.register_core_commands(),  # OPUS-310 core commands
            "manifests": self.scan_manifests(),
            "cartridge_tools": self.scan_cartridge_tools(),
            "tool_registry": self.scan_tool_registry(),
            "circuits": self.scan_circuits(),
            "cli_handlers": self.scan_cli_handlers(),
        }

        self._scanned = True

        # OPUS-311: Load persisted aliases after commands are available
        results["aliases"] = self.load_aliases()

        total = sum(results.values())
        logger.info(f"[COMMAND.REGISTRY] Total: {total} commands from {len(results)} systems")

        return results

    def scan_cartridge_tools(self) -> int:
        """
        Scan CartridgeService for tools.

        Each tool becomes a command: cartridge.tool_id
        """
        count = 0

        try:
            from vibe_core.cartridge_service import CartridgeService

            service = CartridgeService.get_instance()
            service.scan()

            for cartridge in service.list():
                for tool_id, tool_info in cartridge.tools.items():
                    cmd_name = f"{cartridge.cartridge_id}.{tool_id}"

                    if cmd_name in self._commands:
                        continue

                    # Create command spec
                    spec = ManifestCommandSpec(
                        name=cmd_name,
                        description=tool_info.description or f"Tool: {tool_id}",
                        source=f"cartridge:{cartridge.cartridge_id}",
                        parameters=[],  # Will be extracted from tool
                    )

                    # Create command with lazy tool loading
                    command = CartridgeToolCommand(
                        spec=spec,
                        cartridge_id=cartridge.cartridge_id,
                        tool_id=tool_id,
                    )

                    self._commands[cmd_name] = command
                    count += 1

            if count:
                logger.info(f"[COMMAND.REGISTRY] Discovered {count} cartridge tools")

        except ImportError as e:
            logger.debug(f"CartridgeService not available: {e}")

        return count

    def scan_tool_registry(self) -> int:
        """
        Scan ToolRegistry for registered tools.

        Each tool becomes a command: tool.<tool_name>
        """
        count = 0

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.tools.tool_registry import ToolRegistry as TR

            # Try to get from DI first
            tool_registry = ServiceRegistry.get(TR)

            if not tool_registry:
                return 0

            for tool_name in tool_registry.list_tools():
                cmd_name = f"tool.{tool_name}"

                if cmd_name in self._commands:
                    continue

                tool = tool_registry.get(tool_name)
                if not tool:
                    continue

                spec = ManifestCommandSpec(
                    name=cmd_name,
                    description=getattr(tool, "description", f"Tool: {tool_name}"),
                    source="tool_registry",
                    parameters=[],
                )

                command = ToolRegistryCommand(
                    spec=spec,
                    tool_name=tool_name,
                )

                self._commands[cmd_name] = command
                count += 1

            if count:
                logger.info(f"[COMMAND.REGISTRY] Discovered {count} tools from registry")

        except ImportError as e:
            logger.debug(f"ToolRegistry not available: {e}")

        return count

    def scan_circuits(self) -> int:
        """
        Scan PhoenixConfig for circuits.

        Each circuit becomes a command: circuit.<circuit_id>
        """
        count = 0

        try:
            from vibe_core.phoenix.config import PhoenixConfig

            config = PhoenixConfig.from_files()

            for circuit_id, circuit_config in config.circuits.items():
                cmd_name = f"circuit.{circuit_id}"

                if cmd_name in self._commands:
                    continue

                spec = ManifestCommandSpec(
                    name=cmd_name,
                    description=getattr(circuit_config, "description", f"Circuit: {circuit_id}"),
                    source="circuit",
                    parameters=[],
                )

                command = CircuitCommand(
                    spec=spec,
                    circuit_id=circuit_id,
                )

                self._commands[cmd_name] = command
                count += 1

            if count:
                logger.info(f"[COMMAND.REGISTRY] Discovered {count} circuits")

        except ImportError as e:
            logger.debug(f"PhoenixConfig not available: {e}")

        return count

    def scan_cli_handlers(self) -> int:
        """
        Scan CLIRegistry for registered handlers.

        Each handler becomes a command.
        """
        count = 0

        try:
            from vibe_core.protocols.cli import CLIRegistry

            for handler in CLIRegistry.all():
                meta = handler.meta
                cmd_name = meta.command

                if cmd_name in self._commands:
                    continue

                spec = ManifestCommandSpec(
                    name=cmd_name,
                    description=meta.description,
                    source="cli_registry",
                    parameters=[],
                )

                command = CLIHandlerCommand(
                    spec=spec,
                    handler=handler,
                )

                self._commands[cmd_name] = command
                count += 1

            if count:
                logger.info(f"[COMMAND.REGISTRY] Discovered {count} CLI handlers")

        except ImportError as e:
            logger.debug(f"CLIRegistry not available: {e}")

        return count

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
        """
        Get command by name.

        OPUS-311: Resolves aliases automatically.
        """
        # Resolve alias first
        resolved = self.resolve_alias(name)
        return self._commands.get(resolved)

    def has(self, name: str) -> bool:
        """
        Check if command exists.

        OPUS-311: Also checks aliases.
        """
        return name in self._commands or name in self._aliases

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

        OPUS-311: Includes GovernanceGate permission check.
        """
        cmd = self.get(name)
        if not cmd:
            return CommandResult(
                success=False,
                error=f"Command not found: {name}",
                exit_code=127,
            )

        context = context or CommandContext()

        # OPUS-311: Permission check via GovernanceGate
        permission_result = self._check_permission(name, args, context)
        if not permission_result.allowed:
            return CommandResult(
                success=False,
                error=f"Permission denied: {permission_result.message or permission_result.reason.value if permission_result.reason else 'unknown'}",
                exit_code=126,  # Command invoked cannot execute
            )

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

    def _check_permission(self, name: str, args: List[str], context: CommandContext) -> Any:  # PermissionResult
        """
        OPUS-311: Check permission via GovernanceGate.

        Returns PermissionResult (allowed/denied).
        """
        from vibe_core.protocols.governance_gate import (
            ANONYMOUS,
            SYSTEM,
            ExecutionContext,
            GovernanceGate,
            Identity,
            PermissionResult,
        )

        # Get or create governance gate
        if not hasattr(self, "_governance_gate"):
            self._governance_gate = GovernanceGate()

        # Determine identity from context
        if context.caller == "system":
            identity = SYSTEM
        elif context.metadata.get("identity"):
            identity = context.metadata["identity"]
        else:
            identity = ANONYMOUS

        # Build execution context
        exec_context = ExecutionContext(
            command=name,
            args=args,
            caller=context.caller,
            session_id=context.session_id,
        )

        return self._governance_gate.can_execute(identity, name, exec_context)

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
            SyncCICommand,
        )

        count = 0
        for cmd_class in [ChatCommand, BootCommand, StatusCommand, CommandsCommand, SyncCICommand]:
            if self.register(cmd_class()):
                count += 1

        logger.info(f"[COMMAND.REGISTRY] Registered {count} core commands")
        return count
