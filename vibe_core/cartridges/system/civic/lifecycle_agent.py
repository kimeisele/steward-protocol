"""
LIFECYCLE AGENT - Agent Lifecycle & Permission Management Component

Handles:
- Vedic Varna system (Brahmachari → Grihastha → Vanaprastha → Sannyasa)
- Agent lifecycle transitions
- Permission enforcement based on lifecycle status
- Agent violations and demotion

Architecture:
- Naked Agent: no tool instances owned
- Accesses lifecycle_enforcer tool via self.system.execute_tool("civic.lifecycle_enforcer", ...)
- Kernel-managed tool pattern
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xb1f668fa"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict

from vibe_core import Task, VibeAgent

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

        # NO TOOL INSTANCES OWNED - Agent is NAKED
        # Tools accessed via self.system.execute_tool()
        self.system = None  # Will be injected by parent via set_system()

        logger.info("🔄 LIFECYCLE AGENT initialized (Naked Agent - awaiting system injection)")

    def set_system(self, system):
        """
        Inject system interface from parent CIVIC cartridge.

        This allows the LifecycleAgent to access kernel tools
        via self.system.execute_tool().

        Args:
            system: The system interface (from parent agent's self.system)
        """
        self.system = system
        logger.info("✅ CIVIC Lifecycle: system interface injected")

    def process(self, task: Task) -> Dict[str, Any]:
        """Process lifecycle-related tasks."""
        action = task.payload.get("action")

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

        # Execute via kernel
        tool_result = self.system.execute_tool(
            "civic.lifecycle_enforcer",
            {
                "action": "check_action_permission",
                "agent_id": agent_id,
                "action_type": action_type,
                "cost": cost,
            },
        )

        if not tool_result.success:
            logger.error(f"❌ Permission check failed: {tool_result.error}")
            return {
                "status": "error",
                "error": tool_result.error,
                "agent": agent_id,
            }

        result = tool_result.output

        return {
            "status": "success",
            "permitted": result.get("permitted", False),
            "reason": result.get("reason"),
            "agent": agent_id,
            "lifecycle_status": result.get("lifecycle_status"),
            "action_type": action_type,
        }

    def authorize_brahmachari_to_grihastha(
        self, agent_id: str, test_results: Dict[str, Any], initiator: str = "TEMPLE"
    ) -> Dict[str, Any]:
        """Promote an agent from Brahmachari (Student) to Grihastha (Householder)."""
        logger.info(f"🎓 Promoting {agent_id} from BRAHMACHARI to GRIHASTHA")
        logger.info(f"   Initiator: {initiator}")
        logger.info(f"   Test Results: {test_results}")

        # Execute via kernel
        tool_result = self.system.execute_tool(
            "civic.lifecycle_enforcer",
            {
                "action": "authorize_brahmachari_to_grihastha",
                "agent_id": agent_id,
                "test_results": test_results,
                "initiator": initiator,
            },
        )

        if not tool_result.success:
            logger.error(f"❌ Promotion failed: {tool_result.error}")
            return {
                "status": "error",
                "error": tool_result.error,
                "agent": agent_id,
                "promoted": False,
            }

        result = tool_result.output

        return {
            "status": "success" if result.get("promoted") else "error",
            "agent": agent_id,
            "promoted": result.get("promoted", False),
            "initiator": initiator,
            "new_status": result.get("new_status", "brahmachari"),
        }

    def report_violation(self, agent_id: str, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Report a violation and potentially demote an agent."""
        logger.warning(f"⚠️  Violation reported for {agent_id}")
        logger.warning(f"   Details: {violation}")

        # Execute via kernel
        tool_result = self.system.execute_tool(
            "civic.lifecycle_enforcer",
            {
                "action": "report_violation",
                "agent_id": agent_id,
                "violation": violation,
            },
        )

        if not tool_result.success:
            logger.error(f"❌ Violation report failed: {tool_result.error}")
            return {
                "status": "error",
                "error": tool_result.error,
                "agent": agent_id,
                "demoted": False,
            }

        result = tool_result.output

        return {
            "status": "success" if result.get("demoted") else "error",
            "agent": agent_id,
            "demoted": result.get("demoted", False),
            "violation": violation,
        }

    def get_lifecycle_status(self) -> Dict[str, Any]:
        """Get global lifecycle enforcement status."""
        logger.info("📊 Querying lifecycle enforcement status")

        # Execute via kernel
        tool_result = self.system.execute_tool(
            "civic.lifecycle_enforcer",
            {
                "action": "get_enforcement_status",
            },
        )

        if not tool_result.success:
            logger.error(f"❌ Failed to get lifecycle status: {tool_result.error}")
            return {
                "status": "error",
                "error": tool_result.error,
            }

        result = tool_result.output

        return {"status": "success", "enforcement_stats": result.get("enforcement_stats", {})}

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get lifecycle status for a specific agent."""
        logger.info(f"📋 Querying lifecycle status for {agent_id}")

        # Execute via kernel
        tool_result = self.system.execute_tool(
            "civic.lifecycle_enforcer",
            {
                "action": "get_agent_status",
                "agent_id": agent_id,
            },
        )

        if not tool_result.success:
            logger.error(f"❌ Failed to get agent status: {tool_result.error}")
            return {
                "status": "error",
                "agent": agent_id,
                "error": tool_result.error,
            }

        result = tool_result.output

        return {
            "status": "success" if result.get("success") else "error",
            "agent": agent_id,
            "lifecycle": result.get("lifecycle"),
            "error": result.get("error"),
        }

    def report_status(self) -> Dict[str, Any]:
        """Report lifecycle agent status."""
        try:
            # Execute via kernel
            tool_result = self.system.execute_tool(
                "civic.lifecycle_enforcer",
                {
                    "action": "get_enforcement_status",
                },
            )

            if tool_result.success:
                stats = tool_result.output.get("enforcement_stats", {})
                return {
                    "agent_id": "civic_lifecycle",
                    "name": "CIVIC Lifecycle",
                    "status": "RUNNING",
                    "enforcement_stats": stats,
                }
        except Exception as e:
            logger.warning(f"⚠️  Could not get enforcement status: {e}")

        return {
            "agent_id": "civic_lifecycle",
            "name": "CIVIC Lifecycle",
            "status": "RUNNING",
            "enforcement_stats": {},
        }


__all__ = ["LifecycleAgent"]
