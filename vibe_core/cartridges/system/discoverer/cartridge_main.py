#!/usr/bin/env python3
"""
DISCOVERER Cartridge - Agent Discovery and Registration

This is the cartridge wrapper for the Discoverer agent.
The core logic lives in agent.py for backwards compatibility.

Role:
1. Discovery: Monitors `agent_city` for new agent manifests
2. Verification: Validates `steward.json` against the schema
3. Registration: Onboards valid agents into the Kernel
4. Governance: Enforces the Constitution

NOTE: This is a SYSTEM AGENT - infrastructure for agent discovery,
NOT a citizen agent. The Discoverer is "The First Citizen" - the guardian
that enables all other agents to exist.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x394330c0"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict

# NOTE: Absolute import required for Late Binding (ProcessManager loads via importlib)
from vibe_core.cartridges.system.discoverer.agent import Discoverer

logger = logging.getLogger("DISCOVERER_CARTRIDGE")


class DiscovererCartridge(Discoverer):
    """
    Cartridge wrapper for Discoverer agent.

    Inherits all functionality from Discoverer (agent.py).
    This wrapper exists for cartridge system compliance:
    - File must be named cartridge_main.py
    - Class must end with "Cartridge"
    - Must inherit from VibeAgent (via Discoverer)
    """

    def __init__(self, kernel=None, config=None):
        """Initialize Discoverer cartridge."""
        super().__init__(kernel=kernel, config=config)
        logger.info("🧙 DISCOVERER cartridge initialized (The First Citizen)")

    def get_manifest(self) -> Dict[str, Any]:
        """Return agent manifest (identity + capabilities)."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": "1.0.0",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "type": "system_agent",
            "description": "Guardian of Agent City - discovers and registers agents",
        }

    def report_status(self) -> Dict[str, Any]:
        """Report DISCOVERER status for observability (Article IV compliance)."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "RUNNING" if self.monitoring_active else "IDLE",
            "domain": self.domain,
            "capabilities": self.capabilities,
            "known_agents": len(self.known_agents),
            "monitoring_active": self.monitoring_active,
            "description": "Guardian of Agent City - discovers and registers agents",
        }


__all__ = ["DiscovererCartridge"]
