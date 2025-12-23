"""
Samsara Plugin - Entropy Management Engine

OPUS-209: Extracted from kernel_impl.py
OPUS-210: PluginStateContract compliant

Enforces mortality on the ledger - removes oldest events to make room for new creation.
Named after Samsara, the cycle of death and rebirth.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("SAMSARA")

MAX_ENTROPY_EVENTS = 10000
ROTATION_THRESHOLD = 10000


class SamsaraPlugin(KernelPlugin):
    """
    Entropy Management - Ledger cleanup and rotation.

    OPUS-210: Implements PluginStateContract for Prakriti integration.
    """

    plugin_id = "samsara"

    # State paths for PluginStateContract
    STATE_DIR = Path(".vibe/state/plugins/samsara")

    def __init__(self):
        self._kernel: Optional["RealVibeKernel"] = None
        self._rotation_count: int = 0
        self._events_dissolved: int = 0
        self._last_rotation: Optional[str] = None

    # =========================================================================
    # PluginStateContract Implementation (OPUS-210)
    # =========================================================================

    def get_state_paths(self) -> List[Path]:
        """Return paths where this plugin stores state."""
        return [self.STATE_DIR]

    def snapshot_state(self) -> Dict[str, Any]:
        """Return current runtime state for backup."""
        return {
            "version": 1,
            "rotation_count": self._rotation_count,
            "events_dissolved": self._events_dissolved,
            "last_rotation": self._last_rotation,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from snapshot (crash recovery)."""
        if snapshot.get("version") == 1:
            self._rotation_count = snapshot.get("rotation_count", 0)
            self._events_dissolved = snapshot.get("events_dissolved", 0)
            self._last_rotation = snapshot.get("last_rotation")

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
                        ledger.set_meta("health_anchor", (0, "0" * 64))
                except Exception as e:
                    logger.critical(f"🔥 SAMSARA FAILED: {e}")

    def get_api(self):
        return {"enforce_entropy_limits": self.enforce_entropy_limits}
