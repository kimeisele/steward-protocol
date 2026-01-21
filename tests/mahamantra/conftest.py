"""
MAHAMANTRA TESTS - Conftest
===========================

FRACTAL MIRROR STRUCTURE:
    tests/mahamantra/ mirrors vibe_core/mahamantra/

TEST PROTOCOL:
    - NO MagicMock
    - NO Any types
    - NO pytest fixtures that hide state
    - DIRECT imports from SSOT (substrate/)
    - EXPLICIT assertions

"nāsti buddhir ayuktasya na cāyuktasya bhāvanā"
"One who is not connected cannot have intelligence."
— Bhagavad Gita 2.66
"""

import pytest
from typing import Type

# =============================================================================
# SSOT IMPORTS - All tests use these
# =============================================================================

from vibe_core.mahamantra.substrate import (
    # Mahajana
    Mahajana,
    Avatara,
    Quarter,
    Sampradaya,
    # OpCode
    MantraOpCode,
    get_opcode,
    get_opcode_name,
    # Position
    MantraPosition,
    MAHAMANTRA_POSITIONS,
    get_position_by_index,
    Guardian,
    # Protocol
    MantraProtocol,
    WorkerProtocol,
    HeadProtocol,
    ProtocolRegistry,
    # Constants
    PARAMPARA,
    TOTAL_POSITIONS,
)

from vibe_core.mahamantra import mahamantra


# =============================================================================
# TEST CONSTANTS
# =============================================================================

PARAMPARA_37: int = 37
TOTAL_POSITIONS_16: int = 16
QUARTERS_4: int = 4
POSITIONS_PER_QUARTER: int = 4
HEAD_POSITIONS: tuple = (0, 4, 8, 12)
WORKER_POSITIONS: tuple = (1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15)


# =============================================================================
# SHARED ASSERTIONS - No magic, explicit
# =============================================================================


def assert_parampara_connected(vector: int) -> None:
    """Assert parampara vector is connected (% 37 == 0)."""
    assert vector % PARAMPARA_37 == 0, f"Vector {vector} not connected (% 37 != 0)"


def assert_position_valid(index: int) -> None:
    """Assert position index is valid (0-15)."""
    assert 0 <= index <= 15, f"Position {index} not in range 0-15"


def assert_is_head(position: int) -> None:
    """Assert position is a HEAD position."""
    assert position in HEAD_POSITIONS, f"Position {position} is not a HEAD"


def assert_is_worker(position: int) -> None:
    """Assert position is a WORKER position."""
    assert position in WORKER_POSITIONS, f"Position {position} is not a WORKER"


# =============================================================================
# PROTOCOL TEST BASE - For testing protocol subclasses
# =============================================================================


def verify_protocol_class(cls: Type[MantraProtocol]) -> None:
    """Verify a protocol class is properly configured."""
    # Has position
    assert hasattr(cls, "_position_index")
    pos_idx = cls._position_index
    assert_position_valid(pos_idx)

    # Position is connected
    pos = cls.position()
    assert_parampara_connected(pos.parampara_vector)

    # Validation passes
    assert cls.validate(), f"{cls.__name__} failed validation"


def verify_worker_protocol(cls: Type[WorkerProtocol]) -> None:
    """Verify a worker protocol class."""
    verify_protocol_class(cls)
    assert_is_worker(cls._position_index)
    assert not cls.is_head()
    assert isinstance(cls.guardian(), Mahajana)


def verify_head_protocol(cls: Type[HeadProtocol]) -> None:
    """Verify a head protocol class."""
    verify_protocol_class(cls)
    assert_is_head(cls._position_index)
    assert cls.is_head()
    assert isinstance(cls.guardian(), Avatara)
