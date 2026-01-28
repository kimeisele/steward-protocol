"""
BALI SERVICE - Surrender & Resources
====================================

Implements BaliProtocol (Surrender/Yield).
Manages Economic Substrate (Bank/Vault).

"Bali gave everything. In surrender, there is infinite resource."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
# TODO: This should be DERIVED from mahamantra, not declared manually!
# "Manual Labor ist Maya" - MAHAPROMPT.md
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x1b8c8432"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from vibe_core.protocols.mahajanas.bali import (
    BaliProtocol,
    SurrenderResult,
    SurrenderState,
    SurrenderType,
)
from vibe_core.protocols.mahajanas.router import Mahajana

logger = logging.getLogger("BALI_SERVICE")


class BaliService(BaliProtocol):
    """
    BaliService - The Renouncer.
    Manages resources, graceful shutdown, and economic substrate.
    """

    def __init__(self):
        self._is_surrendered = False
        self._total_yields = 0
        self._total_releases = 0
        self._bank = None
        self._vault = None

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BALI  # Position 13

    def yield_cpu(self, duration_ms: int = 0) -> SurrenderResult:
        """Yield control for the specified duration."""
        self._total_yields += 1

        # In a real impl, this would asyncio.sleep(duration_ms / 1000)
        return {
            "success": True,
            "surrender_type": "yield",
            "resources_released": duration_ms,
            "timestamp": datetime.now().isoformat(),
            "message": "Yielded to the Mantra",
        }

    def surrender(self, surrender_type: SurrenderType = SurrenderType.YIELD) -> SurrenderResult:
        """Execute surrender."""
        if surrender_type == SurrenderType.SHUTDOWN or surrender_type == SurrenderType.PRAPATTI:
            self._is_surrendered = True

        return {
            "success": True,
            "surrender_type": surrender_type.value,
            "resources_released": 0,
            "timestamp": datetime.now().isoformat(),
            "message": f"Bali surrendered: {surrender_type.value}",
        }

    def can_surrender(self) -> bool:
        return True

    def is_surrendered(self) -> bool:
        return self._is_surrendered

    def release(self, resource_id: str) -> bool:
        """Release a resource."""
        self._total_releases += 1
        logger.info(f"🎁 BALI: Released resource {resource_id}")
        return True

    def get_state(self) -> SurrenderState:
        return {
            "can_surrender": True,
            "is_surrendered": self._is_surrendered,
            "total_yields": self._total_yields,
            "total_releases": self._total_releases,
            "last_surrender": datetime.now().isoformat(),
            "health": "pristine",
        }

    # --- Economic Substrate Delegation ---

    def get_bank(self, kernel: Any):
        """Get CivicBank via ServiceRegistry."""
        if self._bank is None:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.economy import BankProtocol

            self._bank = ServiceRegistry.get(BankProtocol)
        return self._bank

    def get_vault(self, kernel: Any):
        """Get CivicVault via ServiceRegistry."""
        if self._vault is None:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.economy import VaultProtocol

            self._vault = ServiceRegistry.get(VaultProtocol)
        return self._vault

    async def shutdown_orchestration(self, kernel: object, reason: str) -> None:
        """🛑 THE ASYNC SHUTDOWN ORCHESTRATION (Surrender). Delegated from Kernel."""
        import asyncio

        from vibe_core.ledger import SQLiteLedger

        logger.critical(f"🛑 BALI: Shutting down system (Reason: {reason})")

        if hasattr(kernel, "lineage"):
            from vibe_core.lineage import LineageEventType

            kernel.lineage.add_block(
                event_type=LineageEventType.KERNEL_SHUTDOWN, agent_id=None, data={"reason": reason}
            )
            kernel.lineage.close()

        prakriti = getattr(kernel, "prakriti", None)
        if prakriti:
            try:
                prakriti.end_session()
            except Exception as e:
                logger.error(f"❌ BALI: State preservation failed: {e}")

        # 🍎 ASYNC PERSISTENCE CLEANUP (ADR-204)
        try:
            from vibe_core.state.state_service import get_state_service

            workspace = getattr(kernel, "_workspace", None)
            ss = get_state_service(workspace)
            if ss._worker_task:
                ss._worker_task.cancel()
                logger.info("🛑 BALI: StateService background scribe stopped.")
        except Exception as e:
            logger.warning(f"⚠️ BALI: StateService shutdown failed: {e}")

        # Plugin Hook
        plugins = getattr(kernel, "_plugins", [])
        for plugin in plugins:
            if hasattr(plugin, "on_shutdown"):
                plugin.on_shutdown(kernel)

        setattr(kernel, "_status", "STOPPED")  # KernelStatus.STOPPED

        # Cancel Gateway
        gateway_task = getattr(kernel, "_gateway_task", None)
        if gateway_task:
            gateway_task.cancel()
            try:
                await gateway_task
            except asyncio.CancelledError:
                pass

        # Cleanup processes
        proc_mgr = getattr(kernel, "process_manager", None)
        if proc_mgr:
            proc_mgr.shutdown()

        # Close Ledger
        ledger = getattr(kernel, "ledger", None)
        if isinstance(ledger, SQLiteLedger):
            ledger.close()

        self._is_surrendered = True
