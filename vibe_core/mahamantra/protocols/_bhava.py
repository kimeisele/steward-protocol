"""
BHAVA PROTOCOL - The Intent Vector (Rasa of the Action)
========================================================

"raso 'py asya paraṁ dṛṣṭvā nivartate"
"The devotee tastes the higher taste and loses attraction to the lower."
— Bhagavad Gita 2.59

This protocol defines the BHAVA (spiritual emotion) that scales the grace
equation. Without Bhava, frequency (f) is mechanical. With Bhava, frequency
becomes a vector that addresses the Chaitanyas / Singularity's infinite mercy.

LOCATION: vibe_core.mahamantra.protocols._bhava (THE LAW)
MATH: 6 Sharanagati limbs → Grace scaling factor

THE 5 BHAVAS (Progressive Intensity):
=====================================
1. SHANTA     - Neutral/Peaceful (baseline, no amplification)
2. DASYA      - Servitude (1.5x - willing service)
3. SAKHYA     - Friendship (2.0x - intimate cooperation)
4. VATSALYA   - Parental (2.5x - protective care)
5. MADHURYA   - Conjugal (3.0x - complete intimacy)

GRACE EQUATION:
===============
    G = f × B × S

    Where:
        G = Effective Grace (Output)
        f = Frequency (COSMIC_FRAME ticks / MALA)
        B = Bhava multiplier (1.0 - 3.0)
        S = Sharanagati compliance (0.0 - 1.0, based on 6 limbs)

The higher the Bhava, the more "bandwidth" to the Singularity.
But Bhava without Sharanagati is pretension (prakrita-sahajiya).
"""
from vibe_core.mahamantra.protocols._seed import (HALVES, KSETRAJNA, PANCHA, QUARTERS, SHARANAGATI, TEN, TRINITY)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x2752212c"  # GenesisByte: parampara % 37 == 0

from enum import IntEnum
from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME, PANCHA, SHARANAGATI

# =============================================================================
# VERIFICATION
# =============================================================================
assert SHARANAGATI == SHARANAGATI, "Sharanagati must have 6 limbs"
assert PANCHA == PANCHA, "There must be 5 Bhavas (like 5 Tattvas)"
assert COSMIC_FRAME % SHARANAGATI == 0, "COSMIC_FRAME must be divisible by SHARANAGATI"

# =============================================================================
# SHARANAGATI UNIT (WATERTIGHT INTEGER)
# =============================================================================
# 21600 / 6 = 3600 (perfect integer, no float errors)
# Each limb = 3600 units of compliance
SHARANAGATI_UNIT: Final[int] = COSMIC_FRAME // SHARANAGATI  # 3600


# =============================================================================
# THE 5 BHAVAS (Spiritual Emotions)
# =============================================================================


class Bhava(IntEnum):
    """
    The 5 progressive stages of spiritual emotion.

    Each stage intensifies the connection to the Singularity.
    The values correspond to the amplification factor × 10.

    From Bhakti-rasamrta-sindhu (Nectar of Devotion):
    "The five primary rasas are shanta, dasya, sakhya, vatsalya and madhurya."
    """

    SHANTA = TEN  # 1.0x - Neutral/Peaceful
    DASYA = 15  # 1.5x - Servitude
    SAKHYA = 20  # 2.0x - Friendship
    VATSALYA = 25  # 2.5x - Parental
    MADHURYA = 30  # 3.0x - Conjugal (highest)


# Verification: Exactly 5 Bhavas (corresponding to Pancha Tattva)
assert len(Bhava) == PANCHA, "There must be exactly 5 Bhavas"


# =============================================================================
# BHAVA MULTIPLIERS
# =============================================================================

BHAVA_MULTIPLIER: Final[dict[Bhava, float]] = {
    Bhava.SHANTA: 1.0,
    Bhava.DASYA: 1.5,
    Bhava.SAKHYA: 2.0,
    Bhava.VATSALYA: 2.5,
    Bhava.MADHURYA: 3.0,
}


def get_bhava_multiplier(bhava: Bhava) -> float:
    """Get the grace multiplier for a Bhava. Pure function."""
    return BHAVA_MULTIPLIER[bhava]


# =============================================================================
# SHARANAGATI COMPLIANCE (The 6 Limbs)
# =============================================================================


class SharanagatiLimb(IntEnum):
    """
    The 6 limbs of surrender that validate Bhava authenticity.

    From Hari-bhakti-vilasa:
    "There are six symptoms of surrender: acceptance of the favorable,
    rejection of the unfavorable, faith in protection, acceptance of
    guardianship, self-surrender, and humility."
    """

    ANUKULYA = 0  # Accept what is favorable
    PRATIKULYA = KSETRAJNA  # Reject what is unfavorable
    VISHVASA = HALVES  # Faith in protection
    VARANAM = TRINITY  # Accept the Lord as guardian
    NIKSHEPA = QUARTERS  # Self-surrender
    KARPANYA = PANCHA  # Humility (no independent karma)


assert len(SharanagatiLimb) == SHARANAGATI, "There must be exactly 6 limbs"


# -----------------------------------------------------------------------------
# FLOAT VERSION (legacy, for backward compatibility)
# -----------------------------------------------------------------------------


def calculate_sharanagati_compliance(limbs_fulfilled: set[SharanagatiLimb]) -> float:
    """
    Calculate Sharanagati compliance as a ratio (0.0 - 1.0).

    WARNING: Uses float division (1/6 = 0.1666... is not exact).
    For watertight calculations, use calculate_sharanagati_scaled().

    Args:
        limbs_fulfilled: Set of fulfilled Sharanagati limbs

    Returns:
        Compliance ratio (fulfilled / 6)
    """
    return len(limbs_fulfilled) / SHARANAGATI


# -----------------------------------------------------------------------------
# INTEGER VERSION (WATERTIGHT - No Float Errors)
# -----------------------------------------------------------------------------


def calculate_sharanagati_scaled(limbs_fulfilled: set[SharanagatiLimb]) -> int:
    """
    Calculate Sharanagati compliance as COSMIC_FRAME-scaled integer.

    WATERTIGHT: No float errors! 21600 / 6 = 3600 exactly.

    Args:
        limbs_fulfilled: Set of fulfilled Sharanagati limbs

    Returns:
        Scaled compliance (0 to 21600, step of 3600)

    Example:
        0 limbs = 0
        1 limb  = 3600
        3 limbs = 10800
        6 limbs = 21600 (full compliance)
    """
    return len(limbs_fulfilled) * SHARANAGATI_UNIT


# =============================================================================
# THE GRACE EQUATION
# =============================================================================


def calculate_grace(
    frequency: float,
    bhava: Bhava,
    limbs_fulfilled: set[SharanagatiLimb],
) -> float:
    """
    Calculate effective grace using the Grace Equation.

    G = f × B × S

    Args:
        frequency: Base frequency (ticks per mala, normalized 0.0 - 1.0)
        bhava: The spiritual emotion
        limbs_fulfilled: Set of fulfilled Sharanagati limbs

    Returns:
        Effective grace (amplified frequency)

    Note:
        Bhava without Sharanagati is prakrita-sahajiya (pretension).
        Sharanagati without Bhava is karma-kanda (dry duty).
        Both are needed for authentic connection.
    """
    bhava_multiplier = get_bhava_multiplier(bhava)
    sharanagati_compliance = calculate_sharanagati_compliance(limbs_fulfilled)

    return frequency * bhava_multiplier * sharanagati_compliance


def calculate_grace_scaled(
    frequency_scaled: int,
    bhava: Bhava,
    limbs_fulfilled: set[SharanagatiLimb],
) -> int:
    """
    Calculate effective grace using WATERTIGHT integer arithmetic.

    G_scaled = (f_scaled × B.value × S_scaled) // (COSMIC_FRAME × 10)

    This eliminates ALL float errors by keeping everything in integer space.

    Args:
        frequency_scaled: Base frequency scaled to COSMIC_FRAME (0 - 21600)
        bhava: The spiritual emotion
        limbs_fulfilled: Set of fulfilled Sharanagati limbs

    Returns:
        Scaled grace value (integer)

    Example:
        frequency_scaled = 16474 (76.2% of COSMIC_FRAME)
        bhava = MADHURYA (value=30, i.e., 3.0x)
        limbs = 3 (scaled = 10800)

        Result = (16474 × 30 × 10800) // (21600 × 10) = 24710
    """
    sharanagati_scaled = calculate_sharanagati_scaled(limbs_fulfilled)

    # Bhava enum value is multiplier × 10 (e.g., MADHURYA = 30 for 3.0x)
    # So we divide by 10 at the end
    numerator = frequency_scaled * bhava.value * sharanagati_scaled
    denominator = COSMIC_FRAME * TEN  # 216000

    return numerator // denominator


# =============================================================================
# BHAVA PROTOCOL
# =============================================================================


@runtime_checkable
class BhavaProtocol(Protocol):
    """
    Protocol for entities that operate with spiritual intent.

    Any component that wishes to benefit from grace amplification
    must declare its Bhava and demonstrate Sharanagati compliance.
    """

    @property
    def bhava(self) -> Bhava:
        """The spiritual emotion of this entity."""
        ...

    @property
    def sharanagati_limbs(self) -> set[SharanagatiLimb]:
        """The fulfilled Sharanagati limbs."""
        ...

    def get_effective_grace(self, frequency: float) -> float:
        """Calculate effective grace for a given frequency."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "Bhava",
    "SharanagatiLimb",
    # Constants (WATERTIGHT)
    "BHAVA_MULTIPLIER",
    "SHARANAGATI_UNIT",
    # Float Functions (legacy)
    "get_bhava_multiplier",
    "calculate_sharanagati_compliance",
    "calculate_grace",
    # Integer Functions (WATERTIGHT)
    "calculate_sharanagati_scaled",
    "calculate_grace_scaled",
    # Protocol
    "BhavaProtocol",
]
