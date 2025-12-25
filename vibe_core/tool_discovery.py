"""
Tool Discovery - Automatic tool registration from agent directories.

Scans agent tool directories and registers tools automatically.

OPUS-307 D.1: Now supports dependency injection via ServiceRegistry.
Tools that accept a 'services' parameter will receive the global registry.
"""

import importlib.util
import inspect
import logging
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Type

from vibe_core.tools.tool_protocol import Tool

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("TOOL_DISCOVERY")


class ToolDiscoveryError(Exception):
    """Raised when tool discovery encounters a non-fatal error."""

    pass


class ToolDiscovery:
    """
    Discovers and loads tools from agent directories.

    Scans:
    - vibe_core/cartridges/system/{agent_id}/tools/*.py
    - vibe_core/cartridges/agent_city/{agent_id}/tools/*.py

    For each .py file:
    1. Import module dynamically
    2. Find classes implementing Tool protocol
    3. Return tool instances

    Error Handling:
    - Import errors are logged but don't crash discovery
    - Invalid tools are skipped
    - Discovery continues even if some tools fail
    """

    # Directories to scan for agent tools
    SCAN_PATHS = [
        "vibe_core/cartridges/system",
        "vibe_core/cartridges/agent_city",
    ]

    def __init__(self, root_path: Path = Path("."), services: Optional["ServiceRegistry"] = None):
        """
        Initialize tool discovery.

        Args:
            root_path: Project root path (default: current directory)
            services: ServiceRegistry for dependency injection (OPUS-307 D.1).
                     If provided, tools that accept 'services' will receive it.
        """
        self.root_path = Path(root_path).resolve()
        self.services = services
        self.discovered_tools: List[Tool] = []
        self.failed_tools: List[dict] = []

    def discover_all_tools(self) -> List[Tool]:
        """
        Discover all tools from all agent directories.

        Returns:
            List of Tool instances ready for registration

        Example:
            >>> discovery = ToolDiscovery()
            >>> tools = discovery.discover_all_tools()
            >>> for tool in tools:
            ...     registry.register(tool)
        """
        logger.info("🔍 Starting tool discovery...")

        for scan_path in self.SCAN_PATHS:
            base_dir = self.root_path / scan_path

            if not base_dir.exists():
                logger.debug(f"Scan path does not exist: {base_dir}")
                continue

            logger.info(f"📂 Scanning {scan_path}/")

            # Find all agent directories
            for agent_dir in base_dir.iterdir():
                if not agent_dir.is_dir():
                    continue

                agent_id = agent_dir.name
                tools_dir = agent_dir / "tools"

                if not tools_dir.exists() or not tools_dir.is_dir():
                    continue

                # Discover tools for this agent
                self._discover_agent_tools(agent_id, tools_dir)

        logger.info(
            f"✅ Tool discovery complete: {len(self.discovered_tools)} tools found, {len(self.failed_tools)} failed"
        )

        if self.failed_tools:
            logger.warning(f"⚠️  Failed to load {len(self.failed_tools)} tools:")
            for failure in self.failed_tools:
                logger.warning(f"   - {failure['agent_id']}.{failure['file']}: {failure['error']}")

        return self.discovered_tools

    def _discover_agent_tools(self, agent_id: str, tools_dir: Path) -> None:
        """
        Discover tools for a specific agent.

        Args:
            agent_id: Agent identifier
            tools_dir: Path to agent's tools directory
        """
        logger.info(f"🔧 Discovering tools for agent: {agent_id}")

        # Find all .py files (except __init__.py)
        tool_files = [f for f in tools_dir.glob("*.py") if f.name != "__init__.py"]

        if not tool_files:
            logger.debug(f"   No tool files found in {tools_dir}")
            return

        for tool_file in tool_files:
            try:
                self._load_tool_from_file(agent_id, tool_file)
            except Exception as e:
                # Log error but continue discovery
                logger.error(f"   ❌ Failed to load {tool_file.name}: {type(e).__name__}: {e}")
                self.failed_tools.append(
                    {
                        "agent_id": agent_id,
                        "file": tool_file.name,
                        "error": str(e),
                    }
                )

    def _load_tool_from_file(self, agent_id: str, tool_file: Path) -> None:
        """
        Load tool(s) from a Python file.

        Args:
            agent_id: Agent identifier
            tool_file: Path to .py file containing tool

        Raises:
            ToolDiscoveryError: If tool cannot be loaded
        """
        # Import module dynamically
        module_name = f"{agent_id}_tools_{tool_file.stem}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, tool_file)
            if spec is None or spec.loader is None:
                raise ToolDiscoveryError(f"Cannot create module spec for {tool_file}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        except Exception as e:
            raise ToolDiscoveryError(f"Import failed: {e}") from e

        # Find all Tool classes in module
        tool_classes = self._find_tool_classes(module)

        if not tool_classes:
            logger.debug(f"   ⊘ No Tool classes found in {tool_file.name}")
            return

        # Instantiate and collect tools
        for tool_class in tool_classes:
            try:
                tool = self._instantiate_tool(tool_class)
                self.discovered_tools.append(tool)
                logger.info(f"   ✅ Discovered: {tool.name} ({tool_class.__name__})")

            except Exception as e:
                logger.error(f"   ❌ Failed to instantiate {tool_class.__name__}: {e}")
                self.failed_tools.append(
                    {
                        "agent_id": agent_id,
                        "file": tool_file.name,
                        "error": f"Instantiation failed: {e}",
                    }
                )

    def _instantiate_tool(self, tool_class: Type[Tool]) -> Tool:
        """
        Instantiate a tool with dependency injection support.

        OPUS-307 D.1: Tries to inject ServiceRegistry if tool accepts it.
        Falls back to no-argument instantiation for legacy tools.

        Args:
            tool_class: Tool class to instantiate

        Returns:
            Tool instance
        """
        # Check if tool's __init__ accepts 'services' parameter
        sig = inspect.signature(tool_class.__init__)
        params = sig.parameters

        if "services" in params and self.services is not None:
            # New-style tool with DI support
            return tool_class(services=self.services)
        else:
            # Legacy tool without DI - instantiate without arguments
            return tool_class()

    def _find_tool_classes(self, module) -> List[Type[Tool]]:
        """
        Find all classes in module that implement Tool protocol.

        Args:
            module: Python module to inspect

        Returns:
            List of Tool classes (not instances)
        """
        tool_classes = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip imported classes (only want classes defined in this module)
            if obj.__module__ != module.__name__:
                continue

            # Check if class implements Tool protocol
            if self._is_tool_class(obj):
                tool_classes.append(obj)

        return tool_classes

    def _is_tool_class(self, cls: type) -> bool:
        """
        Check if a class implements the Tool protocol.

        Args:
            cls: Class to check

        Returns:
            True if class implements Tool protocol
        """
        # Check if class is subclass of Tool (but not Tool itself)
        if not issubclass(cls, Tool):
            return False

        if cls is Tool:
            return False

        # Verify required methods exist and are implemented
        required_methods = ["name", "description", "parameters_schema", "validate", "execute"]

        for method in required_methods:
            if not hasattr(cls, method):
                return False

        return True

    def get_discovery_stats(self) -> dict:
        """
        Get discovery statistics.

        Returns:
            Dictionary with discovery stats
        """
        return {
            "total_discovered": len(self.discovered_tools),
            "total_failed": len(self.failed_tools),
            "discovered_by_agent": self._group_by_agent(),
            "failures": self.failed_tools,
        }

    def _group_by_agent(self) -> dict:
        """
        Group discovered tools by agent ID.

        Returns:
            {agent_id: [tool_names]}
        """
        grouped = {}
        for tool in self.discovered_tools:
            # Extract agent_id from tool name (format: agent_id.tool_name)
            tool_name = tool.name
            if "." in tool_name:
                agent_id = tool_name.split(".")[0]
            else:
                agent_id = "unknown"

            if agent_id not in grouped:
                grouped[agent_id] = []

            grouped[agent_id].append(tool_name)

        return grouped
