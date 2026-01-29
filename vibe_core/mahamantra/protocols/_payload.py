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
)

# =============================================================================
# PAYLOAD TYPE (18 Gita Chapters = 18 Data Types)
# =============================================================================


class PayloadType(IntEnum):
    """
    The 18 payload types mapped to Gita chapters.

    GENESIS (1-4):  Raw input data
    DHARMA (5-9):   Validated/structured data
    KARMA (10-14):  Execution/action data
    MOKSHA (15-18): Result/output data
    """

    # GENESIS Quarter (Input/Init)
    ARJUNA_VISHADA = 1   # Ch.1: Raw problem statement
    SANKHYA = 2          # Ch.2: Analysis/breakdown
    KARMA_YOGA = 3       # Ch.3: Action plan
    JNANA_YOGA = 4       # Ch.4: Knowledge context

    # DHARMA Quarter (Validation/Structure)
    KARMA_SANNYASA = 5   # Ch.5: Filtered/renounced data
    DHYANA = 6           # Ch.6: Focused/meditated data
    JNANA_VIJNANA = 7    # Ch.7: Typed/classified data
    AKSARA_BRAHMA = 8    # Ch.8: Immutable/cached data
    RAJA_VIDYA = 9       # Ch.9: Sovereign/authoritative data

    # KARMA Quarter (Execution/Action)
    VIBHUTI = 10         # Ch.10: Manifest/expanded data
    VISVARUPA = 11       # Ch.11: Universal/complete data
    BHAKTI = 12          # Ch.12: Devotional/connected data
    KSETRA = 13          # Ch.13: Field/context data
    GUNA_TRAYA = 14      # Ch.14: Mode/quality data

    # MOKSHA Quarter (Output/Result)
    PURUSOTTAMA = 15     # Ch.15: Supreme/final data
    DAIVASURA = 16       # Ch.16: Classified/evaluated data
    SRADDHA_TRAYA = 17   # Ch.17: Faith/confidence data
    MOKSA_SANNYASA = 18  # Ch.18: Liberation/completion data


# Verification
assert len(PayloadType) == GITA_CHAPTERS, f"Must have {GITA_CHAPTERS} payload types"


# =============================================================================
# PAYLOAD QUARTER (4 Categories)
# =============================================================================


class PayloadQuarter(IntEnum):
    """The 4 payload categories (quarters)."""

    GENESIS = 0  # Chapters 1-4:  Raw input
    DHARMA = 1   # Chapters 5-9:  Validated
    KARMA = 2    # Chapters 10-14: Execution
    MOKSHA = 3   # Chapters 15-18: Output


def get_payload_quarter(payload_type: PayloadType) -> PayloadQuarter:
    """Get quarter for a payload type."""
    chapter = payload_type.value
    if chapter <= 4:
        return PayloadQuarter.GENESIS
    elif chapter <= 9:
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
    LINK = 1       # L1: namnam akari   - Chain/connect
    VALIDATE = 2   # L2: trinad api     - Check integrity
    INTENT = 3     # L3: na dhanam      - Extract purpose
    LIFETIME = 4   # L4: ayi nanda      - Set TTL/scope
    STATE = 5      # L5: nayanam galad  - Track changes
    OPERATE = 6    # L6: yugayitam      - Transform
    COMPLETE = 7   # L7: aslishya va    - Finalize/return


# Verification
assert len(SiksastakamOp) == HALF_SIZE, f"Must have {HALF_SIZE} operations"


# =============================================================================
# PAYLOAD ENCODING (Compress Mahamantra into field)
# =============================================================================

# Bit layout for a 64-bit field:
# [63:56] reserved (8 bits)
# [55:48] siksastakam_stage (8 bits, 0-7)
# [47:40] gita_chapter (8 bits, 1-18)
# [39:32] mahamantra_position (8 bits, 0-15)
# [31:0]  value (32 bits, actual data)

BITS_VALUE: Final[int] = 32
BITS_POSITION: Final[int] = 8
BITS_CHAPTER: Final[int] = 8
BITS_STAGE: Final[int] = 8

SHIFT_POSITION: Final[int] = BITS_VALUE
SHIFT_CHAPTER: Final[int] = SHIFT_POSITION + BITS_POSITION
SHIFT_STAGE: Final[int] = SHIFT_CHAPTER + BITS_CHAPTER

MASK_VALUE: Final[int] = (1 << BITS_VALUE) - 1
MASK_POSITION: Final[int] = (1 << BITS_POSITION) - 1
MASK_CHAPTER: Final[int] = (1 << BITS_CHAPTER) - 1
MASK_STAGE: Final[int] = (1 << BITS_STAGE) - 1


def encode_maha_field(
    value: int,
    position: int = 0,
    chapter: int = 1,
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
    assert 0 <= position < WORDS, f"Position must be 0-{WORDS-1}"
    assert 1 <= chapter <= GITA_CHAPTERS, f"Chapter must be 1-{GITA_CHAPTERS}"
    assert 0 <= stage < HALF_SIZE, f"Stage must be 0-{HALF_SIZE-1}"

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
    metadata: Dict[str, Any] = None

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
        return type_field.to_bytes(8, "little") + self.data

    @classmethod
    def from_bytes(cls, data: bytes) -> "MahaPayload":
        """Deserialize from bytes."""
        if len(data) < 8:
            raise ValueError("Payload must be at least 8 bytes")

        type_field = int.from_bytes(data[:8], "little")
        length, position, chapter, stage = decode_maha_field(type_field)

        payload_data = data[8:8+length]

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
_genesis_val = int(__genesis__, 16)
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
