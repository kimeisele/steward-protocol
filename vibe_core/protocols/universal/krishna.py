"""
KRISHNA PROTOCOL - Layer 2 (Consciousness)

"Ishvara Parama Krishna" - The Supreme Controller is Consciousness.

This protocol defines the Identity and the "Gene Host" capability.
It bridges the gap between the Abstract Identity (SovereignContext)
and the Concrete Capabilities (Genes) provided by Ananta.
"""

from typing import List, Protocol, runtime_checkable

from vibe_core.protocols.substrate import IGeneHost

from .types import SovereignContext


@runtime_checkable
class KrishnaProtocol(IGeneHost, Protocol):
    """
    The Protocol of Consciousness.

    Attributes:
        - Identity (SovereignContext): "Who am I?"
        - Capabilities (IGeneHost): "What can I do?"

    This protocol requires the implementer (The Kernel) to be a Host
    for the Genes provided by the Substrate (Ananta).
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
