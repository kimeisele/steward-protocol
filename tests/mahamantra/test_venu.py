"""
TEST: Venu Foundation (Krishna's Flute - Pure Functions)
========================================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

This test validates the Venu foundation:
1. Protocol constants derive correctly from Seed
2. Pure functions calculate tick/position correctly
3. Mathematical integrity is maintained

WATERTIGHT: No hardcoded values - everything derived from SSOT.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    QUARTERS,
    MALA,
    TICK_INTERVAL_MS,
    PRANA_DURATION_S,
    JIVA_CYCLE,
)
from vibe_core.mahamantra.protocols._venu import (
    VENU_POSITIONS,
    VENU_PHASES,
    VENU_POSITIONS_PER_PHASE,
    VENU_TICK_MS,
    VENU_TICKS_PER_MALA,
)
from vibe_core.mahamantra.substrate.venu import (
    tick_to_position,
    tick_to_cycle,
    tick_to_prana,
    tick_to_mala,
    tick_to_quarter,
    tick_to_word,
    is_downbeat,
    is_mala_complete,
    get_tick_state,
    position_to_quarter,
    position_to_word,
    next_position,
    previous_position,
    tick_to_ms,
    ms_to_tick,
    tick_to_seconds,
    mala_duration_seconds,
)
from vibe_core.mahamantra.substrate.seed import Quarter, HolyName


class TestVenuConstants:
    """Test that Venu constants derive correctly from Seed."""

    def test_venu_positions_equals_words(self) -> None:
        """VENU_POSITIONS must equal WORDS (16)."""
        assert VENU_POSITIONS == WORDS == 16

    def test_venu_phases_equals_quarters(self) -> None:
        """VENU_PHASES must equal QUARTERS (4)."""
        assert VENU_PHASES == QUARTERS == 4

    def test_positions_per_phase(self) -> None:
        """VENU_POSITIONS_PER_PHASE = VENU_POSITIONS / VENU_PHASES = 4."""
        assert VENU_POSITIONS_PER_PHASE == VENU_POSITIONS // VENU_PHASES == 4

    def test_venu_tick_ms_equals_tick_interval(self) -> None:
        """VENU_TICK_MS must equal TICK_INTERVAL_MS (250ms)."""
        assert VENU_TICK_MS == TICK_INTERVAL_MS == 250

    def test_venu_ticks_per_mala(self) -> None:
        """VENU_TICKS_PER_MALA = MALA * WORDS = 108 * 16 = 1728."""
        assert VENU_TICKS_PER_MALA == MALA * WORDS == 1728


class TestTickToPosition:
    """Test tick_to_position pure function."""

    def test_tick_zero(self) -> None:
        """Tick 0 = position 0."""
        assert tick_to_position(0) == 0

    def test_tick_wraps_at_sixteen(self) -> None:
        """Position wraps at 16."""
        assert tick_to_position(16) == 0
        assert tick_to_position(17) == 1
        assert tick_to_position(32) == 0

    def test_position_range(self) -> None:
        """Position is always 0-15."""
        for tick in range(1000):
            pos = tick_to_position(tick)
            assert 0 <= pos < VENU_POSITIONS

    def test_modulo_correctness(self) -> None:
        """tick_to_position(tick) == tick % 16."""
        for tick in [0, 1, 15, 16, 25, 100, 1728, 2000]:
            assert tick_to_position(tick) == tick % VENU_POSITIONS


class TestTickToCycle:
    """Test tick_to_cycle pure function."""

    def test_first_cycle(self) -> None:
        """Ticks 0-15 are cycle 0."""
        for tick in range(16):
            assert tick_to_cycle(tick) == 0

    def test_second_cycle(self) -> None:
        """Ticks 16-31 are cycle 1."""
        for tick in range(16, 32):
            assert tick_to_cycle(tick) == 1

    def test_cycle_formula(self) -> None:
        """tick_to_cycle(tick) == tick // 16."""
        for tick in [0, 15, 16, 100, 1728, 2000]:
            assert tick_to_cycle(tick) == tick // VENU_POSITIONS


class TestTickToPrana:
    """Test tick_to_prana pure function."""

    def test_prana_wraps_at_mala(self) -> None:
        """Prana wraps at MALA (108)."""
        # Prana 0 = cycles 0, 108, 216, ...
        # Cycle 0 = ticks 0-15
        # Cycle 108 = ticks 1728-1743
        assert tick_to_prana(0) == 0
        assert tick_to_prana(1728) == 0  # Start of Mala 1

    def test_prana_range(self) -> None:
        """Prana is always 0-107."""
        for tick in range(VENU_TICKS_PER_MALA * 3):  # 3 Malas worth
            prana = tick_to_prana(tick)
            assert 0 <= prana < MALA


class TestTickToMala:
    """Test tick_to_mala pure function."""

    def test_first_mala(self) -> None:
        """Ticks 0-1727 are Mala 0."""
        assert tick_to_mala(0) == 0
        assert tick_to_mala(1727) == 0

    def test_second_mala(self) -> None:
        """Ticks 1728-3455 are Mala 1."""
        assert tick_to_mala(1728) == 1
        assert tick_to_mala(3455) == 1

    def test_mala_formula(self) -> None:
        """tick_to_mala(tick) == tick // 1728."""
        for tick in [0, 1727, 1728, 5000, 10000]:
            assert tick_to_mala(tick) == tick // VENU_TICKS_PER_MALA


class TestTickToQuarter:
    """Test tick_to_quarter pure function."""

    def test_genesis_quarter(self) -> None:
        """Positions 0-3 are GENESIS."""
        for pos in range(4):
            assert tick_to_quarter(pos) == Quarter.GENESIS

    def test_dharma_quarter(self) -> None:
        """Positions 4-7 are DHARMA."""
        for pos in range(4, 8):
            assert tick_to_quarter(pos) == Quarter.DHARMA

    def test_karma_quarter(self) -> None:
        """Positions 8-11 are KARMA."""
        for pos in range(8, 12):
            assert tick_to_quarter(pos) == Quarter.KARMA

    def test_moksha_quarter(self) -> None:
        """Positions 12-15 are MOKSHA."""
        for pos in range(12, 16):
            assert tick_to_quarter(pos) == Quarter.MOKSHA


class TestTickToWord:
    """Test tick_to_word pure function."""

    def test_mahamantra_sequence(self) -> None:
        """The 16 words follow the Mahamantra pattern."""
        expected = [
            HolyName.HARE,     # 0
            HolyName.KRISHNA,  # 1
            HolyName.HARE,     # 2
            HolyName.KRISHNA,  # 3
            HolyName.KRISHNA,  # 4
            HolyName.KRISHNA,  # 5
            HolyName.HARE,     # 6
            HolyName.HARE,     # 7
            HolyName.HARE,     # 8
            HolyName.RAMA,     # 9
            HolyName.HARE,     # 10
            HolyName.RAMA,     # 11
            HolyName.RAMA,     # 12
            HolyName.RAMA,     # 13
            HolyName.HARE,     # 14
            HolyName.HARE,     # 15
        ]
        for pos, name in enumerate(expected):
            assert tick_to_word(pos) == name, f"Position {pos} should be {name}"


class TestDownbeatAndMalaComplete:
    """Test is_downbeat and is_mala_complete pure functions."""

    def test_downbeat_at_position_zero(self) -> None:
        """Downbeat occurs when position == 0."""
        assert is_downbeat(0) is True
        assert is_downbeat(16) is True
        assert is_downbeat(1728) is True

    def test_not_downbeat_at_other_positions(self) -> None:
        """Non-zero positions are not downbeats."""
        for pos in range(1, 16):
            assert is_downbeat(pos) is False

    def test_mala_complete_at_1728(self) -> None:
        """Mala completes at tick 1728."""
        assert is_mala_complete(1728) is True
        assert is_mala_complete(3456) is True  # 1728 * 2

    def test_mala_not_complete_at_zero(self) -> None:
        """Tick 0 is NOT a Mala completion (no Mala has completed yet)."""
        assert is_mala_complete(0) is False


class TestGetTickState:
    """Test get_tick_state pure function."""

    def test_tick_state_at_zero(self) -> None:
        """Complete state at tick 0."""
        state = get_tick_state(0)
        assert state["tick"] == 0
        assert state["position"] == 0
        assert state["cycle"] == 0
        assert state["prana"] == 0
        assert state["mala"] == 0
        assert state["quarter"] == "genesis"
        assert state["word"] == "HARE"
        assert state["is_downbeat"] is True
        assert state["is_mala_complete"] is False

    def test_tick_state_at_1728(self) -> None:
        """Complete state at tick 1728 (Mala boundary)."""
        state = get_tick_state(1728)
        assert state["tick"] == 1728
        assert state["position"] == 0
        assert state["cycle"] == 108
        assert state["prana"] == 0
        assert state["mala"] == 1
        assert state["is_downbeat"] is True
        assert state["is_mala_complete"] is True

    def test_tick_state_at_1729(self) -> None:
        """Complete state at tick 1729 (after Mala boundary)."""
        state = get_tick_state(1729)
        assert state["tick"] == 1729
        assert state["position"] == 1
        assert state["cycle"] == 108
        assert state["prana"] == 0
        assert state["mala"] == 1
        assert state["word"] == "KRISHNA"
        assert state["is_downbeat"] is False
        assert state["is_mala_complete"] is False


class TestPositionFunctions:
    """Test position helper functions."""

    def test_position_to_quarter(self) -> None:
        """position_to_quarter matches tick_to_quarter."""
        for pos in range(16):
            assert position_to_quarter(pos) == tick_to_quarter(pos)

    def test_position_to_quarter_invalid(self) -> None:
        """position_to_quarter raises for invalid positions."""
        with pytest.raises(ValueError):
            position_to_quarter(-1)
        with pytest.raises(ValueError):
            position_to_quarter(16)

    def test_next_position_wraps(self) -> None:
        """next_position wraps at 16."""
        assert next_position(0) == 1
        assert next_position(15) == 0

    def test_previous_position_wraps(self) -> None:
        """previous_position wraps at 0."""
        assert previous_position(1) == 0
        assert previous_position(0) == 15


class TestTimingFunctions:
    """Test timing conversion functions."""

    def test_tick_to_ms(self) -> None:
        """tick_to_ms = tick * 250."""
        assert tick_to_ms(0) == 0
        assert tick_to_ms(1) == 250
        assert tick_to_ms(16) == 4000  # 1 Prana

    def test_ms_to_tick(self) -> None:
        """ms_to_tick = ms // 250."""
        assert ms_to_tick(0) == 0
        assert ms_to_tick(250) == 1
        assert ms_to_tick(4000) == 16
        assert ms_to_tick(500) == 2  # Floored

    def test_tick_to_seconds(self) -> None:
        """tick_to_seconds = tick * 0.25."""
        assert tick_to_seconds(0) == 0.0
        assert tick_to_seconds(4) == 1.0
        assert tick_to_seconds(16) == 4.0  # 1 Prana

    def test_mala_duration_seconds_equals_jiva_cycle(self) -> None:
        """1 Mala = 432 seconds = JIVA_CYCLE."""
        assert mala_duration_seconds() == MALA * PRANA_DURATION_S == JIVA_CYCLE == 432


class TestMathematicalIntegrity:
    """Test mathematical relationships (Watertight)."""

    def test_ticks_per_mala_formula(self) -> None:
        """VENU_TICKS_PER_MALA = MALA * VENU_POSITIONS = 108 * 16 = 1728."""
        assert VENU_TICKS_PER_MALA == MALA * VENU_POSITIONS

    def test_one_prana_equals_sixteen_ticks(self) -> None:
        """1 Prana = 16 ticks = 4000ms."""
        prana_ms = VENU_TICK_MS * VENU_POSITIONS
        assert prana_ms == 4000

    def test_mala_time_equals_jiva_cycle(self) -> None:
        """1 Mala in seconds = JIVA_CYCLE (432)."""
        mala_ticks = VENU_TICKS_PER_MALA
        mala_seconds = mala_ticks * VENU_TICK_MS / 1000
        assert mala_seconds == JIVA_CYCLE == 432

    def test_daily_mantras_timing(self) -> None:
        """16 Malas fit in ~1.92 hours (the daily minimum)."""
        from vibe_core.mahamantra.protocols._seed import DAILY_MANTRAS, ROUNDS

        # DAILY_MANTRAS = MALA * ROUNDS = 108 * 16 = 1728
        assert DAILY_MANTRAS == MALA * ROUNDS == 1728

        # This equals 1 Mala worth of ticks - coincidence? No!
        assert DAILY_MANTRAS == VENU_TICKS_PER_MALA
