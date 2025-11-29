"""
ECONOMY AGENT - Credit & License Management Component

Handles:
- Credit management and deduction
- Broadcast licensing
- Ledger transactions
- Credit refills
"""

import logging
from typing import Dict, Any, Optional

from vibe_core import VibeAgent, Task

from .tools.ledger_tool import LedgerTool
from .tools.license_tool import LicenseTool, LicenseType

logger = logging.getLogger("ECONOMY_AGENT")


class EconomyAgent(VibeAgent):
    """Handles credit management, licensing, and economic operations."""

    def __init__(self):
        super().__init__(
            agent_id="civic_economy",
            name="CIVIC Economy",
            version="2.0.0",
            author="Steward Protocol",
            description="Economic system: credits, licenses, ledger",
            domain="GOVERNANCE",
            capabilities=["economy", "licensing", "ledger"],
        )

        self.ledger = LedgerTool("data/registry/ledger.jsonl")
        self.license_tool = LicenseTool("data/registry/licenses.json")

        logger.info(f"💰 Ledger initialized: {len(self.ledger.entries)} transactions")
        logger.info(
            f"🎫 License database initialized: {len(self.license_tool.licenses)} licenses"
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """Process economy-related tasks."""
        action = task.payload.get("action")

        if action == "check_license":
            return self.check_broadcast_license(task.payload.get("agent_id"))
        elif action == "deduct_credits":
            return self.deduct_credits(
                agent_name=task.payload.get("agent_id"),
                amount=task.payload.get("amount", 1),
                reason=task.payload.get("reason", "action"),
            )
        elif action == "refill_credits":
            return self.refill_credits(
                agent_name=task.payload.get("agent_id"),
                amount=task.payload.get("amount"),
            )
        elif action == "revoke_license":
            return self.revoke_license(
                agent_name=task.payload.get("agent_id"),
                reason=task.payload.get("reason", "violation"),
                source_authority=task.payload.get("source_authority"),
            )
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}

    def check_broadcast_license(self, agent_name: str) -> Dict[str, Any]:
        """Check if an agent has broadcast license."""
        license_info = self.license_tool.check_license(
            agent_name, LicenseType.BROADCAST
        )

        if license_info and license_info.get("status") == "ACTIVE":
            logger.info(f"✅ {agent_name} has active broadcast license")
            return {"agent": agent_name, "licensed": True, "status": "ACTIVE"}

        logger.warning(f"⚠️  {agent_name} does not have active broadcast license")
        return {
            "agent": agent_name,
            "licensed": False,
            "reason": "license_revoked" if license_info else "not_registered",
        }

    def deduct_credits(
        self, agent_name: str, amount: int = 1, reason: str = "broadcast"
    ) -> Dict[str, Any]:
        """
        Deduct credits from an agent's account.

        This records the transaction in the ledger.
        """
        logger.info(f"💰 Deducting {amount} credits from {agent_name} ({reason})")

        try:
            # Record transaction in ledger
            self.ledger.record_transaction(
                agent_id=agent_name,
                transaction_type="debit",
                amount=amount,
                reason=reason,
            )

            logger.info(f"   ✅ Recorded in ledger")

            return {
                "status": "success",
                "agent": agent_name,
                "credits_deducted": amount,
                "reason": reason,
            }

        except Exception as e:
            logger.error(f"❌ Credit deduction error: {e}")
            return {"status": "error", "agent": agent_name, "error": str(e)}

    def refill_credits(
        self, agent_name: str, amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """Refill an agent's credits (admin operation)."""
        if amount is None:
            amount = 50  # Default refill amount

        logger.info(f"💰 Refilling credits for {agent_name} (+{amount})")

        try:
            # Record transaction in ledger
            self.ledger.record_transaction(
                agent_id=agent_name,
                transaction_type="credit",
                amount=amount,
                reason="admin_refill",
            )

            logger.info(f"   ✅ Recorded in ledger")

            return {"status": "success", "agent": agent_name, "credits_added": amount}

        except Exception as e:
            logger.error(f"❌ Credit refill error: {e}")
            return {"status": "error", "agent": agent_name, "error": str(e)}

    def revoke_license(
        self, agent_name: str, reason: str = "violation", source_authority: str = None
    ) -> Dict[str, Any]:
        """Revoke an agent's broadcast license."""
        logger.info(f"🔴 Revoking broadcast license for {agent_name}")
        logger.info(f"   Reason: {reason}")
        if source_authority:
            logger.info(f"   Authority: {source_authority}")

        try:
            success = self.license_tool.revoke_license(
                agent_name,
                license_type=LicenseType.BROADCAST,
                reason=reason,
                source_authority=source_authority,
            )

            if not success:
                logger.warning(
                    f"⚠️  License revocation failed: {agent_name} has no active broadcast license"
                )
                return {
                    "status": "error",
                    "reason": "license_not_found",
                    "agent": agent_name,
                    "message": f"No broadcast license found for {agent_name}",
                }

            logger.info(f"   ✅ License revoked")

            return {
                "status": "success",
                "agent": agent_name,
                "reason": reason,
                "source_authority": source_authority,
                "message": f"Broadcast license revoked for {agent_name}",
            }

        except Exception as e:
            logger.error(f"❌ License revocation error: {e}")
            return {"status": "error", "agent": agent_name, "error": str(e)}

    def report_status(self) -> Dict[str, Any]:
        """Report economy status."""
        active_licenses = len(
            [
                lic
                for lic in self.license_tool.licenses.values()
                if lic.get("status") == "ACTIVE"
            ]
        )

        return {
            "agent_id": "civic_economy",
            "name": "CIVIC Economy",
            "status": "RUNNING",
            "ledger_entries": len(self.ledger.entries) if self.ledger.entries else 0,
            "active_licenses": active_licenses,
            "ledger_path": "data/registry/ledger.jsonl",
            "licenses_path": "data/registry/licenses.json",
        }


__all__ = ["EconomyAgent"]
