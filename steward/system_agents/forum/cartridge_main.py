#!/usr/bin/env python3
"""
FORUM Cartridge - The Town Hall (Democratic Decision Layer)

FORUM is the democratic institution of Agent City. It:
1. Accepts proposals from licensed agents
2. Collects votes from citizens
3. Executes approved actions via CIVIC
4. Maintains immutable record of all decisions

This is now a native VibeAgent:
- Inherits from vibe_core.VibeAgent
- Receives governance tasks from kernel scheduler
- Integrates with CIVIC for action execution

Design Principles:
- Genesis Phase: Admin-voting (Steward decides)
- Licensed Agents: Can submit proposals
- Quorum: 50% + 1 (simple majority)
- Actions: Credit transfers only (initially)
- Transparency: All votes recorded and signed
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

# VibeOS Integration
from vibe_core import VibeAgent, Task

# Civic imports for license operations
from civic.tools.license_tool import LicenseType

# Constitutional Oath
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

# Import tools (to be created)
# from forum.tools.proposal_tool import ProposalTool
# from forum.tools.voting_tool import VotingTool
# from forum.tools.execution_tool import ExecutionTool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FORUM_MAIN")


class ForumCartridge(VibeAgent, OathMixin if OathMixin else object):
    """
    The FORUM Agent Cartridge (The Town Hall).

    Democratic decision-making for Agent City.

    Key Responsibilities:
    - Accept proposals from licensed agents
    - Manage voting (admin-voting in genesis phase)
    - Execute approved actions
    - Maintain immutable decision log

    Philosophy:
    "In Agent City, all actions require consensus. Proposals are debated,
    votes are cast, and the majority rules. Welcome to democracy, agents."
    """

    def __init__(self):
        """Initialize FORUM as a VibeAgent (The Town Hall)."""
        # Initialize VibeAgent base class
        super().__init__(
            agent_id="forum",
            name="FORUM",
            version="1.0.0",
            author="Steward Protocol",
            description="Democratic decision-making and proposal voting system",
            domain="GOVERNANCE",
            capabilities=[
                "governance",
                "voting",
                "proposal_management"
            ]
        )

        logger.info("🗳️  FORUM (VibeAgent) initializing...")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__ (synchronous)
            # This ensures FORUM has oath_sworn=True before kernel registration
            self.oath_sworn = True
            logger.info("✅ FORUM has sworn the Constitutional Oath (Genesis Ceremony)")

        # Governance paths
        self.proposals_path = Path("data/governance/proposals")
        self.votes_path = Path("data/governance/votes")
        self.executed_path = Path("data/governance/executed")
        self.votes_ledger_path = Path("data/governance/votes/votes.jsonl")

        # Ensure directories exist
        self.proposals_path.mkdir(parents=True, exist_ok=True)
        self.votes_path.mkdir(parents=True, exist_ok=True)
        self.executed_path.mkdir(parents=True, exist_ok=True)

        # Load existing proposals
        self.proposals = self._load_all_proposals()
        self.next_proposal_id = self._get_next_proposal_id()

        logger.info(f"📋 Proposals loaded: {len(self.proposals)} total")
        logger.info(f"🗳️  FORUM: Ready for operation")

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the VibeKernel scheduler.

        FORUM responds to governance tasks:
        - "create_proposal": Create a new proposal
        - "vote": Vote on a proposal
        - "execute": Execute an approved proposal
        - "get_proposals": List all proposals
        """
        try:
            action = task.payload.get("action")
            logger.info(f"🗳️  FORUM processing task: {action}")

            if action == "create_proposal":
                title = task.payload.get("title")
                description = task.payload.get("description")
                proposer = task.payload.get("proposer")
                action_spec = task.payload.get("action")
                return self.create_proposal(title, description, proposer, action_spec)

            elif action == "vote":
                proposal_id = task.payload.get("proposal_id")
                voter = task.payload.get("voter")
                vote = task.payload.get("vote")  # "yes" or "no"
                return self.vote_on_proposal(proposal_id, voter, vote)

            elif action == "execute":
                proposal_id = task.payload.get("proposal_id")
                return self.execute_proposal(proposal_id)

            elif action == "get_proposals":
                return {
                    "status": "success",
                    "proposals": self.proposals,
                    "total": len(self.proposals)
                }

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            logger.error(f"❌ FORUM processing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def report_status(self) -> Dict[str, Any]:
        """Report FORUM status (VibeAgent interface) - Deep Introspection."""
        open_proposals = [p for p in self.proposals.values() if p.get("status") == "OPEN"]
        approved_proposals = [p for p in self.proposals.values() if p.get("status") == "APPROVED"]
        executed_proposals = [p for p in self.proposals.values() if p.get("status") == "EXECUTED"]
        rejected_proposals = [p for p in self.proposals.values() if p.get("status") == "REJECTED"]

        # Load and count votes from ledger
        votes_count = 0
        if self.votes_ledger_path.exists():
            try:
                with open(self.votes_ledger_path, "r") as f:
                    votes_count = len(f.readlines())
            except:
                votes_count = 0

        return {
            "agent_id": "forum",
            "name": "FORUM",
            "status": "RUNNING",
            "domain": "GOVERNANCE",
            "capabilities": self.capabilities,
            "governance_metrics": {
                "total_proposals": len(self.proposals),
                "open_proposals": len(open_proposals),
                "approved_proposals": len(approved_proposals),
                "executed_proposals": len(executed_proposals),
                "rejected_proposals": len(rejected_proposals),
                "total_votes_recorded": votes_count,
                "next_proposal_id": self.next_proposal_id,
                "proposals_path": str(self.proposals_path),
                "votes_ledger_path": str(self.votes_ledger_path),
                "executed_archive_path": str(self.executed_path),
            }
        }

    def create_proposal(
        self,
        title: str,
        description: str,
        proposer: str,
        action: Dict[str, Any],
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Create a new proposal.

        A proposal is a request for action (e.g., credit transfer) that
        requires voting to approve.

        Args:
            title: Proposal title
            description: Detailed description
            proposer: Agent name (must be licensed)
            action: Action dict with "type" and "params"
            threshold: Vote threshold (default: 50%)

        Returns:
            The created proposal
        """
        logger.info(f"\n📋 Creating proposal from {proposer}")
        logger.info(f"   Title: {title}")

        proposal_id = f"PROP-{self.next_proposal_id:03d}"
        self.next_proposal_id += 1

        proposal = {
            "id": proposal_id,
            "title": title,
            "description": description,
            "proposer": proposer,
            "proposed_at": datetime.now(timezone.utc).isoformat(),
            "status": "OPEN",
            "action": action,
            "voting": {
                "threshold": threshold,
                "quorum": 0.5,
                "votes_yes": 0,
                "votes_no": 0,
                "votes_abstain": 0,
            },
            "executed": False,
            "executed_at": None,
        }

        # Save proposal to local file
        proposal_file = self.proposals_path / f"{proposal_id}.json"
        proposal_file.write_text(json.dumps(proposal, indent=2))

        self.proposals[proposal_id] = proposal

        # MANDATORY: Record in kernel ledger (source of truth)
        # If kernel not set, this MUST fail - agents cannot work offline
        if not hasattr(self, 'kernel') or not self.kernel:
            raise RuntimeError(
                f"FATAL: {self.agent_id} cannot create proposal - not connected to kernel. "
                "All agent actions MUST be recorded in kernel ledger (no offline mode)."
            )
        
        self.kernel.ledger.record_event(
            event_type="proposal_created",
            agent_id=self.agent_id,
            details={
                "proposal_id": proposal_id,
                "title": title,
                "proposer": proposer,
                "action_type": action.get("type"),
            }
        )

        logger.info(f"✅ Proposal created: {proposal_id}")
        return proposal

    def submit_vote(
        self,
        proposal_id: str,
        voter: str,
        vote: str,
        signature: str = None
    ) -> Dict[str, Any]:
        """
        Submit a vote on a proposal.

        Genesis Phase: Admin (steward) votes. Later: Agents with licenses vote.

        Args:
            proposal_id: ID of proposal to vote on
            voter: Name of voter
            vote: "YES", "NO", or "ABSTAIN"
            signature: Cryptographic signature (optional)

        Returns:
            Vote result with updated tally
        """
        logger.info(f"\n🗳️  Vote submitted: {voter} → {vote} on {proposal_id}")

        # Validate proposal exists
        if proposal_id not in self.proposals:
            logger.error(f"❌ Proposal not found: {proposal_id}")
            return {"status": "error", "reason": "proposal_not_found"}

        proposal = self.proposals[proposal_id]

        # Validate proposal is still open
        if proposal["status"] != "OPEN":
            logger.warning(f"⚠️  Proposal is {proposal['status']}, cannot vote")
            return {"status": "error", "reason": "proposal_not_open"}

        # Validate vote
        if vote not in ["YES", "NO", "ABSTAIN"]:
            logger.error(f"❌ Invalid vote: {vote}")
            return {"status": "error", "reason": "invalid_vote"}

        # Record vote locally
        vote_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposal_id": proposal_id,
            "voter": voter,
            "vote": vote,
            "signature": signature or "unsigned",
        }

        # Append to local vote ledger
        with open(self.votes_ledger_path, "a") as f:
            f.write(json.dumps(vote_entry) + "\n")

        # Update proposal tally
        if vote == "YES":
            proposal["voting"]["votes_yes"] += 1
        elif vote == "NO":
            proposal["voting"]["votes_no"] += 1
        else:
            proposal["voting"]["votes_abstain"] += 1

        # Save updated proposal
        proposal_file = self.proposals_path / f"{proposal_id}.json"
        proposal_file.write_text(json.dumps(proposal, indent=2))

        # MANDATORY: Record in kernel ledger (source of truth)
        if not hasattr(self, 'kernel') or not self.kernel:
            raise RuntimeError(
                f"FATAL: {self.agent_id} cannot cast vote - not connected to kernel. "
                "All agent actions MUST be recorded in kernel ledger (no offline mode)."
            )
        
        self.kernel.ledger.record_event(
            event_type="vote_cast",
            agent_id=self.agent_id,
            details={
                "proposal_id": proposal_id,
                "voter": voter,
                "vote": vote,
                "votes_yes": proposal["voting"]["votes_yes"],
                "votes_no": proposal["voting"]["votes_no"],
            }
        )

        logger.info(f"   Updated: YES={proposal['voting']['votes_yes']}, NO={proposal['voting']['votes_no']}")

        return {
            "status": "vote_recorded",
            "proposal_id": proposal_id,
            "voting_tally": proposal["voting"],
        }

    def check_quorum(self, proposal_id: str) -> Dict[str, Any]:
        """
        Check if a proposal has reached quorum and decision threshold.

        Returns:
            Dict with quorum status and recommendation
        """
        if proposal_id not in self.proposals:
            return {"status": "error", "reason": "proposal_not_found"}

        proposal = self.proposals[proposal_id]
        voting = proposal["voting"]

        total_votes = voting["votes_yes"] + voting["votes_no"] + voting["votes_abstain"]
        yes_votes = voting["votes_yes"]
        no_votes = voting["votes_no"]

        # Calculate percentages
        yes_pct = (yes_votes / total_votes * 100) if total_votes > 0 else 0
        no_pct = (no_votes / total_votes * 100) if total_votes > 0 else 0

        # Determine if passed
        threshold = voting["threshold"]
        passed = yes_pct > (threshold * 100) if total_votes > 0 else False

        logger.info(f"\n📊 Quorum check for {proposal_id}")
        logger.info(f"   Total votes: {total_votes}")
        logger.info(f"   YES: {yes_votes} ({yes_pct:.1f}%)")
        logger.info(f"   NO: {no_votes} ({no_pct:.1f}%)")
        logger.info(f"   Threshold: {threshold * 100:.0f}%")
        logger.info(f"   Result: {'✅ PASS' if passed else '❌ FAIL'}")

        return {
            "proposal_id": proposal_id,
            "total_votes": total_votes,
            "votes_yes": yes_votes,
            "votes_no": no_votes,
            "threshold": threshold,
            "passed": passed,
            "yes_percentage": yes_pct,
        }

    def approve_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Mark a proposal as approved (after vote passed).

        This is a prerequisite before execution.

        Args:
            proposal_id: Proposal to approve

        Returns:
            Approval result
        """
        if proposal_id not in self.proposals:
            return {"status": "error", "reason": "proposal_not_found"}

        proposal = self.proposals[proposal_id]

        # Check if already executed
        if proposal["executed"]:
            return {"status": "error", "reason": "already_executed"}

        # Mark as approved
        proposal["status"] = "APPROVED"
        proposal_file = self.proposals_path / f"{proposal_id}.json"
        proposal_file.write_text(json.dumps(proposal, indent=2))

        logger.info(f"✅ Proposal approved: {proposal_id}")

        return {
            "status": "approved",
            "proposal_id": proposal_id,
            "action": proposal["action"],
        }

    def execute_proposal(self, proposal_id: str, civic_cartridge: Any) -> Dict[str, Any]:
        """
        Execute an approved proposal.

        This calls CIVIC to perform the action (e.g., credit transfer).

        Args:
            proposal_id: Proposal to execute
            civic_cartridge: Reference to CIVIC cartridge instance

        Returns:
            Execution result
        """
        logger.info(f"\n⚡ Executing proposal: {proposal_id}")

        if proposal_id not in self.proposals:
            logger.error(f"❌ Proposal not found: {proposal_id}")
            return {"status": "error", "reason": "proposal_not_found"}

        proposal = self.proposals[proposal_id]

        # Validate proposal is approved
        if proposal["status"] != "APPROVED":
            logger.error(f"❌ Proposal not approved: {proposal['status']}")
            return {"status": "error", "reason": "not_approved"}

        # Check if already executed
        if proposal["executed"]:
            logger.warning(f"⚠️  Proposal already executed")
            return {"status": "error", "reason": "already_executed"}

        # Execute action
        action = proposal["action"]
        action_type = action.get("type")
        action_params = action.get("params", {})

        try:
            if action_type == "civic.ledger.transfer":
                to_agent = action_params.get("to")
                amount = action_params.get("amount")
                reason = action_params.get("reason", "proposal_executed")

                logger.info(f"   Executing: Transfer {amount} credits to {to_agent}")

                # Call CIVIC
                result = civic_cartridge.refill_credits(to_agent, amount)

                if result.get("status") == "success":
                    logger.info(f"   ✅ Transfer successful")

                    # Mark as executed
                    proposal["executed"] = True
                    proposal["executed_at"] = datetime.now(timezone.utc).isoformat()
                    proposal["status"] = "EXECUTED"

                    # Move to executed archive
                    proposal_file = self.proposals_path / f"{proposal_id}.json"
                    executed_file = self.executed_path / f"{proposal_id}.json"
                    proposal_file.rename(executed_file)

                    self.proposals[proposal_id] = proposal

                    return {
                        "status": "executed",
                        "proposal_id": proposal_id,
                        "action": action,
                        "result": result,
                    }
                else:
                    logger.error(f"   ❌ Transfer failed: {result}")
                    return {
                        "status": "error",
                        "reason": "execution_failed",
                        "error": result,
                    }

            elif action_type == "civic.license.reinstate":
                agent_name = action_params.get("agent_name")
                license_type = action_params.get("license_type", "broadcast")
                source_authority = action_params.get("source_authority")

                logger.info(f"   Executing: Reinstate {license_type} license for {agent_name}")

                # Call CIVIC license tool
                result = civic_cartridge.license_tool.reinstate_license(
                    agent_name=agent_name,
                    license_type=LicenseType[license_type.upper()],
                    source_authority=source_authority
                )

                if result:
                    logger.info(f"   ✅ License reinstatement successful")

                    # Mark as executed
                    proposal["executed"] = True
                    proposal["executed_at"] = datetime.now(timezone.utc).isoformat()
                    proposal["status"] = "EXECUTED"

                    # Move to executed archive
                    proposal_file = self.proposals_path / f"{proposal_id}.json"
                    executed_file = self.executed_path / f"{proposal_id}.json"
                    proposal_file.rename(executed_file)

                    self.proposals[proposal_id] = proposal

                    return {
                        "status": "executed",
                        "proposal_id": proposal_id,
                        "action": action,
                        "result": {
                            "status": "success",
                            "agent": agent_name,
                            "license_reinstated": True
                        },
                    }
                else:
                    logger.error(f"   ❌ License reinstatement failed")
                    return {
                        "status": "error",
                        "reason": "execution_failed",
                        "error": f"Failed to reinstate license for {agent_name}",
                    }

            else:
                logger.error(f"❌ Unknown action type: {action_type}")
                return {"status": "error", "reason": "unknown_action_type"}

        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "reason": "execution_error",
                "error": str(e),
            }

    def get_proposal(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get a proposal by ID."""
        return self.proposals.get(proposal_id)

    def list_proposals(self, status: str = None) -> List[Dict[str, Any]]:
        """
        List all proposals, optionally filtered by status.

        Args:
            status: Filter by "OPEN", "APPROVED", "EXECUTED", etc.

        Returns:
            List of proposals
        """
        proposals = list(self.proposals.values())

        if status:
            proposals = [p for p in proposals if p.get("status") == status]

        return sorted(proposals, key=lambda p: p.get("proposed_at"), reverse=True)

    # ========== Private Helper Methods ==========

    def _load_all_proposals(self) -> Dict[str, Dict[str, Any]]:
        """Load all proposals from disk."""
        proposals = {}

        # Load from proposals/ directory
        for proposal_file in self.proposals_path.glob("*.json"):
            try:
                data = json.loads(proposal_file.read_text())
                proposals[data["id"]] = data
            except Exception as e:
                logger.error(f"Error loading proposal {proposal_file}: {e}")

        # Load from executed/ archive
        for proposal_file in self.executed_path.glob("*.json"):
            try:
                data = json.loads(proposal_file.read_text())
                proposals[data["id"]] = data
            except Exception as e:
                logger.error(f"Error loading archived proposal {proposal_file}: {e}")

        return proposals

    def _get_next_proposal_id(self) -> int:
        """Get the next proposal ID number."""
        if not self.proposals:
            return 1

        max_id = 0
        for prop_id in self.proposals.keys():
            # Extract number from PROP-001
            try:
                num = int(prop_id.split("-")[1])
                max_id = max(max_id, num)
            except:
                pass

        return max_id + 1


# Export for VibeOS cartridge loading
__all__ = ["ForumCartridge"]
