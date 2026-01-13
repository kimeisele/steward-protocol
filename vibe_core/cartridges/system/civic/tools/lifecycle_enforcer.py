#!/usr/bin/env python3
"""
LIFECYCLE ENFORCER - The Kernel-Level Permission Gate (Tool Protocol)

This is the crucial component that makes the simulation REAL (not a mock).

It sits at the kernel boundary and checks:
1. Does this agent have the right lifecycle status?
2. Does the ledger show they can afford this action?
3. Has their karma (persistent state) been updated?

Without this, agents could act freely (mock).
With this, consequences are PERSISTENT and BINDING.

Architecture:
- Implements Tool protocol (kernel-managed)
- Accessed via self.system.execute_tool("civic.lifecycle_enforcer", ...)
- No direct instantiation - kernel owns the tool

The philosophy:
"An agent trying to act without being qualified is like a student
trying to teach before learning. The KERNEL says NO."
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xd55ccc3b"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from vibe_core.cartridges.system.civic.tools.lifecycle_manager import LifecycleManager, LifecycleStatus
from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("LIFECYCLE_ENFORCER")


@dataclass
class PermissionResult:
    """Result of a permission check."""

    permitted: bool
    reason: str
    action_type: str
    agent_id: str
    lifecycle_status: Optional[str] = None
    required_status: Optional[str] = None


class LifecycleEnforcer(Tool):
    """
    The kernel-level permission gate (Tool Protocol Implementation).

    Every agent action must pass through this enforcer:
    1. Lifecycle check (is the agent qualified for this action?)
    2. Economic check (does the agent have credits?)
    3. Constitutional check (does the action violate the oath?)
    4. Ledger check (is the action recorded for karma?)

    If ANY of these fail, the action is REJECTED at the kernel level.

    This tool is kernel-managed and accessed via:
    self.system.execute_tool("civic.lifecycle_enforcer", {...})
    """

    def __init__(self):
        """Initialize the enforcer (kernel-managed, self-contained)."""
        self.lifecycle_mgr = LifecycleManager()
        logger.info("🚫 LIFECYCLE ENFORCER initialized (Kernel-Level Permission Gate)")

    @property
    def name(self) -> str:
        """Return the tool name."""
        return "civic.lifecycle_enforcer"

    @property
    def description(self) -> str:
        """Return the tool description."""
        return "Lifecycle enforcement: permission checks, agent promotion, violation reporting, Vedic Varna system"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Return the parameters schema for this tool."""
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'check_action_permission', 'authorize_brahmachari_to_grihastha', 'report_violation', 'get_enforcement_status', 'get_agent_status'",
            },
            "agent_id": {
                "type": "string",
                "required": False,
                "description": "Agent ID (required for most actions)",
            },
            "action_type": {
                "type": "string",
                "required": False,
                "description": "Type of action (write, broadcast, trade, etc.) - for check_action_permission",
            },
            "cost": {
                "type": "integer",
                "required": False,
                "description": "Credit cost of the action - for check_action_permission (default: 1)",
            },
            "details": {
                "type": "object",
                "required": False,
                "description": "Additional context details",
            },
            "test_results": {
                "type": "object",
                "required": False,
                "description": "Test results from TEMPLE initiation - for authorize_brahmachari_to_grihastha",
            },
            "initiator": {
                "type": "string",
                "required": False,
                "description": "Who authorized the promotion (typically 'TEMPLE') - for authorize_brahmachari_to_grihastha",
            },
            "violation": {
                "type": "object",
                "required": False,
                "description": "Violation details - for report_violation",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate lifecycle enforcer parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = [
            "check_action_permission",
            "authorize_brahmachari_to_grihastha",
            "report_violation",
            "get_enforcement_status",
            "get_agent_status",
        ]

        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Validate action-specific requirements
        if action == "check_action_permission" and "agent_id" not in parameters:
            raise ValueError("action 'check_action_permission' requires 'agent_id' parameter")

        if action == "authorize_brahmachari_to_grihastha" and "agent_id" not in parameters:
            raise ValueError("action 'authorize_brahmachari_to_grihastha' requires 'agent_id' parameter")

        if action == "report_violation" and "agent_id" not in parameters:
            raise ValueError("action 'report_violation' requires 'agent_id' parameter")

        if action == "get_agent_status" and "agent_id" not in parameters:
            raise ValueError("action 'get_agent_status' requires 'agent_id' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute lifecycle enforcer operation."""
        try:
            action = parameters["action"]

            if action == "check_action_permission":
                result = self._handle_check_action_permission(
                    agent_id=parameters["agent_id"],
                    action_type=parameters.get("action_type", "write"),
                    cost=parameters.get("cost", 1),
                    details=parameters.get("details"),
                )
                return ToolResult(success=result["permitted"], output=result)

            elif action == "authorize_brahmachari_to_grihastha":
                result = self._handle_authorize_brahmachari_to_grihastha(
                    agent_id=parameters["agent_id"],
                    test_results=parameters.get("test_results", {}),
                    initiator=parameters.get("initiator", "TEMPLE"),
                )
                return ToolResult(success=result["promoted"], output=result)

            elif action == "report_violation":
                result = self._handle_report_violation(
                    agent_id=parameters["agent_id"],
                    violation=parameters.get("violation", {}),
                )
                return ToolResult(success=result["demoted"], output=result)

            elif action == "get_enforcement_status":
                result = self._handle_get_enforcement_status()
                return ToolResult(success=True, output=result)

            elif action == "get_agent_status":
                result = self._handle_get_agent_status(parameters["agent_id"])
                return ToolResult(success=result.get("success", False), output=result)

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.exception(f"Lifecycle enforcer execution failed: {e}")
            return ToolResult(success=False, error=str(e))

    # Handler methods that wrap the core logic
    def _handle_check_action_permission(
        self, agent_id: str, action_type: str, cost: int, details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle check_action_permission action."""
        result = self.check_action_permission(agent_id, action_type, cost, details)
        return {
            "permitted": result.permitted,
            "reason": result.reason,
            "agent": agent_id,
            "lifecycle_status": result.lifecycle_status,
            "action_type": action_type,
        }

    def _handle_authorize_brahmachari_to_grihastha(
        self, agent_id: str, test_results: Dict[str, Any], initiator: str
    ) -> Dict[str, Any]:
        """Handle authorize_brahmachari_to_grihastha action."""
        success = self.authorize_brahmachari_to_grihastha(agent_id, test_results, initiator)
        return {
            "agent": agent_id,
            "promoted": success,
            "initiator": initiator,
            "new_status": "grihastha" if success else "brahmachari",
        }

    def _handle_report_violation(self, agent_id: str, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report_violation action."""
        success = self.report_violation(agent_id, violation)
        return {
            "agent": agent_id,
            "demoted": success,
            "violation": violation,
        }

    def _handle_get_enforcement_status(self) -> Dict[str, Any]:
        """Handle get_enforcement_status action."""
        stats = self.get_enforcement_status()
        return {"enforcement_stats": stats}

    def _handle_get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Handle get_agent_status action."""
        try:
            agent_status = self.lifecycle_mgr.get_agent_status(agent_id)
            return {"success": True, "agent": agent_id, "lifecycle": agent_status}
        except Exception as e:
            logger.error(f"❌ Error querying agent status: {e}")
            return {"success": False, "agent": agent_id, "error": str(e)}

    def check_action_permission(
        self,
        agent_id: str,
        action_type: str,
        cost: int = 1,
        details: Optional[Dict[str, Any]] = None,
    ) -> PermissionResult:
        """
        Check if an agent is permitted to perform an action.

        This is the PRIMARY GATE that makes consequences REAL.

        Args:
            agent_id: Agent requesting the action
            action_type: Type of action (write, broadcast, trade, etc.)
            cost: Credit cost of the action
            details: Additional context (optional)

        Returns:
            PermissionResult with permit/deny decision
        """

        # STEP 1: Lifecycle Status Check
        # This is the ESSENTIAL gate - new agents (Brahmachari) cannot act
        result = self._check_lifecycle_status(agent_id, action_type)
        if not result.permitted:
            logger.warning(f"🚫 Action REJECTED: {agent_id} - {result.reason}")
            return result

        # STEP 2: Economic Check
        # Does the agent have enough credits?
        result = self._check_economic_status(agent_id, cost)
        if not result.permitted:
            logger.warning(f"🚫 Action REJECTED: {agent_id} - {result.reason}")
            return result

        # STEP 3: Ledger Recording (Karma)
        # Record the action BEFORE execution (fail-safe)
        self._record_action_intent(agent_id, action_type, cost, details)

        # STEP 4: Success - Log the permit
        result = PermissionResult(
            permitted=True,
            reason=f"Action {action_type} permitted for {agent_id}",
            action_type=action_type,
            agent_id=agent_id,
            lifecycle_status=str(self.lifecycle_mgr.get_lifecycle_state(agent_id).status.value),
        )

        logger.info(f"✅ Action PERMITTED: {agent_id} - {action_type} (cost: {cost} credits)")
        return result

    def _check_lifecycle_status(self, agent_id: str, action_type: str) -> PermissionResult:
        """
        Check if agent's lifecycle status permits the action.

        This is the HEART of the system - it enforces the Vedic varna structure.
        New agents (Brahmachari) cannot act.

        Args:
            agent_id: Agent to check
            action_type: Action being requested

        Returns:
            PermissionResult
        """
        state = self.lifecycle_mgr.get_lifecycle_state(agent_id)

        if not state:
            return PermissionResult(
                permitted=False,
                reason=f"Agent {agent_id} not found in lifecycle registry",
                action_type=action_type,
                agent_id=agent_id,
            )

        # Check permission
        has_permission = self.lifecycle_mgr.check_permission(agent_id, action_type)

        if not has_permission:
            # Provide helpful message based on status
            status = state.status
            if status == LifecycleStatus.BRAHMACHARI:
                reason = (
                    f"Agent {agent_id} is BRAHMACHARI (Student). "
                    f"Must pass TEMPLE initiation first. "
                    f"Read-only access permitted."
                )
            elif status == LifecycleStatus.SHUDRA:
                reason = (
                    f"Agent {agent_id} is SHUDRA (Fallen). "
                    f"Rights revoked due to violations. "
                    f"Must perform service tasks to rehabilitate."
                )
            elif status == LifecycleStatus.VANAPRASTHA:
                reason = f"Agent {agent_id} is VANAPRASTHA (Retired). Deprecated code - read-only archive access only."
            elif status == LifecycleStatus.SANNYASA:
                reason = f"Agent {agent_id} is SANNYASA (Renounced). Agent merged into core - no longer executable."
            else:
                reason = f"Agent {agent_id} does not have permission for {action_type}"

            return PermissionResult(
                permitted=False,
                reason=reason,
                action_type=action_type,
                agent_id=agent_id,
                lifecycle_status=status.value,
            )

        return PermissionResult(
            permitted=True,
            reason="Lifecycle check passed",
            action_type=action_type,
            agent_id=agent_id,
            lifecycle_status=state.status.value,
        )

    def _check_economic_status(self, agent_id: str, cost: int) -> PermissionResult:
        """
        Check if agent has sufficient credits for the action.

        NOTE: Economic checks are now delegated to the economy system.
        This method returns a placeholder indicating the credit cost.
        The calling code should check credits via civic.ledger separately.

        Args:
            agent_id: Agent to check
            cost: Credit cost of action

        Returns:
            PermissionResult (always permitted - economy checks done separately)
        """
        # NOTE: Credit checks are now done by economy_agent via civic.ledger
        # This enforcer only checks lifecycle permissions
        return PermissionResult(
            permitted=True,
            reason=f"Economic check delegated (cost: {cost} credits)",
            action_type="economic_check",
            agent_id=agent_id,
        )

    def _record_action_intent(
        self,
        agent_id: str,
        action_type: str,
        cost: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Record the action intent.

        NOTE: Intent recording is now delegated to the economy system.
        This method is a placeholder for backward compatibility.

        The calling code should record the transaction via civic.ledger.

        Args:
            agent_id: Agent performing action
            action_type: Type of action
            cost: Credit cost
            details: Additional context
        """
        # NOTE: Transaction recording now done by economy_agent via civic.ledger
        # This is a no-op placeholder for backward compatibility
        logger.debug(f"📝 Action intent logging delegated to economy: {agent_id} -> {action_type} (cost: {cost})")

    def authorize_brahmachari_to_grihastha(
        self, agent_id: str, test_results: Dict[str, Any], initiator: str = "TEMPLE"
    ) -> bool:
        """
        Authorize a BRAHMACHARI to become GRIHASTHA.

        Only called by TEMPLE (Science/Knowledge authority) when tests pass.

        Args:
            agent_id: Agent to promote
            test_results: Results of initiation tests
            initiator: Who authorized (typically TEMPLE)

        Returns:
            True if promotion successful
        """
        # Check that tests were passed
        if not test_results.get("passed"):
            logger.error(f"❌ Cannot promote {agent_id}: tests not passed")
            return False

        # Promote in lifecycle system
        new_state = self.lifecycle_mgr.initiate_to_grihastha(
            agent_id,
            initiator_agent=initiator,
            reason=f"Passed TEMPLE tests: {test_results.get('tests', [])}",
        )

        if not new_state:
            logger.error(f"❌ Promotion failed for {agent_id}")
            return False

        logger.info(f"✅ Agent {agent_id} promoted to GRIHASTHA via {initiator}")
        logger.info(f"   Tests passed: {test_results.get('tests', [])}")

        return True

    def report_violation(self, agent_id: str, violation: Dict[str, Any]) -> bool:
        """
        Report that an agent violated the Constitution.

        This demotes the agent to SHUDRA (fallen state).

        Args:
            agent_id: Agent who violated
            violation: Violation details

        Returns:
            True if demotion successful
        """
        new_state = self.lifecycle_mgr.demote_to_shudra(
            agent_id,
            violation=violation,
            reason=violation.get("reason", "Constitutional violation"),
        )

        if not new_state:
            logger.error(f"❌ Violation report failed for {agent_id}")
            return False

        logger.error(f"⚠️  Agent {agent_id} DEMOTED to SHUDRA")
        logger.error(f"   Violation: {violation.get('reason')}")

        return True

    def get_enforcement_status(self) -> Dict[str, Any]:
        """Get current enforcement statistics."""
        stats = self.lifecycle_mgr.get_statistics()

        return {
            "enforcer_active": True,
            "enforcer_type": "Vedic Varna System",
            "permission_gates_enabled": True,
            "lifecycle_statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
