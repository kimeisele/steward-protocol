"""
State Sanctifier - DI.py Integration for the Visnu Layer (Priority 0)

OPUS-211: Full System Integration

This module sanctifies the core state components into the ServiceRegistry.
By doing this in the IntegrityGuard (Priority 0), we ensure that all
subsequent plugins and agents have access to the unified state protocols.
"""

import logging
from typing import TYPE_CHECKING

from vibe_core.di import ServiceRegistry
from vibe_core.protocols import (
    PrakritiProtocol,
    StateServiceProtocol,
    StateSyncHolonProtocol,
    StateSyncWeaverProtocol,
)

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("INTEGRITY_GUARD.SANCTIFIER")


def sanctify_state_system(kernel: "KernelProtocol") -> None:
    """
    Sanctifies the state engine into the global ServiceRegistry.

    This is the 'Visnu-protected' way: wiring happens in the Priority 0
    Integrity Aditya, keeping the Kernel Eternal and clean.
    """
    try:
        # 1. Sanctify Prakriti (The Supreme State Engine)
        if hasattr(kernel, "prakriti") and kernel.prakriti:
            ServiceRegistry.register(PrakritiProtocol, kernel.prakriti)
            logger.info("🕉️  Prakriti Protocol sanctified in ServiceRegistry")

            # 2. Sanctify SyncHolon (The Tanmatra Bridge)
            # SyncHolon is managed by Prakriti
            if hasattr(kernel.prakriti, "sync_holon") and kernel.prakriti.sync_holon:
                ServiceRegistry.register(StateSyncHolonProtocol, kernel.prakriti.sync_holon)
                logger.info("🕉️  StateSyncHolon Protocol sanctified in ServiceRegistry")

        # 3. Sanctify StateService (Ahamkara / Persistence)
        from vibe_core.state.state_service import get_state_service

        # Resolve workspace from kernel
        workspace = getattr(kernel, "_workspace", None)
        state_service = get_state_service(workspace)

        ServiceRegistry.register(StateServiceProtocol, state_service)
        logger.info("🕉️  StateService Protocol sanctified in ServiceRegistry")

        # 4. Sanctify StateSyncWeaver (Meta-orchestration)
        from vibe_core.state.weaver import get_state_sync_weaver

        # Weaver is a singleton that needs Prakriti
        if hasattr(kernel, "prakriti") and kernel.prakriti:
            ServiceRegistry.register_factory(StateSyncWeaverProtocol, lambda: get_state_sync_weaver(kernel.prakriti))
            logger.info("🕉️  StateSyncWeaver Protocol sanctified in ServiceRegistry")

    except Exception as e:
        logger.error(f"❌ Failed to sanctify state system: {e}")
        # In Priority 0, we don't necessarily crash, but we log the void
