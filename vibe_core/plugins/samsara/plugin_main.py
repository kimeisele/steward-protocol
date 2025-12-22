"""
Samsara Plugin - Entropy Management Engine

OPUS-209: Extracted from kernel_impl.py

Enforces mortality on the ledger - removes oldest events to make room for new creation.
Named after Samsara, the cycle of death and rebirth.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("SAMSARA")

MAX_ENTROPY_EVENTS = 10000
ROTATION_THRESHOLD = 10000


class SamsaraPlugin(KernelPlugin):
    """Entropy Management - Ledger cleanup and rotation."""

    plugin_id = "samsara"

    def __init__(self):
        self._kernel: Optional["RealVibeKernel"] = None

    def on_boot(self, kernel: "RealVibeKernel", config: Optional[Dict[str, Any]] = None) -> HookResult:
        self._kernel = kernel
        logger.info("🕉️ Samsara Engine initialized")
        return HookResult.ok()

    def enforce_entropy_limits(self):
        """
        SAMSARA ENGINE: Enforces mortality on the ledger.
        Removes oldest events to make room for new creation.
        """
        if not self._kernel:
            return

        from vibe_core.ledger import InMemoryLedger, SQLiteLedger

        ledger = self._kernel._ledger

        if isinstance(ledger, InMemoryLedger):
            if hasattr(ledger, "events"):
                current_entropy = len(ledger.events)
                if current_entropy > MAX_ENTROPY_EVENTS:
                    excess = current_entropy - MAX_ENTROPY_EVENTS
                    ledger.events = ledger.events[excess:]
                    logger.warning(f"🕉️ PRALAYA EXECUTED: Dissolved {excess} stale events.")

        elif isinstance(ledger, SQLiteLedger):
            current_count = ledger.count_events()
            if current_count > ROTATION_THRESHOLD:
                try:
                    logger.info(f"🕉️ SAMSARA TRIGGERED: Event count {current_count} > {ROTATION_THRESHOLD}")
                    archive_path = ledger.rotate()
                    if archive_path:
                        logger.info(f"✅ Samsara complete. Archived to {archive_path}")
                        ledger.set_meta('health_anchor', (0, "0"*64))
                except Exception as e:
                    logger.critical(f"🔥 SAMSARA FAILED: {e}")

    def get_api(self):
        return {"enforce_entropy_limits": self.enforce_entropy_limits}
