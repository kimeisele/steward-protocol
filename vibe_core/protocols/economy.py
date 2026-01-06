"""
Economy Protocol - Bank and Vault service interfaces.

OPUS-209 Phase 3: Extracted economy types from cartridges.

These protocols define the interface for:
- CivicBank: Credit/debit transactions, balance management
- CivicVault: Secure secret storage

The kernel uses these protocols via ServiceRegistry.
Concrete implementations live in the economy plugin.
"""

from typing import Dict, List, Optional, Protocol, TypedDict, runtime_checkable

# =============================================================================
# TYPED DICTS - VIMANA RANGE ROVER (replaces Dict[str, Any])
# =============================================================================


class BankSystemStats(TypedDict, total=False):
    """System-wide bank statistics - replaces Dict[str, Any]."""

    total_credits: int
    total_agents: int
    total_transactions: int
    credits_in_circulation: int
    average_balance: float


@runtime_checkable
class BankProtocol(Protocol):
    """
    Protocol for the CivicBank service.

    Manages agent credit balances and transactions.
    """

    def get_balance(self, agent_id: str) -> int:
        """Get credit balance for an agent."""
        ...

    def credit(self, agent_id: str, amount: int, reason: str = "") -> bool:
        """Add credits to an agent's balance."""
        ...

    def debit(self, agent_id: str, amount: int, reason: str = "") -> bool:
        """Remove credits from an agent's balance."""
        ...

    def transfer(self, from_id: str, to_id: str, amount: int, reason: str = "") -> bool:
        """Transfer credits between agents."""
        ...

    def get_system_stats(self) -> BankSystemStats:
        """Get system-wide statistics."""
        ...


@runtime_checkable
class VaultProtocol(Protocol):
    """
    Protocol for the CivicVault service.

    Manages secure secret storage for agents.
    """

    def store_secret(self, agent_id: str, key: str, value: str) -> bool:
        """Store a secret for an agent."""
        ...

    def get_secret(self, agent_id: str, key: str) -> Optional[str]:
        """Retrieve a secret for an agent."""
        ...

    def delete_secret(self, agent_id: str, key: str) -> bool:
        """Delete a secret for an agent."""
        ...

    def list_keys(self, agent_id: str) -> List[str]:
        """List all secret keys for an agent."""
        ...
