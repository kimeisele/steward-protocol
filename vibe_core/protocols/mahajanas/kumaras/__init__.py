"""
KUMARAS - The 4th Mahajana (Purity/Reset)
=========================================
OpCode: RESET_IP (Bit 16, Position 16 in Mahamantra)
Opulence: Shri (Beauty/Fortune)

The Four Kumaras - Sanaka, Sanandana, Sanatana, Sanat-kumara.
Eternally five years old. Eternally pure.
First sons of Brahma who refused to create.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Kumaras are the PERSONS responsible for all purity.
Not abstract "sanitization" - PERSONAL purification by Kumaras.

OWNED PROTOCOLS:
- Instruction Pointer Reset (RESET_IP OpCode)
- State Reset
- Sanitization
- Input Validation
- Shuddhi (Purification)

A polluted system cannot function. Kumaras restore purity.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.KUMARAS
LOTUS_POSITION: Final[int] = 5  # DHARMA Quarter, Worker 1
LOTUS_QUARTER: Final[str] = "dharma"

OWNED_PROTOCOLS: Final[List[str]] = [
    "kumaras",
    "purity",
    "reset",
    "sanitization",
    "validation",
    "shuddhi",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.RESOLVE_REQ,  # Vyuha: Q2 Worker 1 (RESET_IP -> Yamaraja)
]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

# The union of allowed data types for purification - WATERTIGHT
PurifiableData = Union[str, int, float, bool, Dict[str, str], List[str], bytes]


class PurityLevel(str, Enum):
    """Levels of purity."""
    PRISTINE = "pristine"     # Perfectly pure
    CLEAN = "clean"           # Cleaned/sanitized
    TAINTED = "tainted"       # Needs purification
    CORRUPTED = "corrupted"   # Seriously impure
    MAYAVAD = "mayavad"       # Spiritually contaminated (Any types!)


class PurificationResult(TypedDict, total=False):
    """
    Result of purification.
    WATERTIGHT - no Any!
    """
    success: bool
    input_type: str           # Python type of input
    output_type: str          # Python type of output
    impurities_removed: int
    purity_level: str         # PurityLevel value
    error_message: str


class ResetResult(TypedDict, total=False):
    """
    Result of reset operation.
    WATERTIGHT - no Any!
    """
    success: bool
    previous_state_hash: str
    new_state_hash: str
    timestamp: str            # ISO timestamp
    error_message: str


class PurityState(TypedDict, total=False):
    """
    State of purity.
    WATERTIGHT - no Any!
    """
    is_pure: bool
    purity_level: str         # PurityLevel value
    total_purifications: int
    total_resets: int
    last_purification: str    # ISO timestamp
    health: str


# =============================================================================
# KUMARAS PROTOCOL
# =============================================================================


@runtime_checkable
class KumarasProtocol(Protocol):
    """
    The Purity/Reset Protocol - Kumaras' domain.
    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.KUMARAS."""
        ...

    def reset(self) -> ResetResult:
        """RESET_IP: Reset to pure/initial state."""
        ...

    def is_pure(self) -> bool:
        """Check if state is pure/uncorrupted."""
        ...

    def purify(self, data: PurifiableData) -> PurifiableData:
        """
        Purify/sanitize input data.
        WATERTIGHT: input/output is PurifiableData union, not Any.
        Returns cleaned data of same type.
        """
        ...

    def get_purity_level(self) -> PurityLevel:
        """Get current purity level."""
        ...

    def validate(self, data: PurifiableData) -> bool:
        """Validate data is pure. Returns True if valid."""
        ...

    def get_state(self) -> PurityState:
        """Get purity state. WATERTIGHT."""
        ...


# =============================================================================
# NULL KUMARAS
# =============================================================================


class NullKumaras:
    """The Already Pure. No purification needed (for testing)."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.KUMARAS

    def reset(self) -> ResetResult:
        return ResetResult(
            success=True,
            previous_state_hash="",
            new_state_hash="",
            timestamp=datetime.now().isoformat(),
            error_message="",
        )

    def is_pure(self) -> bool:
        return True  # Always pure

    def purify(self, data: PurifiableData) -> PurifiableData:
        return data  # Already pure

    def get_purity_level(self) -> PurityLevel:
        return PurityLevel.PRISTINE

    def validate(self, data: PurifiableData) -> bool:
        return True  # All data is valid

    def get_state(self) -> PurityState:
        return PurityState(
            is_pure=True,
            purity_level="pristine",
            total_purifications=0,
            total_resets=0,
            health="pristine",
        )


# Import Shuddhi (Purification) - THE core Kumaras protocol
from .shuddhi import (
    ShuddhiStatus,
    ShuddhiResult,
    ShuddhiProtocol,
    RemedyProtocol,
    NullShuddhi,
    LOTUS_POSITION as SHUDDHI_POSITION,
)

__all__ = [
    # Ownership
    "OWNER", "OWNED_PROTOCOLS", "OWNED_OPCODES",
    # Purity types (WATERTIGHT)
    "PurifiableData", "PurityLevel", "PurificationResult",
    "ResetResult", "PurityState",
    # Kumaras Protocol
    "KumarasProtocol", "NullKumaras",
    # Shuddhi Protocol (CST Surgery)
    "ShuddhiStatus", "ShuddhiResult",
    "ShuddhiProtocol", "RemedyProtocol", "NullShuddhi",
    "SHUDDHI_POSITION",
]
