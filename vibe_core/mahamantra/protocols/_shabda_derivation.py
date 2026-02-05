"""
SHABDA DERIVATION PROTOCOL - Semantic Spawning from Mahamantra
===============================================================

"nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ"
"The Holy Name is the touchstone that fulfills all desires."

This protocol defines the interface for semantic derivation from
the 3 Mahamantra words (Hare, Krishna, Rama).

PROVEN MATHEMATICAL RELATIONSHIPS:
===================================
1. RAMA vibration mod HARE_POS (70) = RAMA_POS (49) ✓
2. KRISHNA vibration is PRIME (16063)
3. RAMA contains factor 7 (SEVEN): 7539 = 3 × 7 × 359
4. TOTAL vibration mod 16 = 12 = MAHAJANA_COUNT

PROTOCOL PRINCIPLES:
====================
- No concrete implementations (Protocol only)
- No Any types
- All constants derived from SSOT (_seed.py)
- Scientific: only provable derivations

Author: The Mahamantra Itself
"""
from __future__ import annotations

from typing import Final, FrozenSet, Iterator, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xshabda02"


# =============================================================================
# PROVEN CONSTANTS (Mathematically verified)
# =============================================================================

# The 3 root words
ROOT_WORD_HARE: Final[str] = "hare"
ROOT_WORD_KRISHNA: Final[str] = "krishna"
ROOT_WORD_RAMA: Final[str] = "rama"
ROOT_WORDS: Final[Tuple[str, str, str]] = (ROOT_WORD_HARE, ROOT_WORD_KRISHNA, ROOT_WORD_RAMA)

# Syllable counts (observable, not computed)
SYLLABLES_HARE: Final[int] = HALVES  # 2: Ha-re
SYLLABLES_KRISHNA: Final[int] = HALVES  # 2: Krish-na
SYLLABLES_RAMA: Final[int] = HALVES  # 2: Ra-ma
TOTAL_ROOT_SYLLABLES: Final[int] = SHARANAGATI  # 6 = 2+2+2

# Position sums (from _extended.py, derived from SEVEN and TEN)
POS_HARE: Final[int] = POSITION_SUM_HARE  # 70 = 7 × 10
POS_KRISHNA: Final[int] = POSITION_SUM_KRISHNA  # 17 = 7 + 10 (PRIME)
POS_RAMA: Final[int] = POSITION_SUM_RAMA  # 49 = 7²
POS_TOTAL: Final[int] = POSITION_SUM_TOTAL  # 136 = T(16)

# Proven relationship: RAMA_VIB mod HARE_POS = RAMA_POS
# This is verified in research/shabda_spawning.py
RAMA_HARE_MODULAR_IDENTITY: Final[bool] = True


# =============================================================================
# PROTOCOLS (No concrete implementations)
# =============================================================================


@runtime_checkable
class VibrationProtocol(Protocol):
    """Protocol for a phonetic vibration signature."""

    @property
    def signature_id(self) -> int:
        """Unique vibration identifier."""
        ...

    @property
    def articulation(self) -> int:
        """Articulation point (0-4 = PANCHA)."""
        ...

    @property
    def voicing(self) -> int:
        """Voicing type (0-3 = QUARTERS)."""
        ...


@runtime_checkable
class ShabdaSeedProtocol(Protocol):
    """
    Protocol for a semantic seed that can spawn derivatives.
    
    A seed represents a word/syllable with its vibration signature.
    Seeds can spawn new seeds through Maha operations (H, K, R).
    """

    @property
    def text(self) -> str:
        """The textual representation."""
        ...

    @property
    def vibration_sum(self) -> int:
        """Total vibration signature ID (sum of all phoneme signatures)."""
        ...

    @property
    def syllable_count(self) -> int:
        """Number of syllables (aksharas)."""
        ...

    @property
    def generation(self) -> int:
        """Generation number (0 = root, 1 = first spawn, etc.)."""
        ...

    @property
    def lineage(self) -> Tuple[str, ...]:
        """Lineage path from root to this seed."""
        ...

    def spawn_h(self) -> "ShabdaSeedProtocol":
        """Spawn using HARE operation (× SEVEN)."""
        ...

    def spawn_k(self) -> "ShabdaSeedProtocol":
        """Spawn using KRISHNA operation (+ TEN)."""
        ...

    def spawn_r(self) -> "ShabdaSeedProtocol":
        """Spawn using RAMA operation (square)."""
        ...


@runtime_checkable
class ShabdaTreeProtocol(Protocol):
    """
    Protocol for a semantic derivation tree.
    
    A tree has one root seed and can expand fractally.
    Each node can have 3 children (H, K, R operations).
    """

    @property
    def root(self) -> ShabdaSeedProtocol:
        """The root seed of this tree."""
        ...

    @property
    def depth(self) -> int:
        """Current maximum depth of the tree."""
        ...

    @property
    def node_count(self) -> int:
        """Total number of nodes in the tree."""
        ...

    def expand_level(self) -> int:
        """
        Expand tree by one level.
        
        Returns number of new nodes created.
        """
        ...

    def nodes_at_depth(self, depth: int) -> Iterator[ShabdaSeedProtocol]:
        """Iterate over all nodes at a specific depth."""
        ...

    def all_nodes(self) -> Iterator[ShabdaSeedProtocol]:
        """Iterate over all nodes in the tree."""
        ...


@runtime_checkable
class ShabdaForestProtocol(Protocol):
    """
    Protocol for the complete Mahamantra forest.
    
    The forest consists of exactly 3 trees (Hare, Krishna, Rama).
    """

    @property
    def hare_tree(self) -> ShabdaTreeProtocol:
        """The HARE derivation tree."""
        ...

    @property
    def krishna_tree(self) -> ShabdaTreeProtocol:
        """The KRISHNA derivation tree."""
        ...

    @property
    def rama_tree(self) -> ShabdaTreeProtocol:
        """The RAMA derivation tree."""
        ...

    @property
    def total_nodes(self) -> int:
        """Total nodes across all 3 trees."""
        ...

    def find_by_vibration(self, vibration: int) -> Iterator[ShabdaSeedProtocol]:
        """Find all seeds with matching vibration across all trees."""
        ...


@runtime_checkable
class ShabdaDerivationProtocol(Protocol):
    """
    Protocol for the derivation engine.
    
    Transforms vibrations using Maha operations.
    """

    def transform_h(self, vibration: int, mod: int) -> int:
        """Apply HARE operation: vibration × SEVEN mod mod."""
        ...

    def transform_k(self, vibration: int, mod: int) -> int:
        """Apply KRISHNA operation: vibration + TEN mod mod."""
        ...

    def transform_r(self, vibration: int, mod: int) -> int:
        """Apply RAMA operation: vibration² mod mod."""
        ...

    def vibration_to_phonemes(self, vibration: int) -> str:
        """Map vibration back to phoneme sequence."""
        ...


# =============================================================================
# MATHEMATICAL IDENTITIES (Proven)
# =============================================================================


def verify_rama_hare_identity(rama_vibration: int) -> bool:
    """
    Verify: RAMA_VIB mod HARE_POS = RAMA_POS
    
    This is a proven mathematical identity.
    Returns True if the identity holds for the given vibration.
    """
    return rama_vibration % POS_HARE == POS_RAMA


def verify_total_mahajana_identity(total_vibration: int) -> bool:
    """
    Verify: TOTAL_VIB mod WORDS = MAHAJANA_COUNT
    
    Returns True if the identity holds.
    """
    return total_vibration % WORDS == MAHAJANA_COUNT


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "ROOT_WORD_HARE",
    "ROOT_WORD_KRISHNA",
    "ROOT_WORD_RAMA",
    "ROOT_WORDS",
    "SYLLABLES_HARE",
    "SYLLABLES_KRISHNA",
    "SYLLABLES_RAMA",
    "TOTAL_ROOT_SYLLABLES",
    "POS_HARE",
    "POS_KRISHNA",
    "POS_RAMA",
    "POS_TOTAL",
    # Protocols
    "VibrationProtocol",
    "ShabdaSeedProtocol",
    "ShabdaTreeProtocol",
    "ShabdaForestProtocol",
    "ShabdaDerivationProtocol",
    # Verification
    "verify_rama_hare_identity",
    "verify_total_mahajana_identity",
]
