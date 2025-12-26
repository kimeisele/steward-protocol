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


__all__ = [
    "VarnaType",
    "VedicGovernanceProtocol",
]
