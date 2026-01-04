"""
Tools Plugin - Universal Tool Registry and Auto-Discovery.

Extracted from kernel_impl.py to reduce kernel size.
This plugin manages:
- Core tool registration (read_file, write_file, etc.)
- Agent tool auto-discovery
- Tool registry access via kernel.tool_registry
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.tool_discovery import ToolDiscovery
from vibe_core.tools.tool_registry import ToolRegistry

# SECURITY FIX (OPUS-018/P0.2): Import InvariantChecker for soul.yaml enforcement
try:
    from vibe_core.governance import InvariantChecker
except ImportError:
    InvariantChecker = None  # type: ignore

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("TOOLS_PLUGIN")


class ToolsPlugin(KernelPlugin):
    """
    Universal Tool Registry Plugin.

    Manages tool registration and discovery.
    Exposes kernel.tool_registry for tool access.
    """

    @property
    def plugin_id(self) -> str:
        return "tools"

    @property
    def dependencies(self) -> Set[str]:
        # Tools plugin should boot early - other plugins may need tools
        return set()

    @property
    def priority(self) -> int:
        return 5  # Very early - before most plugins

    def on_boot(
        self,
        kernel: "KernelProtocol",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """Initialize tool registry and discover tools."""
        try:
            # SECURITY FIX (OPUS-018/P0.2): Create InvariantChecker for soul.yaml enforcement
            invariant_checker = None
            if InvariantChecker is not None:
                soul_path = Path("config/soul.yaml")
                if soul_path.exists():
                    invariant_checker = InvariantChecker(str(soul_path))
                    logger.info(f"🛡️ Soul Governance ACTIVE: {invariant_checker.rule_count} rules from {soul_path}")
                else:
                    logger.warning("⚠️ Soul Governance: config/soul.yaml not found (governance disabled)")
            else:
                logger.warning("⚠️ Soul Governance: InvariantChecker not available")

            # Get capability checker
            capability_checker = getattr(kernel, "_check_agent_capability", None)

            # Create tool registry with InvariantChecker for soul.yaml enforcement
            self._registry = ToolRegistry(
                invariant_checker=invariant_checker,
                capability_checker=capability_checker,
                kernel=kernel,
            )

            # Register core tools
            self._register_core_tools(kernel)

            # Discover agent tools
            self._discover_agent_tools(kernel)

            # Expose registry on kernel for backward compatibility
            kernel.tool_registry = self._registry

            logger.info(f"ToolsPlugin booted ({len(self._registry)} tools)")
            return HookResult.ok()

        except Exception as e:
            logger.error(f"ToolsPlugin boot failed: {e}")
            return HookResult.error(str(e))

    def _register_core_tools(self, kernel: "KernelProtocol") -> None:
        """
        Register core tools that are available to all agents.

        Core tools are system-provided capabilities that don't belong to
        any specific agent.
        """
        from vibe_core.tools import (
            AddTaskTool,
            CompleteTaskTool,
            DelegateTool,
            ListTasksTool,
            ReadFileTool,
            WriteFileTool,
        )

        # File operations
        self._registry.register(ReadFileTool())
        self._registry.register(WriteFileTool())

        # Task management
        self._registry.register(AddTaskTool())
        self._registry.register(ListTasksTool())
        self._registry.register(CompleteTaskTool())

        # Inter-agent delegation
        delegate_tool = DelegateTool()
        delegate_tool.set_kernel(kernel)
        self._registry.register(delegate_tool)

        tool_names = ", ".join(self._registry.list_tools())
        logger.info(f"Registered {len(self._registry)} core tools: {tool_names}")

    def _discover_agent_tools(self, kernel: "KernelProtocol") -> None:
        """
        Auto-discover and register agent tools.

        Scans:
        - vibe_core/cartridges/system/{agent_id}/tools/*.py
        - vibe_core/cartridges/agent_city/{agent_id}/tools/*.py
        """
        logger.info("Starting auto-discovery of agent tools...")

        discovery = ToolDiscovery(root_path=Path("."))
        discovered_tools = discovery.discover_all_tools()

        registered_count = 0
        failed_count = 0

        for tool in discovered_tools:
            try:
                self._registry.register(tool)
                registered_count += 1

                # Inject I/O Service for tools that support it
                if hasattr(tool, "set_io_service") and callable(tool.set_io_service):
                    tool.set_io_service(kernel.io)
                    logger.debug(f"Registered: {tool.name} (with I/O Service)")
                else:
                    logger.debug(f"Registered: {tool.name}")

            except ValueError as e:
                logger.warning(f"Skipped {tool.name}: {e}")
                failed_count += 1
            except Exception as e:
                logger.error(f"Failed to register {tool.name}: {e}")
                failed_count += 1

        stats = discovery.get_discovery_stats()
        logger.info(f"Auto-discovery complete: {registered_count} tools, {failed_count} failed")

        if stats["discovered_by_agent"]:
            for agent_id, tool_names in stats["discovered_by_agent"].items():
                logger.debug(f"  {agent_id}: {', '.join(tool_names)}")

    def get_api(self) -> Optional[Any]:
        """Return the tool registry as API."""
        return self._registry
