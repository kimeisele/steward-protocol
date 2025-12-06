#!/usr/bin/env python3
"""
TEST_WATCHMAN Cartridge - GOLDEN TEMPLATE

Copy this file and replace all YOUR_* placeholders.

REQUIRED CHANGES:
1. Rename class: Test_watchmanCartridge
2. Set agent_id, name, description, domain
3. Implement your capabilities in process()
4. Add tools in tools/ directory

ARCHITECTURE:
- Inherits from VibeAgent (or ContextAwareAgent for offline-first)
- OathMixin for Constitutional Oath binding
- Tools accessed via self.system.execute_tool() - NEVER import tools directly
"""

import logging
from typing import Any, Dict, Optional

from steward.oath_mixin import OathMixin
from vibe_core import Task, VibeAgent
from vibe_core.protocols import AgentManifest

logger = logging.getLogger("test_watchman")


class Test_watchmanCartridge(VibeAgent, OathMixin):
    """
    TEST_WATCHMAN - Monitor system health for testing purposes.

    Capabilities:
    - process_task: Description
    - report_status: Description
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config

        super().__init__(
            agent_id="test_watchman",  # lowercase, no spaces
            name="TEST_WATCHMAN",  # Display name
            version="1.0.0",
            author="Engineer",
            description="Monitor system health for testing purposes",
            domain="SPAWNED",  # See cartridge.yaml for options
            capabilities=["process_task", "report_status"],
        )

        # Constitutional Oath binding
        self.oath_mixin_init(self.agent_id)
        self.oath_sworn = True

        # ALL TOOLS: Accessed via kernel (self.system.execute_tool)
        # NEVER import tools directly - always go through the kernel
        logger.info(f"{self.name} initialized")

    def get_manifest(self) -> AgentManifest:
        """Return agent manifest for registration."""
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Main task processing entry point.

        Args:
            task: Task object with payload containing action and parameters

        Returns:
            Dict with status and results
        """
        action = task.payload.get("action")
        logger.info(f"{self.name} processing action: {action}")

        if action == "process_task":
            return self._handle_capability_1(task.payload)
        elif action == "report_status":
            return self._handle_capability_2(task.payload)
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}

    def _handle_capability_1(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle process_task.

        Tool access example:
            result = self.system.execute_tool(
                "test_watchman.main_tool",
                {"param": "value"}
            )
        """
        # TODO: Implement your capability
        return {"status": "success", "result": {}}

    def _handle_capability_2(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report_status."""
        # TODO: Implement your capability
        return {"status": "success", "result": {}}

    def report_status(self) -> Dict[str, Any]:
        """Return current agent status for monitoring."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "oath_sworn": self.oath_sworn,
        }


# Export for dynamic loading
__all__ = ["Test_watchmanCartridge"]
