"""
THE INTROSPECTION ENGINE - System Self-Awareness

Read-only access to all system ledgers:
- Bank Ledger (Economy)
- Vault Ledger (Assets)
- Event Logs (Agent Activity)
- Governance (Decisions)

Philosophy:
"The system must be able to see itself. Not to change, but to understand."

This tool aggregates raw data into meaningful context.
Every method is READ-ONLY. No side effects.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ORACLE_INTROSPECTION")


class IntrospectionError(Exception):
    """Raised when introspection fails."""

    pass


class IntrospectionTool:
    """
    THE INTROSPECTION ENGINE.

    Read-only access to all ledgers. Aggregates data into meaningful context.
    """

    def __init__(self, bank=None):
        """
        Initialize introspection engine.

        Args:
            bank: CivicBank instance (for reading ledger data)
        """
        self.bank = bank
        self.vault = bank.vault if bank else None
        logger.info("🔮 ORACLE INTROSPECTION ENGINE initialized")

    # ==================== AGENT INSPECTION ====================

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get complete status snapshot of an agent.

        Returns aggregated data:
        - Current balance
        - Frozen status
        - Last transactions
        - Error/violation history
        """
        if not self.bank:
            raise IntrospectionError("Bank not available")

        try:
            # 1. Balance & Freeze Status
            balance = self.bank.get_balance(agent_id)
            is_frozen = self.bank.is_frozen(agent_id)

            # 2. Account Statement
            statement = self.bank.get_account_statement(agent_id)

            # 3. Vault Leases (if available)
            vault_leases = []
            if self.vault:
                vault_leases = self.vault.lease_history(agent_id=agent_id, limit=5)

            return {
                "agent_id": agent_id,
                "status": "frozen" if is_frozen else "active",
                "balance": balance,
                "account": statement,
                "recent_leases": vault_leases,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            raise IntrospectionError(f"Failed to get agent status: {e}")

    # ==================== TRANSACTION TRACING ====================

    def trace_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Trace a transaction through the ledger.

        Shows:
        - Sender, receiver, amount
        - Reason & service type
        - Timestamp
        - Chained hash (proof of immutability)
        """
        if not self.bank:
            raise IntrospectionError("Bank not available")

        try:
            cur = self.bank.conn.cursor()
            cur.execute("SELECT * FROM transactions WHERE tx_id = ?", (tx_id,))
            row = cur.fetchone()

            if not row:
                raise IntrospectionError(f"Transaction not found: {tx_id}")

            # Convert row to dict
            tx_dict = dict(row)

            # Get the double-entry detail
            cur.execute("SELECT * FROM entries WHERE tx_id = ?", (tx_id,))
            entries = [dict(e) for e in cur.fetchall()]

            return {
                "tx_id": tx_dict["tx_id"],
                "timestamp": tx_dict["timestamp"],
                "sender": tx_dict["sender_id"],
                "receiver": tx_dict["receiver_id"],
                "amount": tx_dict["amount"],
                "reason": tx_dict["reason"],
                "service_type": tx_dict["service_type"],
                "previous_hash": tx_dict["previous_hash"],
                "tx_hash": tx_dict["tx_hash"],
                "entries": entries,
            }

        except Exception as e:
            raise IntrospectionError(f"Failed to trace transaction: {e}")

    # ==================== FREEZE INVESTIGATION ====================

    def explain_freeze(self, agent_id: str) -> Dict[str, Any]:
        """
        Explain why an agent is frozen.

        Returns:
        - Freeze timestamp
        - Reason for freeze
        - Linked violation evidence
        - Remediation steps
        """
        if not self.bank:
            raise IntrospectionError("Bank not available")

        try:
            # Check if frozen
            if not self.bank.is_frozen(agent_id):
                return {
                    "agent_id": agent_id,
                    "is_frozen": False,
                    "message": f"{agent_id} is not frozen",
                }

            # Find FREEZE transaction
            cur = self.bank.conn.cursor()
            cur.execute(
                """
                SELECT * FROM transactions
                WHERE (sender_id = ? OR receiver_id = ?)
                AND reason LIKE '%FREEZE%'
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (agent_id, agent_id),
            )

            freeze_tx = cur.fetchone()

            if not freeze_tx:
                return {
                    "agent_id": agent_id,
                    "is_frozen": True,
                    "message": f"{agent_id} is frozen but no FREEZE transaction found (manual freeze?)",
                }

            freeze_dict = dict(freeze_tx)

            # Extract violation details from reason
            reason = freeze_dict.get("reason", "")
            violation_details = self._parse_freeze_reason(reason)

            return {
                "agent_id": agent_id,
                "is_frozen": True,
                "freeze_timestamp": freeze_dict["timestamp"],
                "freeze_reason": reason,
                "violation": violation_details,
                "freeze_tx_id": freeze_dict["tx_id"],
                "message": f"{agent_id} was frozen on {freeze_dict['timestamp']} "
                f"due to: {violation_details.get('type', 'unknown')}",
            }

        except Exception as e:
            raise IntrospectionError(f"Failed to explain freeze: {e}")

    def _parse_freeze_reason(self, reason: str) -> Dict[str, Any]:
        """Parse freeze reason into structured violation data."""
        # Format: "FREEZE: [violation_type] in [file]::[function]"
        # Example: "FREEZE: Mock Return in herald/tools/social_tool.py::post"

        if "Mock Return" in reason:
            return {
                "type": "Mock Implementation",
                "severity": "CRITICAL",
                "description": "Function returns hardcoded value without real implementation",
            }
        elif "Placeholder" in reason:
            return {
                "type": "Placeholder Code",
                "severity": "CRITICAL",
                "description": "Placeholder or TODO implementation detected",
            }
        elif "NotImplementedError" in reason:
            return {
                "type": "Stub Implementation",
                "severity": "CRITICAL",
                "description": "Function raises NotImplementedError instead of implementing logic",
            }
        else:
            return {"type": "Violation", "severity": "HIGH", "description": reason}

    # ==================== AUDIT TRAIL ====================

    def audit_trail(
        self, limit: int = 20, agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail of recent transactions.

        Args:
            limit: Max transactions to return
            agent_id: Filter by specific agent (optional)

        Returns:
            List of transaction records
        """
        if not self.bank:
            raise IntrospectionError("Bank not available")

        try:
            cur = self.bank.conn.cursor()

            if agent_id:
                cur.execute(
                    """
                    SELECT * FROM transactions
                    WHERE sender_id = ? OR receiver_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (agent_id, agent_id, limit),
                )
            else:
                cur.execute(
                    "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )

            rows = cur.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            raise IntrospectionError(f"Failed to get audit trail: {e}")

    # ==================== SYSTEM HEALTH ====================

    def system_status(self) -> Dict[str, Any]:
        """
        Get overall system health snapshot.

        Returns:
        - Total agents
        - Frozen agents
        - Total credits in circulation
        - System integrity status
        """
        if not self.bank:
            raise IntrospectionError("Bank not available")

        try:
            # Get system stats
            stats = self.bank.get_system_stats()

            # Get frozen agents count
            cur = self.bank.conn.cursor()
            cur.execute("SELECT COUNT(*) as count FROM accounts WHERE is_frozen = 1")
            frozen_count = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) as count FROM accounts")
            total_agents = cur.fetchone()["count"]

            # Verify integrity
            integrity_ok = self.bank.verify_integrity()

            return {
                "timestamp": datetime.now().isoformat(),
                "total_agents": total_agents,
                "frozen_agents": frozen_count,
                "active_agents": total_agents - frozen_count,
                "total_credits": stats.get("total_credits", 0),
                "circulating_credits": stats.get("circulating_credits", 0),
                "integrity_verified": integrity_ok,
                "system_status": "healthy" if integrity_ok else "compromised",
            }

        except Exception as e:
            raise IntrospectionError(f"Failed to get system status: {e}")

    # ==================== VAULT INSPECTION ====================

    def vault_assets(self) -> List[Dict[str, Any]]:
        """
        List all assets in the Civic Vault.

        Note: Only lists asset names/metadata, NOT values (encrypted).
        """
        if not self.vault:
            return []

        try:
            return self.vault.list_assets()
        except Exception as e:
            logger.warning(f"Failed to list vault assets: {e}")
            return []

    def vault_access_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get vault access audit trail.

        Shows who accessed what secret, when, and at what cost.
        """
        if not self.vault:
            return []

        try:
            return self.vault.lease_history(limit=limit)
        except Exception as e:
            logger.warning(f"Failed to get vault access log: {e}")
            return []
