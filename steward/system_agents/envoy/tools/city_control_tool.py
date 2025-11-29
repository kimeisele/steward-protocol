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

This tool can run in two modes:
1. **Kernel Mode**: Integrated with VibeOS kernel (production)
2. **Direct Mode**: Direct cartridge instantiation (standalone/testing)
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CITY_CONTROL")


class CityControlTool:
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

    def __init__(self, kernel=None):
        """
        Initialize City Control Tool.

        Args:
            kernel: VibeOS kernel instance (optional, for kernel mode)
        """
        self.kernel = kernel
        self.mode = "KERNEL" if kernel else "DIRECT"

        # Lazy-load cartridges (only in DIRECT mode)
        self._herald = None
        self._civic = None
        self._forum = None

        logger.info(f"🏙️  City Control Tool initialized (Mode: {self.mode})")

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
                    civic._get_registry_from_kernel()
                    if self.kernel
                    else {"agents": civic.registry.get("agents", {})}
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
            status = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "city_name": "Agent City",
                "mode": self.mode,
                "agents": {
                    "total": agent_count,
                    "registry": list(registry_data.get("agents", {}).keys()),
                },
                "economy": {
                    "total_credits_allocated": (
                        operations_data.get("credits_allocated", 0)
                        if operations_data
                        else 0
                    ),
                    "total_transactions": (
                        operations_data.get("total_transactions", 0)
                        if operations_data
                        else 0
                    ),
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
            }

            logger.info(
                f"✅ City status retrieved: {agent_count} agents, {len(open_proposals)} open proposals"
            )
            return status

        except Exception as e:
            logger.error(f"❌ Failed to get city status: {e}")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "health": "🔴 ERROR",
            }

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

    def vote_proposal(
        self, proposal_id: str, choice: str, voter: str = "operator"
    ) -> Dict[str, Any]:
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
            agent_name: Name of agent ("herald", "civic", "forum")
            action: Action to perform (e.g., "run_campaign", "check_license")
            **kwargs: Additional parameters for the action

        Returns:
            dict: Action result
        """
        logger.info(f"🤖 Triggering {agent_name}.{action}...")

        try:
            # Get agent cartridge
            if agent_name == "herald":
                agent = self._get_herald()
            elif agent_name == "civic":
                agent = self._get_civic()
            elif agent_name == "forum":
                agent = self._get_forum()
            else:
                return {"status": "error", "reason": f"unknown_agent: {agent_name}"}

            if not agent:
                return {"status": "error", "reason": "agent_not_available"}

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

    # ==================== CARTRIDGE MANAGEMENT (DIRECT MODE) ====================

    def _get_herald(self):
        """Get Herald cartridge (lazy load)."""
        if self.kernel:
            return self.kernel.agent_registry.get("herald")

        if not self._herald:
            try:
                from herald.cartridge_main import HeraldCartridge

                self._herald = HeraldCartridge()
                logger.debug("📦 Herald cartridge loaded")
            except Exception as e:
                logger.error(f"Failed to load Herald: {e}")

        return self._herald

    def _get_civic(self):
        """Get Civic cartridge (lazy load)."""
        if self.kernel:
            return self.kernel.agent_registry.get("civic")

        if not self._civic:
            try:
                from civic.cartridge_main import CivicCartridge

                self._civic = CivicCartridge()
                logger.debug("📦 Civic cartridge loaded")
            except Exception as e:
                logger.error(f"Failed to load Civic: {e}")

        return self._civic

    def _get_forum(self):
        """Get Forum cartridge (lazy load)."""
        if self.kernel:
            return self.kernel.agent_registry.get("forum")

        if not self._forum:
            try:
                from forum.cartridge_main import ForumCartridge

                self._forum = ForumCartridge()
                logger.debug("📦 Forum cartridge loaded")
            except Exception as e:
                logger.error(f"Failed to load Forum: {e}")

        return self._forum

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
