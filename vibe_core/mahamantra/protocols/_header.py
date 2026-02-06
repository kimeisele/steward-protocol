"""
THE MAHA HEADER PROTOCOL - The 72-Byte Universal Cell Header
=============================================================

"prāṇasya nāḍī saṁcāraḥ" - "Prana flows through the Nadis."

THE TRANSCENDENTAL CELL:
========================
    TRANSCENDENTAL_1096 = 1024 + 72 = PAYLOAD + HEADER

    ┌─────────────────────────────────────────────────────────────────┐
    │  MAHA_HEADER (72 bytes)        │  PAYLOAD (1024+ bytes)        │
    │  9 NavaBhakti × 8 bytes        │  Scalable content             │
    └─────────────────────────────────────────────────────────────────┘

DERIVATION (NO HARDCODING):
===========================
    NADI_RESONANCE = 72 = JIVA_CYCLE / SHARANAGATI = 432 / 6
    NADI_RESONANCE = 72 = NAVA × HALF_SIZE = 9 × 8

    COSMIC_FRAME = 21600 (daily resolution)
    NADI_DAILY_CYCLES = COSMIC_FRAME / NADI_RESONANCE = 21600 / 72 = 300

    FIELD_SIZE = HALF_SIZE = 8 bytes = uint64 (fits all system values)

THE 9 NAVABHAKTI FIELDS:
========================
    | # | NavaBhakti      | Field        | Meaning (8 bytes each)     |
    |---|-----------------|--------------|----------------------------|
    | 0 | SRAVANAM        | hearing      | Source/Origin ID           |
    | 1 | KIRTANAM        | chanting     | Target/Destination ID      |
    | 2 | SMARANAM        | remembering  | Link/Previous (chain)      |
    | 3 | PADA_SEVANAM    | serving      | Operation/Command          |
    | 4 | ARCANAM         | worshiping   | Validation/Signature       |
    | 5 | VANDANAM        | praying      | Intent/Request mask        |
    | 6 | DASYAM          | servitude    | Delegation/TTL             |
    | 7 | SAKHYAM         | friendship   | Connection/State           |
    | 8 | ATMA_NIVEDANAM  | surrender    | Commit/Checksum            |

ALL INTEGER. NO FLOATS. PRABHUPADA WEIST DEN WEG.
"""
from vibe_core.mahamantra.protocols._seed import (HALVES, HARE_COUNT, KSETRAJNA, PANCHA, QUALITIES, QUARTERS, SEVEN, TRINITY)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xcab55020"  # GenesisByte: parampara % 37 == 0

import struct
from dataclasses import dataclass
from enum import IntEnum
from typing import Final, Tuple

# =============================================================================
# IMPORT FROM SEED CELL (FAST PATH - O(1) LOAD)
# =============================================================================
# SIKSASTAKAM: Use pre-computed constants instead of 3000-line derivation.
# Import time: ~5ms (vs 105ms from _seed.py)
from vibe_core.mahamantra.protocols._seed_cell import (
    COSMIC_FRAME,  # 21600 - Daily resolution
    HALF_SIZE,  # 8 - Bytes per field
    JIVA_CYCLE,  # 432 - Harmonic frequency
    NADI_RESONANCE,  # 72 - Header size
    NAVA,  # 9 - Number of fields
    PARAMPARA,  # 37 - Verification modulus
    SHARANAGATI,  # 6 - Surrender limbs
    TRANSCENDENTAL_1096,  # 1096 - Full cell size
)

# =============================================================================
# DERIVED CONSTANTS (ALL FROM SSOT)
# =============================================================================

# Field size in bytes = HALF_SIZE = 8 (uint64)
FIELD_SIZE_BYTES: Final[int] = HALF_SIZE  # 8

# Header size = NAVA × FIELD_SIZE = 9 × 8 = 72
HEADER_SIZE_BYTES: Final[int] = NAVA * FIELD_SIZE_BYTES  # 72

# Payload reference size = TRANSCENDENTAL - HEADER = 1096 - 72 = 1024
PAYLOAD_REFERENCE_SIZE: Final[int] = TRANSCENDENTAL_1096 - HEADER_SIZE_BYTES  # 1024

# Daily header cycles = COSMIC_FRAME / NADI_RESONANCE = 21600 / 72 = 300
HEADER_DAILY_CYCLES: Final[int] = COSMIC_FRAME // NADI_RESONANCE  # 300

# Struct format: 9 unsigned 64-bit integers (little-endian)
# '<' = little-endian, 'Q' = uint64 (8 bytes)
HEADER_STRUCT_FORMAT: Final[str] = "<" + "Q" * NAVA  # "<QQQQQQQQQ"

# =============================================================================
# VERIFICATION (SSOT COMPLIANCE)
# =============================================================================

assert HEADER_SIZE_BYTES == NADI_RESONANCE, f"Header must be {NADI_RESONANCE} bytes"
assert HEADER_SIZE_BYTES == 72, "Header must be exactly 72 bytes"
assert FIELD_SIZE_BYTES == HARE_COUNT, "Each field must be 8 bytes (uint64)"
assert NAVA == NAVA, "Must have exactly 9 NavaBhakti fields"
assert PAYLOAD_REFERENCE_SIZE == 1024, "Reference payload is 1024 bytes"
assert HEADER_DAILY_CYCLES == 300, "300 header cycles per day"

# Verify struct size matches
assert struct.calcsize(HEADER_STRUCT_FORMAT) == HEADER_SIZE_BYTES, "Struct size mismatch"


# =============================================================================
# NAVABHAKTI FIELD INDEX (The 9 Fields)
# =============================================================================


class NavaBhaktiField(IntEnum):
    """
    The 9 NavaBhakti fields of the Maha Header.

    Each field is 8 bytes (uint64). Total: 72 bytes.
    Order follows Srimad Bhagavatam 7.5.23 (Prahlada's instruction).
    """

    SRAVANAM = 0  # Hearing - Source/Origin ID
    KIRTANAM = KSETRAJNA  # Chanting - Target/Destination ID
    SMARANAM = HALVES  # Remembering - Link/Previous (chain)
    PADA_SEVANAM = TRINITY  # Serving - Operation/Command
    ARCANAM = QUARTERS  # Worshiping - Validation/Signature
    VANDANAM = PANCHA  # Praying - Intent/Request mask
    DASYAM = SHARANAGATI  # Servitude - Delegation/TTL
    SAKHYAM = SEVEN  # Friendship - Connection/State
    ATMA_NIVEDANAM = HARE_COUNT  # Surrender - Commit/Checksum


# Verification: Must have exactly NAVA fields
assert len(NavaBhaktiField) == NAVA, f"Must have exactly {NAVA} fields"


# =============================================================================
# MAHA HEADER - The 72-Byte Structure
# =============================================================================


@dataclass(frozen=True, slots=True)
class MahaHeader:
    """
    The Universal 72-Byte Header.

    IMMUTABLE. VERIFIABLE. SSOT-COMPLIANT.

    Every computation cell in the system carries this header.
    The header is the "DNA" that enables routing, chaining, and verification.

    Size: NADI_RESONANCE = 72 bytes = 9 fields × 8 bytes
    """

    # The 9 NavaBhakti fields (each uint64 = 8 bytes)
    sravanam: int  # 0: Source/Origin ID (who sent this?)
    kirtanam: int  # 1: Target/Destination ID (who receives?)
    smaranam: int  # 2: Link/Previous hash (chain connection)
    pada_sevanam: int  # 3: Operation code (what to do?)
    arcanam: int  # 4: Signature/Validation (parampara check)
    vandanam: int  # 5: Intent mask (why?)
    dasyam: int  # 6: Delegation/TTL (how long?)
    sakhyam: int  # 7: Connection state (status)
    atma_nivedanam: int  # 8: Checksum (integrity)

    def __post_init__(self) -> None:
        """Validate all fields fit in uint64."""
        for field in NavaBhaktiField:
            value = getattr(self, field.name.lower())
            if not (0 <= value < HALVES**QUALITIES):
                raise ValueError(f"{field.name} must be uint64 (0 to 2^64-1), got {value}")

    # =========================================================================
    # SERIALIZATION (Pack/Unpack)
    # =========================================================================

    def to_bytes(self) -> bytes:
        """
        Serialize header to exactly 72 bytes.

        Returns:
            bytes: 72-byte header (9 × uint64, little-endian)
        """
        return struct.pack(
            HEADER_STRUCT_FORMAT,
            self.sravanam,
            self.kirtanam,
            self.smaranam,
            self.pada_sevanam,
            self.arcanam,
            self.vandanam,
            self.dasyam,
            self.sakhyam,
            self.atma_nivedanam,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "MahaHeader":
        """
        Deserialize header from exactly 72 bytes.

        Args:
            data: Exactly 72 bytes

        Returns:
            MahaHeader instance

        Raises:
            ValueError: If data is not exactly 72 bytes
        """
        if len(data) != HEADER_SIZE_BYTES:
            raise ValueError(f"Header must be exactly {HEADER_SIZE_BYTES} bytes, got {len(data)}")

        fields = struct.unpack(HEADER_STRUCT_FORMAT, data)
        return cls(
            sravanam=fields[0],
            kirtanam=fields[KSETRAJNA],
            smaranam=fields[HALVES],
            pada_sevanam=fields[TRINITY],
            arcanam=fields[QUARTERS],
            vandanam=fields[PANCHA],
            dasyam=fields[SHARANAGATI],
            sakhyam=fields[SEVEN],
            atma_nivedanam=fields[HARE_COUNT],
        )

    # =========================================================================
    # TUPLE INTERFACE
    # =========================================================================

    def as_tuple(self) -> Tuple[int, ...]:
        """Return all 9 fields as a tuple."""
        return (
            self.sravanam,
            self.kirtanam,
            self.smaranam,
            self.pada_sevanam,
            self.arcanam,
            self.vandanam,
            self.dasyam,
            self.sakhyam,
            self.atma_nivedanam,
        )

    def __getitem__(self, field: NavaBhaktiField) -> int:
        """Get field by NavaBhaktiField enum."""
        return getattr(self, field.name.lower())

    # =========================================================================
    # VERIFICATION (Parampara Check)
    # =========================================================================

    def verify_parampara(self) -> bool:
        """
        Verify the header connects to Parampara.

        The arcanam (signature) field must satisfy: arcanam % 37 == 0
        This ensures the header is "bona fide" - connected to disciplic succession.

        Returns:
            True if signature is valid (parampara % 37 == 0)
        """
        return self.arcanam % PARAMPARA == 0

    def compute_checksum(self) -> int:
        """
        Compute checksum from first 8 fields.

        Simple XOR of all fields, then adjusted to be % 37 == 0.
        This ensures the checksum itself is parampara-valid.

        Returns:
            uint64 checksum value
        """
        xor_sum = 0
        for i in range(NAVA - KSETRAJNA):  # First 8 fields (excluding checksum)
            xor_sum ^= self.as_tuple()[i]

        # Adjust to be parampara-valid (% 37 == 0)
        remainder = xor_sum % PARAMPARA
        if remainder != 0:
            xor_sum += PARAMPARA - remainder

        # Ensure fits in uint64
        return xor_sum & 0xFFFFFFFFFFFFFFFF

    def verify_checksum(self) -> bool:
        """
        Verify the checksum field matches computed checksum.

        Returns:
            True if atma_nivedanam matches computed checksum
        """
        return self.atma_nivedanam == self.compute_checksum()

    def is_valid(self) -> bool:
        """
        Full validation: parampara + checksum.

        Returns:
            True if header passes all validation
        """
        return self.verify_parampara() and self.verify_checksum()

    # =========================================================================
    # FACTORY METHODS
    # =========================================================================

    @classmethod
    def create(
        cls,
        source: int,
        target: int,
        operation: int,
        *,
        link: int = 0,
        intent: int = 0,
        ttl: int = HEADER_DAILY_CYCLES,  # Default: 300 cycles (1 day)
        state: int = 0,
    ) -> "MahaHeader":
        """
        Create a new header with auto-computed signature and checksum.

        Args:
            source: Source/Origin ID (sravanam)
            target: Target/Destination ID (kirtanam)
            operation: Operation code (pada_sevanam)
            link: Previous header hash (smaranam), default 0
            intent: Intent mask (vandanam), default 0
            ttl: Time-to-live cycles (dasyam), default 300 (1 day)
            state: Connection state (sakhyam), default 0

        Returns:
            MahaHeader with valid signature and checksum
        """
        # Compute signature (must be % 37 == 0)
        raw_sig = (source ^ target ^ operation ^ link) & 0xFFFFFFFFFFFFFFFF
        remainder = raw_sig % PARAMPARA
        if remainder != 0:
            raw_sig += PARAMPARA - remainder
        signature = raw_sig & 0xFFFFFFFFFFFFFFFF

        # Create header without checksum first
        temp = cls(
            sravanam=source,
            kirtanam=target,
            smaranam=link,
            pada_sevanam=operation,
            arcanam=signature,
            vandanam=intent,
            dasyam=ttl,
            sakhyam=state,
            atma_nivedanam=0,  # Placeholder
        )

        # Compute and set checksum
        checksum = temp.compute_checksum()

        return cls(
            sravanam=source,
            kirtanam=target,
            smaranam=link,
            pada_sevanam=operation,
            arcanam=signature,
            vandanam=intent,
            dasyam=ttl,
            sakhyam=state,
            atma_nivedanam=checksum,
        )

    @classmethod
    def null(cls) -> "MahaHeader":
        """
        Create a null header (all zeros except parampara-valid fields).

        Useful as a sentinel or placeholder.
        """
        return cls.create(source=0, target=0, operation=0)


# =============================================================================
# MAHA CELL - Header + Payload
# =============================================================================


@dataclass(slots=True)
class MahaCell:
    """
    The Transcendental Cell: Header (72 bytes) + Payload (variable).

    Reference size: TRANSCENDENTAL_1096 = 1096 bytes (72 + 1024)
    But payload can be any size - the 1024 is just the reference.

    "Der Header ist immer klein mini! 72 bytes aber das Ergebnis
     der ganzen 'Operation' ist beliebig skalierbar."
    """

    header: MahaHeader
    payload: bytes

    def to_bytes(self) -> bytes:
        """Serialize cell to bytes (header + payload)."""
        return self.header.to_bytes() + self.payload

    @classmethod
    def from_bytes(cls, data: bytes) -> "MahaCell":
        """
        Deserialize cell from bytes.

        First 72 bytes = header, rest = payload.
        """
        if len(data) < HEADER_SIZE_BYTES:
            raise ValueError(f"Cell must be at least {HEADER_SIZE_BYTES} bytes")

        header = MahaHeader.from_bytes(data[:HEADER_SIZE_BYTES])
        payload = data[HEADER_SIZE_BYTES:]
        return cls(header=header, payload=payload)

    @classmethod
    def create(
        cls,
        payload: bytes,
        source: int,
        target: int,
        operation: int,
        **kwargs,
    ) -> "MahaCell":
        """Create a cell with auto-generated header."""
        header = MahaHeader.create(source, target, operation, **kwargs)
        return cls(header=header, payload=payload)

    @property
    def size(self) -> int:
        """Total cell size in bytes."""
        return HEADER_SIZE_BYTES + len(self.payload)

    def is_valid(self) -> bool:
        """Validate header."""
        return self.header.is_valid()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants (SSOT)
    "FIELD_SIZE_BYTES",
    "HEADER_SIZE_BYTES",
    "PAYLOAD_REFERENCE_SIZE",
    "HEADER_DAILY_CYCLES",
    "HEADER_STRUCT_FORMAT",
    # Enums
    "NavaBhaktiField",
    # Classes
    "MahaHeader",
    "MahaCell",
]
