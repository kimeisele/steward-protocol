"""
VEDIC GOVERNANCE PROTOCOL - Layer 1: Interface Only

Protocol for Vedic taxonomy and agent classification.
Used by OS-level code (prana_init) to access Vedic concepts
without direct plugin imports.

No implementations here - see vibe_core/plugins/vedic_governance/
"""

from enum import Enum
from typing import Any, Dict, List, Protocol


class VarnaType(Enum):
    """
    Vedic species classification for agents.

    This is the PROTOCOL-LEVEL enum that OS code can use.
    The plugin has the full implementation.
    """

    MANUSHA = "manusha"  # Conscious, self-directed
    PASHU = "pashu"  # Task-oriented, follows directives
    PAKSHI = "pakshi"  # Messenger, lightweight
    KRIMAYO = "krimayo"  # Background, minimal consciousness


class AsharamaStage(Enum):
    """
    Ashrama lifecycle stages for agents.

    Determines write privileges and permissions:
    - BRAHMACHARI: Read-only, learning phase
    - GRIHASTHA: Full write access, active work
    - VANAPRASTHA: Read + teach, deprecating
    - SANNYASA: System functions only, daemon mode
    """

    BRAHMACHARI = "brahmachari"  # Student: read, observe, learn
    GRIHASTHA = "grihastha"  # Householder: read, write, create
    VANAPRASTHA = "vanaprastha"  # Retiree: read, teach, archive
    SANNYASA = "sannyasa"  # Renunciate: system functions only


class VedicGovernanceProtocol(Protocol):
    """
    Protocol for Vedic governance operations.

    Implemented by: VedicGovernancePlugin
    Used by: prana_init.py, any OS-level code needing Vedic taxonomy
    """

    def get_all_agents(self) -> List[str]:
        """Return list of all registered agent IDs."""
        ...

    def get_agent_varna(self, agent_id: str) -> VarnaType:
        """Get the Varna (species) classification of an agent."""
        ...

    def get_agents_by_varna(self, varna: VarnaType) -> List[str]:
        """Get all agents of a specific Varna."""
        ...

    def get_agent_metadata(self, agent_id: str) -> Dict[str, Any]:
        """Get full metadata for an agent."""
        ...

    def verify_agent_oaths(self) -> bool:
        """Verify all agents have taken the constitutional oath."""
        ...

    # =========================================================================
    # ASHRAMA LIFECYCLE (Stage-based permissions)
    # =========================================================================

    def get_agent_ashrama(self, agent_id: str) -> AsharamaStage:
        """Get the Ashrama lifecycle stage of an agent."""
        ...

    def promote_agent(self, agent_id: str, reason: str = "Promotion") -> bool:
        """Promote agent to next Ashrama stage (BRAHMACHARI→GRIHASTHA→etc)."""
        ...

    def get_agent_permissions(self, agent_id: str) -> List[str]:
        """Get list of permissions for agent based on Ashrama stage."""
        ...

    def check_agent_permission(self, agent_id: str, permission: str) -> bool:
        """Check if agent has a specific permission (e.g., 'write', 'create')."""
        ...

    # =========================================================================
    # BHAKTI (Earned trust/karma)
    # =========================================================================

    def get_bhakti_balance(self, agent_id: str) -> int:
        """
        Get agent's Bhakti (devotion/trust) balance.

        Bhakti is earned through:
        - Successful task completion
        - Selfless service (seva)
        - Code purification (tapas)
        - Tests before code (TDD dharma)

        Scale: 0-200+ (50+ allows permission overrides)
        """
        ...

    def add_bhakti(self, agent_id: str, amount: int, reason: str = "Service") -> bool:
        """Add Bhakti points to agent (reward for devotional practice)."""
        ...

    # =========================================================================
    # GUNA (Quality ratios - Sattva/Rajas/Tamas)
    # =========================================================================

    def get_agent_guna(self, agent_id: str) -> Dict[str, float]:
        """
        Get agent's Guna composition (quality ratios).

        Returns: {"sattva": 0.0-1.0, "rajas": 0.0-1.0, "tamas": 0.0-1.0}
        Sum always equals 1.0
        """
        ...


__all__ = [
    "VarnaType",
    "AsharamaStage",
    "VedicGovernanceProtocol",
]
