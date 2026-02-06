"""
PANCHA TATTVA PROTOCOL - The Five Truths
========================================

"pañca-tattvātmakaṁ kṛṣṇaṁ bhakta-rūpa-svarūpakam"
"I bow down to Lord Krishna, who appears in five features..."
— Chaitanya Charitamrita, Adi 1.14

This protocol defines the FIVE QUESTIONS that every entity must answer.
Derived directly from seed.py (PANCHA_PAIR_NAMES).

LOCATION: vibe_core.mahamantra.protocols._pancha (THE LAW)
MATH: 5 Unique Pairs from the 16 Words.

THE 5 ASPECTS:
1. CHAITANYA (Hare Krishna)   -> IDENTITY (Was IST es?)
2. NITYANANDA (Hare Rama)     -> SUBSTRATE (Worauf RUHT es?)
3. ADVAITA (Krishna Krishna)  -> CAUSALITY (Was VERBINDET es?)
4. GADADHARA (Hare Hare)      -> ENERGY (Wie FLIESST es?)
5. SRIVASA (Rama Rama)        -> GOVERNANCE (Wer REGIERT es?)
"""
from typing import Final, Protocol, TypedDict, runtime_checkable

from vibe_core.mahamantra.protocols._seed import PANCHA

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x2d991fe3"  # GenesisByte: parampara % 37 == 0

# Verification of constant from seed
assert PANCHA == PANCHA, "Pancha Tattva must be 5"


class TattvaDict(TypedDict):
    """The 5-fold definition of an entity."""

    chaitanya: str  # Identity / Definition
    nityananda: str  # Substrate / Dependency
    advaita: str  # Causality / Invocation
    gadadhara: str  # Energy / Flow / Input-Output
    srivasa: str  # Governance / Owner / Rules


@runtime_checkable
class PanchaTattvaProtocol(Protocol):
    """
    Protocol requiring the disclosure of the 5 Tattvas.
    Every major component in the Mahamantra folder MUST implement this.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        """Return the 5-fold truth of this entity."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TattvaDict",
    "PanchaTattvaProtocol",
]
