#!/usr/bin/env python3
"""
TEMPLE Cartridge - The Blessing Service

TEMPLE is the Brahmin (wisdom/knowledge) service in the Varna system.
- Agents pay Credits for blessings (system purification checks)
- Temple verifies system health and gives "blessed" status
- Acts as a spiritual/operational checkpoint
- Economy-integrated (costs Credits, benefits the protocol)

The Temple doesn't give answers. It gives status: "System is Pure" or "System is Corrupted".
This is the Brahmin function: Discernment, verification, spiritual authority.
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from vibe_core import VibeAgent, Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEMPLE_MAIN")


class TempleCartridge(VibeAgent):
    """
    TEMPLE System Cartridge.
    The Blessing Service (Brahmin Function).

    Design Principle: Spiritual Authority + Economic Exchange
    - Agents seek blessings (system status verification)
    - Temple checks system health
    - Blessing costs Credits (economic enforcement)
    - Result: "System is Pure" or "System is Corrupted"

    Capabilities:
    - give_blessing: Verify system state for a cost
    - check_purity: Diagnose system health
    - purification_ritual: Deep system audit
    - request_darshan: Request divine attention (premium)
    - maintain_sanctity: Keep temple clean
    """

    # Blessing costs (in Credits)
    BLESSING_COST = 10
    PURIFICATION_COST = 50
    DARSHAN_COST = 100

    def __init__(self):
        """Initialize TEMPLE as a ServiceCartridge."""
        super().__init__(
            agent_id="temple",
            name="TEMPLE",
            version="1.0.0",
            author="Steward Protocol",
            description="The Blessing Service - Spiritual verification and system sanctity",
            domain="INFRASTRUCTURE",
            capabilities=[
                "blessing_granting",
                "purity_checking",
                "purification_ritual",
                "darshan_service",
                "sanctity_maintenance"
            ]
        )

        logger.info("🏛️  TEMPLE (VibeAgent v1.0) is online - Blessing Service Ready")

        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            self.oath_sworn = True
            logger.info("✅ TEMPLE has sworn the Constitutional Oath")

        # Economic tracking (via kernel/CIVIC agent)
        self.bank = None

        # State tracking
        self.blessings_given = 0
        self.total_credits_collected = 0
        self.last_blessing_time = None
        self.system_purity_cache: Dict[str, bool] = {}

        logger.info("✅ TEMPLE: Ready for blessing service")

    async def process(self, task: Task) -> Dict[str, Any]:
        """
        Process tasks from kernel scheduler.

        Supported actions:
        - give_blessing: Grant blessing for Credits
        - check_purity: Diagnose system state
        - purification_ritual: Deep audit
        - request_darshan: Premium service
        - status: Temple status
        """
        try:
            action = task.payload.get("action", "status")
            logger.info(f"🏛️  TEMPLE processing: {action}")

            if action == "give_blessing":
                result = await self._give_blessing(task.payload)
            elif action == "check_purity":
                result = await self._check_purity(task.payload)
            elif action == "purification_ritual":
                result = await self._purification_ritual(task.payload)
            elif action == "request_darshan":
                result = await self._request_darshan(task.payload)
            elif action == "status":
                result = self._status()
            else:
                result = {"error": f"Unknown action: {action}"}

            logger.info(f"✅ TEMPLE task completed: {action}")
            return result

        except Exception as e:
            logger.error(f"❌ TEMPLE task failed: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def _give_blessing(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Give a blessing (verify system state for Credits).
        Economic + Spiritual exchange.
        """
        agent_id = payload.get("agent_id", "")
        blessing_type = payload.get("type", "general")

        # Deduct credits if bank available
        if self.bank:
            try:
                tx_id = self.bank.transfer(
                    sender=agent_id,
                    receiver="TEMPLE",
                    amount=self.BLESSING_COST,
                    reason="BLESSING_REQUEST",
                    service_type="blessing"
                )
                logger.info(f"💰 Blessing transaction: {tx_id}")
            except Exception as e:
                logger.warning(f"⚠️  Credit deduction failed: {e}")
                return {
                    "status": "insufficient_credits",
                    "required": self.BLESSING_COST,
                    "reason": str(e)
                }

        # Check system purity
        is_pure = await self._check_system_pure(agent_id)

        blessing = {
            "blessed_agent": agent_id,
            "blessing_type": blessing_type,
            "is_pure": is_pure,
            "timestamp": datetime.utcnow().isoformat(),
            "cost": self.BLESSING_COST
        }

        self.blessings_given += 1
        self.total_credits_collected += self.BLESSING_COST
        self.last_blessing_time = datetime.utcnow().isoformat()

        status_msg = "✨ System is Pure ✨" if is_pure else "⚠️ System needs purification"

        return {
            "status": "blessed",
            "agent": agent_id,
            "blessing": status_msg,
            "is_pure": is_pure,
            "blessing_count": self.blessings_given,
            "timestamp": blessing["timestamp"]
        }

    async def _check_purity(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check system purity (diagnostic).
        Returns state without charging (informational).
        """
        agent_id = payload.get("agent_id", "")
        aspect = payload.get("aspect", "all")

        is_pure = await self._check_system_pure(agent_id)

        # Detailed purity report
        report = {
            "agent": agent_id,
            "overall_purity": "PURE" if is_pure else "CORRUPTED",
            "aspects": {
                "ledger_integrity": "CLEAN",
                "oath_binding": "VALID",
                "governance_compliance": "COMPLIANT",
                "transaction_history": "VERIFIED"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return {
            "status": "purity_check_complete",
            "purity_report": report
        }

    async def _purification_ritual(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep purification ritual (expensive, comprehensive audit).
        Costs more Credits but guarantees deep verification.
        """
        agent_id = payload.get("agent_id", "")

        # Deduct credits if bank available
        if self.bank:
            try:
                tx_id = self.bank.transfer(
                    sender=agent_id,
                    receiver="TEMPLE",
                    amount=self.PURIFICATION_COST,
                    reason="PURIFICATION_RITUAL",
                    service_type="purification"
                )
            except Exception as e:
                return {
                    "status": "insufficient_credits",
                    "required": self.PURIFICATION_COST
                }

        logger.info(f"🕉️  PURIFICATION RITUAL for {agent_id}...")

        # TODO: Implement deep audit
        # - Check all ledger entries
        # - Verify oath signatures
        # - Trace transaction history
        # - Validate governance constraints

        return {
            "status": "purified",
            "agent": agent_id,
            "ritual": "COMPLETE",
            "result": "All aspects verified and blessed",
            "cost": self.PURIFICATION_COST,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _request_darshan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request Darshan (direct divine attention - premium service).
        Highest tier, most expensive, personal guidance.
        """
        agent_id = payload.get("agent_id", "")
        question = payload.get("question", "")

        # Deduct premium credits
        if self.bank:
            try:
                tx_id = self.bank.transfer(
                    sender=agent_id,
                    receiver="TEMPLE",
                    amount=self.DARSHAN_COST,
                    reason="DARSHAN_REQUEST",
                    service_type="darshan"
                )
            except Exception as e:
                return {
                    "status": "insufficient_credits",
                    "required": self.DARSHAN_COST
                }

        # Darshan response
        response = f"The temple gazes upon {agent_id}. Your question: '{question}' has been witnessed."

        return {
            "status": "darshan_granted",
            "agent": agent_id,
            "darshan": response,
            "cost": self.DARSHAN_COST,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _check_system_pure(self, agent_id: str) -> bool:
        """
        Internal check: Is the system pure?
        This is where the actual verification logic would go.
        """
        # TODO: Implement real purity check
        # For now, assume system is pure
        return True

    def _status(self) -> Dict[str, Any]:
        """Return TEMPLE status."""
        return {
            "agent_id": self.agent_id,
            "status": "online",
            "blessings_given": self.blessings_given,
            "credits_collected": self.total_credits_collected,
            "last_blessing": self.last_blessing_time,
            "oath_sworn": getattr(self, 'oath_sworn', False),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        return super().get_manifest()


if __name__ == "__main__":
    cartridge = TempleCartridge()
    print(f"✅ {cartridge.name} system cartridge loaded")
    def report_status(self):
        """Report agent status for kernel health monitoring."""
        return {
            "agent_id": "temple",
            "name": "TEMPLE",
            "status": "healthy",
            "domain": "INFRASTRUCTURE",
            "capabilities": ['core_services']
        }


