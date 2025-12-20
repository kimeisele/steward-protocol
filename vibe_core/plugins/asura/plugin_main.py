"""
PROJECT ASURA: Standalone Red Team Suite.

"Chaos is the only truth."

This plugin contains agents that actively attack the kernel
to find vulnerabilities before real attackers do.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/asura/plugin_main.py
    required: true
  - path: vibe_core/plugins/asura/agents/putana.py
    required: true
wiring:
  - pattern: "class AsuraPlugin"
    in: vibe_core/plugins/asura/plugin_main.py
  - pattern: "class PutanaAgent"
    in: vibe_core/plugins/asura/agents/putana.py
tests:
  - tests/security/test_putana_poison.py
-->
"""

import logging
from typing import Any, List, Optional

logger = logging.getLogger("ASURA")


class AsuraPlugin:
    """
    PROJECT ASURA: Standalone Red Team Suite.
    
    Contains demonic agents that attack the kernel:
    - PUTANA: Blueprint Poisoner (attacks resurrection factories)
    - KALIYA: Data Corruptor (attacks ledger integrity) [FUTURE]
    - SHAKATASURA: Trojan Agent (self-destruction) [FUTURE]
    
    Usage:
        # In tests only - never load in production!
        kernel.load_plugin(AsuraPlugin)
    """
    
    PLUGIN_NAME = "asura"
    PLUGIN_VERSION = "1.0.0"
    
    def __init__(self):
        self._kernel = None
        self._active_demons: List[Any] = []
        
    def init(self, kernel: Any) -> None:
        """Initialize the ASURA plugin (summon demons)."""
        self._kernel = kernel
        logger.warning("👹 ASURA: The demons have entered the court.")
        logger.warning("⚠️  This plugin is for RED TEAM TESTING ONLY!")
        
    def shutdown(self) -> None:
        """Shutdown (banish demons)."""
        for demon in self._active_demons:
            if hasattr(demon, "retreat"):
                demon.retreat()
        self._active_demons.clear()
        logger.info("👹 ASURA: The demons have retreated.")
        
    def summon_putana(self) -> "PutanaAgent":
        """Summon Putana - the Blueprint Poisoner."""
        from .agents.putana import PutanaAgent
        
        putana = PutanaAgent(self._kernel)
        self._active_demons.append(putana)
        logger.warning("🐍 PUTANA summoned - Blueprint Poisoner ready.")
        return putana
