"""
Tool Discovery - Automatic tool registration from agent directories.

OPUS-307 Phase D: Now uses CartridgeService for discovery (GAD-000).
No more duplicate scanning - single source of truth.

OPUS-307 D.1: Supports dependency injection via ServiceRegistry.
Tools that accept a 'services' parameter will receive the global registry.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from vibe_core.tools.tool_protocol import Tool

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("TOOL_DISCOVERY")


class ToolDiscoveryError(Exception):
    """Raised when tool discovery encounters a non-fatal error."""

    pass


class ToolDiscovery:
    """
    Discovers and loads tools from cartridges.

    OPUS-307: Uses CartridgeService for discovery (single source of truth).

    Error Handling:
    - Import errors are logged but don't crash discovery
    - Invalid tools are skipped
    - Discovery continues even if some tools fail
    """

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
        Discover all tools from all cartridges.

        OPUS-307: Uses CartridgeService for discovery.

        Returns:
            List of Tool instances ready for registration
        """
        logger.info("🔍 Starting tool discovery via CartridgeService...")

        # OPUS-307: Use CartridgeService instead of direct scanning
        from vibe_core.cartridge_service import CartridgeService

        svc = CartridgeService.get_instance(self.root_path)
        svc.scan()

        for cartridge in svc.list():
            if not cartridge.enabled:
                continue

            cartridge_id = cartridge.cartridge_id

            for tool_id in cartridge.tools.keys():
                try:
                    tool = svc.load_tool(cartridge_id, tool_id)
                    if tool:
                        self.discovered_tools.append(tool)
                        logger.info(f"   ✅ Discovered: {cartridge_id}.{tool_id}")
                except Exception as e:
                    logger.error(f"   ❌ Failed to load {cartridge_id}.{tool_id}: {e}")
                    self.failed_tools.append(
                        {
                            "agent_id": cartridge_id,
                            "file": tool_id,
                            "error": str(e),
                        }
                    )

        logger.info(
            f"✅ Tool discovery complete: {len(self.discovered_tools)} tools found, {len(self.failed_tools)} failed"
        )

        if self.failed_tools:
            logger.warning(f"⚠️  Failed to load {len(self.failed_tools)} tools:")
            for failure in self.failed_tools:
                logger.warning(f"   - {failure['agent_id']}.{failure['file']}: {failure['error']}")

        return self.discovered_tools

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
