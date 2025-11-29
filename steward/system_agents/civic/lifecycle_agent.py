"""
LIFECYCLE AGENT - Agent Lifecycle & Permission Management Component

Handles:
- Vedic Varna system (Brahmachari → Grihastha → Vanaprastha → Sannyasa)
- Agent lifecycle transitions
- Permission enforcement based on lifecycle status
- Agent violations and demotion
"""

import logging
from typing import Any, Dict, Optional

from vibe_core import Task, VibeAgent

try:
    from .tools.lifecycle_enforcer import LifecycleEnforcer
    from .tools.lifecycle_manager import LifecycleStatus

    LIFECYCLE_AVAILABLE = True
except ImportError as e:
    logger_setup = logging.getLogger("LIFECYCLE_AGENT")
    logger_setup.warning(f"⚠️  Lifecycle Enforcer not available: {e}")
    LIFECYCLE_AVAILABLE = False

logger = logging.getLogger("LIFECYCLE_AGENT")


class LifecycleAgent(VibeAgent):
    """Manages agent lifecycle through Vedic Varna system."""

    def __init__(self):
        super().__init__(
            agent_id="civic_lifecycle",
            name="CIVIC Lifecycle",
            version="2.0.0",
            author="Steward Protocol",
            description="Agent lifecycle management: Vedic Varna system",
            domain="GOVERNANCE",
            capabilities=["lifecycle_management", "permission_enforcement"],
        )

        if LIFECYCLE_AVAILABLE:
            self.lifecycle_enforcer = LifecycleEnforcer()
            logger.info("🔄 LIFECYCLE ENFORCER initialized (Vedic Varna System)")
            logger.info("   Status: ACTIVE - Managing Brahmachari → Grihastha progression")
        else:
            self.lifecycle_enforcer = None
            logger.warning("⚠️  Lifecycle Enforcer NOT available - system running in degraded mode")

    def process(self, task: Task) -> Dict[str, Any]:
        """Process lifecycle-related tasks."""
        action = task.payload.get("action")

        if not self.lifecycle_enforcer:
            return {"status": "error", "error": "Lifecycle enforcer not available"}

        if action == "check_action_permission":
            return self.check_action_permission(
                agent_id=task.payload.get("agent_id"),
                action_type=task.payload.get("action_type", "write"),
                cost=task.payload.get("cost", 1),
            )
        elif action == "authorize_brahmachari_to_grihastha":
            return self.authorize_brahmachari_to_grihastha(
                agent_id=task.payload.get("agent_id"),
                test_results=task.payload.get("test_results", {}),
                initiator=task.payload.get("initiator", "TEMPLE"),
            )
        elif action == "report_violation":
            return self.report_violation(
                agent_id=task.payload.get("agent_id"),
                violation=task.payload.get("violation", {}),
            )
        elif action == "get_lifecycle_status":
            return self.get_lifecycle_status()
        elif action == "get_agent_status":
            return self.get_agent_status(task.payload.get("agent_id"))
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}

    def check_action_permission(self, agent_id: str, action_type: str = "write", cost: int = 1) -> Dict[str, Any]:
        """Check if an agent has permission to perform an action based on lifecycle status."""
        logger.info(f"🔐 Checking permission: {agent_id} for {action_type} action (cost: {cost})")

        result = self.lifecycle_enforcer.check_action_permission(agent_id, action_type, cost)

        return {
            "status": "success",
            "permitted": result.permitted,
            "reason": result.reason,
            "agent": agent_id,
            "lifecycle_status": result.lifecycle_status,
            "action_type": action_type,
        }

    def authorize_brahmachari_to_grihastha(
        self, agent_id: str, test_results: Dict[str, Any], initiator: str = "TEMPLE"
    ) -> Dict[str, Any]:
        """Promote an agent from Brahmachari (Student) to Grihastha (Householder)."""
        logger.info(f"🎓 Promoting {agent_id} from BRAHMACHARI to GRIHASTHA")
        logger.info(f"   Initiator: {initiator}")
        logger.info(f"   Test Results: {test_results}")

        success = self.lifecycle_enforcer.authorize_brahmachari_to_grihastha(agent_id, test_results, initiator)

        return {
            "status": "success" if success else "error",
            "agent": agent_id,
            "promoted": success,
            "initiator": initiator,
            "new_status": "grihastha" if success else "brahmachari",
        }

    def report_violation(self, agent_id: str, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Report a violation and potentially demote an agent."""
        logger.warning(f"⚠️  Violation reported for {agent_id}")
        logger.warning(f"   Details: {violation}")

        success = self.lifecycle_enforcer.report_violation(agent_id, violation)

        return {
            "status": "success" if success else "error",
            "agent": agent_id,
            "demoted": success,
            "violation": violation,
        }

    def get_lifecycle_status(self) -> Dict[str, Any]:
        """Get global lifecycle enforcement status."""
        logger.info("📊 Querying lifecycle enforcement status")

        stats = self.lifecycle_enforcer.get_enforcement_status()

        return {"status": "success", "enforcement_stats": stats}

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get lifecycle status for a specific agent."""
        logger.info(f"📋 Querying lifecycle status for {agent_id}")

        try:
            lifecycle_mgr = self.lifecycle_enforcer.lifecycle_mgr
            agent_status = lifecycle_mgr.get_agent_status(agent_id)

            return {"status": "success", "agent": agent_id, "lifecycle": agent_status}

        except Exception as e:
            logger.error(f"❌ Error querying agent status: {e}")
            return {"status": "error", "agent": agent_id, "error": str(e)}

    def report_status(self) -> Dict[str, Any]:
        """Report lifecycle agent status."""
        if not self.lifecycle_enforcer:
            return {
                "agent_id": "civic_lifecycle",
                "name": "CIVIC Lifecycle",
                "status": "DEGRADED",
                "note": "Lifecycle enforcer not available",
            }

        stats = self.lifecycle_enforcer.get_enforcement_status()

        return {
            "agent_id": "civic_lifecycle",
            "name": "CIVIC Lifecycle",
            "status": "RUNNING",
            "enforcement_stats": stats,
        }


__all__ = ["LifecycleAgent"]
