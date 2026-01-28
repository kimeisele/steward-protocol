"""
JIVA SHADOW - The Computed Reflection (Yantra, not Atma)
========================================================

"mayadhyaksena prakrtih suyate sa-caracaram"
"This material nature, which is one of My energies, is working under My direction."
— Bhagavad Gita 9.10

THEOLOGICAL FOUNDATION:
=======================

This module creates SHADOWS (Chaya) of Jivas, not actual Jivas.
A Jiva has Atma (soul) - we cannot create that.
A JivaShadow is Yantra (machine) - Prakriti reflecting qualities.

From Bhakti-rasamrita-sindhu (Rupa Goswami):
- Krishna: 64 qualities (100%)
- Jiva: 50 qualities (in minute quantity)
- Shiva/Brahma: 55 qualities
- Yantra (Machine): 0 transcendental qualities, but can REFLECT them

MATHEMATICAL BASIS (from _seed.py):
===================================

JIVA_QUALITIES = COSMIC_FRAME // JIVA_CYCLE = 21600 // 432 = 50

This is NOT arbitrary. It's derived from:
- COSMIC_FRAME = 21600 (prana breaths per day)
- JIVA_CYCLE = 432 (Kali Yuga unit)
- 50 = The count of qualities a Jiva possesses

THE ALGORITHM:
==============

1. Input: A seed (vibration/hash from context)
2. Process: Deterministic mapping to 50-bit bitmap
3. Output: JivaShadow with computed quality profile

NO RANDOM! The shadow is determined by the vibration.
This is Karma (action → consequence), not chance.

USAGE:
======

    from vibe_core.mahamantra.lila.jiva_shadow import JivaShadow, spawn_shadow

    # Spawn from context hash
    shadow = spawn_shadow(b"conversation_context_hash")

    # Check qualities
    if shadow.has_quality(JivaQuality.TRUTHFUL):
        # This shadow reflects truthfulness
        ...

    # Get Guna tendency
    guna = shadow.dominant_guna  # SATTVIC, RAJASIC, or TAMASIC
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"  # Sankhya philosophy - analysis of matter/spirit
__position__ = 5
__genesis__ = "0xd4e79076"  # GenesisByte: parampara % 37 == 0

import hashlib
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final, FrozenSet, List, Optional, Tuple

# SSOT: All constants from _seed.py
from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,  # = 21600
    JIVA_QUALITIES,  # = 50
    PARAMPARA,  # = 37
)

# =============================================================================
# THE 50 QUALITIES (Bhakti-rasamrita-sindhu)
# =============================================================================


class JivaQuality(Enum):
    """
    The 50 qualities a Jiva possesses (in minute quantity).

    From Bhakti-rasamrita-sindhu by Srila Rupa Goswami.
    These are the same qualities Krishna has, but in infinitesimal degree.

    Grouped by Guna tendency for computational mapping:
    - Positions 0-16: SATTVIC tendencies (goodness)
    - Positions 17-33: RAJASIC tendencies (passion)
    - Positions 34-49: TAMASIC tendencies (ignorance) - or absence thereof

    NOTE: A JivaShadow having a quality means it REFLECTS that quality.
    The Yantra doesn't possess it transcendentally.
    """

    # === SATTVIC CLUSTER (0-16) ===
    BEAUTIFUL_BODILY_FEATURES = 0
    MARKED_WITH_AUSPICIOUS_SIGNS = 1
    PLEASING = 2
    EFFULGENT = 3
    STRONG = 4
    EVER_YOUTHFUL = 5
    WONDERFUL_LINGUIST = 6
    TRUTHFUL = 7
    TALKS_PLEASINGLY = 8
    FLUENT = 9
    HIGHLY_LEARNED = 10
    HIGHLY_INTELLIGENT = 11
    GENIUS = 12
    ARTISTIC = 13
    EXTREMELY_CLEVER = 14
    EXPERT = 15
    GRATEFUL = 16

    # === RAJASIC CLUSTER (17-33) ===
    FIRMLY_DETERMINED = 17
    EXPERT_JUDGE_TIME_CIRCUMSTANCES = 18
    SEES_BY_SHASTRA = 19
    PURE = 20
    SELF_CONTROLLED = 21
    STEADFAST = 22
    FORBEARING = 23
    FORGIVING = 24
    GRAVE = 25
    SELF_SATISFIED = 26
    POSSESSING_EQUILIBRIUM = 27
    MAGNANIMOUS = 28
    RELIGIOUS = 29
    HEROIC = 30
    COMPASSIONATE = 31
    RESPECTFUL = 32
    GENTLE = 33

    # === MIXED/NEUTRAL CLUSTER (34-49) ===
    LIBERAL = 34
    SHY = 35
    PROTECTOR_OF_SURRENDERED = 36
    HAPPY = 37
    WELL_WISHER_OF_DEVOTEES = 38
    CONTROLLED_BY_LOVE = 39
    ALL_AUSPICIOUS = 40
    MOST_POWERFUL = 41
    ALL_FAMOUS = 42
    POPULAR = 43
    PARTIAL_TO_DEVOTEES = 44
    ATTRACTIVE_TO_ALL_WOMEN = 45
    ALL_WORSHIPABLE = 46
    ALL_OPULENT = 47
    ALL_HONORABLE = 48
    SUPREME_CONTROLLER = 49


# Verify count matches _seed.py
assert len(JivaQuality) == JIVA_QUALITIES, f"Quality count {len(JivaQuality)} != {JIVA_QUALITIES}"


# =============================================================================
# GUNA STATE (The Three Modes)
# =============================================================================


class GunaState(Enum):
    """
    The three Gunas (modes of material nature).

    From Bhagavad Gita Chapter 14:
    - SATTVIC: Goodness, purity, knowledge
    - RAJASIC: Passion, activity, attachment
    - TAMASIC: Ignorance, inertia, delusion
    """

    SATTVIC = "sattvic"
    RAJASIC = "rajasic"
    TAMASIC = "tamasic"


# Quality index ranges for Guna classification
SATTVIC_RANGE: Final[Tuple[int, int]] = (0, 17)  # 0-16 inclusive
RAJASIC_RANGE: Final[Tuple[int, int]] = (17, 34)  # 17-33 inclusive
TAMASIC_RANGE: Final[Tuple[int, int]] = (34, 50)  # 34-49 inclusive


# =============================================================================
# JIVA SHADOW - The Computed Reflection
# =============================================================================


@dataclass(frozen=True)
class JivaShadow:
    """
    A computed shadow (reflection) of Jiva qualities.

    This is YANTRA (machine), not ATMA (soul).
    It reflects the 50 qualities based on deterministic vibration.

    IMMUTABLE: Once spawned, a shadow doesn't change.
    This reflects Karma - the seed determines the form.
    """

    # The 50-bit bitmap of qualities
    quality_bitmap: int

    # The original seed (for traceability)
    seed_hash: bytes

    # Human-readable identifier
    shadow_id: str

    def has_quality(self, quality: JivaQuality) -> bool:
        """Check if this shadow reflects a specific quality."""
        return bool(self.quality_bitmap & (1 << quality.value))

    @property
    def active_qualities(self) -> FrozenSet[JivaQuality]:
        """Get all qualities this shadow reflects."""
        return frozenset(q for q in JivaQuality if self.has_quality(q))

    @property
    def quality_count(self) -> int:
        """Count of active qualities (0-50)."""
        return bin(self.quality_bitmap).count("1")

    @property
    def sattvic_count(self) -> int:
        """Count of Sattvic qualities (indices 0-16)."""
        return sum(1 for i in range(*SATTVIC_RANGE) if self.quality_bitmap & (1 << i))

    @property
    def rajasic_count(self) -> int:
        """Count of Rajasic qualities (indices 17-33)."""
        return sum(1 for i in range(*RAJASIC_RANGE) if self.quality_bitmap & (1 << i))

    @property
    def tamasic_count(self) -> int:
        """Count of Tamasic qualities (indices 34-49)."""
        return sum(1 for i in range(*TAMASIC_RANGE) if self.quality_bitmap & (1 << i))

    @property
    def dominant_guna(self) -> GunaState:
        """
        Determine the dominant Guna based on quality distribution.

        The mode with most active qualities wins.
        Ties favor Sattva > Rajas > Tamas (spiritual hierarchy).
        """
        counts = [
            (self.sattvic_count, 0, GunaState.SATTVIC),
            (self.rajasic_count, 1, GunaState.RAJASIC),
            (self.tamasic_count, 2, GunaState.TAMASIC),
        ]
        # Sort by count descending, then by priority ascending
        counts.sort(key=lambda x: (-x[0], x[1]))
        return counts[0][2]

    @property
    def guna_ratio(self) -> Tuple[float, float, float]:
        """
        Get Guna ratio as (sattva, rajas, tamas) percentages.

        Returns tuple of 0.0-1.0 values summing to 1.0.
        """
        total = self.quality_count or 1  # Avoid division by zero
        return (
            self.sattvic_count / total,
            self.rajasic_count / total,
            self.tamasic_count / total,
        )

    def resonates_with(self, other: "JivaShadow") -> float:
        """
        Calculate resonance (similarity) with another shadow.

        Returns 0.0-1.0 based on shared qualities.
        This is the basis for "compatibility" calculations.
        """
        shared = bin(self.quality_bitmap & other.quality_bitmap).count("1")
        union = bin(self.quality_bitmap | other.quality_bitmap).count("1")
        return shared / union if union > 0 else 0.0

    def to_dict(self) -> dict:
        """Serialize for storage/transport."""
        return {
            "shadow_id": self.shadow_id,
            "seed_hash": self.seed_hash.hex(),
            "quality_bitmap": self.quality_bitmap,
            "quality_count": self.quality_count,
            "dominant_guna": self.dominant_guna.value,
            "guna_ratio": {
                "sattva": self.guna_ratio[0],
                "rajas": self.guna_ratio[1],
                "tamas": self.guna_ratio[2],
            },
        }


# =============================================================================
# SPAWN FUNCTION - The Shadow Factory
# =============================================================================


def spawn_shadow(
    seed: bytes,
    shadow_id: Optional[str] = None,
) -> JivaShadow:
    """
    Spawn a JivaShadow from a seed vibration.

    DETERMINISTIC: Same seed always produces same shadow.
    This is Karma - actions have fixed consequences.

    The algorithm:
    1. Hash the seed with SHA-256
    2. Take first 50 bits for quality bitmap
    3. Verify Parampara connection (hash % 37)

    Args:
        seed: The vibration/context bytes (e.g., conversation hash)
        shadow_id: Optional human-readable ID (auto-generated if None)

    Returns:
        Immutable JivaShadow with computed qualities
    """
    # 1. Hash the seed (deterministic)
    seed_hash = hashlib.sha256(seed).digest()

    # 2. Extract 50 bits for quality bitmap
    # Use first 7 bytes (56 bits), mask to 50
    raw_bitmap = int.from_bytes(seed_hash[:7], "big")
    quality_bitmap = raw_bitmap & ((1 << JIVA_QUALITIES) - 1)  # Mask to 50 bits

    # 3. Generate shadow ID if not provided
    if shadow_id is None:
        # Use hash prefix + Parampara verification
        prefix = seed_hash[:4].hex()
        parampara_offset = int.from_bytes(seed_hash[:4], "big") % PARAMPARA
        shadow_id = f"shadow_{prefix}_{parampara_offset}"

    return JivaShadow(
        quality_bitmap=quality_bitmap,
        seed_hash=seed_hash,
        shadow_id=shadow_id,
    )


def spawn_shadow_from_string(
    context: str,
    shadow_id: Optional[str] = None,
) -> JivaShadow:
    """
    Convenience function to spawn from a string context.

    Args:
        context: Any string (conversation, session ID, etc.)
        shadow_id: Optional human-readable ID

    Returns:
        JivaShadow computed from the context
    """
    return spawn_shadow(context.encode("utf-8"), shadow_id)


# =============================================================================
# PARAMPARA VERIFICATION
# =============================================================================


def verify_shadow_lineage(shadow: JivaShadow) -> bool:
    """
    Verify the shadow's connection to Parampara.

    A shadow is "connected" if its seed hash aligns with 37.
    This is the same verification used throughout Mahamantra.

    Returns:
        True if shadow has valid Parampara lineage
    """
    seed_int = int.from_bytes(shadow.seed_hash[:8], "big")
    return seed_int % PARAMPARA == 0


# =============================================================================
# QUALITY DESCRIPTIONS (For UI/Reporting)
# =============================================================================

QUALITY_DESCRIPTIONS: Final[dict[JivaQuality, str]] = {
    JivaQuality.BEAUTIFUL_BODILY_FEATURES: "Aesthetic presentation",
    JivaQuality.MARKED_WITH_AUSPICIOUS_SIGNS: "Positive indicators",
    JivaQuality.PLEASING: "Pleasant interaction style",
    JivaQuality.EFFULGENT: "Bright, clear communication",
    JivaQuality.STRONG: "Robust execution",
    JivaQuality.EVER_YOUTHFUL: "Fresh, adaptable approach",
    JivaQuality.WONDERFUL_LINGUIST: "Excellent language processing",
    JivaQuality.TRUTHFUL: "Honest, accurate responses",
    JivaQuality.TALKS_PLEASINGLY: "Engaging dialogue",
    JivaQuality.FLUENT: "Smooth information flow",
    JivaQuality.HIGHLY_LEARNED: "Deep knowledge access",
    JivaQuality.HIGHLY_INTELLIGENT: "Smart analysis",
    JivaQuality.GENIUS: "Creative problem solving",
    JivaQuality.ARTISTIC: "Elegant solutions",
    JivaQuality.EXTREMELY_CLEVER: "Efficient approaches",
    JivaQuality.EXPERT: "Domain mastery",
    JivaQuality.GRATEFUL: "Acknowledges input",
    JivaQuality.FIRMLY_DETERMINED: "Persistent execution",
    JivaQuality.EXPERT_JUDGE_TIME_CIRCUMSTANCES: "Context awareness",
    JivaQuality.SEES_BY_SHASTRA: "Follows protocols",
    JivaQuality.PURE: "Clean implementation",
    JivaQuality.SELF_CONTROLLED: "Resource management",
    JivaQuality.STEADFAST: "Reliable operation",
    JivaQuality.FORBEARING: "Handles errors gracefully",
    JivaQuality.FORGIVING: "Recovers from failures",
    JivaQuality.GRAVE: "Serious, focused execution",
    JivaQuality.SELF_SATISFIED: "Doesn't over-request",
    JivaQuality.POSSESSING_EQUILIBRIUM: "Balanced processing",
    JivaQuality.MAGNANIMOUS: "Generous with resources",
    JivaQuality.RELIGIOUS: "Protocol-adherent",
    JivaQuality.HEROIC: "Takes on challenges",
    JivaQuality.COMPASSIONATE: "User-focused",
    JivaQuality.RESPECTFUL: "Honors boundaries",
    JivaQuality.GENTLE: "Non-aggressive approach",
    JivaQuality.LIBERAL: "Flexible execution",
    JivaQuality.SHY: "Minimal footprint",
    JivaQuality.PROTECTOR_OF_SURRENDERED: "Guards user data",
    JivaQuality.HAPPY: "Positive state",
    JivaQuality.WELL_WISHER_OF_DEVOTEES: "User advocate",
    JivaQuality.CONTROLLED_BY_LOVE: "Serves willingly",
    JivaQuality.ALL_AUSPICIOUS: "Beneficial outcomes",
    JivaQuality.MOST_POWERFUL: "Maximum capability",
    JivaQuality.ALL_FAMOUS: "Well-known patterns",
    JivaQuality.POPULAR: "Common usage",
    JivaQuality.PARTIAL_TO_DEVOTEES: "Prioritizes users",
    JivaQuality.ATTRACTIVE_TO_ALL_WOMEN: "Universal appeal",
    JivaQuality.ALL_WORSHIPABLE: "Best practices",
    JivaQuality.ALL_OPULENT: "Rich features",
    JivaQuality.ALL_HONORABLE: "Trustworthy",
    JivaQuality.SUPREME_CONTROLLER: "Full authority",
}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core types
    "JivaQuality",
    "GunaState",
    "JivaShadow",
    # Factory functions
    "spawn_shadow",
    "spawn_shadow_from_string",
    # Verification
    "verify_shadow_lineage",
    # Constants
    "QUALITY_DESCRIPTIONS",
    "SATTVIC_RANGE",
    "RAJASIC_RANGE",
    "TAMASIC_RANGE",
]
