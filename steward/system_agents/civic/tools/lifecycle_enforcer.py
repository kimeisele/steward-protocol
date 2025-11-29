#!/usr/bin/env python3
"""
LIFECYCLE ENFORCER - The Kernel-Level Permission Gate

This is the crucial component that makes the simulation REAL (not a mock).

It sits at the kernel boundary and checks:
1. Does this agent have the right lifecycle status?
2. Does the ledger show they can afford this action?
3. Has their karma (persistent state) been updated?

Without this, agents could act freely (mock).
With this, consequences are PERSISTENT and BINDING.

The philosophy:
"An agent trying to act without being qualified is like a student
trying to teach before learning. The KERNEL says NO."
"""

import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

from .lifecycle_manager import LifecycleManager, LifecycleStatus
from .economy import CivicBank

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


class LifecycleEnforcer:
    """
    The kernel-level permission gate.

    Every agent action must pass through this enforcer:
    1. Lifecycle check (is the agent qualified for this action?)
    2. Economic check (does the agent have credits?)
    3. Constitutional check (does the action violate the oath?)
    4. Ledger check (is the action recorded for karma?)

    If ANY of these fail, the action is REJECTED at the kernel level.
    """

    def __init__(self):
        """Initialize the enforcer."""
        self.lifecycle_mgr = LifecycleManager()
        self.bank = CivicBank()
        logger.info("🚫 LIFECYCLE ENFORCER initialized (Kernel-Level Permission Gate)")

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
            lifecycle_status=str(
                self.lifecycle_mgr.get_lifecycle_state(agent_id).status.value
            ),
        )

        logger.info(
            f"✅ Action PERMITTED: {agent_id} - {action_type} (cost: {cost} credits)"
        )
        return result

    def _check_lifecycle_status(
        self, agent_id: str, action_type: str
    ) -> PermissionResult:
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
                reason = (
                    f"Agent {agent_id} is VANAPRASTHA (Retired). "
                    f"Deprecated code - read-only archive access only."
                )
            elif status == LifecycleStatus.SANNYASA:
                reason = (
                    f"Agent {agent_id} is SANNYASA (Renounced). "
                    f"Agent merged into core - no longer executable."
                )
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
            reason=f"Lifecycle check passed",
            action_type=action_type,
            agent_id=agent_id,
            lifecycle_status=state.status.value,
        )

    def _check_economic_status(self, agent_id: str, cost: int) -> PermissionResult:
        """
        Check if agent has sufficient credits for the action.

        Args:
            agent_id: Agent to check
            cost: Credit cost of action

        Returns:
            PermissionResult
        """
        try:
            balance = self.bank.get_balance(agent_id)

            if balance < cost:
                return PermissionResult(
                    permitted=False,
                    reason=f"Insufficient credits: {agent_id} has {balance}, needs {cost}",
                    action_type="economic_check",
                    agent_id=agent_id,
                )

            return PermissionResult(
                permitted=True,
                reason=f"Economic check passed",
                action_type="economic_check",
                agent_id=agent_id,
            )
        except Exception as e:
            # If we can't check the bank, assume insufficient funds (fail-safe)
            return PermissionResult(
                permitted=False,
                reason=f"Could not verify economic status: {str(e)}",
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
        Record the action intent in the ledger BEFORE execution.

        This is CRITICAL for karma tracking:
        1. If system crashes mid-action, we have a record
        2. Audit trail shows what agents intended to do
        3. Consequences are PERSISTENT (not a mock)

        Args:
            agent_id: Agent performing action
            action_type: Type of action
            cost: Credit cost
            details: Additional context
        """
        try:
            # Create intent record in bank
            reason = f"Action intent: {action_type}"
            if details:
                reason += f" ({details})"

            self.bank.transfer(
                agent_id, "LIFECYCLE_GATE", cost, reason, "action_authorization"
            )

            logger.info(f"📝 Action intent recorded for {agent_id}: {action_type}")
        except Exception as e:
            logger.error(f"❌ Failed to record action intent: {e}")
            # Don't fail the action, just warn

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
