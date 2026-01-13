#!/usr/bin/env python3
"""
YOUR_AGENT_NAME Cartridge - GOLDEN TEMPLATE

Copy this file and replace all YOUR_* placeholders.

REQUIRED CHANGES:
1. Rename class: YourAgentCartridge
2. Set agent_id, name, description, domain
3. Implement your capabilities in process()
4. Add tools in tools/ directory

ARCHITECTURE:
- Inherits from VibeAgent (or ContextAwareAgent for offline-first)
- OathMixin for Constitutional Oath binding
- Tools accessed via self.system.execute_tool() - NEVER import tools directly
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x0a67b66f"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict, Optional

from vibe_core import Task, VibeAgent
from vibe_core.protocols import AgentManifest
from vibe_core.steward.oath_mixin import OathMixin

logger = logging.getLogger("YOUR_AGENT_ID")


class YourAgentCartridge(VibeAgent, OathMixin):
    """
    YOUR_AGENT_NAME - YOUR_SHORT_DESCRIPTION.

    Capabilities:
    - YOUR_CAPABILITY_1: Description
    - YOUR_CAPABILITY_2: Description
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config

        super().__init__(
            agent_id="YOUR_AGENT_ID",  # lowercase, no spaces
            name="YOUR_AGENT_NAME",  # Display name
            version="1.0.0",
            author="YOUR_NAME",
            description="YOUR_AGENT_DESCRIPTION",
            domain="YOUR_DOMAIN",  # See cartridge.yaml for options
            capabilities=["YOUR_CAPABILITY_1", "YOUR_CAPABILITY_2"],
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

        if action == "YOUR_CAPABILITY_1":
            return self._handle_capability_1(task.payload)
        elif action == "YOUR_CAPABILITY_2":
            return self._handle_capability_2(task.payload)
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}

    def _handle_capability_1(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle YOUR_CAPABILITY_1.

        Tool access example:
            result = self.system.execute_tool(
                "YOUR_AGENT_ID.YOUR_TOOL_NAME",
                {"param": "value"}
            )
        """
        # TODO: Implement your capability
        return {"status": "success", "result": {}}

    def _handle_capability_2(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle YOUR_CAPABILITY_2."""
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
__all__ = ["YourAgentCartridge"]
