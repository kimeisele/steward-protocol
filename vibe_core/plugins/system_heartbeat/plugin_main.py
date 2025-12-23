"""
System Heartbeat Plugin - The Pulse of the State.

OPUS-212: Survivor of VISNU.

This plugin nationalizes the pulse logic previously held in legacy scripts.
It provides a unified breathing cycle for snapshots, state sync, and cognition.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from vibe_core.di import ServiceRegistry
from vibe_core.event_bus import Event, EventType
from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.protocols import (
    CognitiveKernelProtocol,
    StateSyncWeaverProtocol,
    SystemHeartbeatProtocol,
    VibeKernel,
)

logger = logging.getLogger("SYSTEM_HEARTBEAT")


class SystemHeartbeatPlugin(KernelPlugin, SystemHeartbeatProtocol):
    """
    Orchestrates the unified system pulse.
    Registered as a plugin to avoid Ring 0 modification.
    """

    @property
    def plugin_id(self) -> str:
        return "system_heartbeat"

    def on_boot(self, kernel: VibeKernel, config: Optional[Dict[str, Any]] = None) -> HookResult:
        """Initialize the heartbeat service on kernel boot."""
        self._kernel = kernel

        # Register in ServiceRegistry for global discovery
        ServiceRegistry.register(SystemHeartbeatProtocol, self)

        logger.info("💓 SYSTEM_HEARTBEAT: Nationalized pulse service online")
        return HookResult.ok()

    def pulse(self) -> Dict[str, Any]:
        """
        Execute a unified system pulse via the Kernel.
        """
        if not self._kernel:
            logger.error("❌ Pulse failed: Kernel not injected")
            return {"success": False, "error": "No kernel"}

        # Delegate orchestration to the kernel
        return self._kernel.pulse()

    def on_pulse(self, kernel: VibeKernel, transaction: Any) -> Dict[str, Any]:
        """
        Implementation of the pulse for THIS plugin.
        (Previously part of the monolithic pulse() method)
        """
        start_time = datetime.utcnow()
        results = {
            "success": True,
            "snapshot": False,
            "state_sync": False,
        }

        # 1. PROJECTION (Snapshot)
        try:
            snapshot = self._generate_snapshot()
            if hasattr(kernel, "io"):
                kernel.io.write_snapshot("vibe_snapshot.json", snapshot, writer_id="HEARTBEAT")
                results["snapshot"] = True
                logger.info("   + Snapshot projected: vibe_snapshot.json")
        except Exception as e:
            logger.error(f"   ❌ Snapshot failed: {e}")
            results["success"] = False

        # 2. SYNCHRONIZATION (Weaver)
        try:
            weaver = ServiceRegistry.get(StateSyncWeaverProtocol)
            if weaver:
                logger.info("   + StateSyncWeaver: Sealing runtime state...")
                res = weaver.pulse()
                results["state_sync"] = res.success
                if res.success:
                    logger.info(f"   ✅ State synchronized: {res.git_sha}")
                else:
                    logger.warning(f"   ⚠️ State sync partial: {res.error}")
            else:
                logger.warning("   ⚠️ StateSyncWeaver not available in DI")
        except Exception as e:
            logger.error(f"   ❌ Sync failed: {e}")
            results["success"] = False

        return results

    def _generate_snapshot(self) -> Dict[str, Any]:
        """Generate a raw kernel status snapshot."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_status": str(self._kernel.status.value),
            "agents": list(self._kernel.agent_registry.keys()),
            "scheduler": self._kernel.scheduler.get_queue_status(),
            "ledger": {
                "events": self._kernel.ledger.count_events() if hasattr(self._kernel.ledger, "count_events") else 0
            },
        }


# Entry point for Loader
def get_plugin():
    return SystemHeartbeatPlugin()
