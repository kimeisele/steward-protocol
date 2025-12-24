#!/usr/bin/env python3
"""
SCRIBE Cartridge - The Documentarian

SCRIBE is a VibeAgent that can be tasked with documentation-related work.

NOTE: UI Rendering is handled by InterfacePlugin, NOT by SCRIBE.
SCRIBE is just an agent that can be asked to do documentation tasks.
The actual markdown file rendering happens via the Interface Plugin's
renderer system (vibe_core/plugins/interface/renderers/).
"""

import logging
from typing import Any, Dict, Optional

from vibe_core.config import CityConfig
from vibe_core.protocols import AgentManifest, VibeAgent
from vibe_core.scheduling.task import Task
from vibe_core.steward import OathMixin

logger = logging.getLogger("SCRIBE")


class ScribeCartridge(VibeAgent, OathMixin):
    """
    SCRIBE Agent - The Documentarian.

    NOTE: This agent does NOT render UI files.
    UI rendering is handled by InterfacePlugin.
    """

    def __init__(self, config: Optional[CityConfig] = None):
        self.config = config or CityConfig()

        super().__init__(
            agent_id="scribe",
            name="SCRIBE",
            version="2.0.0",
            author="Steward Protocol",
            description="Documentation agent",
            domain="INFRASTRUCTURE",
            capabilities=["documentation", "publish_root"],
        )

        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.swear_oath_sync()

        logger.info("SCRIBE initialized (v2.0 - UI delegated to InterfacePlugin)")

    def get_manifest(self) -> AgentManifest:
        return AgentManifest(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            domain=self.domain,
            capabilities=self.capabilities,
            dependencies=[],
        )

    async def process(self, task: Task) -> Dict[str, Any]:
        """Process documentation tasks."""
        action = task.input.get("action") if hasattr(task, "input") else task.payload.get("action")
        logger.info(f"SCRIBE processing: {action}")

        # SCRIBE no longer does UI rendering - that's InterfacePlugin's job
        # SCRIBE can still be extended for other doc tasks (e.g., LLM-generated docs)

        return {
            "success": True,
            "message": f"SCRIBE received action: {action}",
            "note": "UI rendering delegated to InterfacePlugin",
        }

    def report_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "OPERATIONAL",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "oath_sworn": getattr(self, "oath_sworn", False),
        }
