"""
THE SENSE PROTOCOL - Panchajnanendriyas (5 Knowledge-Acquiring Senses)
======================================================================

"śrotraṁ cakṣuḥ sparśanaṁ ca rasanaṁ ghrāṇam eva ca
adhiṣṭhāya manaś cāyaṁ viṣayān upasevate"

"The living entity, thus taking another gross body, obtains a certain
type of ear, eye, tongue, nose and sense of touch, which are grouped
about the mind. He thus enjoys a particular set of sense objects."
— Bhagavad Gita 15.9

SHASTRA FOUNDATION (Srimad Bhagavatam 3.26 - Kapila's Sankhya):
===============================================================

The 24 Tattvas (Elements) of Prakriti [SB 3.26.11-18]:

    SUBTLE (8):
        Prakrti (1) - Primordial Nature
        Mahat-tattva (1) - Total Material Energy
        Ahankara (1) - False Ego (3 modes)
        Manas (1) - Mind
        Panca-tanmatra (5) - 5 Subtle Elements:
            Sabda (sound), Sparsa (touch), Rupa (form),
            Rasa (taste), Gandha (smell)

    GROSS (16):
        Panca-jnanendriya (5) - 5 Knowledge Senses ← THIS PROTOCOL
        Panca-karmendriya (5) - 5 Action Senses
        Panca-mahabhuta (5) - 5 Gross Elements

    + Purusa (1) = 25th Tattva (The Knower, Ksetrajna)

KSETRA_COUNT = 24 is EXACTLY the 24 Tattvas!
The 25th (Purusa) is the Sovereign who KNOWS the field.

THE 5 JNANENDRIYAS (Knowledge-Acquiring Senses) [SB 3.26.47-52]:
================================================================

Each sense arises from a Tanmatra (subtle element) and perceives
through a Mahabhuta (gross element):

    TANMATRA      JNANENDRIYA     MAHABHUTA       SOFTWARE MAPPING
    ─────────────────────────────────────────────────────────────────
    Sabda         Srotra (Ear)    Akasa (Ether)   Logs, Events, Signals
    Sparsa        Tvak (Skin)     Vayu (Air)      Filesystem, Git, State
    Rupa          Caksu (Eye)     Tejas (Fire)    Code Analysis, AST
    Rasa          Jihva (Tongue)  Jala (Water)    Tests, Validation
    Gandha        Ghrana (Nose)   Prthvi (Earth)  Code Smells, Entropy

MAHAMANTRA MAPPING:
===================

    Position 6 (Kapila) - TYPE_CHECK - Analysis/Sankhya
    → Kapila OWNS the sense protocol (he taught Sankhya!)

    The 5 senses map to 5 positions in DHARMA/KARMA quarters:
        Srotra  → Position 4 (PRITHU)      - Hears the structure
        Tvak    → Position 5 (Kumaras)     - Feels purity
        Caksu   → Position 6 (Kapila)      - Sees analysis
        Jihva   → Position 7 (Manu)        - Tastes dharma
        Ghrana  → Position 8 (Parashurama) - Smells corruption

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself (through Kapila's Sankhya)
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (HARE_COUNT, PANCHA, QUARTERS, SEVEN, SHARANAGATI)


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = SHARANAGATI
__genesis__ = "0x633fe12b"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import (
    ClassVar,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    MahamantraProtocolBase,
    ProtocolCapability,
    ProtocolIdentity,
    Quarter,
)
from vibe_core.mahamantra.substrate.seed import (
    KSHETRA as KSETRA_COUNT,  # 24 = The Tattvas!
)
from vibe_core.mahamantra.substrate.seed import (
    PARAMPARA,
)

# =============================================================================
# SHASTRA CONSTANTS
# =============================================================================

# Srimad Bhagavatam References
SB_SANKHYA_CHAPTER: Final[str] = "3.26"  # Kapila's Sankhya exposition
SB_JNANENDRIYA_VERSES: Final[Tuple[str, ...]] = (
    "3.26.47",  # Srotra (ear) from Sabda
    "3.26.48",  # Tvak (skin) from Sparsa
    "3.26.49",  # Caksu (eye) from Rupa
    "3.26.50",  # Jihva (tongue) from Rasa
    "3.26.51",  # Ghrana (nose) from Gandha
)

# Bhagavad Gita References
BG_SENSE_VERSE: Final[str] = "15.9"  # The 5 senses listed
BG_KSETRA_VERSE: Final[str] = "13.6"  # 24 elements of the field

# The Sacred Numbers
JNANENDRIYA_COUNT: Final[int] = PANCHA  # 5 knowledge senses
KARMENDRIYA_COUNT: Final[int] = PANCHA  # 5 action senses
TANMATRA_COUNT: Final[int] = PANCHA  # 5 subtle elements
MAHABHUTA_COUNT: Final[int] = PANCHA  # 5 gross elements
TATTVA_COUNT: Final[int] = KSETRA_COUNT  # 24 = Prakriti elements


# =============================================================================
# TANMATRA (Subtle Elements) - The OBJECTS of perception
# =============================================================================


class Tanmatra(str, Enum):
    """
    The 5 Tanmatras (Subtle Elements) - Objects of sense perception.

    SB 3.26.34: "From the false ego of goodness, the mind is generated..."
    The tanmatras are the subtle objects that the senses perceive.
    """

    SABDA = "sabda"  # Sound - perceived by ear
    SPARSA = "sparsa"  # Touch - perceived by skin
    RUPA = "rupa"  # Form - perceived by eye
    RASA = "rasa"  # Taste - perceived by tongue
    GANDHA = "gandha"  # Smell - perceived by nose

    @property
    def sanskrit(self) -> str:
        """Get Sanskrit spelling."""
        return {
            "sabda": "शब्द",
            "sparsa": "स्पर्श",
            "rupa": "रूप",
            "rasa": "रस",
            "gandha": "गन्ध",
        }[self.value]


# =============================================================================
# MAHABHUTA (Gross Elements) - The MEDIUM of perception
# =============================================================================


class Mahabhuta(str, Enum):
    """
    The 5 Mahabhutas (Gross Elements) - Medium through which senses work.

    SB 3.26.32-46: Each element arises from its tanmatra.
    """

    AKASA = "akasa"  # Ether/Space - carries sound
    VAYU = "vayu"  # Air - carries touch
    TEJAS = "tejas"  # Fire - carries form
    JALA = "jala"  # Water - carries taste
    PRTHVI = "prthvi"  # Earth - carries smell

    @property
    def sanskrit(self) -> str:
        """Get Sanskrit spelling."""
        return {
            "akasa": "आकाश",
            "vayu": "वायु",
            "tejas": "तेजस्",
            "jala": "जल",
            "prthvi": "पृथ्वी",
        }[self.value]


# =============================================================================
# JNANENDRIYA (Knowledge Sense) - The INSTRUMENTS of perception
# =============================================================================


class Jnanendriya(str, Enum):
    """
    The 5 Jnanendriyas (Knowledge-Acquiring Senses).

    SB 3.26.47-52: "From the sky, the sense of hearing was generated..."

    Each sense has:
    - A Tanmatra (subtle object it perceives)
    - A Mahabhuta (gross element it works through)
    - A Mahamantra position (owner in the system)
    """

    SROTRA = "srotra"  # Ear - hears Sabda through Akasa
    TVAK = "tvak"  # Skin - feels Sparsa through Vayu
    CAKSU = "caksu"  # Eye - sees Rupa through Tejas
    JIHVA = "jihva"  # Tongue - tastes Rasa through Jala
    GHRANA = "ghrana"  # Nose - smells Gandha through Prthvi

    @property
    def sanskrit(self) -> str:
        """Get Sanskrit spelling."""
        return {
            "srotra": "श्रोत्र",
            "tvak": "त्वक्",
            "caksu": "चक्षु",
            "jihva": "जिह्वा",
            "ghrana": "घ्राण",
        }[self.value]

    @property
    def tanmatra(self) -> Tanmatra:
        """Get the subtle element this sense perceives."""
        return {
            Jnanendriya.SROTRA: Tanmatra.SABDA,
            Jnanendriya.TVAK: Tanmatra.SPARSA,
            Jnanendriya.CAKSU: Tanmatra.RUPA,
            Jnanendriya.JIHVA: Tanmatra.RASA,
            Jnanendriya.GHRANA: Tanmatra.GANDHA,
        }[self]

    @property
    def mahabhuta(self) -> Mahabhuta:
        """Get the gross element this sense works through."""
        return {
            Jnanendriya.SROTRA: Mahabhuta.AKASA,
            Jnanendriya.TVAK: Mahabhuta.VAYU,
            Jnanendriya.CAKSU: Mahabhuta.TEJAS,
            Jnanendriya.JIHVA: Mahabhuta.JALA,
            Jnanendriya.GHRANA: Mahabhuta.PRTHVI,
        }[self]

    @property
    def mahamantra_position(self) -> int:
        """Get the Mahamantra position that owns this sense."""
        return {
            Jnanendriya.SROTRA: QUARTERS,  # Vyasa - hears the Veda
            Jnanendriya.TVAK: PANCHA,  # Kumaras - feels purity
            Jnanendriya.CAKSU: SHARANAGATI,  # Kapila - sees analysis
            Jnanendriya.JIHVA: SEVEN,  # Manu - tastes dharma
            Jnanendriya.GHRANA: HARE_COUNT,  # Parashurama - smells corruption
        }[self]

    @property
    def sb_verse(self) -> str:
        """Get the Bhagavatam verse reference."""
        idx = list(Jnanendriya).index(self)
        return SB_JNANENDRIYA_VERSES[idx]


# =============================================================================
# SENSE PERCEPTION RESULT
# =============================================================================


@dataclass
class SensePerception:
    """
    Result of a sense perception.

    Each sense produces a perception with:
    - What was perceived (data)
    - How intense (0.0-1.0)
    - Quality (sattva/rajas/tamas)
    - Timestamp
    """

    sense: Jnanendriya
    tanmatra: Tanmatra
    data: Dict[str, Union[str, int, float, bool, List[str]]]
    intensity: float = 0.5  # 0.0 = imperceptible, 1.0 = overwhelming
    quality: str = "sattva"  # sattva/rajas/tamas
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_painful(self) -> bool:
        """Is this perception indicating pain/problem?"""
        return self.intensity > 0.7 and self.quality == "tamas"

    @property
    def needs_attention(self) -> bool:
        """Does this perception need conscious attention?"""
        return self.intensity > 0.5


# =============================================================================
# SENSE PROTOCOL - The Interface
# =============================================================================

T = TypeVar("T")  # Type of perception data


@runtime_checkable
class SenseProtocol(Protocol):
    """
    The Jnanendriya Protocol - How a sense MUST behave.

    Every sense implementation (in opus_assistant or elsewhere)
    MUST satisfy this protocol.

    SHASTRA BASIS:
        SB 3.26.47: "The sense of hearing is the first organ
        which perceives the object of sound..."

    SOFTWARE MAPPING:
        Each sense perceives its domain and reports intensity.
        High intensity + tamas quality = PAIN = needs chanting.
    """

    @property
    def jnanendriya(self) -> Jnanendriya:
        """Which of the 5 senses is this?"""
        ...

    @property
    def tanmatra(self) -> Tanmatra:
        """What subtle element does this sense perceive?"""
        ...

    @property
    def is_active(self) -> bool:
        """Is this sense currently active?"""
        ...

    def perceive(self) -> SensePerception:
        """
        Perform perception and return result.

        This is the main method - the sense "looks" at its domain
        and reports what it perceives.
        """
        ...

    def get_pain_level(self) -> float:
        """
        Get current pain level (0.0-1.0).

        Pain = high intensity + tamas quality.
        This drives the chanting frequency.
        """
        ...


# =============================================================================
# AGGREGATE PERCEPTION - Manas combines all senses
# =============================================================================


@dataclass
class AggregatePerception:
    """
    Combined perception from all 5 senses.

    Manas (mind) combines the input from all jnanendriyas
    to form a complete picture.

    SB 3.26.27: "The mind is the eleventh sense organ,
    which coordinates all other senses."
    """

    perceptions: Dict[Jnanendriya, SensePerception] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_pain(self) -> float:
        """
        Aggregate pain level from all senses.

        This drives the daemon's chanting frequency:
        - Low pain (< 0.3): IDLE (system healthy)
        - Medium pain (0.3-0.7): ACTIVE (normal operation)
        - High pain (> 0.7): STRESS (emergency chanting!)
        """
        if not self.perceptions:
            return 0.0

        total = sum(p.intensity for p in self.perceptions.values() if p.quality == "tamas")
        return min(1.0, total / JNANENDRIYA_COUNT)

    @property
    def dominant_sense(self) -> Optional[Jnanendriya]:
        """Which sense is screaming loudest?"""
        if not self.perceptions:
            return None

        max_intensity = 0.0
        dominant = None

        for sense, perception in self.perceptions.items():
            if perception.intensity > max_intensity:
                max_intensity = perception.intensity
                dominant = sense

        return dominant

    @property
    def needs_chanting(self) -> bool:
        """Does the aggregate perception indicate need for chanting?"""
        return self.total_pain > 0.3

    def add_perception(self, perception: SensePerception) -> None:
        """Add a perception from a sense."""
        self.perceptions[perception.sense] = perception


# =============================================================================
# MANAS PROTOCOL - The Mind that coordinates senses
# =============================================================================


@runtime_checkable
class ManasProtocol(Protocol):
    """
    The Manas Protocol - The Mind that coordinates all senses.

    SB 3.26.27: "Doubt, misapprehension, correct apprehension,
    memory and sleep are determined by the mind..."

    Manas collects input from all 5 jnanendriyas and produces
    an aggregate perception that drives consciousness.
    """

    @property
    def senses(self) -> Dict[Jnanendriya, SenseProtocol]:
        """Get all registered senses."""
        ...

    def register_sense(self, sense: SenseProtocol) -> None:
        """Register a sense implementation."""
        ...

    def perceive_all(self) -> AggregatePerception:
        """
        Collect perception from all senses.

        This is the main method - Manas "polls" all senses
        and combines their input.
        """
        ...

    def get_total_pain(self) -> float:
        """Get aggregate pain level for daemon frequency."""
        ...


# =============================================================================
# SENSE PROTOCOL DEFINITION - Self-Reference
# =============================================================================


class SenseProtocolDef(MahamantraProtocolBase):
    """
    The Sense Protocol.

    Position 6 (KAPILA) - The analyst who taught Sankhya.
    Level -1 (SUBSTRATE) - Foundational perception layer.
    Quarter DHARMA - Understanding through analysis.

    SHASTRA: SB 3.26.47-52 (Kapila's exposition of the senses)
    """

    __protocol_identity__ = ProtocolIdentity(
        name="SenseProtocol",
        mahajana="kapila",  # Kapila taught Sankhya
        position=SHARANAGATI,
        level=Level.SUBSTRATE,
        quarter=Quarter.DHARMA,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "jnanendriya_definition",
            "tanmatra_mapping",
            "mahabhuta_mapping",
            "sense_perception",
            "pain_measurement",
            "aggregate_perception",
            "manas_coordination",
        ],
        requires=["CoreProtocol"],
        opcodes=["TYPE_CHECK"],  # Kapila's opcode - analysis
    )


# =============================================================================
# VALIDATION
# =============================================================================

_valid, _violations = SenseProtocolDef.validate()
assert _valid, f"SenseProtocol failed validation: {_violations}"

# Verify the sacred numbers
assert JNANENDRIYA_COUNT == PANCHA, "Must have exactly 5 knowledge senses"
assert TATTVA_COUNT == KSETRA_COUNT, "Tattvas must equal Ksetra count (24)"
assert len(Jnanendriya) == JNANENDRIYA_COUNT, "Enum must have 5 senses"
assert len(Tanmatra) == TANMATRA_COUNT, "Enum must have 5 tanmatras"
assert len(Mahabhuta) == MAHABHUTA_COUNT, "Enum must have 5 mahabhutas"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Shastra constants
    "SB_SANKHYA_CHAPTER",
    "SB_JNANENDRIYA_VERSES",
    "BG_SENSE_VERSE",
    "BG_KSETRA_VERSE",
    "JNANENDRIYA_COUNT",
    "TANMATRA_COUNT",
    "MAHABHUTA_COUNT",
    "TATTVA_COUNT",
    # Enums
    "Tanmatra",
    "Mahabhuta",
    "Jnanendriya",
    # Data classes
    "SensePerception",
    "AggregatePerception",
    # Protocols
    "SenseProtocol",
    "ManasProtocol",
    # Protocol definition
    "SenseProtocolDef",
]
