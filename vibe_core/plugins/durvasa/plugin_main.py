"""
Durvasa Plugin - Prana Triage Engine

OPUS-209: Extracted from kernel_impl.py

Sacrifices lower-dharma agents to preserve the system core during resource famine.
Named after the sage Durvasa, known for his fierce temper and curses.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("DURVASA")

CRITICAL_THRESHOLD = 0.90  # Start triage at 90% pressure
SAFE_LEVEL = 0.80          # Stop when we reach 80%


class DurvasaPlugin(KernelPlugin):
    """
    Prana Triage Engine.

    When system resources are critically low, sacrifices lower-priority
    agents to preserve the kernel and critical infrastructure.
    """

    plugin_id = "durvasa"

    def __init__(self):
        self._kernel: Optional["RealVibeKernel"] = None

    def on_boot(self, kernel: "RealVibeKernel", config: Optional[Dict[str, Any]] = None) -> HookResult:
        """Store kernel reference for later use."""
        self._kernel = kernel
        logger.info("🔱 Durvasa Protocol armed")
        return HookResult.ok()

    def enforce_prana_limits(self, pressure: float = None) -> int:
        """
        DURVASA PROTOCOL: The Prana Triage Engine.

        Sacrifices lower-dharma agents to preserve the system core.

        Args:
            pressure: Optional override for system pressure (0.0-1.0).

        Returns:
            Number of agents sacrificed
        """
        if not self._kernel:
            return 0

        kernel = self._kernel

        # 1. Measure system pressure
        if pressure is None:
            total_agents = len(kernel._agent_registry)
            running_processes = len(kernel.process_manager.processes) if kernel.process_manager else 0
            pressure = min(running_processes / max(total_agents, 1), 1.0)

        if pressure < CRITICAL_THRESHOLD:
            return 0

        logger.critical(f"🚨 DURVASA ALERT: System pressure at {pressure:.0%}. Initiating triage...")

        kernel._ledger.record_event("PRANA_EMERGENCY", "kernel", {
            "pressure": pressure,
            "msg": "Durvasa Alert triggered",
            "timestamp": datetime.utcnow().isoformat()
        })

        # 2. Identify candidates
        candidates = []
        for agent_id, agent in list(kernel._agent_registry.items()):
            if hasattr(agent, "__dict__"):
                meta = agent.__dict__
            elif isinstance(agent, dict):
                meta = agent
            else:
                meta = {}

            candidates.append({
                "id": agent_id,
                "dharma": str(meta.get("dharma", "tamas")).lower(),
                "priority": str(meta.get("priority", "low")).lower()
            })

        # 3. Sort by sacrifice priority
        dharma_rank = {"tamas": 0, "rajas": 1, "sattva": 2}
        priority_rank = {"disposable": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

        candidates.sort(key=lambda x: (
            dharma_rank.get(x["dharma"], 0),
            priority_rank.get(x["priority"], 0)
        ))

        # 4. The Sacrifice
        sacrifices = 0

        for victim in candidates:
            if priority_rank.get(victim["priority"], 0) >= 3:
                kernel._ledger.record_event("TRIAGE_LIMIT", "kernel", {
                    "msg": "Only High/Critical agents remain. Holding.",
                    "remaining": [c["id"] for c in candidates if priority_rank.get(c["priority"], 0) >= 3]
                })
                break

            if dharma_rank.get(victim["dharma"], 0) >= 2:
                kernel._ledger.record_event("TRIAGE_LIMIT", "kernel", {
                    "msg": "Only Sattva agents remain. Holding."
                })
                break

            success = kernel.terminate_agent(victim["id"], reason="PRANA_FAMINE_SACRIFICE")

            if success:
                sacrifices += 1
                kernel._ledger.record_event("AGENT_SACRIFICED", "kernel", {
                    "agent": victim["id"],
                    "dharma": victim["dharma"],
                    "priority": victim["priority"],
                    "reason": "Sacrificed to appease Durvasa"
                })
                pressure -= 0.10
                if pressure <= SAFE_LEVEL:
                    break

        if sacrifices > 0:
            logger.warning(f"🔱 DURVASA APPEASED: {sacrifices} agent(s) sacrificed. System stabilized.")

        return sacrifices

    def get_api(self):
        """Return triage function for direct access."""
        return {"enforce_prana_limits": self.enforce_prana_limits}
