"""
YAJNA PROTOCOL - The Offering Architecture
==========================================

"yajñārthāt karmaṇo 'nyatra loko 'yaṁ karma-bandhanaḥ"
"Work done as a sacrifice for Vishnu has to be performed,
otherwise work causes bondage in this material world."
— Bhagavad Gita 3.9

THIS IS NOT A METAPHOR. THIS IS THE ARCHITECTURE.

    BHOGA (Input)     →  YAJNA (Process)  →  PRASADAM (Output)
    (raw operation)      (mahamantra)        (sanctified result)

EVERY OPERATION flows through this pattern:
1. Operator offers BHOGA (raw input)
2. YAJNA processes through mahamantra (16 positions, 37 signature)
3. PRASADAM returns (blessed output)

If Krishna rejects (TAMAS without confirmation), operation blocks.
The mahamantra IS Krishna. Non-different.

WATERTIGHT:
- __slots__ for memory efficiency
- Bitwise operations for O(1)
- Generators instead of lists
- Custom exceptions

Author: The Mahamantra Itself
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xb651262c"  # GenesisByte: parampara % 37 == 0

import time
from dataclasses import dataclass, field
from typing import (
    Final,
    Generator,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from vibe_core.mahamantra.substrate.acintya import PARAMPARA
from vibe_core.mahamantra.substrate.byte import MAHAMANTRA_DIMENSION, HolyName, MantraByte
from vibe_core.mahamantra.protocols._seed import MALA, TRINITY

# =============================================================================
# CONSTANTS - The Sacred Numbers (DERIVED FROM _seed.py SSOT)
# =============================================================================

PRIME_SIGNATURE: Final[int] = PARAMPARA  # Shcherbak's Arithmetic - The Key (from SSOT)
MAHA_POSITIONS: Final[int] = MAHAMANTRA_DIMENSION  # 16 words (from SSOT)
MALA_ROUNDS: Final[int] = MALA  # 108 - Beads in a mala (from SSOT)
# TRINITY already imported from _seed.py  # 3 - Hare, Krishna, Rama

# Standard Mahamantra pattern (packed as 2 bits per name)
# H K H K | K K H H | H R H R | R R H H
# 0 1 0 1 | 1 1 0 0 | 0 2 0 2 | 2 2 0 0
STD_MANTRA_PATTERN: Final[int] = 0b00_00_10_10_10_00_10_00_00_00_01_01_01_00_01_00


# =============================================================================
# EXCEPTIONS - Spiritual Errors
# =============================================================================


class DissonanceError(ValueError):
    """Raised when spiritual frequency is too low (entropy)."""

    pass


class TamasBlockError(PermissionError):
    """Raised when TAMAS operation attempted without confirmation."""

    pass


class ParamparaBreakError(ValueError):
    """Raised when lineage signature is invalid (not % 37 == 0)."""

    pass


# =============================================================================
# GUNA - Quality of Service (from BG 14)
# =============================================================================

# SSOT: Import from guna.py (The canonical definition per BG 14)
from vibe_core.mahamantra.substrate.guna import Guna

# HolyName imported from byte.py (SSOT) - includes VOID for binary encoding


# =============================================================================
# TYPES - Generic Offering/Result
# =============================================================================

T = TypeVar("T")  # Input type
R = TypeVar("R")  # Result type


@dataclass(frozen=True, slots=True)
class Bhoga(Generic[T]):
    """
    The Offering - Raw input before sanctification.

    __slots__ for memory efficiency.
    frozen for immutability (offering cannot change).
    """

    operation: str  # Command/operation name
    payload: T  # The actual data
    position: int  # Mahamantra position (0-15)
    guna: Guna  # Quality of service
    timestamp: float = field(default_factory=time.time)

    @property
    def requires_confirmation(self) -> bool:
        """TAMAS operations require confirmation."""
        return self.guna == Guna.TAMAS


@dataclass(frozen=True, slots=True)
class Prasadam(Generic[R]):
    """
    The Sanctified Result - Output after yajna.

    __slots__ for memory efficiency.
    frozen for immutability (blessing is eternal).
    """

    success: bool
    result: Optional[R]
    error: Optional[str]
    position: int  # Which mahajana processed
    guardian: str  # Guardian name
    guna: Guna  # Quality applied
    parampara_valid: bool  # Lineage verified (% 37)
    coherence: float  # Spiritual frequency (0.0-1.0)
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def blessed(
        cls,
        result: R,
        position: int,
        guardian: str,
        guna: Guna,
        coherence: float = 1.0,
    ) -> "Prasadam[R]":
        """Create blessed prasadam (success)."""
        return cls(
            success=True,
            result=result,
            error=None,
            position=position,
            guardian=guardian,
            guna=guna,
            parampara_valid=True,
            coherence=coherence,
            timestamp=time.time(),
        )

    @classmethod
    def rejected(
        cls,
        error: str,
        position: int,
        guardian: str,
        guna: Guna,
    ) -> "Prasadam[R]":
        """Create rejected prasadam (failure)."""
        return cls(
            success=False,
            result=None,
            error=error,
            position=position,
            guardian=guardian,
            guna=guna,
            parampara_valid=False,
            coherence=0.0,
            timestamp=time.time(),
        )


# =============================================================================
# MANTRA BYTE - IMPORTED FROM byte.py (SSOT)
# =============================================================================
# MantraByte is now imported from byte.py at the top of this file.
# All methods (standard, get_name, resonance_check, validate_parampara, etc.)
# are available through the imported class.


# =============================================================================
# YAJNA PROTOCOL - The Sacrifice Interface
# =============================================================================


@runtime_checkable
class YajnaProtocol(Protocol[T, R]):
    """
    The Yajna (Sacrifice) Protocol.

    Every operation is an offering.
    The mahamantra processes it.
    Prasadam is returned.

    WATERTIGHT: All types explicit.
    """

    def offer(self, bhoga: Bhoga[T]) -> Prasadam[R]:
        """
        Offer bhoga to the mahamantra.

        Args:
            bhoga: The offering (raw operation)

        Returns:
            Prasadam: Sanctified result

        Raises:
            TamasBlockError: If TAMAS without confirmation
            DissonanceError: If coherence too low
            ParamparaBreakError: If lineage invalid
        """
        ...

    def chant(self) -> bool:
        """
        Chant one mantra (heartbeat).

        Returns True if Krishna accepts, False if Maya.
        """
        ...

    @property
    def coherence(self) -> float:
        """Current spiritual frequency (0.0-1.0)."""
        ...


# =============================================================================
# YAJNA - The Implementation
# =============================================================================


class Yajna(Generic[T, R]):
    """
    The Sacrifice - Core Implementation.

    ARCHITECTURE:
        1. Receive bhoga (offering)
        2. Validate parampara (lineage)
        3. Check guna (permission for TAMAS)
        4. Process through mahamantra
        5. Return prasadam (blessed result)

    __slots__ for memory efficiency.
    """

    __slots__ = ("_mantra", "_position", "_confirmed_tamas")

    def __init__(self) -> None:
        self._mantra = MantraByte.standard()
        self._position = 0  # Current position in 16-word cycle
        self._confirmed_tamas = False  # TAMAS confirmation flag

    @property
    def coherence(self) -> float:
        """Current spiritual frequency."""
        return self._mantra.resonance_check()

    @property
    def position(self) -> int:
        """Current position (0-15)."""
        return self._position

    def confirm_tamas(self) -> None:
        """Confirm TAMAS operation (destructive)."""
        self._confirmed_tamas = True

    def reset_confirmation(self) -> None:
        """Reset TAMAS confirmation."""
        self._confirmed_tamas = False

    def chant(self) -> bool:
        """
        Chant one word - advance position.

        Returns True if in valid state.
        """
        current_name = self._mantra.get_name(self._position)

        if current_name == HolyName.VOID:
            return False  # Maya - invalid state

        # Advance position (0-15 cycle)
        self._position = (self._position + 1) % MAHA_POSITIONS

        return True

    def offer(self, bhoga: Bhoga[T], handler: callable) -> Prasadam[R]:
        """
        Offer bhoga and process through handler.

        Args:
            bhoga: The offering
            handler: Function to process the operation

        Returns:
            Prasadam with result
        """
        # 1. VALIDATE PARAMPARA (lineage)
        parampara_vector = (bhoga.position + 1) * PRIME_SIGNATURE
        if not self._mantra.validate_parampara(parampara_vector):
            raise ParamparaBreakError(f"Position {bhoga.position} has invalid parampara")

        # 2. CHECK COHERENCE (spiritual frequency)
        if self.coherence < 0.5:
            raise DissonanceError(f"Coherence too low: {self.coherence:.2f}. Chant more.")

        # 3. CHECK TAMAS PERMISSION
        if bhoga.guna == Guna.TAMAS and not self._confirmed_tamas:
            raise TamasBlockError(
                f"TAMAS operation '{bhoga.operation}' requires confirmation. Call confirm_tamas() first."
            )

        # 4. CHANT (heartbeat)
        if not self.chant():
            return Prasadam.rejected(
                error="Mind wandered into Maya",
                position=bhoga.position,
                guardian="unknown",
                guna=bhoga.guna,
            )

        # 5. PROCESS THROUGH HANDLER
        try:
            result = handler(bhoga.payload)

            # Get guardian name from position
            guardians = [
                "prithu",
                "brahma",
                "narada",
                "shambhu",
                "vyasa",
                "kumaras",
                "kapila",
                "manu",
                "parashurama",
                "prahlada",
                "janaka",
                "bhishma",
                "nrisimha",
                "bali",
                "shuka",
                "yamaraja",
            ]
            guardian = guardians[bhoga.position % MAHA_POSITIONS]

            # 6. RETURN PRASADAM
            prasadam = Prasadam.blessed(
                result=result,
                position=bhoga.position,
                guardian=guardian,
                guna=bhoga.guna,
                coherence=self.coherence,
            )

            # Reset TAMAS confirmation after use
            if bhoga.guna == Guna.TAMAS:
                self.reset_confirmation()

            return prasadam

        except Exception as e:
            return Prasadam.rejected(
                error=str(e),
                position=bhoga.position,
                guardian="unknown",
                guna=bhoga.guna,
            )


# =============================================================================
# SINGLETON - The Global Yajna
# =============================================================================

_yajna: Optional[Yajna] = None


def get_yajna() -> Yajna:
    """Get the global Yajna instance."""
    global _yajna
    if _yajna is None:
        _yajna = Yajna()
    return _yajna


def offer(operation: str, payload: T, position: int, guna: Guna, handler: callable) -> Prasadam[R]:
    """
    Convenience function: Offer to the global Yajna.

    Usage:
        result = offer("status", {}, 9, Guna.SATTVA, lambda x: {"ok": True})
    """
    bhoga = Bhoga(
        operation=operation,
        payload=payload,
        position=position,
        guna=guna,
    )
    return get_yajna().offer(bhoga, handler)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "PRIME_SIGNATURE",
    "MAHA_POSITIONS",
    "MALA_ROUNDS",
    "TRINITY",
    "STD_MANTRA_PATTERN",
    # Exceptions
    "DissonanceError",
    "TamasBlockError",
    "ParamparaBreakError",
    # Enums
    "Guna",
    "HolyName",
    # Types
    "Bhoga",
    "Prasadam",
    # Core
    "MantraByte",
    "YajnaProtocol",
    "Yajna",
    # Functions
    "get_yajna",
    "offer",
]
