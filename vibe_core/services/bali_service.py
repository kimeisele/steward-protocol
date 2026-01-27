"""
BALI SERVICE - Surrender & Resources
====================================

Implements BaliProtocol (Surrender/Yield).
Manages Economic Substrate (Bank/Vault).

"Bali gave everything. In surrender, there is infinite resource."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x1b8c8432"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import Any, Dict, Optional

# MAHA COMPUTE INTEGRATION: Attractor-based resource allocation
from vibe_core.mahamantra.protocols._maha_compute import (
    ATTRACTOR_FIELD,
    ATTRACTOR_FIXED,
    MahaComputeProtocol,
)
from vibe_core.protocols.mahajanas.bali import (
    BaliProtocol,
    SurrenderResult,
    SurrenderState,
    SurrenderType,
)
from vibe_core.protocols.mahajanas.router import Mahajana

logger = logging.getLogger("BALI_SERVICE")

# =============================================================================
# ATTRACTOR YIELD CONSTANTS (from Bhagavad Gita Chapter 18)
# =============================================================================
# Resource allocation follows attractor dynamics:
# - Attractor 18: Fixed yield of 18ms (stable, predictable)
# - Attractor 99: Yield = total_yields % 99 (cyclic, dynamic)
# - Attractor 136: Yield proportional to field coherence
# =============================================================================


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
        """
        YIELD_CPU: Yield control with ATTRACTOR-BASED RESOURCE ALLOCATION.

        The MahaCompute attractor determines yield behavior:
        - Attractor 18 (fixed): Yield exactly 18ms (stable)
        - Attractor 99 (cycle): Yield = total_yields % 99 ms (cyclic)
        - Attractor 136 (field): Yield proportional to field (136 * coherence)
        """
        self._total_yields += 1

        # === MAHA COMPUTE STEERING ===
        actual_yield_ms = duration_ms
        attractor_used = None
        steering_applied = False

        try:
            from vibe_core.di import ServiceRegistry

            if ServiceRegistry.is_registered(MahaComputeProtocol):
                maha_service = ServiceRegistry.get(MahaComputeProtocol)
                result = maha_service.compute_now(seed=self._total_yields)
                attractor_used = result.attractor

                # Apply attractor-based yield timing
                if attractor_used == ATTRACTOR_FIXED:  # 18
                    actual_yield_ms = 18  # Fixed, stable yield
                elif attractor_used == 99:
                    actual_yield_ms = self._total_yields % 99  # Cyclic
                elif attractor_used == ATTRACTOR_FIELD:  # 136
                    # Proportional to field coherence (iterations as proxy)
                    coherence = 1.0 - (result.iterations / 137)
                    actual_yield_ms = int(136 * coherence)
                else:
                    # Other attractors: use requested duration
                    actual_yield_ms = duration_ms

                steering_applied = True

        except Exception as e:
            logger.debug(f"MahaCompute steering unavailable: {e}")

        # In a real impl, this would asyncio.sleep(actual_yield_ms / 1000)
        message = (
            f"Yielded {actual_yield_ms}ms (attractor={attractor_used})" if steering_applied else "Yielded to the Mantra"
        )

        return {
            "success": True,
            "surrender_type": "yield",
            "resources_released": actual_yield_ms,  # Now meaningful!
            "timestamp": datetime.now().isoformat(),
            "message": message,
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
