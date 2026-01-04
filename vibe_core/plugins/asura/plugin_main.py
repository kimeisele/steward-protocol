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

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

    from .agents.putana import PutanaAgent

logger = logging.getLogger("ASURA")


class AsuraPlugin(KernelPlugin):
    """
    PROJECT ASURA: Standalone Red Team Suite.

    Contains demonic agents that attack the kernel:
    - PUTANA: Blueprint Poisoner (attacks resurrection factories)
    - KALIYA: Data Corruptor (attacks ledger integrity) [FUTURE]
    - SHAKATASURA: Trojan Agent (self-destruction) [FUTURE]

    OPUS-307: Now properly implements KernelPlugin protocol.

    Usage:
        # In tests only - never load in production!
        kernel.load_plugin(AsuraPlugin)
    """

    def __init__(self):
        self._kernel: Optional["KernelProtocol"] = None
        self._active_demons: List[Any] = []

    @property
    def plugin_id(self) -> str:
        """Unique identifier for ASURA plugin."""
        return "asura"

    def on_boot(
        self,
        kernel: "KernelProtocol",
        config: Optional[Dict[str, object]] = None,
    ) -> HookResult:
        """Initialize the ASURA plugin (summon demons)."""
        self._kernel = kernel
        logger.warning("👹 ASURA: The demons have entered the court.")
        logger.warning("⚠️  This plugin is for RED TEAM TESTING ONLY!")
        return HookResult.ok()

    def on_shutdown(self, kernel: "KernelProtocol") -> HookResult:
        """Shutdown (banish demons)."""
        for demon in self._active_demons:
            if hasattr(demon, "retreat"):
                demon.retreat()
        self._active_demons.clear()
        logger.info("👹 ASURA: The demons have retreated.")
        return HookResult.ok()

    def summon_putana(self) -> "PutanaAgent":
        """Summon Putana - the Blueprint Poisoner."""
        from .agents.putana import PutanaAgent

        putana = PutanaAgent(self._kernel)
        self._active_demons.append(putana)
        logger.warning("🐍 PUTANA summoned - Blueprint Poisoner ready.")
        return putana
