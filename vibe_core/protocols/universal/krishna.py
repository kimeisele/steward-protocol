"""
KRISHNA PROTOCOL - Layer 2 (Consciousness)

"Ishvara Parama Krishna" - The Supreme Controller is Krishna.

This protocol defines the Identity and the "Gene Host" capability.
It bridges the gap between the Abstract Identity (SovereignContext)
and the Concrete Capabilities (Genes) provided by Ananta.

GAD-000 COMPLIANT:
- Discoverability: sovereign_context property
- Observability: get_identity_status() ← RED-001 FIX
- Parseability: IdentityStatus dataclass
- Composability: bind_genes() pipeable
- Idempotency: bind_genes() safe to retry
- Recoverability: status includes health
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Protocol, runtime_checkable

from vibe_core.protocols.substrate import IGeneHost

from .types import SovereignContext


@dataclass
class IdentityStatus:
    """GAD-000 Observability: Status of the Conscious Identity."""

    identity_id: str
    is_valid: bool
    genes_bound: List[str] = field(default_factory=list)
    last_bind_time: datetime = field(default_factory=datetime.now)
    health: str = "HEALTHY"  # HEALTHY, DEGRADED, INVALID


@runtime_checkable
class KrishnaProtocol(IGeneHost, Protocol):
    """
    The Protocol of Consciousness.

    Attributes:
        - Identity (SovereignContext): "Who am I?"
        - Capabilities (IGeneHost): "What can I do?"

    This protocol requires the implementer (The Kernel) to be a Host
    for the Genes provided by the Substrate (Ananta).

    GAD-000: Observability via get_identity_status()
    """

    @property
    def sovereign_context(self) -> SovereignContext:
        """
        The Immutable Identity of the current cycle.
        """
        ...

    def bind_genes(self, gene_names: List[str]) -> bool:
        """
        The 'Positive Pathogen' Mechanism.
        Injects capabilities (genes) into this Consciousness.

        This corresponds to MantraOpCode.BIND_CTX.

        Args:
            gene_names: List of genes (e.g. "scribe", "warrior") to inject.

        Returns:
            True if binding successful (Genes accepted the Host).
        """
        ...

    def get_identity_status(self) -> IdentityStatus:
        """
        GAD-000 Observability: Get current identity state.

        Returns:
            IdentityStatus with id, validity, bound genes, health.
        """
        ...
