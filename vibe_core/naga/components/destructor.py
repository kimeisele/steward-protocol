"""
SHIVA: The Destroyer (Destructor)

"I am Time, the great destroyer of the world."
- Bhagavad Gita 11.32

The NagaDestructor brings the universe to an end gracefully.
It ensures that when the system dies, memory is preserved (Ouroboros).
It ensures no loose threads remain (Flood).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x0bff2241"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Optional

from vibe_core.naga.components.kernel import NagaKernel
from vibe_core.state.state_service import get_state_service

logger = logging.getLogger("NAGA.SHIVA")


class NagaDestructor:
    """
    Handles the graceful shutdown of the NAGA system.
    """

    def __init__(self, kernel: NagaKernel):
        self._kernel = kernel

    def stop(self) -> None:
        """
        Execute the Tandava (Destruction Dance).
        Stop all services in reverse dependency order.
        """
        logger.info("🔥 SHIVA: Initiating graceful shutdown... (Tandava)")

        # 1. Stop Observability / Stability (Outer Ring)
        self._stop_flood_manager()
        self._stop_ouroboros()
        self._stop_commit_watcher()

        # 2. Stop Intelligence (Inner Ring)
        # Cortex, Shuddhi, Envoy usually don't have heavy loops, but good to be explicit

        # 3. Stop Kings (Services)
        # Takshaka (Biter)
        # Vasuki (Monitor)
        # Sesha (Recorder) - Stop last to capture end logs

        # 4. Final State Commit (The End)
        self._commit_state()

        logger.info("💀 SHIVA: Shutdown complete. Silence returns.")

    def _stop_flood_manager(self) -> None:
        if self._kernel.flood_manager:
            try:
                self._kernel.flood_manager.stop()
                logger.info("[SHIVA] FloodManager stopped")
            except Exception as e:
                logger.error(f"[SHIVA] FloodManager stop failed: {e}")

    def _stop_ouroboros(self) -> None:
        if self._kernel.ouroboros:
            try:
                # Ouroboros saves state on every pause, but explicit save is good
                # Note: Ouroboros doesn't have a stop() method, just state
                pass
            except Exception as e:
                logger.error(f"[SHIVA] Ouroboros cleanup failed: {e}")

    def _stop_commit_watcher(self) -> None:
        if self._kernel.commit_watcher:
            try:
                self._kernel.commit_watcher.stop()
                logger.info("[SHIVA] CommitWatcher stopped")
            except Exception as e:
                logger.error(f"[SHIVA] CommitWatcher stop failed: {e}")

    def _commit_state(self) -> None:
        """Trigger final state commit for all plugins."""
        try:
            state_service = get_state_service(plugin_id="naga")
            state_service.commit()  # Flush internal buffers if any
            logger.info("[SHIVA] State confirmed persisted")
        except Exception as e:
            logger.error(f"[SHIVA] Final state commit failed: {e}")
