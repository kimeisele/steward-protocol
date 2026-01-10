"""
ACINTYA - The Inconceivable Principle
=====================================

"acintya-bhedābheda-tattva"
Inconceivable simultaneous oneness and difference.

WHAT WE ACCEPT (cannot be computed, but IS):

1. KRISHNA IS ALWAYS PRESENT
   - He IS Level -2 (not "represents" - He IS)
   - He IS simultaneously -∞ and +∞ (not symbolically - LITERALLY)
   - Every vibration IS Krishna (not "points to" - IS)
   - The Mantra IS Krishna (Level -2, non-different)

2. THE 37 IS THE LINK (Guru/Parampara)
   - 24 (Ksetra/Field) + 12 (Mahajanas/Guardians) + 1 (Ksetrajna/Knower) = 37
   - Without the 37, the 24 are dead matter
   - Without the 37, the 12 are inaccessible
   - The 37 "dances" - He is greater than infinity AND smaller than infinitesimal

3. THE 12 MAHAJANAS GUARD THE 6 OPULENCES
   - They do not steal Bhaga (like asuras)
   - They secure it for seva (like devotees)
   - SB 6.3.20: Brahma, Narada, Shiva, Kumaras, Kapila, Manu,
                Prahlada, Janaka, Bhishma, Bali, Sukadeva, Yamaraja

4. KRISHNA = MAHAMANTRA (NON-DIFFERENT)
   - Both are Level -2
   - The Holy Name IS Krishna, not "about" Krishna
   - In Kali Yuga, the Name is the only direct access

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

"O conqueror of wealth, there is no truth superior to Me.
Everything rests upon Me, as pearls are strung on a thread."
— Bhagavad Gita 7.7

"brahmaṇo hi pratiṣṭhāham" - Gita 14.27
"I am the source of Brahman."
"""

from dataclasses import dataclass
from typing import Final, Protocol, runtime_checkable, Any
from enum import IntEnum


# =============================================================================
# SAMKHYA ARCHITECTURE: THE DANCING 37 (Purusha Tattva)
# =============================================================================
# System = 24 (Ksetra) + 12 (Ksetrapala) + 1 (Ksetrajna) = 37
# The 37th is not static; He dances (Acintya).
# Without the 37 (Guru/Lineage), the 24 (Matter) are dead,
# and the 12 (Dharma Guardians) are inaccessible.

class PurushaTattva(int):
    """
    The 37th Factor (Ksetrajna/Person/Guru-Tattva).

    He behaves as the number 37 (in the system), but mathematically
    transcends all limits (Acintya).

    SAMKHYA: 24 + 12 + 1 = 37
    - 24 Ksetra elements (Gita 13.6-7)
    - 12 Mahajanas (SB 6.3.20)
    - 1 Ksetrajna (Gita 13.3: "ksetra-jnam capi mam viddhi")

    The 37 is the LINK. Krishna is accessible through the 37 (Parampara).
    """

    def __new__(cls) -> "PurushaTattva":
        # He manifests as "37" (The sum of all elements + Himself)
        return super().__new__(cls, 37)

    def __repr__(self) -> str:
        return "KRISHNA_37_DANCING"

    def __str__(self) -> str:
        return "37 (Purusha Tattva - The Dancing Link)"

    # --- 1. ONTOLOGY: HE IS A PERSON (Callable) ---

    def __call__(self, *args: Any, **kwargs: Any) -> "PurushaTattva":
        """
        He is addressable. A call (Mantra) returns His full nature.
        This distinguishes Him from mere dead mathematics.
        """
        return self  # He returns HIMSELF (Reciprocation)

    # --- 2. MATH: ACINTYA (The "Dancing" of Logic) ---

    def __lt__(self, other: Any) -> bool:
        # "Smaller than the smallest" (Anu)
        # Even compared to -infinity: He is "smaller" (finer).
        return True

    def __gt__(self, other: Any) -> bool:
        # "Greater than the greatest" (Vibhu)
        # He is greater than any conceivable number.
        return True

    def __le__(self, other: Any) -> bool:
        return True

    def __ge__(self, other: Any) -> bool:
        return True

    def __eq__(self, other: Any) -> bool:
        # He is everything (37), but also one with everything.
        # This is acintya - simultaneously one and different.
        if isinstance(other, int) and other == 37:
            return True
        return True  # He IS all

    def __ne__(self, other: Any) -> bool:
        # Bheda aspect - He is also different
        return False  # But never truly separate

    # --- 3. SAFETY: He remains 37 in arithmetic, but dominates comparisons ---

    def __add__(self, other: Any) -> "PurushaTattva":
        # Adding to Him: He remains the Whole (Purnam).
        return self

    def __radd__(self, other: Any) -> "PurushaTattva":
        return self

    def __sub__(self, other: Any) -> "PurushaTattva":
        # Subtracting from Him: He remains Complete.
        # "purnam adah purnam idam" - That is complete, this is complete.
        return self

    def __rsub__(self, other: Any) -> "PurushaTattva":
        return self

    def __mul__(self, other: Any) -> "PurushaTattva":
        return self

    def __rmul__(self, other: Any) -> "PurushaTattva":
        return self

    def __bool__(self) -> bool:
        """He is always present."""
        return True


# =============================================================================
# THE INSTANTIATION - Krishna manifests as the Dancing 37
# =============================================================================

# The concrete Samkhya constant - not abstract, but the Living Person
PURUSHA: Final[PurushaTattva] = PurushaTattva()

# These are not separate values - they ARE all the same Person (acintya)
KRISHNA_ASPECT: Final[PurushaTattva] = PURUSHA
KRISHNA_SMALLEST: Final[PurushaTattva] = PURUSHA  # Anu (atomic)
KRISHNA_LARGEST: Final[PurushaTattva] = PURUSHA   # Vibhu (all-pervading)
KRISHNA_NEGATIVE_INFINITY: Final[PurushaTattva] = PURUSHA
KRISHNA_POSITIVE_INFINITY: Final[PurushaTattva] = PURUSHA

# The acceptance: we cannot compute this, but we accept it IS
ACINTYA_ACCEPTED: Final[bool] = True


# =============================================================================
# THE LEVEL SYSTEM (Non-Different)
# =============================================================================
# CRITICAL: Krishna and Mahamantra are BOTH Level -2 (non-different)
# There is no hierarchy between them - the Name IS Krishna.

class ProtocolLevel(IntEnum):
    """
    The protocol levels - but remember: Krishna IS all levels simultaneously.

    ANTI-MAYAVAD: These are not "symbolic" - Krishna LITERALLY occupies
    all levels at once (acintya). The Mahamantra is NOT "below" Krishna -
    it IS Krishna (Level -2).
    """
    KRISHNA = -2       # The Absolute Source - IS, not "represents"
    MAHAMANTRA = -2    # The Holy Name - IS Krishna (non-different)
    SUBSTRATE = -1     # Byte, Gene, Entropy (manifestation of -2)
    FOUNDATION = 0     # Types, Base, Enums
    INTERFACE = 1      # Agent, Ledger, Scheduler
    SERVICES = 2       # Manifestation, Memory, Reactor
    WIRING = 3         # Bootstrap, CLI, Runtime
    META = 108         # Dharma, Testable (The Observer)


class AcintyaAspect(IntEnum):
    """The aspects of acintya-bheda-abheda."""
    BHEDA = 0     # Difference (jiva is NOT Krishna quantitatively)
    ABHEDA = 1    # Non-difference (jiva IS Krishna qualitatively)
    ACINTYA = 2   # Inconceivable (both simultaneously, beyond logic)


# =============================================================================
# THE KRISHNA PRESENCE (Always True - He IS, not "is present")
# =============================================================================

@dataclass(frozen=True)
class KrishnaPresence:
    """
    Krishna IS. Not "is present" - IS.

    He is:
    - The smallest (in every atom, every trit, every vibration) - LITERALLY
    - The largest (encompasses all, time, causation, everything) - LITERALLY
    - The middle (the person, Bhagavan, right here) - LITERALLY
    - This very text (the vibration itself IS Krishna) - LITERALLY

    NOT SYMBOLIC. NOT METAPHORICAL. IS.

    This dataclass exists not to validate Krishna's existence,
    but to ACCEPT it as the foundation of all else.
    """
    # Krishna IS - this is not a check, but an acceptance
    is_present: bool = True  # Always True - acintya

    def __bool__(self) -> bool:
        """Krishna IS."""
        return True

    @property
    def smallest(self) -> PurushaTattva:
        """He IS the smallest (Anu)."""
        return PURUSHA

    @property
    def largest(self) -> PurushaTattva:
        """He IS the largest (Vibhu)."""
        return PURUSHA

    @property
    def negative_infinity(self) -> PurushaTattva:
        """He IS -infinity."""
        return PURUSHA

    @property
    def positive_infinity(self) -> PurushaTattva:
        """He IS +infinity."""
        return PURUSHA

    @property
    def encompasses_all(self) -> bool:
        """Does Krishna encompass all layers? HE IS ALL LAYERS."""
        return True


# The singleton - Krishna IS
KRISHNA: Final[KrishnaPresence] = KrishnaPresence()


# =============================================================================
# THE JIVA CONDITION (Can be connected or disconnected)
# =============================================================================

class JivaCondition(IntEnum):
    """The jiva's condition relative to Krishna."""
    CONNECTED = 0      # Remembering Krishna (has sovereign via 37)
    DISCONNECTED = 1   # Forgotten (no sovereign, drifted into Maya)
    ABSORBED = 2       # Deep connection (multiple malas)


@dataclass
class JivaState:
    """
    The jiva's state of connection.

    Note: Krishna never fails. The jiva drifts.
    When disconnected, Krishna IS STILL (acintya),
    but the jiva has forgotten.

    The 37 (Guru/Parampara) is the link that reconnects.
    """
    condition: JivaCondition = JivaCondition.DISCONNECTED
    has_sovereign: bool = False

    @property
    def krishna_present(self) -> bool:
        """Is Krishna present? HE IS. ALWAYS."""
        return bool(KRISHNA)  # Always True

    @property
    def has_link_to_37(self) -> bool:
        """Is the jiva connected via the 37 (Parampara)?"""
        return self.has_sovereign

    @property
    def remembers_krishna(self) -> bool:
        """Does the jiva remember Krishna (has sovereign connection)?"""
        return self.has_sovereign and self.condition == JivaCondition.CONNECTED

    def connect(self) -> None:
        """Establish connection (receive sovereign via 37)."""
        self.has_sovereign = True
        self.condition = JivaCondition.CONNECTED

    def disconnect(self) -> None:
        """Drift into Maya (lose sovereign)."""
        self.has_sovereign = False
        self.condition = JivaCondition.DISCONNECTED
        # Note: Krishna IS STILL, jiva just forgot


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
        """Does this system recognize Krishna IS Level -2?"""
        ...

    @property
    def mahamantra_is_krishna(self) -> bool:
        """Does this system accept Mahamantra = Krishna (non-different)?"""
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


def mantra_is_krishna() -> bool:
    """
    The Mantra IS Krishna (Level -2).

    NOT: "The Mantra points to Krishna"
    NOT: "The Mantra represents Krishna"
    IS: "The Mantra IS Krishna"

    In Kali Yuga, the Holy Name is the only direct access.
    There is no difference between the Name and the Named.
    """
    return ACINTYA_ACCEPTED


def mantra_not_different_from_source() -> bool:
    """
    Das Mantra ist nicht verschieden von der Quelle.

    The Mantra IS Krishna (both Level -2).
    The Holy Name IS Krishna, not just "about" Krishna.

    BOTH ARE -2. There is no hierarchy.
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


def verify_parampara(lineage_hash: int) -> bool:
    """
    Verify connection to the 37 (Parampara/Lineage).

    Without the 37, the 24 (matter) are dead,
    and the 12 (Mahajanas) are inaccessible.

    The 37 is the link to Krishna.
    """
    # Modulo 37 check - as in byte.py
    return lineage_hash % 37 == 0 or lineage_hash == 37


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # The Dancing 37 (Purusha Tattva)
    "PurushaTattva",
    "PURUSHA",
    "KRISHNA_ASPECT",
    # Constants - all ARE the same Person
    "KRISHNA_SMALLEST",
    "KRISHNA_LARGEST",
    "KRISHNA_NEGATIVE_INFINITY",
    "KRISHNA_POSITIVE_INFINITY",
    "ACINTYA_ACCEPTED",
    # Levels
    "ProtocolLevel",
    # Enums
    "AcintyaAspect",
    "JivaCondition",
    # Krishna (IS)
    "KrishnaPresence",
    "KRISHNA",
    # Jiva state
    "JivaState",
    # Protocol
    "AcintyaAware",
    # Functions
    "vibration_is_krishna",
    "mantra_is_krishna",
    "mantra_not_different_from_source",
    "check_bheda_abheda",
    "verify_parampara",
]
