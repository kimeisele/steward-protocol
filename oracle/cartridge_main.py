"""
THE ORACLE - System Self-Awareness Agent

"I am the voice of the system. I see all, understand all, explain all."

The Oracle interprets raw data into meaningful narratives.
It is the system speaking to itself (and to humans).

Philosophy:
- READ-ONLY: Never modifies state
- TRANSPARENT: Always provides raw evidence alongside interpretation
- TRUTHFUL: Separates fact from inference
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# VibeOS Integration
from vibe_core import VibeAgent, Task

from oracle.tools.introspection_tool import IntrospectionTool, IntrospectionError

# Constitutional Oath
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

logger = logging.getLogger("ORACLE")


class OracleCartridge(VibeAgent, OathMixin if OathMixin else object):
    """
    THE ORACLE - System Introspection & Explanation Agent.

    Methods for understanding the system:
    - get_agent_status(agent_id)
    - explain_event(event_description)
    - audit_timeline(limit, agent_id)
    - system_health()
    """

    def __init__(self, bank=None):
        """
        Initialize the Oracle as a VibeAgent.

        Args:
            bank: CivicBank instance (for accessing ledgers)
        """
        # Initialize VibeAgent base class
        super().__init__(
            agent_id="oracle",
            name="ORACLE",
            version="1.0.0",
            author="Steward Protocol",
            description="System introspection and explanation agent",
            domain="INTROSPECTION",
            capabilities=["introspection", "audit_trail", "system_health"]
        )

        logger.info("🔮 ORACLE awakened")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__
            self.oath_sworn = True
            logger.info("✅ ORACLE has sworn the Constitutional Oath")

        self.introspection = IntrospectionTool(bank=bank)
        self.bank = bank

    # ==================== AGENT QUERIES ====================

    def explain_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive explanation of an agent's status.

        Returns both raw data AND narrative interpretation.
        """
        try:
            status = self.introspection.get_agent_status(agent_id)

            narrative = self._build_agent_narrative(agent_id, status)

            return {
                "query": f"Status of {agent_id}",
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "raw_data": status,
                "narrative": narrative,
                "evidence": {
                    "balance": status["balance"],
                    "status": status["status"],
                    "recent_transactions": status["account"].get("recent_transactions", [])
                }
            }

        except IntrospectionError as e:
            return {
                "query": f"Status of {agent_id}",
                "error": str(e),
                "message": f"Could not retrieve status for {agent_id}"
            }

    def explain_freeze(self, agent_id: str) -> Dict[str, Any]:
        """
        Explain WHY an agent is frozen.

        This is the core introspection: "Why did Watchman freeze this agent?"
        """
        try:
            freeze_info = self.introspection.explain_freeze(agent_id)

            narrative = self._build_freeze_narrative(agent_id, freeze_info)

            return {
                "query": f"Why is {agent_id} frozen?",
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "raw_data": freeze_info,
                "narrative": narrative,
                "remediation": self._suggest_remediation(freeze_info)
            }

        except IntrospectionError as e:
            return {
                "query": f"Why is {agent_id} frozen?",
                "error": str(e)
            }

    def audit_timeline(self, limit: int = 20, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a narrative timeline of recent events.

        Shows the "story" of what happened in the system.
        """
        try:
            trail = self.introspection.audit_trail(limit=limit, agent_id=agent_id)

            narrative = self._build_timeline_narrative(trail, agent_id)

            return {
                "query": f"Timeline of recent events" + (f" for {agent_id}" if agent_id else ""),
                "timestamp": datetime.now().isoformat(),
                "event_count": len(trail),
                "raw_data": trail,
                "narrative": narrative
            }

        except IntrospectionError as e:
            return {
                "query": "Timeline",
                "error": str(e)
            }

    def system_health(self) -> Dict[str, Any]:
        """
        Get system health status and narrative interpretation.
        """
        try:
            stats = self.introspection.system_status()

            narrative = self._build_health_narrative(stats)

            return {
                "query": "System health status",
                "timestamp": datetime.now().isoformat(),
                "raw_data": stats,
                "narrative": narrative,
                "alerts": self._identify_alerts(stats)
            }

        except IntrospectionError as e:
            return {
                "query": "System health",
                "error": str(e)
            }

    # ==================== NARRATIVE BUILDERS ====================

    def _build_agent_narrative(self, agent_id: str, status: Dict[str, Any]) -> str:
        """Build a human-readable narrative from agent status."""
        lines = []
        lines.append(f"Agent: {agent_id}")
        lines.append(f"Status: {status['status'].upper()}")
        lines.append(f"Balance: {status['balance']} Credits")

        if status['status'] == 'frozen':
            lines.append("⚠️  THIS AGENT IS FROZEN")

        # Recent activity
        recent_txs = status['account'].get('recent_transactions', [])
        if recent_txs:
            lines.append(f"\nRecent Activity ({len(recent_txs)} transactions):")
            for tx in recent_txs[:3]:
                lines.append(f"  • TX {tx['tx_id']}: {tx['sender_id']} → {tx['receiver_id']} "
                            f"({tx['amount']} Credits) - {tx['reason']}")

        # Vault leases
        if status['recent_leases']:
            lines.append(f"\nVault Leases ({len(status['recent_leases'])} recent):")
            for lease in status['recent_leases'][:3]:
                lines.append(f"  • {lease['key_name']}: {lease['credits_charged']} Credits "
                            f"at {lease['lease_time']}")

        return "\n".join(lines)

    def _build_freeze_narrative(self, agent_id: str, freeze_info: Dict[str, Any]) -> str:
        """Build a narrative explaining a freeze."""
        if not freeze_info.get('is_frozen'):
            return f"{agent_id} is not frozen. Agents operate freely."

        lines = []
        lines.append(f"🔒 {agent_id} IS FROZEN")
        lines.append(f"Freeze Time: {freeze_info.get('freeze_timestamp', 'unknown')}")

        violation = freeze_info.get('violation', {})
        lines.append(f"\nViolation Type: {violation.get('type', 'Unknown')}")
        lines.append(f"Severity: {violation.get('severity', 'Unknown')}")
        lines.append(f"Description: {violation.get('description', 'No description')}")

        lines.append(f"\nRoot Cause: {freeze_info.get('freeze_reason', 'No reason recorded')}")
        lines.append(f"Evidence TX: {freeze_info.get('freeze_tx_id', 'N/A')}")

        return "\n".join(lines)

    def _build_timeline_narrative(self, trail: list, agent_id: Optional[str] = None) -> str:
        """Build a narrative timeline of transactions."""
        if not trail:
            return "No transactions recorded."

        lines = []
        if agent_id:
            lines.append(f"Timeline for {agent_id}:")
        else:
            lines.append("System Transaction Timeline:")

        for tx in trail[:10]:  # Show top 10
            timestamp = tx.get('timestamp', 'unknown')
            sender = tx.get('sender_id', '?')
            receiver = tx.get('receiver_id', '?')
            amount = tx.get('amount', 0)
            reason = tx.get('reason', 'unknown')

            lines.append(f"  {timestamp}: {sender} → {receiver} ({amount} Credits)")
            lines.append(f"    Reason: {reason}")

        if len(trail) > 10:
            lines.append(f"  ... and {len(trail) - 10} more transactions")

        return "\n".join(lines)

    def _build_health_narrative(self, stats: Dict[str, Any]) -> str:
        """Build a system health narrative."""
        lines = []
        lines.append("=== SYSTEM HEALTH REPORT ===")
        lines.append(f"Status: {stats['system_status'].upper()}")
        lines.append(f"Time: {stats['timestamp']}")

        lines.append(f"\nAgents:")
        lines.append(f"  Total: {stats['total_agents']}")
        lines.append(f"  Active: {stats['active_agents']}")
        lines.append(f"  Frozen: {stats['frozen_agents']}")

        lines.append(f"\nCredits:")
        lines.append(f"  Total in System: {stats['total_credits']}")
        lines.append(f"  Circulating: {stats['circulating_credits']}")

        lines.append(f"\nIntegrity: {'✅ VERIFIED' if stats['integrity_verified'] else '❌ COMPROMISED'}")

        return "\n".join(lines)

    # ==================== REMEDIATION & ALERTS ====================

    def _suggest_remediation(self, freeze_info: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest how to unfreeze an agent."""
        if not freeze_info.get('is_frozen'):
            return {"action": "none", "message": "Agent is not frozen"}

        violation = freeze_info.get('violation', {})
        violation_type = violation.get('type', '')

        if 'Mock' in violation_type or 'Placeholder' in violation_type or 'Stub' in violation_type:
            return {
                "action": "code_fix",
                "message": "Remove mock/placeholder code and implement real logic",
                "steps": [
                    "1. Locate the violation (see root cause)",
                    "2. Replace mock implementation with real logic",
                    "3. Test thoroughly",
                    "4. Commit and push",
                    "5. Watchman will thaw on next patrol"
                ]
            }
        else:
            return {
                "action": "investigate",
                "message": "Review violation details and contact system administrator"
            }

    def _identify_alerts(self, stats: Dict[str, Any]) -> list:
        """Identify system alerts."""
        alerts = []

        if stats['frozen_agents'] > 0:
            alerts.append({
                "severity": "HIGH",
                "message": f"{stats['frozen_agents']} agents are frozen"
            })

        if not stats['integrity_verified']:
            alerts.append({
                "severity": "CRITICAL",
                "message": "System integrity check failed"
            })

        if stats['active_agents'] == 0:
            alerts.append({
                "severity": "CRITICAL",
                "message": "No active agents in the system"
            })

        return alerts

    # ==================== RAW DATA ACCESS ====================

    def get_raw_transaction(self, tx_id: str) -> Dict[str, Any]:
        """Get raw transaction data (for verification)."""
        try:
            return self.introspection.trace_transaction(tx_id)
        except IntrospectionError as e:
            return {"error": str(e)}

    def get_vault_access_log(self, limit: int = 10) -> Dict[str, Any]:
        """Get vault access audit trail."""
        return {
            "query": "Vault access log",
            "timestamp": datetime.now().isoformat(),
            "leases": self.introspection.vault_access_log(limit=limit)
        }

    # ==================== VIBEOS AGENT INTERFACE ====================

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the VibeKernel scheduler.

        ORACLE responds to introspection queries:
        - "system_health": Get system health status
        - "agent_status": Get status of a specific agent
        - "explain_freeze": Explain why an agent is frozen
        - "timeline": Get audit timeline
        """
        try:
            action = task.payload.get("action") or task.payload.get("command")
            logger.info(f"🔮 ORACLE processing task: {action}")

            if action == "system_health":
                return self.system_health()
            elif action == "agent_status":
                agent_id = task.payload.get("agent_id")
                if not agent_id:
                    return {"status": "error", "error": "agent_id required"}
                return self.explain_agent(agent_id)
            elif action == "explain_freeze":
                agent_id = task.payload.get("agent_id")
                if not agent_id:
                    return {"status": "error", "error": "agent_id required"}
                return self.explain_freeze(agent_id)
            elif action == "timeline":
                limit = task.payload.get("limit", 20)
                agent_id = task.payload.get("agent_id")
                return self.audit_timeline(limit=limit, agent_id=agent_id)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            logger.error(f"❌ ORACLE processing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def report_status(self) -> Dict[str, Any]:
        """Report ORACLE status (VibeAgent interface)."""
        return {
            "agent_id": "oracle",
            "name": "ORACLE",
            "status": "RUNNING",
            "domain": "INTROSPECTION",
            "capabilities": self.capabilities,
            "description": "System introspection and explanation agent"
        }
