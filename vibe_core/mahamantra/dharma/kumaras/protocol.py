"""
KUMARAS PROTOCOL - The Purity Standard
======================================

Moved from protocols/mahajanas/kumaras/__init__.py

POSITION: 5 (DHARMA Quarter, RESOLVE_REQ OpCode)

DERIVED FROM MAHAMANTRA:
    Position 5 → guardian=KUMARAS, opcode=RESOLVE_REQ, quarter=DHARMA
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0x40aefaac"  # GenesisByte: parampara % 37 == 0

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
    """

    _position_index: ClassVar[int] = 5  # THE ONLY CONFIGURATION


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

from .types import (
    PurifiableData,
    PurityLevel,
    PurificationResult,
    ResetResult,
    PurityState,
    PurifyCliResult,
)


# =============================================================================
# KUMARAS PROTOCOL
# =============================================================================


@runtime_checkable
class KumarasProtocol(Protocol):
    """
    The Purity/Reset Protocol - Kumaras' domain.
    """

    @classmethod
    def position_index(cls) -> int: ...

    def reset(self) -> ResetResult: ...

    def is_pure(self) -> bool: ...

    def purify(self, data: PurifiableData) -> PurifiableData: ...

    def get_purity_level(self) -> PurityLevel: ...

    def validate(self, data: PurifiableData) -> bool: ...

    def get_state(self) -> PurityState: ...


# =============================================================================
# NULL KUMARAS
# =============================================================================


class NullKumaras(KumarasProtocolBase):
    """The Already Pure. No purification needed (for testing)."""

    def reset(self) -> ResetResult:
        return ResetResult(
            success=True,
            previous_state_hash="",
            new_state_hash="",
            timestamp=datetime.now().isoformat(),
            error_message="",
        )

    def is_pure(self) -> bool:
        return True

    def purify(self, data: PurifiableData = None) -> PurifiableData:
        return data

    def get_purity_level(self) -> PurityLevel:
        return PurityLevel.PRISTINE

    def validate(self, data: PurifiableData = None) -> bool:
        return True

    def get_state(self) -> PurityState:
        return PurityState(
            is_pure=True,
            purity_level="pristine",
            total_purifications=0,
            total_resets=0,
            health="pristine",
        )

    def purify_cli(self, target: str = "input") -> PurifyCliResult:
        state = self.get_state()
        return PurifyCliResult(
            success=True,
            is_pure=self.is_pure(),
            purity_level=self.get_purity_level().value,
            health=state.get("health", "pristine"),
        )


# Import Shuddhi (Purification) from SSOT
from vibe_core.mahamantra.substrate.shuddhi import (
    ShuddhiProtocolBase,
    ShuddhiStatus,
    ShuddhiResult,
    ShuddhiProtocol,
    RemedyProtocol,
    NullShuddhi,
)

SHUDDHI_POSITION = ShuddhiProtocolBase.lotus_position()

# =============================================================================
# VALIDATION - Input Validation
# =============================================================================

from .validation import (
    ValidationType,
    ValidationRule,
    ValidationResult,
    ValidatorFunc,
    ValidationProtocol,
    Validator,
    NullValidator,
    required,
    type_check,
    range_check,
    pattern_check,
    length_check,
    LOTUS_POSITION as VALIDATION_POSITION,
)

__all__ = [
    "KumarasProtocolBase",
    "ShuddhiProtocolBase",
    "PurifiableData",
    "PurityLevel",
    "PurificationResult",
    "ResetResult",
    "PurityState",
    "PurifyCliResult",
    "KumarasProtocol",
    "NullKumaras",
    "ShuddhiStatus",
    "ShuddhiResult",
    "ShuddhiProtocol",
    "RemedyProtocol",
    "NullShuddhi",
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
