"""
COMPOSITION PROTOCOL — Language as Vibration Routing (THE LAW)
==============================================================

"vāṇī tasya kā" — What is the speech of that One?

This protocol defines the interface for composing English output
from a Lotus __call__() response. The Lotus response IS the
Maha-vector — all computation is already done. Composition is
the final projection from vibration space to language space.

LOCATION: vibe_core.mahamantra.protocols._composition (THE LAW)
IMPLEMENTATION: vibe_core.mahamantra.adapters.composition (THE BRIDGE)
SUBSTRATE: vibe_core.mahamantra.substrate.language/ (Pure Math)

PROTOCOL PRINCIPLES:
====================
- No concrete implementations (Protocol only)
- No Any types
- All constants derived from SSOT (_seed.py)
- Composition consumes lotus_response dict — zero coupling to Lotus internals
- Output length driven by context (quarter/prana), NOT hardcoded caps
"""

from __future__ import annotations

from typing import Dict, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import PARAMPARA

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x3a5e7c13"

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


@runtime_checkable
class CompositionProtocol(Protocol):
    """Protocol for composing English output from a Lotus response.

    The Lotus __call__() has already run the full NavaBhakti pipeline.
    The lotus_response dict carries the complete Maha-vector:
        vibration, smaranam, verse, guardian, quarter, guna, diw, antaranga.

    A CompositionProtocol implementation reads this vector and projects
    it into language space via syllable alignment on the mantra grid.
    """

    def compose(self, lotus_response: Dict, input_text: str) -> str:
        """Compose English output from a Lotus response.

        Args:
            lotus_response: The complete dict from MahamantraLotus.__call__().
            input_text: The original input text.

        Returns:
            Composed English string. Deterministic for same lotus_response.
        """
        ...

    @property
    def compositions(self) -> int:
        """Total number of compositions performed."""
        ...

    @property
    def last_context(self) -> Dict:
        """Context extracted from the last composition (for observability)."""
        ...


@runtime_checkable
class CompositionScorerProtocol(Protocol):
    """Protocol for a single scoring dimension in the ranking pipeline.

    Each scorer takes a word candidate dict and returns a float score.
    Scorers are composable — the adapter combines them additively.
    """

    @property
    def name(self) -> str:
        """Scorer identity (e.g. 'prana', 'rhythm', 'semantic', 'mode')."""
        ...

    def score(self, item: Dict, seed: int, **kwargs) -> float:
        """Score a word candidate.

        Args:
            item: Pool item dict with keys: sanskrit, meaning, score,
                  packed_hex, first_coord, coords, source.
            seed: The vibration seed from lotus_response.
            **kwargs: Scorer-specific context (antaranga, rhythm, etc.)

        Returns:
            Score contribution. Same scale as other scorers.
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CompositionProtocol",
    "CompositionScorerProtocol",
]
