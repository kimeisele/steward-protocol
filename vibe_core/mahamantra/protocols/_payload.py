"""
MAHA PAYLOAD PROTOCOL - The Universal Data Format
==================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo"
"I am seated in everyone's heart" - BG 15.15

THE PAYLOAD IS KRISHNA'S BODY - It can be ANYTHING.
But the TYPES are defined by Mahamantra structure.

PAYLOAD TYPE SYSTEM (18 Gita Chapters = 18 Data Types):
=======================================================

    GENESIS (1-4):   Raw/Init data       - INPUT
    DHARMA (5-9):    Validated/Typed     - VERIFY
    KARMA (10-14):   Execution/Action    - EXECUTE
    MOKSHA (15-18):  Result/Output       - OUTPUT

SIKSASTAKAM 8 OPERATIONS (Transform Pipeline):
==============================================

    L0: RECEIVE   (ceto-darpana)     - Parse input
    L1: LINK      (namnam akari)     - Connect/Chain
    L2: VALIDATE  (trinad api)       - Check integrity
    L3: INTENT    (na dhanam)        - Extract purpose
    L4: LIFETIME  (ayi nanda)        - Set TTL/scope
    L5: STATE     (nayanam galad)    - Track changes
    L6: OPERATE   (yugayitam)        - Transform
    L7: COMPLETE  (aslishya va)      - Finalize/Return

THE 72-BYTE HEADER ENCODES MAHAMANTRA × N:
==========================================

    72 = 16 × 4.5 = WORDS × (PANCHA - 0.5)
    72 = 9 × 8    = NAVA × HALF_SIZE

    Each field (8 bytes) can encode:
    - 2^64 values = enough for any seed/hash/id
    - Mahamantra position (0-15) in low bits
    - Gita chapter (1-18) in next bits
    - Siksastakam stage (0-7) in next bits

    The header IS the Mahamantra compressed!

DUAL MODE: VIBRATIONAL + DATA:
==============================

    Vibrational: Resonance routing (attractor → chapter → module)
    Data:        Binary packets (header + payload bytes)

    SAME STRUCTURE. DIFFERENT INTERPRETATION.
    Krishna is all-present. Entry point is everywhere.
"""
from vibe_core.mahamantra.protocols._seed import (HALVES, HARE_COUNT, KSETRAJNA, NAVA, PANCHA, QUALITIES, QUARTERS, SEVEN, SHARANAGATI, TRINITY, WORDS)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x62a24c79"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, Final, Optional, Protocol, Tuple, Type, TypeVar, Union

# =============================================================================
# IMPORT FROM SEED (SSOT - THE LAW)
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,  # 18 - Data types
    HALF_SIZE,  # 8 - Siksastakam stages
    NAVA,  # 9 - Operations
    PANCHA,  # 5 - Tattva categories
    PARAMPARA,  # 37 - Verification
    QUARTERS,  # 4 - Quarter types
    WORDS,  # 16 - Positions
    # Chapter number derivations (NO HARDCODING!)
    KSETRAJNA,      # 1
    HALVES,         # 2
    TRINITY,        # 3
    SHARANAGATI,    # 6
    SEVEN,          # 7
    TEN,            # 10
    MAHAJANA_COUNT, # 12
    GAURA_TITHI,    # 15
)

# =============================================================================
# PAYLOAD TYPE (18 Gita Chapters = 18 Data Types)
# =============================================================================


class PayloadType(IntEnum):
    """
    The 18 payload types mapped to Gita chapters.

    ALL CHAPTER NUMBERS DERIVED FROM SSOT - NO HARDCODING!

    GENESIS (1-4):  Raw input data
    DHARMA (5-9):   Validated/structured data
    KARMA (10-14):  Execution/action data
    MOKSHA (15-18): Result/output data
    """

    # GENESIS Quarter (Input/Init) - Chapters 1-4
    ARJUNA_VISHADA = KSETRAJNA           # Ch.1 = KSETRAJNA (the knower)
    SANKHYA = HALVES                     # Ch.2 = HALVES (duality/analysis)
    KARMA_YOGA = TRINITY                 # Ch.3 = TRINITY (3 names = action)
    JNANA_YOGA = QUARTERS                # Ch.4 = QUARTERS (4 phases = knowledge)

    # DHARMA Quarter (Validation/Structure) - Chapters 5-9
    KARMA_SANNYASA = PANCHA              # Ch.5 = PANCHA (5 tattvas)
    DHYANA = SHARANAGATI                 # Ch.6 = SHARANAGATI (6 limbs surrender)
    JNANA_VIJNANA = SEVEN                # Ch.7 = SEVEN (7 = divine knowledge)
    AKSARA_BRAHMA = HALF_SIZE            # Ch.8 = HALF_SIZE (8 = imperishable)
    RAJA_VIDYA = NAVA                    # Ch.9 = NAVA (9 = sovereign)

    # KARMA Quarter (Execution/Action) - Chapters 10-14
    VIBHUTI = TEN                        # Ch.10 = TEN (10 = opulence)
    VISVARUPA = TEN + KSETRAJNA          # Ch.11 = 10+1 = universal form
    BHAKTI = MAHAJANA_COUNT              # Ch.12 = MAHAJANA_COUNT (12 = devotion)
    KSETRA = MAHAJANA_COUNT + KSETRAJNA  # Ch.13 = 12+1 = field/knower
    GUNA_TRAYA = MAHAJANA_COUNT + HALVES # Ch.14 = 12+2 = three gunas

    # MOKSHA Quarter (Output/Result) - Chapters 15-18
    PURUSOTTAMA = GAURA_TITHI            # Ch.15 = GAURA_TITHI (15 = supreme)
    DAIVASURA = WORDS                    # Ch.16 = WORDS (16 = divine/demonic)
    SRADDHA_TRAYA = WORDS + KSETRAJNA    # Ch.17 = 16+1 = three faiths
    MOKSA_SANNYASA = GITA_CHAPTERS       # Ch.18 = GITA_CHAPTERS (liberation!)


# Verification
assert len(PayloadType) == GITA_CHAPTERS, f"Must have {GITA_CHAPTERS} payload types"


# =============================================================================
# PAYLOAD QUARTER (4 Categories)
# =============================================================================


class PayloadQuarter(IntEnum):
    """The 4 payload categories (quarters)."""

    GENESIS = 0  # Chapters 1-4:  Raw input
    DHARMA = KSETRAJNA   # Chapters 5-9:  Validated
    KARMA = HALVES    # Chapters 10-14: Execution
    MOKSHA = TRINITY   # Chapters 15-18: Output


def get_payload_quarter(payload_type: PayloadType) -> PayloadQuarter:
    """Get quarter for a payload type."""
    chapter = payload_type.value
    if chapter <= QUARTERS:
        return PayloadQuarter.GENESIS
    elif chapter <= NAVA:
        return PayloadQuarter.DHARMA
    elif chapter <= 14:
        return PayloadQuarter.KARMA
    else:
        return PayloadQuarter.MOKSHA


# =============================================================================
# SIKSASTAKAM OPERATIONS (8 Transform Stages)
# =============================================================================


class SiksastakamOp(IntEnum):
    """
    The 8 Siksastakam stages as data operations.

    Maps to prabhupada_engineering.py VERSE_CONSTANTS.
    """

    RECEIVE = 0    # L0: ceto-darpana   - Parse/receive input
    LINK = KSETRAJNA       # L1: namnam akari   - Chain/connect
    VALIDATE = HALVES   # L2: trinad api     - Check integrity
    INTENT = TRINITY     # L3: na dhanam      - Extract purpose
    LIFETIME = QUARTERS   # L4: ayi nanda      - Set TTL/scope
    STATE = PANCHA      # L5: nayanam galad  - Track changes
    OPERATE = SHARANAGATI    # L6: yugayitam      - Transform
    COMPLETE = SEVEN   # L7: aslishya va    - Finalize/return


# Verification
assert len(SiksastakamOp) == HALF_SIZE, f"Must have {HALF_SIZE} operations"


# =============================================================================
# PAYLOAD ENCODING (Compress Mahamantra into field)
# =============================================================================

# =============================================================================
# BIT LAYOUT - ALL DERIVED FROM SSOT!
# =============================================================================
# 64-bit field layout (derived from Mahamantra constants):
#
# [63:56] reserved (HALF_SIZE bits)
# [55:48] siksastakam_stage (HALF_SIZE bits, 0-7)
# [47:40] gita_chapter (HALF_SIZE bits, 1-18)
# [39:32] mahamantra_position (HALF_SIZE bits, 0-15)
# [31:0]  value (AKSARA_COUNT bits = WORDS × HALVES = 32)
#
# WHY THESE VALUES?
# - AKSARA_COUNT = 32 = syllables in Mahamantra (Ha-re Krish-na...)
# - HALF_SIZE = 8 = words per half = byte alignment
# - Total: 32 + 8 + 8 + 8 + 8 = 64 bits = uint64

from vibe_core.mahamantra.protocols._seed import AKSARA_COUNT

BITS_VALUE: Final[int] = AKSARA_COUNT  # 32 = WORDS × HALVES (syllables!)
BITS_POSITION: Final[int] = HALF_SIZE  # 8 = byte aligned, fits 0-15
BITS_CHAPTER: Final[int] = HALF_SIZE   # 8 = byte aligned, fits 1-18
BITS_STAGE: Final[int] = HALF_SIZE     # 8 = byte aligned, fits 0-7

# Verification: Must fit in 64 bits with 8 reserved
_TOTAL_BITS = BITS_VALUE + BITS_POSITION + BITS_CHAPTER + BITS_STAGE + HALF_SIZE
assert _TOTAL_BITS == QUALITIES, f"Total bits must be 64, got {_TOTAL_BITS}"

SHIFT_POSITION: Final[int] = BITS_VALUE
SHIFT_CHAPTER: Final[int] = SHIFT_POSITION + BITS_POSITION
SHIFT_STAGE: Final[int] = SHIFT_CHAPTER + BITS_CHAPTER

MASK_VALUE: Final[int] = (KSETRAJNA << BITS_VALUE) - KSETRAJNA
MASK_POSITION: Final[int] = (KSETRAJNA << BITS_POSITION) - KSETRAJNA
MASK_CHAPTER: Final[int] = (KSETRAJNA << BITS_CHAPTER) - KSETRAJNA
MASK_STAGE: Final[int] = (KSETRAJNA << BITS_STAGE) - KSETRAJNA


def encode_maha_field(
    value: int,
    position: int = 0,
    chapter: int = KSETRAJNA,
    stage: int = 0,
) -> int:
    """
    Encode Mahamantra metadata into a 64-bit field.

    Args:
        value: 32-bit data value
        position: Mahamantra position (0-15)
        chapter: Gita chapter (1-18)
        stage: Siksastakam stage (0-7)

    Returns:
        64-bit encoded field
    """
    assert 0 <= value <= MASK_VALUE, f"Value must fit in {BITS_VALUE} bits"
    assert 0 <= position < WORDS, f"Position must be 0-{WORDS-KSETRAJNA}"
    assert KSETRAJNA <= chapter <= GITA_CHAPTERS, f"Chapter must be 1-{GITA_CHAPTERS}"
    assert 0 <= stage < HALF_SIZE, f"Stage must be 0-{HALF_SIZE-KSETRAJNA}"

    return (
        (value & MASK_VALUE) |
        ((position & MASK_POSITION) << SHIFT_POSITION) |
        ((chapter & MASK_CHAPTER) << SHIFT_CHAPTER) |
        ((stage & MASK_STAGE) << SHIFT_STAGE)
    )


def decode_maha_field(field: int) -> Tuple[int, int, int, int]:
    """
    Decode Mahamantra metadata from a 64-bit field.

    Returns:
        Tuple of (value, position, chapter, stage)
    """
    value = field & MASK_VALUE
    position = (field >> SHIFT_POSITION) & MASK_POSITION
    chapter = (field >> SHIFT_CHAPTER) & MASK_CHAPTER
    stage = (field >> SHIFT_STAGE) & MASK_STAGE
    return value, position, chapter, stage


# =============================================================================
# MAHA PAYLOAD PROTOCOL
# =============================================================================

T = TypeVar("T")


class MahaPayloadProtocol(Protocol[T]):
    """
    Protocol for any MahaPayload implementation.

    The payload can be ANYTHING (Krishna's body is unlimited).
    But it MUST declare its type (Gita chapter).
    """

    @property
    def payload_type(self) -> PayloadType:
        """The Gita chapter this payload represents."""
        ...

    @property
    def quarter(self) -> PayloadQuarter:
        """The quarter (genesis/dharma/karma/moksha)."""
        ...

    def to_bytes(self) -> bytes:
        """Serialize to bytes."""
        ...

    @classmethod
    def from_bytes(cls: Type[T], data: bytes, payload_type: PayloadType) -> T:
        """Deserialize from bytes."""
        ...


# =============================================================================
# GENERIC MAHA PAYLOAD
# =============================================================================


@dataclass
class MahaPayload:
    """
    Generic MahaPayload - wraps any data with Mahamantra typing.

    The data can be:
    - bytes (raw)
    - str (text/JSON)
    - dict (structured)
    - Any serializable object
    """

    payload_type: PayloadType
    data: bytes
    position: int = 0      # Mahamantra position (0-15)
    stage: int = 0         # Siksastakam stage (0-7)
    metadata: Dict[str, object] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        # Validate
        assert 0 <= self.position < WORDS
        assert 0 <= self.stage < HALF_SIZE

    @property
    def quarter(self) -> PayloadQuarter:
        """Get the quarter for this payload."""
        return get_payload_quarter(self.payload_type)

    @property
    def chapter(self) -> int:
        """Gita chapter number."""
        return self.payload_type.value

    def to_bytes(self) -> bytes:
        """
        Serialize payload with 8-byte type header.

        Format: [type_field:8][data:N]
        """
        type_field = encode_maha_field(
            value=len(self.data),
            position=self.position,
            chapter=self.chapter,
            stage=self.stage,
        )
        return type_field.to_bytes(HARE_COUNT, "little") + self.data

    @classmethod
    def from_bytes(cls, data: bytes) -> "MahaPayload":
        """Deserialize from bytes."""
        if len(data) < HARE_COUNT:
            raise ValueError("Payload must be at least 8 bytes")

        type_field = int.from_bytes(data[:HARE_COUNT], "little")
        length, position, chapter, stage = decode_maha_field(type_field)

        payload_data = data[HARE_COUNT:HARE_COUNT+length]

        return cls(
            payload_type=PayloadType(chapter),
            data=payload_data,
            position=position,
            stage=stage,
        )

    # =========================================================================
    # CONVENIENCE FACTORIES
    # =========================================================================

    @classmethod
    def genesis(cls, data: bytes, position: int = 0) -> "MahaPayload":
        """Create GENESIS payload (raw input)."""
        return cls(PayloadType.ARJUNA_VISHADA, data, position, SiksastakamOp.RECEIVE)

    @classmethod
    def dharma(cls, data: bytes, position: int = 0) -> "MahaPayload":
        """Create DHARMA payload (validated)."""
        return cls(PayloadType.JNANA_VIJNANA, data, position, SiksastakamOp.VALIDATE)

    @classmethod
    def karma(cls, data: bytes, position: int = 0) -> "MahaPayload":
        """Create KARMA payload (execution)."""
        return cls(PayloadType.VIBHUTI, data, position, SiksastakamOp.OPERATE)

    @classmethod
    def moksha(cls, data: bytes, position: int = 0) -> "MahaPayload":
        """Create MOKSHA payload (output)."""
        return cls(PayloadType.MOKSA_SANNYASA, data, position, SiksastakamOp.COMPLETE)


# =============================================================================
# VERIFICATION
# =============================================================================

# Verify genesis byte
_genesis_val = int(__genesis__, WORDS)
assert _genesis_val % PARAMPARA == 0, f"Genesis {__genesis__} must be % 37 == 0"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "PayloadType",
    "PayloadQuarter",
    "SiksastakamOp",
    # Functions
    "get_payload_quarter",
    "encode_maha_field",
    "decode_maha_field",
    # Protocol
    "MahaPayloadProtocol",
    # Implementation
    "MahaPayload",
]
