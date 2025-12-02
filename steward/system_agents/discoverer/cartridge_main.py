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

from .agent import Discoverer


class DiscovererCartridge(Discoverer):
    """
    Cartridge wrapper for Discoverer agent.

    Inherits all functionality from Discoverer (agent.py).
    This wrapper exists for cartridge system compliance:
    - File must be named cartridge_main.py
    - Class must end with "Cartridge"
    - Must inherit from VibeAgent (via Discoverer)
    """

    pass


__all__ = ["DiscovererCartridge"]
