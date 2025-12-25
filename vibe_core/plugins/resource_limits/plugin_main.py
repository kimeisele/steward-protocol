"""
Resource Limits Plugin - Resource Quota Management as a Service

OPUS-209 Phase 2.3: Extracted from kernel_impl.py
OPUS-210: PluginStateContract compliant

This is a CRITICAL PLUGIN - the kernel needs resource control to prevent
runaway agents from consuming all system resources.

Philosophy:
    "Credits are not numbers in a database. Credits are CPU cycles and memory bytes.
    The economy is the operating system."
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from vibe_core.di import ServiceRegistry
from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.protocols.resource import ResourceSupervisorProtocol
from vibe_core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RESOURCE_LIMITS")


class ResourceLimitsPlugin(KernelPlugin):
    """
    CRITICAL PLUGIN - Kernel needs resource control.

    Manages agent resource quotas:
    - Set quotas based on credit balance
    - Enforce CPU/RAM limits via psutil
    - Monitor usage and detect violations

    The kernel no longer instantiates ResourceManager directly.
    Instead, it accesses the manager via:
        manager = ServiceRegistry.get(ResourceSupervisorProtocol)

    Or via backward-compatible:
        kernel.resource_manager

    OPUS-210: Implements PluginStateContract for Prakriti integration.
    """

    plugin_id = "resource_limits"

    # State paths for PluginStateContract
    STATE_DIR = Path(".vibe/state/plugins/resource_limits")

    def __init__(self):
        self._manager: Optional[ResourceManager] = None
        self._quota_updates: int = 0
        self._violations_detected: int = 0

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
            "quota_updates": self._quota_updates,
            "violations_detected": self._violations_detected,
            "manager_active": self._manager is not None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from snapshot (crash recovery)."""
        if snapshot.get("version") == 1:
            self._quota_updates = snapshot.get("quota_updates", 0)
            self._violations_detected = snapshot.get("violations_detected", 0)

    @property
    def dependencies(self) -> Set[str]:
        """No dependencies - core infrastructure."""
        return set()

    @property
    def priority(self) -> int:
        """High priority - must boot early."""
        return 15

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        Boot the resource manager.

        Creates the ResourceManager instance and registers it
        in the ServiceRegistry for kernel access.
        """
        try:
            # Create the resource manager
            self._manager = ResourceManager()

            # Register in ServiceRegistry for DI
            ServiceRegistry.register(ResourceSupervisorProtocol, self._manager)

            # Also set on kernel for backward compatibility
            kernel.resource_manager = self._manager

            logger.info("📊 Resource Limits Plugin booted - ResourceManager registered")
            return HookResult.ok()

        except Exception as e:
            logger.critical(f"❌ CRITICAL: Resource Limits Plugin failed to boot: {e}")
            return HookResult.fatal(str(e))

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """
        Set initial resource quota for newly registered agent.

        OPUS-209: This logic was extracted from kernel register_agent().
        The kernel only registers; the plugin handles quota management.
        """
        if not self._manager:
            return

        # Set initial resource quota (default: 100 credits)
        self._manager.set_quota(agent_id, credits=100)

        # Enforce quota if process is running
        if kernel.process_manager:
            proc_info = kernel.process_manager.processes.get(agent_id)
            if proc_info and proc_info.process.is_alive():
                self._manager.enforce_quota(agent_id, proc_info.process)
                logger.debug(f"📊 Quota enforced for {agent_id}")

    def get_api(self) -> Optional[ResourceManager]:
        """Return the resource manager for direct access if needed."""
        return self._manager

    # =========================================================================
    # OPUS-307 Phase II: CLI Command Handlers
    # "steward resources" namespace - visibility into resource usage
    # =========================================================================

    def cmd_resources_usage(self, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward resources:usage

        Show resource usage per agent - like `top` for the agent OS.

        Args:
            json: If True, return raw JSON-compatible data

        Returns:
            Dict with usage data
        """
        if not self._manager:
            return {"success": False, "error": "ResourceManager not initialized"}

        # We need process_manager from kernel - try to get from ServiceRegistry
        process_manager = None
        try:
            from vibe_core.protocols.process import ProcessSupervisorProtocol

            process_manager = ServiceRegistry.get(ProcessSupervisorProtocol)
        except Exception:
            pass

        if not process_manager:
            return {
                "success": True,
                "message": "No active processes",
                "usage": {},
                "formatted": "📊 No active agent processes to monitor",
            }

        usage_data = self._manager.get_all_usage(process_manager)

        result = {
            "success": True,
            "count": len(usage_data),
            "usage": usage_data,
        }

        if not json:
            lines = ["📊 RESOURCE USAGE (per agent)"]
            lines.append("=" * 60)
            lines.append(f"{'Agent':<20} {'CPU%':>8} {'RAM MB':>10} {'Status':>10}")
            lines.append("-" * 60)
            for agent_id, data in usage_data.items():
                cpu = data.get("cpu_percent", 0)
                ram = data.get("ram_mb", 0)
                status = "🟢" if cpu < 50 else "🟡" if cpu < 80 else "🔴"
                lines.append(f"{agent_id:<20} {cpu:>7.1f}% {ram:>9.1f} {status:>10}")
            lines.append("=" * 60)
            result["formatted"] = "\n".join(lines)

        return result

    def cmd_resources_quotas(self) -> Dict[str, Any]:
        """
        CLI Handler: steward resources:quotas

        Show resource quotas for all agents.

        Returns:
            Dict with quota data
        """
        if not self._manager:
            return {"success": False, "error": "ResourceManager not initialized"}

        # Access internal quota storage
        quotas = getattr(self._manager, "_quotas", {})

        result = {
            "success": True,
            "count": len(quotas),
            "quotas": dict(quotas),
        }

        lines = ["📊 RESOURCE QUOTAS"]
        lines.append("=" * 60)
        lines.append(f"{'Agent':<20} {'Credits':>10} {'CPU Limit':>12} {'RAM MB':>10}")
        lines.append("-" * 60)
        for agent_id, credits in quotas.items():
            # Credits map: 100 credits = 10% CPU + 100MB RAM
            cpu_limit = credits / 10
            ram_limit = credits
            lines.append(f"{agent_id:<20} {credits:>10} {cpu_limit:>11.0f}% {ram_limit:>10}")
        lines.append("=" * 60)
        result["formatted"] = "\n".join(lines)

        return result

    def cmd_resources_violations(self) -> Dict[str, Any]:
        """
        CLI Handler: steward resources:violations

        Check for quota violations.

        Returns:
            Dict with violation data
        """
        if not self._manager:
            return {"success": False, "error": "ResourceManager not initialized"}

        # Try to get process_manager
        process_manager = None
        try:
            from vibe_core.protocols.process import ProcessSupervisorProtocol

            process_manager = ServiceRegistry.get(ProcessSupervisorProtocol)
        except Exception:
            pass

        if not process_manager:
            return {
                "success": True,
                "message": "No active processes to check",
                "violations": [],
                "formatted": "✅ No active processes - no violations possible",
            }

        violations = self._manager.check_violations(process_manager)

        result = {
            "success": True,
            "count": len(violations),
            "violations": violations,
        }

        if violations:
            lines = ["⚠️ QUOTA VIOLATIONS DETECTED"]
            lines.append("=" * 60)
            for v in violations:
                lines.append(f"  🔴 {v}")
            lines.append("=" * 60)
        else:
            lines = ["✅ NO QUOTA VIOLATIONS"]
            lines.append("All agents within resource limits")

        result["formatted"] = "\n".join(lines)
        return result
