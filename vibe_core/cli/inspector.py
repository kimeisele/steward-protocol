"""
GAD-000 Inspector Pattern.

Implements compliance tests by inspecting the kernel from the OUTSIDE.
This preserves the "Eternal Kernel" architecture.
"""

import time
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class SystemInspector:
    """
    GAD-000 System Inspector.

    Provides machine-readable introspection of the kernel.
    """

    @staticmethod
    def get_system_capabilities(kernel: "RealVibeKernel") -> Dict[str, Any]:
        """
        GAD-000 Test 1: Discoverability.

        Returns machine-readable schema of system capabilities.
        """
        registry = getattr(kernel, "agent_registry", {})

        # Discover plugins if available
        plugins = []
        if hasattr(kernel, "_plugins"):
            plugins = [p.id for p in kernel._plugins]
        elif hasattr(kernel, "plugins"):
            plugins = [p.id for p in kernel.plugins]

        return {
            "version": "1.0",
            "kernel_type": type(kernel).__name__,
            "capabilities": [
                {"name": "submit_task", "description": "Submit a task for execution", "args": ["agent_id", "payload"]},
                {"name": "get_status", "description": "Get system status", "args": []},
            ],
            "agents": list(registry.keys()),
            "plugins": plugins,
        }

    @staticmethod
    def get_system_status(kernel: "RealVibeKernel") -> Dict[str, Any]:
        """
        GAD-000 Test 2: Observability.

        Returns machine-readable system state.
        """
        # 1. Kernel Status
        status_val = "UNKNOWN"
        if hasattr(kernel, "status"):
            status_val = kernel.status.value if hasattr(kernel.status, "value") else str(kernel.status)

        # 2. Queue Stats (Safe Inspection)
        queue_stats = {"pending": 0, "in_progress": 0}
        if hasattr(kernel, "_scheduler"):
            try:
                # Try public interface first
                if hasattr(kernel._scheduler, "get_queue_status"):
                    queue_stats = kernel._scheduler.get_queue_status()
                # Fallback to direct inspection if needed (Python is permissive)
                elif hasattr(kernel._scheduler, "_queue"):
                    queue_stats["pending"] = len(kernel._scheduler._queue)
            except Exception as e:
                # OPUS-312: Log scheduler inspection failures
                import logging

                logging.getLogger("CLI").debug(f"Scheduler inspection failed: {e}")

        # 3. Agent Stats
        agents_status = {}
        registry = getattr(kernel, "agent_registry", {})
        for agent_id, agent in registry.items():
            agent_st = "UNKNOWN"
            if hasattr(agent, "status"):
                agent_st = str(agent.status)
            agents_status[agent_id] = agent_st

        return {
            "timestamp": time.time(),
            "status": status_val,
            "queue": queue_stats,
            "agents": agents_status,
            "monitor": "SystemInspector",
        }
