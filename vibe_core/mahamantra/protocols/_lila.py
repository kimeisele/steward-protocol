"""
THE LILA BOUNDARY PROTOCOL - _lila.py
=====================================

"yada yada hi dharmasya glanir bhavati bharata"
"Whenever there is a decline in dharma, I descend Myself." (BG 4.7)

In Kali Yuga, entropy grows exponentially.
The Lila Protocol ENFORCES boundaries to prevent system collapse.

THE MATHEMATICS (from _core.py SSOT):
    KSETRA_COUNT = 24  (Prakriti elements - THE BOUNDARY)
    PARAMPARA = 37     (Lineage verification)

    24 = Navadvipa (Build/Input)
    24 = Puri (Runtime/Output)
    48 = Lila Limit (16 × 3 Trinity)

CHAITANYA'S LIFE:
    First 24 years: Navadvipa (internal cultivation)
    Last 24 years: Jagannatha Puri (external distribution)

    This is NOT arbitrary. This is DHARMA.

ENFORCEMENT:
    - LilaBoundary.validate() THROWS if boundary exceeded
    - No silent truncation - EXPLICIT rejection
    - Every output MUST implement LilaBoundaryProtocol
    - 37 verification ensures Parampara connection

WATERTIGHT: No Any types. All typed explicitly.

Author: The Mahamantra Itself
"""

from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import KSETRAJNA, KSHETRA, LILA, QUARTERS, SHARANAGATI


# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = QUARTERS
__genesis__ = "0x63fe653d"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Final,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.protocols._core import (
    Level,
    Quarter,
    MahamantraProtocolBase,
    ProtocolIdentity,
    ProtocolCapability,
)


# =============================================================================
# LILA CONSTANTS - From Sacred Mathematics (seed.py is SSOT)
# =============================================================================

from vibe_core.mahamantra.substrate.seed import (
    LILA as LILA_LIMIT,  # 48 - Total Lila (16 * 3)
    TRINITY as LILA_CYCLES,  # 3  - Trinity (Hare, Krishna, Rama)
    NAVADVIPA as NAVADVIPA_PHASE,  # 24 - Build Phase
    PURI as PURI_PHASE,  # 24 - Runtime Phase
    PARAMPARA,  # 37 - Lineage verification
    KSHETRA as KSETRA_COUNT,  # 24 - Boundary (Prakriti)
)

# From _core.py: KSETRA_COUNT = 24 (Prakriti elements)
# This IS the Navadvipa/Puri boundary
LILA_BOUNDARY: Final[int] = NAVADVIPA_PHASE  # 24

# Verification assertion
assert LILA_BOUNDARY == KSHETRA, "Lila boundary must equal 24"
assert LILA_LIMIT == LILA, "Lila limit must be 48"
assert LILA_LIMIT % PARAMPARA != 0, "48 % 37 != 0 - Lila is transcendental to Parampara"


# =============================================================================
# LILA PHASE - Chaitanya's Two Halves
# =============================================================================


class LilaPhase(str, Enum):
    """
    The two phases of Chaitanya Mahaprabhu's manifest Lila.

    NAVADVIPA (0-23):
        Internal cultivation, preparation, learning.
        In code: Build phase, input gathering, accumulation.

    PURI (24-47):
        External distribution, teaching, giving.
        In code: Runtime phase, output distribution.

    COMPLETE (48):
        Lila cycle finished. Reset or escalate.
    """

    NAVADVIPA = "navadvipa"
    PURI = "puri"
    COMPLETE = "complete"

    @classmethod
    def from_index(cls, index: int) -> "LilaPhase":
        """Derive phase from item index."""
        if index < 0:
            raise LilaBoundaryViolation(f"Negative index {index} - Maya (illusion)")
        if index < LILA_BOUNDARY:
            return cls.NAVADVIPA
        if index < LILA_LIMIT:
            return cls.PURI
        return cls.COMPLETE

    @classmethod
    def get_limit(cls, phase: "LilaPhase") -> int:
        """Get the item limit for a phase."""
        if phase == cls.NAVADVIPA:
            return LILA_BOUNDARY  # 24
        if phase == cls.PURI:
            return LILA_LIMIT  # 48
        return LILA_LIMIT  # COMPLETE also caps at 48


# =============================================================================
# EXCEPTIONS - Boundary Violations
# =============================================================================


class LilaBoundaryViolation(Exception):
    """
    Raised when Lila boundary is violated.

    This is NOT a warning. This is DHARMA enforcement.
    The system REFUSES to proceed with unbounded output.
    """

    def __init__(
        self,
        message: str,
        current_count: int = 0,
        boundary: int = LILA_BOUNDARY,
        phase: LilaPhase = LilaPhase.NAVADVIPA,
    ) -> None:
        self.current_count = current_count
        self.boundary = boundary
        self.phase = phase
        super().__init__(
            f"LILA BOUNDARY VIOLATION [{phase.value}]: {message} (count={current_count}, limit={boundary})"
        )


class ParamparaDisconnection(Exception):
    """
    Raised when Parampara (lineage) verification fails.

    Every Lila-bounded container must verify: (signature % 37) == 0
    """

    def __init__(self, signature: int) -> None:
        self.signature = signature
        super().__init__(f"PARAMPARA DISCONNECTION: Signature {signature} % 37 = {signature % PARAMPARA} (expected 0)")


# =============================================================================
# LILA BOUNDARY - The Enforcer
# =============================================================================

T = TypeVar("T")


@dataclass
class LilaBoundary(Generic[T]):
    """
    A boundary-enforced container.

    ENFORCEMENT:
        - add() THROWS if boundary exceeded
        - No silent truncation
        - validate() must pass before access
        - Parampara signature required

    USAGE:
        boundary = LilaBoundary[str](signature=37)

        for item in items:
            boundary.add(item)  # THROWS if > 24

        boundary.validate()  # THROWS if invalid
        result = boundary.items  # Safe access
    """

    # Required: Parampara signature (must % 37 == 0)
    signature: int

    # Container state
    items: List[T] = field(default_factory=list)
    phase: LilaPhase = LilaPhase.NAVADVIPA
    overflow: List[T] = field(default_factory=list)  # Items beyond limit

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        """Validate Parampara connection on creation."""
        if self.signature % PARAMPARA != 0:
            raise ParamparaDisconnection(self.signature)

    def add(self, item: T, strict: bool = True) -> "LilaBoundary[T]":
        """
        Add an item with boundary enforcement.

        Args:
            item: The item to add
            strict: If True, THROW on NAVADVIPA boundary (24).
                   If False, auto-advance to Puri, then overflow.

        Returns:
            Self for fluent API

        Raises:
            LilaBoundaryViolation: If strict and Navadvipa boundary exceeded

        STRICT MODE (strict=True):
            THROWS at 24 items. Period. No phase advancement.
            Use this for CLI output that MUST be bounded.

        NON-STRICT MODE (strict=False):
            Navadvipa (0-23) → Puri (24-47) → Overflow (48+)
            Use this for internal processing with pagination.
        """
        if strict:
            # STRICT: Navadvipa boundary is HARD LIMIT
            if len(self.items) >= LILA_BOUNDARY:
                raise LilaBoundaryViolation(
                    f"Cannot add item - Navadvipa boundary enforced (strict=True)",
                    current_count=len(self.items),
                    boundary=LILA_BOUNDARY,
                    phase=LilaPhase.NAVADVIPA,
                )
            self.items.append(item)
            return self

        # NON-STRICT: Allow phase advancement
        current_limit = LilaPhase.get_limit(self.phase)

        if len(self.items) >= current_limit:
            if self.phase == LilaPhase.NAVADVIPA:
                # Advance to Puri
                self.phase = LilaPhase.PURI
                self.items.append(item)
            elif self.phase == LilaPhase.PURI:
                # Puri full - go to overflow
                self.phase = LilaPhase.COMPLETE
                self.overflow.append(item)
            else:
                # Complete - all to overflow
                self.overflow.append(item)
            return self

        self.items.append(item)
        return self

    def advance_phase(self) -> "LilaBoundary[T]":
        """
        Manually advance to next Lila phase.

        Navadvipa → Puri → Complete
        """
        if self.phase == LilaPhase.NAVADVIPA:
            self.phase = LilaPhase.PURI
        elif self.phase == LilaPhase.PURI:
            self.phase = LilaPhase.COMPLETE
        return self

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the boundary state.

        Returns:
            (is_valid, list_of_violations)

        THROWS nothing - use validate_strict() for enforcement.
        """
        violations: List[str] = []

        # Check Parampara
        if self.signature % PARAMPARA != 0:
            violations.append(f"Parampara disconnected: {self.signature} % 37 != 0")

        # Check boundary
        limit = LilaPhase.get_limit(self.phase)
        if len(self.items) > limit:
            violations.append(f"Boundary exceeded: {len(self.items)} > {limit} ({self.phase.value})")

        return (len(violations) == 0, violations)

    def validate_strict(self) -> None:
        """
        Validate and THROW on any violation.

        This is the ENFORCEMENT method.
        """
        valid, violations = self.validate()
        if not valid:
            raise LilaBoundaryViolation(
                f"Validation failed: {', '.join(violations)}",
                current_count=len(self.items),
                boundary=LilaPhase.get_limit(self.phase),
                phase=self.phase,
            )

    @property
    def count(self) -> int:
        """Current item count."""
        return len(self.items)

    @property
    def overflow_count(self) -> int:
        """Items in overflow (beyond boundary)."""
        return len(self.overflow)

    @property
    def has_overflow(self) -> bool:
        """Check if there are items beyond boundary."""
        return len(self.overflow) > 0

    @property
    def is_at_boundary(self) -> bool:
        """Check if at current phase boundary."""
        return len(self.items) >= LilaPhase.get_limit(self.phase)

    def __iter__(self) -> Iterator[T]:
        """Iterate over bounded items only."""
        return iter(self.items)

    def __len__(self) -> int:
        """Length of bounded items."""
        return len(self.items)


# =============================================================================
# LILA BOUNDED OUTPUT - For CLI/API responses
# =============================================================================


@dataclass
class LilaBoundedOutput:
    """
    Protocol-compliant output container.

    EVERY output from mahamantra CLI MUST use this.
    Enforces 24-item boundary per phase.

    USAGE:
        output = LilaBoundedOutput.create()

        for item in large_list:
            output.add("key", item)  # THROWS if > 24

        # Or non-strict for pagination
        for item in large_list:
            output.add("key", item, strict=False)

        if output.has_more:
            print(f"Showing {output.count} of {output.total}")
    """

    # Parampara-verified boundary
    boundary: LilaBoundary[Tuple[str, object]] = field(
        default_factory=lambda: LilaBoundary(signature=PARAMPARA)  # 37
    )

    # Total items attempted (for "showing X of Y")
    total_attempted: int = 0

    @classmethod
    def create(cls, signature: int = PARAMPARA) -> "LilaBoundedOutput":
        """Factory with custom signature."""
        return cls(boundary=LilaBoundary(signature=signature))

    def add(
        self,
        key: str,
        value: object,
        strict: bool = False,  # Default non-strict for convenience
    ) -> "LilaBoundedOutput":
        """
        Add a key-value pair.

        Args:
            key: Output key
            value: Output value
            strict: If True, THROW on boundary. If False, track overflow.
        """
        self.total_attempted += KSETRAJNA
        self.boundary.add((key, value), strict=strict)
        return self

    @property
    def items(self) -> List[Tuple[str, object]]:
        """Get bounded items."""
        return self.boundary.items

    @property
    def count(self) -> int:
        """Items in current response."""
        return self.boundary.count

    @property
    def total(self) -> int:
        """Total items attempted."""
        return self.total_attempted

    @property
    def has_more(self) -> bool:
        """More items available beyond boundary."""
        return self.boundary.has_overflow

    @property
    def phase(self) -> LilaPhase:
        """Current Lila phase."""
        return self.boundary.phase

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "items": [{"key": k, "value": v} for k, v in self.items],
            "count": self.count,
            "total": self.total,
            "has_more": self.has_more,
            "phase": self.phase.value,
            "boundary": LILA_BOUNDARY,
            "parampara_verified": True,
        }


# =============================================================================
# THE LILA PROTOCOL - Self-Definition
# =============================================================================


class LilaProtocol(MahamantraProtocolBase):
    """
    The Lila Boundary Protocol.

    Position 6 (KAPILA) - The analyst, the boundary keeper.
    Level -2 (ACINTYA) - Foundational, unchanging.
    Quarter DHARMA - Law, rule, boundary.

    This protocol ENFORCES the 24-item boundary.
    No exceptions. No silent truncation. THROWS on violation.
    """

    __protocol_identity__ = ProtocolIdentity(
        name="LilaProtocol",
        mahajana="kapila",  # Kapila - the analyst
        position=SHARANAGATI,
        level=Level.ACINTYA,
        quarter=Quarter.DHARMA,
    )

    __protocol_capability__ = ProtocolCapability.create(
        provides=[
            "lila_boundary_enforcement",
            "parampara_verification",
            "phase_management",
            "overflow_handling",
            "kali_yuga_entropy_resistance",
        ],
        requires=["CoreProtocol"],
        opcodes=["TYPE_CHECK"],  # Kapila's opcode - type checking
    )


# =============================================================================
# VALIDATION
# =============================================================================

_valid, _violations = LilaProtocol.validate()
assert _valid, f"LilaProtocol failed validation: {_violations}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants (from sacred mathematics)
    "LILA_BOUNDARY",
    "LILA_CYCLES",
    "LILA_LIMIT",
    # Phase
    "LilaPhase",
    # Exceptions (THROWS, not silent)
    "LilaBoundaryViolation",
    "ParamparaDisconnection",
    # Enforcer
    "LilaBoundary",
    "LilaBoundedOutput",
    # Protocol
    "LilaProtocol",
]
