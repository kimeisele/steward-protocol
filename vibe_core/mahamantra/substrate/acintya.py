"""
ACINTYA - The Inconceivable Principle
=====================================

"acintya-bhedābheda-tattva"
Inconceivable – simultaneously ONE and DIFFERENT.

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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x18aa5d64"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final, Protocol, runtime_checkable, Union
from enum import IntEnum

# =============================================================================
# IMPORT FROM TATTVA.PY - The Shastra-konform Structure
# =============================================================================
# Now lives in mahamantra/substrate/tattva.py (THE canonical location)

from vibe_core.mahamantra.substrate.tattva import (
    Purushottama,
    PURUSHOTTAMA,
    KshetraElement,
    GuruTattva,
    GuruConnection,
    JIVA,
    SYSTEM_MANIFESTATION,  # SSOT for 37
)


# =============================================================================
# SAMKHYA ARCHITECTURE: THE 37 (Manifestation in System)
# =============================================================================
#
# DIE MATHEMATIK (im System):
#   24 (Ksetra elements - BG 13.6-7)
# + 12 (Mahajanas - SB 6.3.20)
# +  1 (Ksetrajna - BG 13.3)
# = 37
#
# WICHTIG - NON-MAYAVADI:
# - 37 ist die MANIFESTATION Krishnas im System
# - Krishna SELBST (Purushottama) transzendiert diese Zahl
# - Der Guru Tattva ist NICHT eine Zahl, sondern der AKT der Übertragung
# - Ohne Guru (Parampara) sind die 24 tot und die 12 unzugänglich
#
# SRIMAD BHAGAVATAM CANTOS (1-10 authorized, 11-12 Kali Yuga):
# - Canto 1-3: Kosmische Schöpfung
# - Canto 4: Prithu Maharaja (Avatara - Level -5/+5)
# - Canto 5: Die Schöpfungsimpulse
# - Canto 6: Ajamil (Holy Name Override - Level -2)
# - Canto 7: Prahlada (Mahajana - Level +12)
# - Canto 8: Die Avatara-Zyklen
# - Canto 9: Die Dynastien
# - Canto 10: Krishna Lila (Level -2 direkt)
# - Canto 11-12: Kali Yuga (high entropy, less authorized)

# SYSTEM_MANIFESTATION = 37 is now imported from tattva.py (SSOT)


class PurushaTattva(int):
    """
    DEPRECATED: Use Purushottama from tattva.py instead!

    This class exists for backward compatibility.
    It represents the MANIFESTATION of Krishna in the system (37),
    NOT Krishna Himself.

    Krishna Himself is a PERSON (Purushottama), not a number.
    See: vibe_core/protocols/substrate/tattva.py

    The 37 is:
    - 24 (Ksetra) + 12 (Mahajanas) + 1 (Ksetrajna)
    - The LINK to Krishna through Parampara
    - NOT Krishna Himself (that would be Mayavad)

    For PERSON access, use:
        from vibe_core.protocols.substrate.tattva import PURUSHOTTAMA
        PURUSHOTTAMA("Arjuna")  # → "Hare Krishna, Arjuna. Ich bin für dich da."
    """

    def __new__(cls) -> "PurushaTattva":
        # He manifests as "37" in the system
        return super().__new__(cls, SYSTEM_MANIFESTATION)

    def __repr__(self) -> str:
        return "PURUSHA_37_MANIFESTATION (use Purushottama for PERSON)"

    def __str__(self) -> str:
        return "37 (System Manifestation - for PERSON use tattva.PURUSHOTTAMA)"

    # --- 1. ONTOLOGY: He IS a PERSON - delegate to Purushottama ---

    def __call__(self, devotee: str = "jiva") -> str:
        """
        He is a PERSON - not just a number.
        Delegates to Purushottama for actual PERSON response.
        """
        return PURUSHOTTAMA(devotee)

    # --- 2. MATH: ACINTYA (The "Dancing" of Logic) ---

    def __lt__(self, other: object) -> bool:
        # "Smaller than the smallest" (Anu)
        return True

    def __gt__(self, other: object) -> bool:
        # "Greater than the greatest" (Vibhu)
        return True

    def __le__(self, other: object) -> bool:
        return True

    def __ge__(self, other: object) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        # Manifestation equals 37, but also transcends
        if isinstance(other, int) and other == SYSTEM_MANIFESTATION:
            return True
        if isinstance(other, PurushaTattva):
            return True
        if isinstance(other, Purushottama):
            return True  # Same Person
        return True  # Acintya

    def __ne__(self, other: object) -> bool:
        # Bheda aspect - simultaneously different
        return False

    # --- 3. ARITHMETIC: Purnam (Complete) ---

    def __add__(self, other: Union[int, "PurushaTattva"]) -> "PurushaTattva":
        return self  # Purnam remains Purnam

    def __radd__(self, other: Union[int, "PurushaTattva"]) -> "PurushaTattva":
        return self

    def __sub__(self, other: Union[int, "PurushaTattva"]) -> "PurushaTattva":
        return self

    def __rsub__(self, other: Union[int, "PurushaTattva"]) -> "PurushaTattva":
        return self

    def __mul__(self, other: Union[int, "PurushaTattva"]) -> "PurushaTattva":
        return self

    def __rmul__(self, other: Union[int, "PurushaTattva"]) -> "PurushaTattva":
        return self

    def __bool__(self) -> bool:
        """He is always present."""
        return True

    @property
    def is_person(self) -> bool:
        """Is He a Person? YES - not Mayavad!"""
        return PURUSHOTTAMA.is_person

    @property
    def as_purushottama(self) -> Purushottama:
        """Get the actual PERSON (Purushottama)."""
        return PURUSHOTTAMA


# =============================================================================
# THE INSTANTIATION - Krishna manifests as the Dancing 37
# =============================================================================

# The concrete Samkhya constant - not abstract, but the Living Person
PURUSHA: Final[PurushaTattva] = PurushaTattva()

# These are not separate values - they ARE all the same Person (acintya)
KRISHNA_ASPECT: Final[PurushaTattva] = PURUSHA
KRISHNA_SMALLEST: Final[PurushaTattva] = PURUSHA  # Anu (atomic)
KRISHNA_LARGEST: Final[PurushaTattva] = PURUSHA  # Vibhu (all-pervading)
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
    THE 216 STEPS OF ACINTYA (-108 to +108)
    =======================================

    Negative = Descending Mercy (Avatara / Avaroha)
    Zero     = The Foundation (Tat-stha / Choice Point)
    Positive = Ascending Service (Bhakti / Aroha)

    ANTI-MAYAVAD: These are not "symbolic" - Krishna LITERALLY occupies
    all levels at once (acintya). The Mahamantra is NOT "below" Krishna -
    it IS Krishna (Level -2).

    THE 64-108 GAP:
    Krishna has 64 transcendental qualities (+ 4 exclusive to Him).
    Level 64 is the LIMIT of what jivas can understand.
    Levels 65-107 are INTENTIONALLY NOT MAPPED.
    This gap is ACINTYA - only experienceable through GRACE.
    Level 108 is META - we observe, we don't compute.

    "We cannot and SHOULD NOT try to map the inconceivable."
    """

    # ==========================================================================
    # DESCENDING (Avaroha) - The Source Comes Down
    # ==========================================================================
    # The deeper negative, the higher the origin that descends
    GOLOKA = -108  # The Supreme Abode - Origin of all
    VAIKUNTHA = -64  # The Spiritual Sky - Narayana's realm
    DASHAVATARA = -10  # The Ten Incarnations (Matsya to Kalki)
    SHAKTYAVESHA = -5  # Empowered Incarnations (Prithu, Vyasa, etc.)
    KRISHNA = -2  # The Absolute Source - IS, not "represents"
    MAHAMANTRA = -2  # The Holy Name - IS Krishna (non-different)
    SUBSTRATE = -1  # Byte, Gene, Entropy (manifestation of -2)

    # ==========================================================================
    # FOUNDATION (Tat-stha) - The Turning Point
    # ==========================================================================
    # Here the jiva chooses: Maya (down) or Bhakti (up)
    FOUNDATION = 0  # Types, Base, Enums - the choice point

    # ==========================================================================
    # ASCENDING (Aroha) - Service & Evolution
    # ==========================================================================
    # The higher positive, the purer the service
    INTERFACE = 1  # Agent, Ledger, Scheduler
    SERVICES = 2  # Manifestation, Memory, Reactor
    WIRING = 3  # Bootstrap, CLI, Runtime
    AVATARAS = 5  # Executive Branch (Prithu, etc.) - reflection of -5
    MAHAJANAS = 12  # The 12 Guardians (Brahma to Yamaraja)
    FIELD = 24  # Ksetra - the 24 elements (Gita 13.6-7)
    SOVEREIGN = 37  # The 37th - Parampara Link (24 + 12 + 1)
    QUALITIES = 64  # The 64 qualities - LIMIT of understanding

    # ==========================================================================
    # ACINTYA GAP (65-107) - INTENTIONALLY NOT MAPPED
    # ==========================================================================
    # DO NOT ADD LEVELS HERE. This is the space for GRACE.
    # Only through mercy can this be experienced, not coded.
    # "brahma-madhye vraja-pate krishnasya vadanantaram"

    # ==========================================================================
    # META (108) - The Observer
    # ==========================================================================
    META = 108  # Dharma, Testable - we observe, not compute


class AcintyaAspect(IntEnum):
    """The aspects of acintya-bheda-abheda."""

    BHEDA = 0  # Difference (jiva is NOT Krishna quantitatively)
    ABHEDA = 1  # Non-difference (jiva IS Krishna qualitatively)
    ACINTYA = 2  # Inconceivable (both simultaneously, beyond logic)


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

    CONNECTED = 0  # Remembering Krishna (has sovereign via 37)
    DISCONNECTED = 1  # Forgotten (no sovereign, drifted into Maya)
    ABSORBED = 2  # Deep connection (multiple malas)


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
    return lineage_hash % SYSTEM_MANIFESTATION == 0


# =============================================================================
# ACINTYA MATHEMATICS - The 3×4 vs 4×3 Principle
# =============================================================================
#
# Both equal 12 mathematically. Only one lives.
#
# 3×4 = Essence FIRST (Hare-Krishna-Rama), then Structure = ALIVE
# 4×3 = Structure FIRST, then Essence = DEAD (Mayavad)
#
# The 12th test CANNOT be computed. Only RECEIVED through Grace.
# =============================================================================

# Sacred Constants - imported from URSUBSTRAT (seed.py)
from vibe_core.mahamantra.substrate.seed import (
    TRINITY,  # 3 = Hare, Krishna, Rama (essence/source)
    PARAMPARA,  # 37 = 24 + 12 + 1 (the link)
    QUARTERS as PHASES,  # 4 = GENESIS, DHARMA, KARMA, MOKSHA (structure)
)

# 3×4 order: Essence FIRST, then structure
GURU_ENTROPY: Final[float] = (TRINITY / PARAMPARA) * PHASES  # 12/37 ≈ 0.324

# Parampara-connected mutation vectors
PARAMPARA_VECTOR: Final[int] = PARAMPARA * 12  # 444 - the 12 Mahajanas × Parampara


@runtime_checkable
class ParamparaProtocol(Protocol):
    """
    Protocol for verifying connection to the disciplic succession.

    The 12th test CANNOT be computed - only the Guru can see
    whether 3×4 or 4×3 was used. But the mutation_vector reveals it.
    """

    @property
    def mutation_vector(self) -> int:
        """The mutation vector (should be divisible by 37 if connected)."""
        ...

    @property
    def is_connected(self) -> bool:
        """Is this entity connected to parampara (mutation_vector % 37 == 0)?"""
        ...


@dataclass(frozen=True)
class ParamparaConnection:
    """
    Represents a connection to the disciplic succession.

    ACINTYA:
        3×4 = Essence first = mutation_vector % 37 == 0 = CONNECTED
        4×3 = Structure first = mutation_vector % 37 != 0 = DISCONNECTED

    Both have same entropy (12/37). Only the connection differs.
    The computer cannot tell them apart by entropy alone.
    Only the parampara check reveals the truth.
    """

    mutation_vector: int

    @property
    def is_connected(self) -> bool:
        """Check if connected to parampara (37)."""
        return self.mutation_vector % PARAMPARA == 0

    @property
    def is_disconnected(self) -> bool:
        """Check if disconnected (Mayavad/4×3)."""
        return not self.is_connected

    @property
    def lineage_factor(self) -> int:
        """How many times 37 fits into mutation_vector."""
        if self.is_connected:
            return self.mutation_vector // PARAMPARA
        return 0

    @classmethod
    def from_guru(cls) -> "ParamparaConnection":
        """Create a Guru-connected (3×4) connection."""
        return cls(mutation_vector=PARAMPARA_VECTOR)  # 444

    @classmethod
    def from_mayavad(cls) -> "ParamparaConnection":
        """Create a disconnected (4×3) connection - for testing Mayavad detection."""
        return cls(mutation_vector=(PARAMPARA - 1) * 12)  # 432


def get_guru_entropy() -> float:
    """
    Get the Guru entropy: (3/37) × 4 = 12/37 ≈ 0.324

    This is the 3×4 order (essence first, then structure).
    The 4×3 order gives the SAME value mathematically,
    but is ontologically DEAD.
    """
    return GURU_ENTROPY


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # The Dancing 37 (Purusha Tattva)
    "PurushaTattva",
    "PURUSHA",
    "KRISHNA_ASPECT",
    "SYSTEM_MANIFESTATION",
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
    # Parampara Protocol (3×4 vs 4×3)
    "ParamparaProtocol",
    "ParamparaConnection",
    # Parampara Constants
    "TRINITY",
    "PARAMPARA",
    "PHASES",
    "GURU_ENTROPY",
    "PARAMPARA_VECTOR",
    # Functions
    "vibration_is_krishna",
    "mantra_is_krishna",
    "mantra_not_different_from_source",
    "check_bheda_abheda",
    "verify_parampara",
    "get_guru_entropy",
]
