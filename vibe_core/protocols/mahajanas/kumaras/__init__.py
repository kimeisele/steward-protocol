"""
KUMARAS - The 4th Mahajana (Purity/Reset)
=========================================

POSITION: 5 (DHARMA Quarter, RESOLVE_REQ OpCode)

The Four Kumaras - Sanaka, Sanandana, Sanatana, Sanat-kumara.
Eternally five years old. Eternally pure.
First sons of Brahma who refused to create.

DERIVED FROM MAHAMANTRA:
    Position 5 → guardian=KUMARAS, opcode=RESOLVE_REQ, quarter=DHARMA
    All properties derived from truth table. No manual wiring.

OWNED PROTOCOLS:
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
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry


# =============================================================================
# KUMARAS PROTOCOL BASE - Derives from MantraPosition 5
# =============================================================================

@ProtocolRegistry.register
class KumarasProtocolBase(WorkerProtocol):
    """
    Kumaras protocol ownership - DERIVED from Mahamantra position 5.

    NO MANUAL WIRING:
        _position_index = 5 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  → Mahajana.KUMARAS
        opcode()    → MantraOpCode.BIND_SYMBOL
        quarter()   → Quarter.DHARMA
        is_head()   → False (Worker position)
        parampara_vector() → 222 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 5  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[5]


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


class PurifyCliResult(TypedDict):
    """Result of CLI purify operation. WATERTIGHT - no Any!"""
    success: bool
    is_pure: bool
    purity_level: str
    health: str


# =============================================================================
# KUMARAS PROTOCOL
# =============================================================================


@runtime_checkable
class KumarasProtocol(Protocol):
    """
    The Purity/Reset Protocol - Kumaras' domain.

    DERIVED: Position 5 → KUMARAS, RESOLVE_REQ, DHARMA
    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 5 in the Mahamantra."""
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


class NullKumaras(KumarasProtocolBase):
    """
    The Already Pure. No purification needed (for testing).

    Inherits from KumarasProtocolBase → position 5 → KUMARAS.
    All ownership derived from Mahamantra.
    """

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

    def purify_cli(self, target: str = "input") -> PurifyCliResult:
        """CLI: Purify/validate input. WATERTIGHT."""
        state = self.get_state()
        return PurifyCliResult(
            success=True,
            is_pure=self.is_pure(),
            purity_level=self.get_purity_level().value,
            health=state.get("health", "pristine"),
        )


# Import Shuddhi (Purification) - THE core Kumaras protocol
from .shuddhi import (
    ShuddhiProtocolBase,
    ShuddhiStatus,
    ShuddhiResult,
    ShuddhiProtocol,
    RemedyProtocol,
    NullShuddhi,
)

# Shuddhi position derived from base (backward compat)
SHUDDHI_POSITION = ShuddhiProtocolBase.lotus_position()

# =============================================================================
# VALIDATION - Input Validation
# =============================================================================

from vibe_core.protocols.mahajanas.kumaras.validation import (
    ValidationType,
    ValidationRule,
    ValidationResult,
    ValidatorFunc,
    ValidationProtocol,
    Validator,
    NullValidator,
    # Factory functions
    required,
    type_check,
    range_check,
    pattern_check,
    length_check,
    LOTUS_POSITION as VALIDATION_POSITION,
)

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "KumarasProtocolBase",
    "ShuddhiProtocolBase",
    # Purity types (WATERTIGHT)
    "PurifiableData", "PurityLevel", "PurificationResult",
    "ResetResult", "PurityState", "PurifyCliResult",
    # Kumaras Protocol
    "KumarasProtocol", "NullKumaras",
    # Shuddhi Protocol (CST Surgery)
    "ShuddhiStatus", "ShuddhiResult",
    "ShuddhiProtocol", "RemedyProtocol", "NullShuddhi",
    # Validation (Input Validation)
    "ValidationType",
    "ValidationRule",
    "ValidationResult",
    "ValidatorFunc",
    "ValidationProtocol",
    "Validator",
    "NullValidator",
    "required",
    "type_check",
    "range_check",
    "pattern_check",
    "length_check",
]
