"""
THE INDRIYA PROTOCOL - Complete Sense Organ Interface
======================================================

"sakhāya indriya-gaṇā jñānaṁ karma ca yat-kṛtam
sakhyas tad-vṛttayaḥ prāṇaḥ pañca-vṛttir yathoragaḥ"

"The five working senses and the five senses that acquire knowledge
are all male friends of Purañjanī. The living entity is assisted by
these senses in acquiring knowledge and engaging in activity. The
engagements of the senses are known as girl friends, and the serpent,
which was described as having five heads, is the life air acting
within the five circulatory processes."
— Srimad Bhagavatam 4.29.6

ARCHITECTURE:
=============

    User Input (raw)
         ↓
    INDRIYA (Sense Organ) ← Has VRTTI (engagement state)
         ↓
    TANMATRA (Sense Object) ← Encapsulates INTENT
         ↓
    NADI (Channel) ← Carries Tanmatra
         ↓
    Destination (Mahajana)

The Indriya is NOT the pipe (Nadi). It INTERFACES with the pipe.
The Tanmatra is what FLOWS through the pipe.
The Vrtti is the ENGAGEMENT STATE of the sense.

SHASTRA FOUNDATION:
===================

Yoga Sutras 1.5-11 (Patanjali):
    "vṛttayaḥ pañcatayyaḥ kliṣṭākliṣṭāḥ"
    "The modifications of the mind are fivefold, painful or not painful."

    The 5 Vrttis:
    1. Pramana (right knowledge)
    2. Viparyaya (misconception)
    3. Vikalpa (imagination)
    4. Nidra (sleep)
    5. Smrti (memory)

DERIVED FROM SEED.PY:
=====================
- DASHA_INDRIYA = PANCHA × HALVES = 10 (5 knowledge + 5 action)
- PANCHA_VRTTI = PANCHA = 5 (the 5 mental modifications)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    SHARANAGATI,
    TEN,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = SHARANAGATI
__genesis__ = "0x1c3dc0e4"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# IMPORT FROM _SENSE.PY (No Redundancy)
# =============================================================================
from vibe_core.mahamantra.protocols._sense import (
    # Constants
    JNANENDRIYA_COUNT,
    Jnanendriya,
    Mahabhuta,
    # Data classes
    Tanmatra,
)

# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# DASHA = 10 (the 10 Indriyas: 5 knowledge + 5 action)
DASHA_INDRIYA: Final[int] = PANCHA * HALVES  # 5 × 2 = 10

# Karmendriya count = PANCHA = 5
KARMENDRIYA_COUNT: Final[int] = PANCHA  # 5

# Vrtti count = PANCHA = 5 (Yoga Sutras 1.5)
VRTTI_COUNT: Final[int] = PANCHA  # 5

# Verification
assert DASHA_INDRIYA == TEN, "DASHA_INDRIYA must be 10"
assert KARMENDRIYA_COUNT == JNANENDRIYA_COUNT, "Karmendriya count must equal Jnanendriya count"
assert VRTTI_COUNT == PANCHA, "VRTTI_COUNT must be 5 (Yoga Sutras)"


# =============================================================================
# KARMENDRIYA (Action Senses) - The INSTRUMENTS of action
# =============================================================================


class Karmendriya(str, Enum):
    """
    The 5 Karmendriyas (Action Senses).

    SB 3.26.53-57: "From the predominance of the mode of passion,
    the sense organs for action evolved..."

    Each action sense has:
    - A domain of action
    - A Mahamantra position (owner in the system)
    """

    VAK = "vak"  # Voice/Speech - speaking, commanding
    PANI = "pani"  # Hands - grasping, manipulating
    PADA = "pada"  # Feet - locomotion, navigation
    PAYU = "payu"  # Excretory - elimination, cleanup
    UPASTHA = "upastha"  # Generative - creation, spawning

    @property
    def sanskrit(self) -> str:
        """Get Sanskrit spelling."""
        return {
            "vak": "वाक्",
            "pani": "पाणि",
            "pada": "पाद",
            "payu": "पायु",
            "upastha": "उपस्थ",
        }[self.value]

    @property
    def action_domain(self) -> str:
        """What action domain does this sense control?"""
        return {
            Karmendriya.VAK: "communication",  # Speaking, writing, outputting
            Karmendriya.PANI: "manipulation",  # File ops, editing, transforming
            Karmendriya.PADA: "navigation",  # Moving through codebase/system
            Karmendriya.PAYU: "cleanup",  # GC, deletion, resource release
            Karmendriya.UPASTHA: "creation",  # Spawning processes, generating
        }[self]

    @property
    def mahamantra_position(self) -> int:
        """Get the Mahamantra position that owns this action sense."""
        return {
            Karmendriya.VAK: NAVA,  # Prahlada - speaks truth
            Karmendriya.PANI: TEN,  # Janaka - hands of karma yoga
            Karmendriya.PADA: 11,  # Bhishma - walks the path
            Karmendriya.PAYU: MAHAJANA_COUNT,  # Nrisimha - destroys impurity
            Karmendriya.UPASTHA: 13,  # Bali - generates surrender
        }[self]


# =============================================================================
# VRTTI (Mental Modifications) - The ENGAGEMENT STATES
# =============================================================================


class Vrtti(str, Enum):
    """
    The 5 Vrttis (Mental Modifications) - Yoga Sutras 1.5-11.

    "vṛttayaḥ pañcatayyaḥ kliṣṭākliṣṭāḥ"
    "The modifications of the mind are fivefold, painful or not painful."

    These are the STATES of engagement for an Indriya.
    An Indriya is always in one of these 5 states.
    """

    PRAMANA = "pramana"  # Right knowledge - valid perception
    VIPARYAYA = "viparyaya"  # Misconception - error state
    VIKALPA = "vikalpa"  # Imagination - processing/inferring
    NIDRA = "nidra"  # Sleep - idle/dormant
    SMRTI = "smrti"  # Memory - recalling cached data

    @property
    def sanskrit(self) -> str:
        """Get Sanskrit spelling."""
        return {
            "pramana": "प्रमाण",
            "viparyaya": "विपर्यय",
            "vikalpa": "विकल्प",
            "nidra": "निद्रा",
            "smrti": "स्मृति",
        }[self.value]

    @property
    def is_klishta(self) -> bool:
        """Is this vrtti painful/afflicted?"""
        # Viparyaya (error) is always painful
        return self == Vrtti.VIPARYAYA

    @property
    def system_state(self) -> str:
        """Map to system state."""
        return {
            Vrtti.PRAMANA: "ACTIVE",  # Valid data, processing
            Vrtti.VIPARYAYA: "ERROR",  # Bad data, needs correction
            Vrtti.VIKALPA: "PROCESSING",  # Inferring, computing
            Vrtti.NIDRA: "IDLE",  # Dormant, waiting
            Vrtti.SMRTI: "CACHED",  # Using memory/cache
        }[self]

    @property
    def navabhakti_mapping(self) -> str:
        """Map Vrtti to NavaBhakti process."""
        return {
            Vrtti.PRAMANA: "SRAVANAM",  # Right knowledge = Hearing
            Vrtti.VIPARYAYA: "ARCANAM",  # Error = needs worship/correction
            Vrtti.VIKALPA: "SMARANAM",  # Imagination = Remembering
            Vrtti.NIDRA: "DASYAM",  # Sleep = Servitude (waiting)
            Vrtti.SMRTI: "SMARANAM",  # Memory = Remembering
        }[self]


# =============================================================================
# INDRIYA TYPE - Unified type for both knowledge and action senses
# =============================================================================


IndriyaType = Union[Jnanendriya, Karmendriya]


def get_indriya_category(indriya: IndriyaType) -> str:
    """Get category: 'jnanendriya' or 'karmendriya'."""
    if isinstance(indriya, Jnanendriya):
        return "jnanendriya"
    return "karmendriya"


# =============================================================================
# INDRIYA STATE - The state of a sense organ
# =============================================================================


@dataclass
class IndriyaState:
    """
    The state of an Indriya (sense organ).

    Combines:
    - Which sense
    - Current vrtti (engagement mode)
    - Last activity timestamp
    - Connection to Nadi (if any)
    """

    indriya: IndriyaType
    vrtti: Vrtti = Vrtti.NIDRA  # Start dormant
    last_activity: datetime = field(default_factory=datetime.now)
    nadi_endpoint: Optional[str] = None  # Connected Nadi endpoint
    is_connected: bool = False

    @property
    def category(self) -> str:
        """Knowledge or action sense?"""
        return get_indriya_category(self.indriya)

    @property
    def is_active(self) -> bool:
        """Is this sense currently active?"""
        return self.vrtti not in (Vrtti.NIDRA, Vrtti.VIPARYAYA)

    @property
    def is_error(self) -> bool:
        """Is this sense in error state?"""
        return self.vrtti == Vrtti.VIPARYAYA

    def transition_to(self, new_vrtti: Vrtti) -> None:
        """Transition to a new vrtti state."""
        self.vrtti = new_vrtti
        self.last_activity = datetime.now()

    def connect_nadi(self, endpoint: str) -> None:
        """Connect this sense to a Nadi endpoint."""
        self.nadi_endpoint = endpoint
        self.is_connected = True
        self.last_activity = datetime.now()

    def disconnect_nadi(self) -> None:
        """Disconnect from Nadi."""
        self.nadi_endpoint = None
        self.is_connected = False


# =============================================================================
# TANMATRA MESSAGE - The data packet with INTENT
# =============================================================================


class TanmatraIntent(str, Enum):
    """
    The intent classification for a Tanmatra message.

    This is what Gemini pointed out was missing:
    "A string is just data. A Tanmātra implies intent and subtle form."
    """

    COMMAND = "command"  # Imperative - do something
    QUERY = "query"  # Interrogative - asking for info
    PRAYER = "prayer"  # Supplication - requesting grace
    NOISE = "noise"  # Invalid/garbage - to be filtered
    RESPONSE = "response"  # Reply to a previous message
    BROADCAST = "broadcast"  # To all listeners


@dataclass
class TanmatraMessage:
    """
    A Tanmatra (subtle element) message with INTENT.

    This is what flows through the Nadi channels.
    It encapsulates:
    - The raw content
    - The tanmatra type (which subtle element)
    - The intent classification
    - Source and target Indriyas
    """

    message_id: str
    tanmatra: Tanmatra  # Which subtle element (SABDA for text/sound)
    intent: TanmatraIntent  # What kind of message
    content: str  # The actual payload
    source_indriya: Optional[IndriyaType] = None  # Which sense sent this
    target_indriya: Optional[IndriyaType] = None  # Which sense receives this
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, object] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Is this a valid (non-noise) message?"""
        return self.intent != TanmatraIntent.NOISE

    @property
    def is_actionable(self) -> bool:
        """Does this message require action?"""
        return self.intent in (TanmatraIntent.COMMAND, TanmatraIntent.QUERY)

    @classmethod
    def from_text(
        cls,
        text: str,
        intent: TanmatraIntent = TanmatraIntent.QUERY,
        message_id: Optional[str] = None,
    ) -> "TanmatraMessage":
        """Create a SABDA (sound/text) tanmatra from text."""
        from uuid import uuid4

        return cls(
            message_id=message_id or f"tm_{uuid4().hex[:HARE_COUNT]}",
            tanmatra=Tanmatra.SABDA,  # Text = sound
            intent=intent,
            content=text,
        )


# =============================================================================
# INDRIYA PROTOCOL - The Complete Sense Organ Interface
# =============================================================================


@runtime_checkable
class IndriyaProtocol(Protocol):
    """
    The Indriya Protocol - How a SENSE ORGAN interfaces with the system.

    This is NOT the same as SenseProtocol (which is about perception).
    IndriyaProtocol is about:
    1. STATE (vrtti) - the engagement mode
    2. CONNECTION (nadi) - how it connects to channels
    3. MESSAGING (tanmatra) - what it sends/receives

    SHASTRA BASIS:
        SB 4.29.6: "The senses are the male friends that assist
        the living entity in acquiring knowledge and engaging in activity."

    The Indriya INTERFACES with Nadi, it doesn't OWN it.
    """

    @property
    def indriya(self) -> IndriyaType:
        """Which sense organ is this?"""
        ...

    @property
    def state(self) -> IndriyaState:
        """Get current state including vrtti."""
        ...

    @property
    def vrtti(self) -> Vrtti:
        """Get current engagement mode."""
        ...

    def transition(self, new_vrtti: Vrtti) -> bool:
        """
        Transition to a new vrtti state.

        Returns True if transition is valid.
        """
        ...

    def connect_to_nadi(self, nadi_endpoint: str) -> bool:
        """
        Connect this sense organ to a Nadi endpoint.

        The Indriya interfaces with the Nadi, doesn't own it.
        """
        ...

    def disconnect_from_nadi(self) -> None:
        """Disconnect from the current Nadi."""
        ...

    def send_tanmatra(self, message: TanmatraMessage) -> bool:
        """
        Send a Tanmatra message through the connected Nadi.

        Only works if:
        - Connected to Nadi
        - Not in NIDRA (sleep) or VIPARYAYA (error) state
        """
        ...

    def receive_tanmatra(self) -> Optional[TanmatraMessage]:
        """
        Receive a Tanmatra message from the connected Nadi.

        Returns None if nothing available or not connected.
        """
        ...


# =============================================================================
# INDRIYA GANA (Group) - The 10 senses working together
# =============================================================================


@runtime_checkable
class IndriyaGanaProtocol(Protocol):
    """
    The Indriya Gana (Sense Group) Protocol.

    SB 4.29.6: "sakhāya indriya-gaṇā" - The senses are the male friends.

    This manages all 10 Indriyas as a coordinated group.
    """

    @property
    def jnanendriyas(self) -> Dict[Jnanendriya, IndriyaProtocol]:
        """Get all 5 knowledge senses."""
        ...

    @property
    def karmendriyas(self) -> Dict[Karmendriya, IndriyaProtocol]:
        """Get all 5 action senses."""
        ...

    def get_indriya(self, indriya: IndriyaType) -> Optional[IndriyaProtocol]:
        """Get a specific Indriya by type."""
        ...

    def get_active_indriyas(self) -> List[IndriyaProtocol]:
        """Get all currently active Indriyas."""
        ...

    def get_indriyas_by_vrtti(self, vrtti: Vrtti) -> List[IndriyaProtocol]:
        """Get all Indriyas in a specific vrtti state."""
        ...

    def broadcast_tanmatra(self, message: TanmatraMessage) -> int:
        """
        Broadcast a Tanmatra to all connected Indriyas.

        Returns count of Indriyas that received it.
        """
        ...


# =============================================================================
# VALIDATION
# =============================================================================

# Verify the sacred numbers
assert len(Karmendriya) == KARMENDRIYA_COUNT, "Must have exactly 5 action senses"
assert len(Vrtti) == VRTTI_COUNT, "Must have exactly 5 vrttis"
assert JNANENDRIYA_COUNT + KARMENDRIYA_COUNT == DASHA_INDRIYA, "Total must be 10"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "DASHA_INDRIYA",
    "KARMENDRIYA_COUNT",
    "VRTTI_COUNT",
    # Enums (new)
    "Karmendriya",
    "Vrtti",
    "TanmatraIntent",
    # Re-exports from _sense.py (for convenience)
    "Tanmatra",
    "Mahabhuta",
    "Jnanendriya",
    # Types
    "IndriyaType",
    "get_indriya_category",
    # Data classes
    "IndriyaState",
    "TanmatraMessage",
    # Protocols
    "IndriyaProtocol",
    "IndriyaGanaProtocol",
]
