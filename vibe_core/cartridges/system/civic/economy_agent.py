"""
ECONOMY AGENT - Credit & License Management Component

Handles:
- Credit management and deduction
- Broadcast licensing
- Ledger transactions
- Credit refills
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x070cb261"  # GenesisByte: parampara % 37 == 0

import logging
from typing import Any, Dict, Optional

from vibe_core import Task, VibeAgent

# NO TOOL IMPORTS - Tools accessed via self.system.execute_tool()

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

        # NO TOOL INSTANCES OWNED - Agent is NAKED
        # Tools accessed via self.system.execute_tool()
        self.system = None  # Will be injected by parent via set_system()

        logger.info("💰 CIVIC Economy initialized (Naked Agent - awaiting system injection)")

    def set_system(self, system):
        """
        Inject system interface from parent CIVIC cartridge.

        This allows the EconomyAgent sub-agent to access kernel tools
        via self.system.execute_tool().

        Args:
            system: The system interface (from parent agent's self.system)
        """
        self.system = system
        logger.info("✅ CIVIC Economy: system interface injected")

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
        # Execute license check via kernel
        result = self.system.execute_tool(
            "civic.license",
            {"action": "check_license", "agent_id": agent_name, "license_type": "broadcast"},
        )

        if not result.success:
            logger.error(f"❌ License check failed: {result.error}")
            return {"agent": agent_name, "licensed": False, "reason": "check_failed", "error": result.error}

        license_info = result.output

        if license_info and license_info.get("status") == "active":
            logger.info(f"✅ {agent_name} has active broadcast license")
            return {"agent": agent_name, "licensed": True, "status": "ACTIVE"}

        logger.warning(f"⚠️  {agent_name} does not have active broadcast license")
        return {
            "agent": agent_name,
            "licensed": False,
            "reason": "license_revoked" if license_info else "not_registered",
        }

    def deduct_credits(self, agent_name: str, amount: int = 1, reason: str = "broadcast") -> Dict[str, Any]:
        """
        Deduct credits from an agent's account.

        This records the transaction in the ledger.
        """
        logger.info(f"💰 Deducting {amount} credits from {agent_name} ({reason})")

        try:
            # Record transaction in ledger via kernel
            result = self.system.execute_tool(
                "civic.ledger",
                {
                    "action": "record_transaction",
                    "agent_id": agent_name,
                    "transaction_type": "debit",
                    "amount": amount,
                    "reason": reason,
                },
            )

            if not result.success:
                logger.error(f"❌ Credit deduction error: {result.error}")
                return {"status": "error", "agent": agent_name, "error": result.error}

            logger.info("   ✅ Recorded in ledger")

            return {
                "status": "success",
                "agent": agent_name,
                "credits_deducted": amount,
                "reason": reason,
            }

        except Exception as e:
            logger.error(f"❌ Credit deduction error: {e}")
            return {"status": "error", "agent": agent_name, "error": str(e)}

    def refill_credits(self, agent_name: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Refill an agent's credits (admin operation)."""
        if amount is None:
            amount = 50  # Default refill amount

        logger.info(f"💰 Refilling credits for {agent_name} (+{amount})")

        try:
            # Record transaction in ledger via kernel
            result = self.system.execute_tool(
                "civic.ledger",
                {
                    "action": "record_transaction",
                    "agent_id": agent_name,
                    "transaction_type": "credit",
                    "amount": amount,
                    "reason": "admin_refill",
                },
            )

            if not result.success:
                logger.error(f"❌ Credit refill error: {result.error}")
                return {"status": "error", "agent": agent_name, "error": result.error}

            logger.info("   ✅ Recorded in ledger")

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
            # Revoke license via kernel
            result = self.system.execute_tool(
                "civic.license",
                {
                    "action": "revoke_license",
                    "agent_id": agent_name,
                    "license_type": "broadcast",
                    "reason": reason,
                    "source_authority": source_authority,
                },
            )

            if not result.success:
                logger.warning(f"⚠️  License revocation failed: {result.error}")
                return {
                    "status": "error",
                    "reason": "license_not_found",
                    "agent": agent_name,
                    "message": f"No broadcast license found for {agent_name}",
                    "error": result.error,
                }

            logger.info("   ✅ License revoked")

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
        # Get ledger summary via kernel
        ledger_result = self.system.execute_tool("civic.ledger", {"action": "get_summary"})
        ledger_summary = ledger_result.output if ledger_result.success else {}

        # Get licenses summary via kernel
        license_result = self.system.execute_tool("civic.license", {"action": "list_licenses"})
        all_licenses = license_result.output.get("all_licenses", {}) if license_result.success else {}

        # Count active licenses
        active_licenses = 0
        for agent, licenses in all_licenses.items():
            for lic in licenses:
                if lic.get("status") == "active" and lic.get("valid"):
                    active_licenses += 1

        return {
            "agent_id": "civic_economy",
            "name": "CIVIC Economy",
            "status": "RUNNING",
            "ledger_entries": ledger_summary.get("total_transactions", 0),
            "active_licenses": active_licenses,
            "ledger_path": "data/economy.db",
            "licenses_path": "data/registry/licenses.json",
        }


__all__ = ["EconomyAgent"]
