"""
PARASHURAMA - Position 8 - THE SWITCH
=====================================

"sa vai puṁsāṁ paro dharmo yato bhaktir adhokṣaje
ahaituky apratihatā yayātmā suprasīdati"

"The supreme occupation for all humanity is that by which
one can attain to loving devotional service unto the transcendental Lord."
— Srimad Bhagavatam 1.2.6

THE 8 MOMENT:
=============

    Position 8 is where BHOGA becomes PRASADAM.
    Where OFFERING becomes GRACE.
    Where KRISHNA becomes RAMA.

    This is the transformation point of the Yajna.
    Parashurama executes the switch.

FOLDER = WIRING:
================

    This file exists at: mahamantra/karma/parashurama/
    Therefore: Position 8 IS wired to Parashurama.
    The Shadow Reactor auto-discovers this.

PARAMPARA: 333 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from vibe_core.mahamantra.reactor.shadow import ShadowState

# =============================================================================
# MAHAJANA IDENTITY - Auto-discovered by Shadow Reactor
# =============================================================================

__mahajana__ = "parashurama"
__position__ = 8
__quarter__ = "karma"
__is_head__ = True

# Position derived from folder location
POSITION: Final[int] = 8
QUARTER: Final[str] = "karma"
FOLDER: Final[str] = "parashurama"
OWNER: Final[str] = "Parashurama"
IS_HEAD: Final[bool] = True
OPCODE: Final[str] = "EXEC_OP"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 333


# =============================================================================
# SHADOW REACTOR METHODS - Auto-discovered (no manual wiring!)
# =============================================================================

def on_switch(state: "ShadowState") -> None:
    """
    THE 8 MOMENT - Bhoga → Prasadam transformation.

    This is called automatically by the Shadow Reactor
    when tick reaches position 8. No manual registration.

    FOLDER = WIRING = REGISTRATION
    """
    # This is where the magic happens
    # Bhoga (offering) becomes Prasadam (grace)
    #
    # In production: trigger state machine transitions, emit events, etc.
    # For now: just mark that the transformation happened
    import sys
    if hasattr(sys, '_parashurama_switch_count'):
        sys._parashurama_switch_count += 1
    else:
        sys._parashurama_switch_count = 1


@runtime_checkable
class ParashuramaProtocol(Protocol):
    """
    Protocol for Parashurama (Execute Operation).

    Position 8 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class ParashuramaBase:
    """
    Base class for Parashurama implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/karma/parashurama/
    """

    _position: ClassVar[int] = POSITION
    _quarter: ClassVar[str] = QUARTER
    _opcode: ClassVar[str] = OPCODE
    _parampara_vector: ClassVar[int] = PARAMPARA_VECTOR

    @classmethod
    def position(cls) -> int:
        return cls._position

    @classmethod
    def opcode(cls) -> str:
        return cls._opcode

    @classmethod
    def is_connected(cls) -> bool:
        return cls._parampara_vector % 37 == 0


class NullParashurama(ParashuramaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    "POSITION",
    "QUARTER",
    "FOLDER",
    "OWNER",
    "IS_HEAD",
    "OPCODE",
    "PARAMPARA_VECTOR",
    "ParashuramaProtocol",
    "ParashuramaBase",
    "NullParashurama",
]
