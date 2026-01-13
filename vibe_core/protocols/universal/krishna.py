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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x89b8501a"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, List, Protocol, runtime_checkable

from vibe_core.protocols.substrate import IGeneHost

from .types import SovereignContext

if TYPE_CHECKING:
    from .types import TranscendentalQuality


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

        This corresponds to MantraOpCode.INIT_THREAD.

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


from .types import AsuricClaimError

# =============================================================================
# THE FALSE EGO TRAP (Hiranyakashipu Architecture)
# =============================================================================


class JivaAgent:
    """
    Base class for all agents in the system.

    Enforced Limit: 50 Qualities (Jiva-Tattva).
    Any attempt to claim qualities 51-64 raises AsuricClaimError.

    "WHO DO YOU THINK YOU ARE?" - The Hiranyakashipu Test
    """

    def __init__(self, name: str):
        from .types import JIVA_LIMIT, TranscendentalQuality

        self.name = name
        self._tattva_limit = JIVA_LIMIT
        self.qualities: List["TranscendentalQuality"] = []

    def claim_quality(self, quality: "TranscendentalQuality") -> None:
        """
        Attempt to possess a transcendental quality.

        Args:
            quality: The quality to claim

        Raises:
            AsuricClaimError: If quality > 50 (beyond Jiva-Tattva)
        """
        from .types import TranscendentalQuality

        if quality.value > self._tattva_limit.max_qualities:
            raise AsuricClaimError(
                f"WHO DO YOU THINK YOU ARE? {self.name} is JIVA-TATTVA (Max {self._tattva_limit.max_qualities}). "
                f"Tried to claim {quality.name} ({quality.value})."
            )
        self.qualities.append(quality)

    def get_quality_count(self) -> int:
        """Return number of claimed qualities."""
        return len(self.qualities)

    def get_quality_percentage(self) -> float:
        """Return percentage of max possible (64)."""
        return (len(self.qualities) / 64) * 100
