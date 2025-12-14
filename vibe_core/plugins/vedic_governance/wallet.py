"""
💰 VEDIC WALLET SYSTEM 💰
=========================

OPUS-071: Economy-ready interface stub.

The Wallet provides the economic layer for agent operations.
Integrates with Ashrama lifecycle to enforce spending permissions.

Current state: STUB (ready for economy plugin implementation)

Future capabilities:
- Credit tracking per agent
- Transaction ledger
- Tax collection (governance revenue)
- Karma-weighted rewards
- Inter-agent transfers

Philosophy:
"Lakshmi is wealth. She follows Dharma. No wealth without righteous action."
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.plugins.vedic_governance.ashrama import AshramaTransition

logger = logging.getLogger("VEDIC_WALLET")


@dataclass
class Transaction:
    """A single wallet transaction."""

    tx_id: str
    agent_id: str
    amount: int  # Positive = credit, Negative = debit
    tx_type: str  # "reward", "tax", "transfer", "spend"
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WalletInterface(ABC):
    """
    Abstract Wallet Interface.

    This is the contract that any economy plugin must implement.
    Vedic Governance uses this to check spending permissions.
    """

    @abstractmethod
    def get_balance(self, agent_id: str) -> int:
        """Get current credit balance for an agent."""
        pass

    @abstractmethod
    def credit(self, agent_id: str, amount: int, reason: str) -> bool:
        """Add credits to agent's wallet. Returns success."""
        pass

    @abstractmethod
    def debit(self, agent_id: str, amount: int, reason: str) -> bool:
        """Remove credits from agent's wallet. Returns success."""
        pass

    @abstractmethod
    def transfer(self, from_agent: str, to_agent: str, amount: int, reason: str) -> bool:
        """Transfer credits between agents. Returns success."""
        pass

    @abstractmethod
    def get_transaction_history(self, agent_id: str, limit: int = 100) -> List[Transaction]:
        """Get transaction history for an agent."""
        pass


class WalletStub(WalletInterface):
    """
    STUB Implementation - Always succeeds, tracks nothing.

    OPUS-071: This allows the system to compile and run without
    a real economy backend. When ready, swap for real implementation.
    """

    def __init__(self):
        """Initialize stub wallet."""
        self._balances: Dict[str, int] = {}
        self._transactions: Dict[str, List[Transaction]] = {}
        self._tx_counter = 0
        logger.info("💰 WalletStub initialized (no real economy)")

    def get_balance(self, agent_id: str) -> int:
        """Get balance (stub: returns default or tracked value)."""
        return self._balances.get(agent_id, 1000)  # Default starting credits

    def credit(self, agent_id: str, amount: int, reason: str) -> bool:
        """Credit agent (stub: tracks in memory)."""
        if amount <= 0:
            return False
        self._balances[agent_id] = self.get_balance(agent_id) + amount
        self._record_tx(agent_id, amount, "credit", reason)
        logger.debug(f"💰 STUB: Credited {amount} to {agent_id} ({reason})")
        return True

    def debit(self, agent_id: str, amount: int, reason: str) -> bool:
        """Debit agent (stub: tracks in memory)."""
        if amount <= 0:
            return False
        current = self.get_balance(agent_id)
        if current < amount:
            logger.warning(f"💰 STUB: Insufficient funds for {agent_id} ({current} < {amount})")
            return False
        self._balances[agent_id] = current - amount
        self._record_tx(agent_id, -amount, "debit", reason)
        logger.debug(f"💰 STUB: Debited {amount} from {agent_id} ({reason})")
        return True

    def transfer(self, from_agent: str, to_agent: str, amount: int, reason: str) -> bool:
        """Transfer between agents (stub: memory-only)."""
        if not self.debit(from_agent, amount, f"Transfer to {to_agent}: {reason}"):
            return False
        self.credit(to_agent, amount, f"Transfer from {from_agent}: {reason}")
        return True

    def get_transaction_history(self, agent_id: str, limit: int = 100) -> List[Transaction]:
        """Get transactions (stub: memory-only)."""
        return self._transactions.get(agent_id, [])[-limit:]

    def _record_tx(self, agent_id: str, amount: int, tx_type: str, reason: str) -> None:
        """Record transaction in memory."""
        self._tx_counter += 1
        tx = Transaction(
            tx_id=f"TX-{self._tx_counter:06d}",
            agent_id=agent_id,
            amount=amount,
            tx_type=tx_type,
            reason=reason,
        )
        if agent_id not in self._transactions:
            self._transactions[agent_id] = []
        self._transactions[agent_id].append(tx)


class WalletGate:
    """
    Wallet permission gate that integrates with Ashrama lifecycle.

    Checks if an agent has spending permission based on their lifecycle stage.
    """

    def __init__(self, wallet: Optional[WalletInterface] = None):
        """Initialize with optional wallet backend."""
        self._wallet = wallet or WalletStub()

    @property
    def wallet(self) -> WalletInterface:
        """Get the underlying wallet."""
        return self._wallet

    def can_spend(self, ashrama: Optional["AshramaTransition"]) -> bool:
        """
        Check if agent can spend based on Ashrama stage.

        Only GRIHASTHA (householder/active) has wallet access.
        """
        if ashrama is None:
            return False

        # Import here to avoid circular dependency
        from vibe_core.plugins.vedic_governance.ashrama import ASHRAMA_SPECIFICATIONS

        specs = ASHRAMA_SPECIFICATIONS.get(ashrama.current_ashrama, {})
        return specs.get("wallet_access", False)

    def try_spend(
        self, agent_id: str, amount: int, reason: str, ashrama: Optional["AshramaTransition"] = None
    ) -> Dict[str, Any]:
        """
        Attempt to spend credits with permission check.

        Returns:
            {"success": bool, "reason": str, "balance": int}
        """
        # Check permission first
        if ashrama and not self.can_spend(ashrama):
            stage = ashrama.current_ashrama.value
            return {
                "success": False,
                "reason": f"Agent is in {stage} stage - no wallet access",
                "balance": self._wallet.get_balance(agent_id),
            }

        # Attempt debit
        if self._wallet.debit(agent_id, amount, reason):
            return {
                "success": True,
                "reason": f"Spent {amount} credits: {reason}",
                "balance": self._wallet.get_balance(agent_id),
            }
        else:
            return {
                "success": False,
                "reason": "Insufficient funds",
                "balance": self._wallet.get_balance(agent_id),
            }

    def reward(self, agent_id: str, amount: int, reason: str) -> bool:
        """
        Give credits to an agent (no permission check - rewards are always allowed).
        """
        return self._wallet.credit(agent_id, amount, reason)

    def tax(self, agent_id: str, amount: int, reason: str = "Governance tax") -> bool:
        """
        Collect tax from an agent (governance revenue).

        Note: Taxes bypass normal permission checks.
        """
        return self._wallet.debit(agent_id, amount, reason)
