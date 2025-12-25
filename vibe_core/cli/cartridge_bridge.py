"""
OPUS-307: Universal Cartridge Bridge - Lazy Loading Edition

THE BRIDGE that makes 43 tools accessible via dedicated CLI namespaces.

CRITICAL: Lazy Loading
- At boot: Only scans YAML manifests and lists .py files (NO Python imports)
- At execution: Imports tool module on-demand

Namespace Logic:
    vibe_core/cartridges/system/watchman/tools/system_health_check.py
    Tool name: watchman.health
    CLI: steward watchman health --action check_all

Usage:
    steward watchman health --action check_all
    steward auditor compliance --action inspect
    steward civic bank --action balance --agent_id foo
    steward <cartridge> --help         List tools for cartridge
    steward cartridges                 List all cartridges
"""

import importlib.util
import inspect
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

from vibe_core.protocols.cli import CLIMeta, register_cli
from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("CARTRIDGE_BRIDGE")


# =============================================================================
# LAZY REGISTRY - No Python imports at boot
# =============================================================================


@dataclass
class ToolStub:
    """Lightweight tool metadata - NO Python import."""

    tool_id: str  # e.g., "watchman.health"
    file_path: Path
    cartridge_id: str
    tool_name: str  # e.g., "health" (short name for CLI)

    # These are populated lazily on first access
    _tool_instance: Optional[Tool] = field(default=None, repr=False)
    _schema: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _description: Optional[str] = field(default=None, repr=False)


@dataclass
class CartridgeStub:
    """Lightweight cartridge metadata from YAML - NO Python import."""

    cartridge_id: str  # e.g., "watchman"
    name: str
    description: str
    domain: str
    yaml_path: Path
    tools_dir: Path
    tool_stubs: Dict[str, ToolStub] = field(default_factory=dict)


class LazyCartridgeRegistry:
    """
    Lazy cartridge registry.

    CRITICAL: Scans manifests and file listings ONLY.
    Never imports Python until tool execution.
    """

    _instance: Optional["LazyCartridgeRegistry"] = None

    CARTRIDGE_PATHS = [
        "vibe_core/cartridges/system",
        "vibe_core/cartridges/agent_city",
    ]

    def __init__(self, root_path: Path = None):
        self.root_path = (root_path or Path.cwd()).resolve()
        self._cartridges: Dict[str, CartridgeStub] = {}
        self._scanned = False

    @classmethod
    def get_instance(cls, root_path: Path = None) -> "LazyCartridgeRegistry":
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls(root_path)
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton (for testing)."""
        cls._instance = None

    def scan_manifests(self, force: bool = False) -> int:
        """
        Scan cartridge YAMLs and list tool files.

        OPUS-307 CONSOLIDATION: Delegates to CartridgeService.
        Converts CartridgeInfo -> CartridgeStub for CLI compatibility.

        Returns count of cartridges found.
        """
        if self._scanned and not force:
            return len(self._cartridges)

        self._cartridges.clear()

        # OPUS-307: Use unified CartridgeService
        from vibe_core.cartridge_service import CartridgeService

        svc = CartridgeService.get_instance(self.root_path)
        svc.scan(force=force)

        # Convert CartridgeInfo -> CartridgeStub
        for info in svc.list():
            stub = CartridgeStub(
                cartridge_id=info.cartridge_id,
                name=info.name,
                description=info.description,
                domain=info.domain,
                yaml_path=info.path / "cartridge.yaml",
                tools_dir=info.path / "tools",
            )

            # Convert ToolInfo -> ToolStub
            for tool_id, tool_info in info.tools.items():
                stub.tool_stubs[tool_id] = ToolStub(
                    tool_id=f"{info.cartridge_id}.{tool_id}",
                    file_path=info.path / "tools" / tool_info.tool_file,
                    cartridge_id=info.cartridge_id,
                    tool_name=tool_id,
                )

            self._cartridges[info.cartridge_id] = stub

        self._scanned = True
        logger.info(
            f"Lazy scan complete: {len(self._cartridges)} cartridges, "
            f"{sum(len(c.tool_stubs) for c in self._cartridges.values())} tool stubs"
        )
        return len(self._cartridges)

    def _scan_single_cartridge(self, cartridge_dir: Path, yaml_path: Path) -> None:
        """Scan one cartridge YAML and list tools (NO import)."""
        try:
            with open(yaml_path) as f:
                manifest = yaml.safe_load(f)

            meta = manifest.get("meta", {})
            agent = manifest.get("agent", {})

            # Extract cartridge ID from full ID or directory name
            full_id = meta.get("id", "")
            # "agent.steward.watchman" -> "watchman"
            cartridge_id = full_id.split(".")[-1] if full_id else cartridge_dir.name

            stub = CartridgeStub(
                cartridge_id=cartridge_id,
                name=meta.get("name", cartridge_id),
                description=meta.get("description", ""),
                domain=agent.get("domain", "UNKNOWN"),
                yaml_path=yaml_path,
                tools_dir=cartridge_dir / "tools",
            )

            # List tool files (NO import)
            if stub.tools_dir.exists():
                self._list_tool_files(stub)

            self._cartridges[cartridge_id] = stub

        except Exception as e:
            logger.warning(f"Failed to scan {yaml_path}: {e}")

    def _list_tool_files(self, cartridge: CartridgeStub) -> None:
        """List tool files and create stubs (NO import)."""
        for py_file in cartridge.tools_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if py_file.name.startswith("_"):
                continue

            # Derive tool name from file name
            # system_health_check.py -> health (simplified)
            # compliance_tool.py -> compliance
            file_stem = py_file.stem

            # Remove common suffixes
            tool_name = file_stem
            for suffix in ["_tool", "_tools", "_check", "_inspection"]:
                if tool_name.endswith(suffix):
                    tool_name = tool_name[: -len(suffix)]
                    break

            # Remove prefix if it matches cartridge
            if tool_name.startswith(f"{cartridge.cartridge_id}_"):
                tool_name = tool_name[len(cartridge.cartridge_id) + 1 :]

            # Create stub
            tool_id = f"{cartridge.cartridge_id}.{tool_name}"

            stub = ToolStub(
                tool_id=tool_id,
                file_path=py_file,
                cartridge_id=cartridge.cartridge_id,
                tool_name=tool_name,
            )

            cartridge.tool_stubs[tool_name] = stub

    def get_cartridge(self, cartridge_id: str) -> Optional[CartridgeStub]:
        """Get cartridge stub by ID."""
        if not self._scanned:
            self.scan_manifests()
        return self._cartridges.get(cartridge_id)

    def list_cartridges(self) -> List[CartridgeStub]:
        """List all cartridge stubs."""
        if not self._scanned:
            self.scan_manifests()
        return list(self._cartridges.values())

    def get_tool_stub(self, cartridge_id: str, tool_name: str) -> Optional[ToolStub]:
        """Get tool stub by cartridge and tool name."""
        cartridge = self.get_cartridge(cartridge_id)
        if not cartridge:
            return None
        return cartridge.tool_stubs.get(tool_name)

    def load_tool(self, stub: ToolStub) -> Optional[Tool]:
        """
        Actually import and instantiate the tool.

        THIS is where Python import happens - on demand only.
        """
        if stub._tool_instance is not None:
            return stub._tool_instance

        try:
            # Dynamic import
            module_name = f"cartridge_{stub.cartridge_id}_{stub.file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, stub.file_path)
            if spec is None or spec.loader is None:
                logger.error(f"Cannot create module spec for {stub.file_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find Tool classes
            tool_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ != module.__name__:
                    continue
                if issubclass(obj, Tool) and obj is not Tool:
                    # Verify it's not abstract
                    try:
                        # Check if all abstract methods are implemented
                        if not inspect.isabstract(obj):
                            tool_classes.append(obj)
                    except Exception:
                        pass

            if not tool_classes:
                logger.warning(f"No Tool classes found in {stub.file_path}")
                return None

            # Instantiate first tool class
            tool_class = tool_classes[0]

            # Try with services, fall back to no args
            try:
                from vibe_core.di import ServiceRegistry

                sig = inspect.signature(tool_class.__init__)
                if "services" in sig.parameters:
                    stub._tool_instance = tool_class(services=ServiceRegistry)
                else:
                    stub._tool_instance = tool_class()
            except Exception as e:
                logger.debug(f"Falling back to no-arg init: {e}")
                stub._tool_instance = tool_class()

            # Cache schema and description
            stub._schema = stub._tool_instance.parameters_schema
            stub._description = stub._tool_instance.description

            return stub._tool_instance

        except Exception as e:
            logger.error(f"Failed to load tool {stub.tool_id}: {e}")
            return None


# =============================================================================
# CLI BRIDGE - Dynamic namespace per cartridge
# =============================================================================


def parse_args_from_schema(args: List[str], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse CLI arguments based on tool's parameters_schema.

    Schema format:
        {
            "action": {"type": "string", "required": True, "description": "..."},
            "agent_id": {"type": "string", "required": False}
        }

    Args format:
        --action check_all --agent_id foo
        OR
        --action=check_all --agent_id=foo
    """
    params = {}
    i = 0

    while i < len(args):
        arg = args[i]

        if arg.startswith("--"):
            if "=" in arg:
                # --key=value format
                key, value = arg[2:].split("=", 1)
                params[key] = _coerce_type(value, schema.get(key, {}))
            elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                # --key value format
                key = arg[2:]
                value = args[i + 1]
                params[key] = _coerce_type(value, schema.get(key, {}))
                i += 1
            else:
                # --flag (boolean)
                key = arg[2:]
                params[key] = True
        i += 1

    return params


def _coerce_type(value: str, spec: Dict[str, Any]) -> Any:
    """Coerce string value to schema type."""
    type_name = spec.get("type", "string")

    if type_name == "integer":
        try:
            return int(value)
        except ValueError:
            return value
    elif type_name == "number":
        try:
            return float(value)
        except ValueError:
            return value
    elif type_name == "boolean":
        return value.lower() in ("true", "1", "yes")
    elif type_name == "array":
        # Support comma-separated values
        return value.split(",")
    elif type_name == "object":
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    else:
        return value


class CartridgeBridgeCLI:
    """
    Dynamic CLI handler for a single cartridge namespace.

    Created lazily for each cartridge on first access.
    """

    def __init__(self, cartridge: CartridgeStub, registry: LazyCartridgeRegistry):
        self.cartridge = cartridge
        self.registry = registry

    @property
    def meta(self) -> CLIMeta:
        tool_names = list(self.cartridge.tool_stubs.keys())
        return CLIMeta(
            command=self.cartridge.cartridge_id,
            description=f"{self.cartridge.name} - {self.cartridge.description[:50]}",
            domain=self.cartridge.domain.lower(),
            subcommands=tool_names,
            tags=["cartridge", self.cartridge.domain.lower()],
        )

    def run(self, args: List[str]) -> int:
        """Run cartridge command."""
        if not args or args[0] in ("--help", "-h", "help"):
            self._print_help()
            return 0

        tool_name = args[0]
        remaining = args[1:]

        # Handle --json flag
        as_json = "--json" in remaining
        remaining = [a for a in remaining if a != "--json"]

        # Get tool stub
        stub = self.cartridge.tool_stubs.get(tool_name)
        if not stub:
            # Try fuzzy match
            matches = [n for n in self.cartridge.tool_stubs.keys() if tool_name in n or n in tool_name]
            if matches:
                print(f"Unknown tool: {tool_name}")
                print(f"Did you mean: {', '.join(matches)}")
            else:
                print(f"Unknown tool: {tool_name}")
                self._print_help()
            return 1

        # Lazy load tool
        print(f"Loading {stub.tool_id}...")
        tool = self.registry.load_tool(stub)
        if not tool:
            print(f"Failed to load tool: {stub.tool_id}")
            return 1

        # Parse arguments
        schema = tool.parameters_schema
        params = parse_args_from_schema(remaining, schema)

        # Validate required parameters
        missing = []
        for param_name, param_spec in schema.items():
            if param_spec.get("required") and param_name not in params:
                missing.append(param_name)

        if missing:
            print(f"\nMissing required parameters: {', '.join(missing)}")
            self._print_tool_help(stub, schema)
            return 1

        # Execute
        try:
            tool.validate(params)
            result: ToolResult = tool.execute(params)

            if as_json:
                output = {
                    "tool_id": stub.tool_id,
                    "success": result.success,
                    "output": result.output,
                    "error": result.error,
                    "metadata": result.metadata,
                }
                print(json.dumps(output, indent=2, default=str))
            else:
                if result.success:
                    print(f"\n{stub.tool_id} completed successfully")
                    if result.output:
                        if isinstance(result.output, dict):
                            for k, v in result.output.items():
                                print(f"  {k}: {v}")
                        else:
                            print(f"Output: {result.output}")
                else:
                    print(f"\n{stub.tool_id} failed")
                    if result.error:
                        print(f"Error: {result.error}")

            return 0 if result.success else 1

        except Exception as e:
            print(f"Execution error: {e}")
            return 1

    def _print_help(self):
        """Print cartridge help."""
        print(f"\n{'=' * 60}")
        print(f"CARTRIDGE: {self.cartridge.cartridge_id}")
        print(f"{'=' * 60}")
        print(f"Name:   {self.cartridge.name}")
        print(f"Domain: {self.cartridge.domain}")
        if self.cartridge.description:
            print(f"Desc:   {self.cartridge.description[:80]}")

        print(f"\nTools ({len(self.cartridge.tool_stubs)}):")
        print("-" * 40)
        for tool_name, stub in sorted(self.cartridge.tool_stubs.items()):
            desc = stub._description or "(load for details)"
            print(f"  {tool_name:<25} {desc[:35]}...")

        print("\nUsage:")
        print(f"  steward {self.cartridge.cartridge_id} <tool> [--param=value]")
        print(f"  steward {self.cartridge.cartridge_id} <tool> --help")
        print(f"\n{'=' * 60}")

    def _print_tool_help(self, stub: ToolStub, schema: Dict[str, Any]):
        """Print tool help with parameters."""
        print(f"\n{'=' * 60}")
        print(f"TOOL: {stub.tool_id}")
        print(f"{'=' * 60}")
        if stub._description:
            print(f"Description: {stub._description}")

        print("\nParameters:")
        print("-" * 40)
        for param_name, param_spec in schema.items():
            req = "[required]" if param_spec.get("required") else "[optional]"
            ptype = param_spec.get("type", "string")
            desc = param_spec.get("description", "")[:40]
            print(f"  --{param_name:<20} {req:<12} ({ptype}) {desc}")

        print("\nExample:")
        example_params = []
        for param_name, param_spec in schema.items():
            if param_spec.get("required"):
                example_params.append(f"--{param_name}=<value>")
        print(f"  steward {stub.cartridge_id} {stub.tool_name} {' '.join(example_params)}")
        print(f"\n{'=' * 60}")


# =============================================================================
# MASTER CLI - Lists cartridges and routes to bridges
# =============================================================================


@register_cli
class CartridgesCLI:
    """
    Master CLI for listing all cartridges.

    Usage:
        steward cartridges              List all available cartridges
        steward cartridges --json       JSON output
    """

    @property
    def meta(self) -> CLIMeta:
        return CLIMeta(
            command="cartridges",
            description="List all available cartridge namespaces",
            domain="system",
            subcommands=[],
            tags=["cartridges", "discovery"],
        )

    def run(self, args: List[str]) -> int:
        """List all cartridges."""
        as_json = "--json" in args

        registry = LazyCartridgeRegistry.get_instance()
        registry.scan_manifests()

        cartridges = registry.list_cartridges()

        if as_json:
            output = {
                "total": len(cartridges),
                "cartridges": [
                    {
                        "id": c.cartridge_id,
                        "name": c.name,
                        "domain": c.domain,
                        "tools": list(c.tool_stubs.keys()),
                    }
                    for c in sorted(cartridges, key=lambda x: x.cartridge_id)
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'=' * 60}")
            print(f"CARTRIDGES ({len(cartridges)} available)")
            print(f"{'=' * 60}\n")

            for c in sorted(cartridges, key=lambda x: x.cartridge_id):
                tool_count = len(c.tool_stubs)
                tools_preview = ", ".join(list(c.tool_stubs.keys())[:3])
                if tool_count > 3:
                    tools_preview += f", +{tool_count - 3} more"
                print(f"  {c.cartridge_id:<15} [{c.domain:<12}] {tool_count} tools: {tools_preview}")

            print("\nUsage:")
            print("  steward <cartridge> --help           Show cartridge tools")
            print("  steward <cartridge> <tool> [args]    Execute tool")
            print(f"\n{'=' * 60}")

        return 0


# =============================================================================
# DYNAMIC REGISTRATION
# =============================================================================


def register_cartridge_bridges():
    """
    Dynamically register CLI handlers for each cartridge.

    Called during CLI initialization.
    CRITICAL: This uses lazy manifest scanning - NO Python imports.
    """
    from vibe_core.protocols.cli import CLIRegistry

    registry = LazyCartridgeRegistry.get_instance()
    registry.scan_manifests()

    registered = 0
    for cartridge in registry.list_cartridges():
        if CLIRegistry.has(cartridge.cartridge_id):
            continue  # Don't override existing CLIs (like 'test')

        bridge = CartridgeBridgeCLI(cartridge, registry)
        # Register in both _handlers (for commands()) and _instances (for get())
        # Use CartridgeBridgeCLI class as placeholder in _handlers
        CLIRegistry._handlers[cartridge.cartridge_id] = CartridgeBridgeCLI
        CLIRegistry._instances[cartridge.cartridge_id] = bridge
        registered += 1

    logger.info(f"Registered {registered} cartridge CLI bridges (lazy loading)")


def main():
    """Entry point for testing."""
    cli = CartridgesCLI()
    sys.exit(cli.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
