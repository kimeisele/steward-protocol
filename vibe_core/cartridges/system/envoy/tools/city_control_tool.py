#!/usr/bin/env python3
"""
THE ENVOY CITY CONTROL TOOL - Universal Operator Interface to Agent City

This tool provides LLM-friendly methods for controlling Agent City without shell access.
Perfect for shell-less environments (Claude Code Web, Vibe Cloud, etc.).

The Missing Link: GAD-000 Layer 3 - The AI Operating the AI

Usage:
    # Initialize
    tool = CityControlTool()

    # Check city status
    status = tool.get_city_status()

    # List proposals
    proposals = tool.list_proposals()

    # Vote on a proposal
    tool.vote_proposal("PROP-001", "YES", voter="operator")

    # Trigger agent action
    tool.trigger_agent("herald", "run_campaign", dry_run=True)

ARCHITECTURE: Requires VibeOS kernel for operation.
All agent access goes through kernel.agent_registry.
Protected agents (narasimha, auditor, etc.) cannot be triggered via Envoy.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CITY_CONTROL")

# PERMISSION LAYER: Agents that Envoy CANNOT trigger without elevated permission
# These are system-critical agents that could damage the system if misused
PROTECTED_AGENTS = frozenset(
    [
        "narasimha",  # Kill switch - can terminate agents
        "auditor",  # Compliance enforcement - should not be triggered casually
        "supreme_court",  # Justice system - requires formal process
        "discoverer",  # Agent registration - system-level operation
        "watchman",  # System integrity - monitoring only, not triggerable
        "kernel",  # The kernel itself (if exposed as agent)
    ]
)

# Agents that Envoy CAN trigger freely (citizen agents + safe system agents)
# All agents in kernel.agent_registry are allowed EXCEPT protected ones


class CityControlTool(Tool):
    """
    Universal Operator Interface to Agent City.

    Provides high-level control methods that an LLM can call without shell access.

    Capabilities:
    - 🏙️  get_city_status() - View the city pulse
    - 📋 list_proposals() - See open governance issues
    - 🗳️  vote_proposal() - Participate in democracy
    - 🤖 trigger_agent() - Command agents to act
    - 💰 check_credits() - View economic status
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, kernel=None):
        super().__init__(services)
        """
        Initialize City Control Tool.

        Args:
            kernel: VibeOS kernel instance (REQUIRED for production)
        """
        self.kernel = kernel

        # NO MORE DIRECT MODE - Kernel is required for proper operation
        if not kernel:
            logger.warning("⚠️ CityControlTool initialized without kernel - limited functionality")

        # Operating mode (for status display)
        self.mode = "KERNEL" if kernel else "STANDALONE"

        logger.info("🏙️  City Control Tool initialized")

    @property
    def name(self) -> str:
        return "envoy.city_control"

    @property
    def description(self) -> str:
        return "Universal Operator Interface to Agent City (The Golden Straw)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: get_city_status | list_proposals | vote_proposal | execute_proposal | trigger_agent | check_credits | refill_credits",
            },
            "status": {"type": "string", "required": False, "description": "Proposal status filter"},
            "proposal_id": {"type": "string", "required": False, "description": "Proposal ID"},
            "choice": {"type": "string", "required": False, "description": "Vote choice (YES/NO)"},
            "voter": {"type": "string", "required": False, "description": "Voter name"},
            "agent_name": {"type": "string", "required": False, "description": "Agent name"},
            "agent_action": {"type": "string", "required": False, "description": "Agent action to trigger"},
            "amount": {"type": "int", "required": False, "description": "Credit amount"},
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute city control operations."""
        try:
            action = parameters["action"]

            if action == "get_city_status":
                status = self.get_city_status()
                return ToolResult(success=True, output=status, metadata={"action": action})

            elif action == "list_proposals":
                status_filter = parameters.get("status", "OPEN")
                proposals = self.list_proposals(status_filter)
                return ToolResult(success=True, output={"proposals": proposals}, metadata={"action": action})

            elif action == "vote_proposal":
                proposal_id = parameters.get("proposal_id")
                choice = parameters.get("choice")
                voter = parameters.get("voter", "operator")
                if not proposal_id or not choice:
                    return ToolResult(success=False, error="vote_proposal requires proposal_id and choice")
                result = self.vote_proposal(proposal_id, choice, voter)
                return ToolResult(success=True, output=result, metadata={"action": action})

            elif action == "execute_proposal":
                proposal_id = parameters.get("proposal_id")
                if not proposal_id:
                    return ToolResult(success=False, error="execute_proposal requires proposal_id")
                result = self.execute_proposal(proposal_id)
                return ToolResult(success=True, output=result, metadata={"action": action})

            elif action == "trigger_agent":
                agent_name = parameters.get("agent_name")
                agent_action = parameters.get("agent_action")
                if not agent_name or not agent_action:
                    return ToolResult(success=False, error="trigger_agent requires agent_name and agent_action")
                kwargs = {k: v for k, v in parameters.items() if k not in ["action", "agent_name", "agent_action"]}
                result = self.trigger_agent(agent_name, agent_action, **kwargs)
                return ToolResult(success=True, output=result, metadata={"action": action})

            elif action == "check_credits":
                agent_name = parameters.get("agent_name")
                if not agent_name:
                    return ToolResult(success=False, error="check_credits requires agent_name")
                result = self.check_credits(agent_name)
                return ToolResult(success=True, output=result, metadata={"action": action})

            elif action == "refill_credits":
                agent_name = parameters.get("agent_name")
                amount = parameters.get("amount", 50)
                if not agent_name:
                    return ToolResult(success=False, error="refill_credits requires agent_name")
                result = self.refill_credits(agent_name, amount)
                return ToolResult(success=True, output=result, metadata={"action": action})

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            error_msg = f"City control operation failed: {type(e).__name__}: {e!s}"
            logger.error(error_msg, exc_info=True)
            return ToolResult(success=False, error=error_msg)

    # ==================== HIGH-LEVEL OPERATOR METHODS ====================

    def get_city_status(self) -> Dict[str, Any]:
        """
        Get comprehensive city status.

        Returns overview of:
        - Total agents registered
        - Credit economy status
        - Open proposals
        - Recent activity

        This is the "pulse check" for the operator.

        Returns:
            dict: City status snapshot
        """
        logger.info("📊 Fetching city status...")

        try:
            # Read OPERATIONS.md for metrics
            operations_path = Path("OPERATIONS.md")
            operations_data = None
            if operations_path.exists():
                operations_data = self._parse_operations_md(operations_path)

            # Get agent registry from Civic
            civic = self._get_civic()
            if civic:
                registry_data = (
                    civic._get_registry_from_kernel() if self.kernel else {"agents": civic.registry.get("agents", {})}
                )
                agent_count = len(registry_data.get("agents", {}))
            else:
                agent_count = 0
                registry_data = {}

            # Get open proposals from Forum
            forum = self._get_forum()
            open_proposals = []
            if forum:
                open_proposals = forum.list_proposals(status="OPEN")

            # Compile status
            agent_list = list(registry_data.get("agents", {}).keys())
            credits_allocated = operations_data.get("credits_allocated", 0) if operations_data else 0
            total_transactions = operations_data.get("total_transactions", 0) if operations_data else 0

            status = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "city_name": "Agent City",
                "mode": self.mode,
                "agents": {
                    "total": agent_count,
                    "registry": agent_list,
                },
                "economy": {
                    "total_credits_allocated": credits_allocated,
                    "total_transactions": total_transactions,
                },
                "governance": {
                    "open_proposals": len(open_proposals),
                    "proposals": [
                        {
                            "id": p.get("id"),
                            "title": p.get("title"),
                            "proposer": p.get("proposer"),
                            "status": p.get("status"),
                        }
                        for p in open_proposals
                    ],
                },
                "health": "🟢 OPERATIONAL",
                # Human-readable response for ENVOY.md display
                "response": self._format_status_markdown(
                    agent_count, agent_list, credits_allocated, total_transactions, open_proposals, self.mode
                ),
            }

            logger.info(f"✅ City status retrieved: {agent_count} agents, {len(open_proposals)} open proposals")
            return status

        except Exception as e:
            logger.error(f"❌ Failed to get city status: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "health": "🔴 ERROR",
                "response": f"Error: {e}",
            }

    def _format_status_markdown(
        self,
        agent_count: int,
        agent_list: List[str],
        credits_allocated: int,
        total_transactions: int,
        open_proposals: List[Dict],
        mode: str,
    ) -> str:
        """
        Format status data as human-readable markdown.

        This is the neuro-symbolic output layer - transforms structured
        data into readable format without LLM.
        """
        lines = [
            f"🏙️ **Agent City** | Mode: {mode} | Health: 🟢 OPERATIONAL",
            "",
        ]

        # Agents section
        if agent_count > 0:
            agent_display = ", ".join(agent_list[:5])
            if agent_count > 5:
                agent_display += f" (+{agent_count - 5} more)"
            lines.append(f"**Agents ({agent_count}):** {agent_display}")
        else:
            lines.append("**Agents:** None registered")

        # Economy section
        if credits_allocated > 0 or total_transactions > 0:
            lines.append(f"**Economy:** {credits_allocated} credits | {total_transactions} transactions")

        # Governance section
        if open_proposals:
            lines.append(f"**Proposals ({len(open_proposals)} open):**")
            for p in open_proposals[:3]:
                lines.append(f"  - {p.get('id', '?')}: {p.get('title', 'Untitled')}")
        else:
            lines.append("**Proposals:** None open")

        return " | ".join(lines[:3]) if len(lines) <= 3 else "\n".join(lines)

    def list_proposals(self, status: str = "OPEN") -> List[Dict[str, Any]]:
        """
        List governance proposals.

        Args:
            status: Filter by status ("OPEN", "APPROVED", "EXECUTED", or None for all)

        Returns:
            list: Proposals matching filter
        """
        logger.info(f"📋 Listing proposals (status: {status})...")

        try:
            forum = self._get_forum()
            if not forum:
                logger.error("❌ Forum not available")
                return []

            proposals = forum.list_proposals(status=status)
            logger.info(f"✅ Found {len(proposals)} proposals")
            return proposals

        except Exception as e:
            logger.error(f"❌ Failed to list proposals: {e}")
            return []

    def vote_proposal(self, proposal_id: str, choice: str, voter: str = "operator") -> Dict[str, Any]:
        """
        Vote on a proposal.

        Args:
            proposal_id: Proposal ID (e.g., "PROP-001")
            choice: Vote choice ("YES", "NO", or "ABSTAIN")
            voter: Name of voter (default: "operator")

        Returns:
            dict: Vote result with updated tally
        """
        logger.info(f"🗳️  Voting on {proposal_id}: {choice}")

        try:
            forum = self._get_forum()
            if not forum:
                return {"status": "error", "reason": "forum_not_available"}

            # Submit vote
            result = forum.submit_vote(proposal_id, voter, choice.upper())

            # Check if we should auto-approve
            if result.get("status") == "vote_recorded":
                quorum_check = forum.check_quorum(proposal_id)

                if quorum_check.get("passed"):
                    logger.info("✅ Quorum reached! Approving proposal...")
                    approval = forum.approve_proposal(proposal_id)
                    result["auto_approved"] = True
                    result["approval"] = approval

            return result

        except Exception as e:
            logger.error(f"❌ Failed to vote: {e}")
            return {"status": "error", "error": str(e)}

    def execute_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Execute an approved proposal.

        Args:
            proposal_id: Proposal ID to execute

        Returns:
            dict: Execution result
        """
        logger.info(f"⚡ Executing proposal: {proposal_id}")

        try:
            forum = self._get_forum()
            civic = self._get_civic()

            if not forum or not civic:
                return {"status": "error", "reason": "agents_not_available"}

            result = forum.execute_proposal(proposal_id, civic)
            return result

        except Exception as e:
            logger.error(f"❌ Failed to execute proposal: {e}")
            return {"status": "error", "error": str(e)}

    def trigger_agent(self, agent_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """
        Trigger an agent action.

        Args:
            agent_name: Name of any registered agent (dynamic lookup)
            action: Action to perform (e.g., "run_campaign", "check_license")
            **kwargs: Additional parameters for the action

        Returns:
            dict: Action result
        """
        logger.info(f"🤖 Triggering {agent_name}.{action}...")

        try:
            # PERMISSION CHECK: Block protected agents
            if agent_name in PROTECTED_AGENTS:
                logger.warning(f"🚫 PERMISSION DENIED: '{agent_name}' is a protected system agent")
                return {
                    "status": "error",
                    "reason": "permission_denied",
                    "message": f"Agent '{agent_name}' is protected and cannot be triggered via Envoy. "
                    f"Protected agents: {sorted(PROTECTED_AGENTS)}",
                    "hint": "Use kernel syscalls or governance proposals to interact with protected agents.",
                }

            # DYNAMIC AGENT LOOKUP
            agent = self._get_agent(agent_name)
            if not agent:
                # List available agents for helpful error message
                available = self._list_available_agents()
                return {
                    "status": "error",
                    "reason": f"unknown_agent: {agent_name}",
                    "available_agents": available,
                }

            # Create task
            from vibe_core.scheduling import Task

            task = Task(agent_id=agent_name, payload={"action": action, **kwargs})

            # Process task
            result = agent.process(task)
            logger.info(f"✅ Action completed: {result.get('status')}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to trigger agent: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}

    def check_credits(self, agent_name: str) -> Dict[str, Any]:
        """
        Check an agent's credit balance.

        Args:
            agent_name: Name of agent to check

        Returns:
            dict: Credit balance and license status
        """
        logger.info(f"💰 Checking credits for {agent_name}...")

        try:
            civic = self._get_civic()
            if not civic:
                return {"status": "error", "reason": "civic_not_available"}

            license_check = civic.check_broadcast_license(agent_name)
            return license_check

        except Exception as e:
            logger.error(f"❌ Failed to check credits: {e}")
            return {"status": "error", "error": str(e)}

    def refill_credits(self, agent_name: str, amount: int = 50) -> Dict[str, Any]:
        """
        Refill an agent's credits (admin operation).

        Args:
            agent_name: Agent to refill
            amount: Credits to add (default: 50)

        Returns:
            dict: Refill result
        """
        logger.info(f"💰 Refilling credits for {agent_name} (+{amount})...")

        try:
            civic = self._get_civic()
            if not civic:
                return {"status": "error", "reason": "civic_not_available"}

            result = civic.refill_credits(agent_name, amount)
            return result

        except Exception as e:
            logger.error(f"❌ Failed to refill credits: {e}")
            return {"status": "error", "error": str(e)}

    # ==================== AGENT ACCESS (KERNEL REQUIRED) ====================

    def _get_agent(self, agent_name: str):
        """
        Get any agent by name from kernel registry.

        KERNEL REQUIRED - No legacy fallback. The kernel is the source of truth.
        """
        if not self.kernel:
            logger.error("Cannot get agent: kernel not initialized")
            return None

        agent = self.kernel.agent_registry.get(agent_name)
        if agent:
            logger.debug(f"📦 Agent '{agent_name}' found in kernel registry")
            return agent
        else:
            logger.warning(f"Agent '{agent_name}' not found in kernel registry")
            return None

    def _list_available_agents(self) -> List[str]:
        """List all available agents (excluding protected ones)."""
        if not self.kernel:
            return []

        # Return all agents EXCEPT protected ones
        all_agents = set(self.kernel.agent_registry.keys())
        available = all_agents - PROTECTED_AGENTS
        return sorted(available)

    def _get_civic(self):
        """Get Civic agent from kernel (required for credits/governance)."""
        return self._get_agent("civic")

    def _get_forum(self):
        """Get Forum agent from kernel (required for proposals)."""
        return self._get_agent("forum")

    # ==================== HELPER METHODS ====================

    def _parse_operations_md(self, path: Path) -> Optional[Dict[str, Any]]:
        """Parse OPERATIONS.md for metrics."""
        try:
            content = path.read_text()

            # Extract key metrics (simple regex parsing)
            import re

            data = {}

            # Total Transactions
            match = re.search(r"\| Total Transactions \| (\d+) \|", content)
            if match:
                data["total_transactions"] = int(match.group(1))

            # Credits Allocated
            match = re.search(r"\| Credits Allocated \| (\d+) \|", content)
            if match:
                data["credits_allocated"] = int(match.group(1))

            # Credits Spent
            match = re.search(r"\| Credits Spent \| (\d+) \|", content)
            if match:
                data["credits_spent"] = int(match.group(1))

            return data

        except Exception as e:
            logger.error(f"Failed to parse OPERATIONS.md: {e}")
            return None


# ==================== CONVENIENCE FUNCTIONS ====================


def create_city_controller(kernel=None) -> CityControlTool:
    """
    Factory function to create a City Control Tool.

    Args:
        kernel: VibeOS kernel (optional)

    Returns:
        CityControlTool instance
    """
    return CityControlTool(kernel=kernel)


if __name__ == "__main__":
    # Demo: City Control in action
    print("\n" + "=" * 70)
    print("🏙️  CITY CONTROL TOOL - DEMO")
    print("=" * 70)

    # Initialize
    tool = CityControlTool()

    # 1. Get city status
    print("\n📊 CITY STATUS:")
    status = tool.get_city_status()
    print(json.dumps(status, indent=2))

    # 2. List proposals
    print("\n📋 OPEN PROPOSALS:")
    proposals = tool.list_proposals(status="OPEN")
    if proposals:
        for prop in proposals:
            print(f"  - {prop['id']}: {prop['title']} (by {prop['proposer']})")
    else:
        print("  No open proposals")

    # 3. Check Herald's credits
    print("\n💰 HERALD CREDITS:")
    credits = tool.check_credits("herald")
    print(json.dumps(credits, indent=2))

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)


__all__ = ["CityControlTool", "create_city_controller"]
