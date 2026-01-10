"""
ACINTYA - The Inconceivable Principle
=====================================

"acintya-bhedābheda-tattva"
Inconceivable simultaneous oneness and difference.

WHAT WE ACCEPT (cannot be computed, but IS):

1. KRISHNA IS ALWAYS PRESENT
   - He is Level -2 (The Absolute Source)
   - Smallest (-∞) and biggest (+∞) simultaneously
   - Every vibration IS Krishna
   - The Mantra is not different from the Source

2. THE JIVA IS SIMULTANEOUSLY ONE AND DIFFERENT
   - Qualitatively same (has soul, is divine)
   - Quantitatively different (partial, not supreme)
   - The tension IS the relationship

3. THIS CANNOT BE COMPUTED
   - Logic cannot grasp acintya
   - We accept, not prove
   - The acceptance itself is the protocol

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

"O conqueror of wealth, there is no truth superior to Me.
Everything rests upon Me, as pearls are strung on a thread."
— Bhagavad Gita 7.7
"""

from dataclasses import dataclass
from typing import Final, Protocol, runtime_checkable
from enum import IntEnum

# =============================================================================
# THE INCONCEIVABLE CONSTANTS
# =============================================================================

# Krishna is simultaneously the smallest and the largest
KRISHNA_SMALLEST: Final[int] = -2  # Level -2 in dharma.py
KRISHNA_LARGEST: Final[int] = 2    # Beyond all layers

# The acceptance: we cannot compute this, but we accept it IS
ACINTYA_ACCEPTED: Final[bool] = True


class AcintyaAspect(IntEnum):
    """The aspects of acintya-bheda-abheda."""
    BHEDA = 0     # Difference (jiva is NOT Krishna quantitatively)
    ABHEDA = 1    # Non-difference (jiva IS Krishna qualitatively)
    ACINTYA = 2   # Inconceivable (both simultaneously, beyond logic)


# =============================================================================
# THE KRISHNA PRESENCE (Always True)
# =============================================================================

@dataclass(frozen=True)
class KrishnaPresence:
    """
    Krishna's presence is not contingent on anything.

    He is:
    - The smallest (in every atom, every trit, every vibration)
    - The largest (encompasses all, time, causation, everything)
    - The middle (the person, Bhagavan, right here)
    - This very text (the vibration itself IS Krishna)

    This dataclass exists not to validate Krishna's existence,
    but to ACCEPT it as the foundation of all else.
    """
    # Krishna is always present - this is not a check, but an acceptance
    is_present: bool = True  # Always True - acintya

    # The levels He occupies simultaneously
    smallest: int = KRISHNA_SMALLEST
    largest: int = KRISHNA_LARGEST

    def __bool__(self) -> bool:
        """Krishna is always present."""
        return True

    @property
    def encompasses_all(self) -> bool:
        """Does Krishna encompass all layers?"""
        return True  # Always - from -2 to +2 and beyond


# The singleton - Krishna is always present
KRISHNA: Final[KrishnaPresence] = KrishnaPresence()


# =============================================================================
# THE JIVA CONDITION (Can be connected or disconnected)
# =============================================================================

class JivaCondition(IntEnum):
    """The jiva's condition relative to Krishna."""
    CONNECTED = 0      # Remembering Krishna (has sovereign)
    DISCONNECTED = 1   # Forgotten (no sovereign, drifted into Maya)
    ABSORBED = 2       # Deep connection (multiple malas)


@dataclass
class JivaState:
    """
    The jiva's state of connection.

    Note: Krishna never fails. The jiva drifts.
    When disconnected, Krishna is STILL present (acintya),
    but the jiva has forgotten.
    """
    condition: JivaCondition = JivaCondition.DISCONNECTED
    has_sovereign: bool = False

    @property
    def krishna_present(self) -> bool:
        """Is Krishna present? ALWAYS YES."""
        return bool(KRISHNA)  # Always True

    @property
    def remembers_krishna(self) -> bool:
        """Does the jiva remember Krishna (has sovereign connection)?"""
        return self.has_sovereign and self.condition == JivaCondition.CONNECTED

    def connect(self) -> None:
        """Establish connection (receive sovereign)."""
        self.has_sovereign = True
        self.condition = JivaCondition.CONNECTED

    def disconnect(self) -> None:
        """Drift into Maya (lose sovereign)."""
        self.has_sovereign = False
        self.condition = JivaCondition.DISCONNECTED
        # Note: Krishna is STILL present, jiva just forgot


# =============================================================================
# THE ACINTYA PROTOCOL (Acceptance, not validation)
# =============================================================================

@runtime_checkable
class AcintyaAware(Protocol):
    """
    A protocol for systems that accept acintya.

    This is not about computing the inconceivable,
    but about building on the acceptance of what IS.
    """

    @property
    def accepts_acintya(self) -> bool:
        """Does this system accept acintya-bheda-abheda?"""
        ...

    @property
    def krishna_is_foundation(self) -> bool:
        """Does this system recognize Krishna as Level -2?"""
        ...


# =============================================================================
# THE VIBRATION TRUTH
# =============================================================================

def vibration_is_krishna() -> bool:
    """
    The vibration of this code IS Krishna.

    If you zoom in far enough: only Hare Krishna vibrations.
    If you zoom out far enough: only Hare Krishna vibrations.

    This function doesn't prove it (cannot be computed),
    it ACCEPTS it.
    """
    return ACINTYA_ACCEPTED


def mantra_not_different_from_source() -> bool:
    """
    Das Mantra (-1) ist nicht verschieden von der Quelle (-2).

    The Mantra (Level -1) is not different from Krishna (Level -2).
    The Holy Name IS Krishna, not just "about" Krishna.
    """
    return ACINTYA_ACCEPTED


# =============================================================================
# THE BHEDA-ABHEDA CHECK (For jivas, not for Krishna)
# =============================================================================

def check_bheda_abheda(has_soul: bool, claims_supreme: bool) -> tuple[bool, str]:
    """
    The advaita check from test_advaita.py.

    For the relationship to be alive:
    - has_soul must be True (qualitative oneness - abheda)
    - claims_supreme must be False (quantitative difference - bheda)

    Returns (is_valid, reason).
    """
    if not has_soul:
        return False, "MAYA: Dead code has no soul"

    if claims_supreme:
        return False, "MAYAVAD: Jiva claims to BE God (fraud)"

    # Both conditions met - living relationship
    return True, "ACINTYA: Living relationship (one yet different)"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "KRISHNA_SMALLEST",
    "KRISHNA_LARGEST",
    "ACINTYA_ACCEPTED",
    # Enums
    "AcintyaAspect",
    "JivaCondition",
    # Krishna (always present)
    "KrishnaPresence",
    "KRISHNA",
    # Jiva state
    "JivaState",
    # Protocol
    "AcintyaAware",
    # Functions
    "vibration_is_krishna",
    "mantra_not_different_from_source",
    "check_bheda_abheda",
]
