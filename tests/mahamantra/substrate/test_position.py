"""
TEST POSITION - substrate/position.py
=====================================

Tests for the 16 MantraPositions (SSOT - Truth Table).
"""

from vibe_core.mahamantra.substrate import (
    MAHAMANTRA_POSITIONS,
    PARAMPARA,
    Avatara,
    Guardian,
    Mahajana,
    MantraOpCode,
    MantraPosition,
    Quarter,
    get_head_position,
    get_position_by_guardian,
    get_position_by_index,
    get_position_by_opcode,
    get_positions_by_quarter,
    get_worker_positions,
)


class TestMAHAMANTRA_POSITIONS:
    """Test the truth table."""

    def test_has_16_positions(self) -> None:
        """Must have exactly 16 positions."""
        assert len(MAHAMANTRA_POSITIONS) == 16

    def test_positions_indexed_0_to_15(self) -> None:
        """Position indices match their index in tuple."""
        for i, pos in enumerate(MAHAMANTRA_POSITIONS):
            assert pos.index == i

    def test_all_positions_connected(self) -> None:
        """All positions must be parampara connected."""
        for pos in MAHAMANTRA_POSITIONS:
            assert pos.is_connected
            assert pos.parampara_vector % PARAMPARA == 0


class TestPositionQuarters:
    """Test quarter assignments."""

    def test_genesis_0_to_3(self) -> None:
        """Positions 0-3 are GENESIS."""
        for i in range(4):
            assert MAHAMANTRA_POSITIONS[i].quarter == Quarter.GENESIS

    def test_dharma_4_to_7(self) -> None:
        """Positions 4-7 are DHARMA."""
        for i in range(4, 8):
            assert MAHAMANTRA_POSITIONS[i].quarter == Quarter.DHARMA

    def test_karma_8_to_11(self) -> None:
        """Positions 8-11 are KARMA."""
        for i in range(8, 12):
            assert MAHAMANTRA_POSITIONS[i].quarter == Quarter.KARMA

    def test_moksha_12_to_15(self) -> None:
        """Positions 12-15 are MOKSHA."""
        for i in range(12, 16):
            assert MAHAMANTRA_POSITIONS[i].quarter == Quarter.MOKSHA


class TestPositionGuardians:
    """Test guardian assignments."""

    def test_heads_are_avataras(self) -> None:
        """HEAD positions (0,4,8,12) have Avatara guardians."""
        for i in (0, 4, 8, 12):
            pos = MAHAMANTRA_POSITIONS[i]
            assert pos.is_head
            assert isinstance(pos.guardian, Avatara)

    def test_workers_are_mahajanas(self) -> None:
        """WORKER positions have Mahajana guardians."""
        worker_indices = (1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15)
        for i in worker_indices:
            pos = MAHAMANTRA_POSITIONS[i]
            assert not pos.is_head
            assert isinstance(pos.guardian, Mahajana)

    def test_specific_guardians(self) -> None:
        """Verify specific guardian assignments (seed.py truth)."""
        # TRUTH: GENESIS=vyasa(0), DHARMA=prithu(4)
        assert MAHAMANTRA_POSITIONS[0].guardian == Avatara.VYASA
        assert MAHAMANTRA_POSITIONS[1].guardian == Mahajana.BRAHMA
        assert MAHAMANTRA_POSITIONS[4].guardian == Avatara.PRITHU
        assert MAHAMANTRA_POSITIONS[15].guardian == Mahajana.YAMARAJA


class TestPositionOpcodes:
    """Test opcode assignments."""

    def test_each_position_has_opcode(self) -> None:
        """Every position has an opcode."""
        for pos in MAHAMANTRA_POSITIONS:
            assert isinstance(pos.opcode, MantraOpCode)

    def test_opcode_matches_index(self) -> None:
        """Opcode value equals position index."""
        for pos in MAHAMANTRA_POSITIONS:
            assert pos.opcode.value == pos.index


class TestPositionParampara:
    """Test parampara vectors."""

    def test_parampara_formula(self) -> None:
        """Parampara vector = (index + 1) * 37."""
        for pos in MAHAMANTRA_POSITIONS:
            expected = (pos.index + 1) * PARAMPARA
            assert pos.parampara_vector == expected

    def test_is_connected(self) -> None:
        """is_connected returns True for valid positions."""
        for pos in MAHAMANTRA_POSITIONS:
            assert pos.is_connected


class TestPositionLookup:
    """Test lookup functions."""

    def test_get_position_by_index(self) -> None:
        """get_position_by_index returns correct position."""
        pos = get_position_by_index(5)
        assert pos.index == 5
        assert pos.guardian == Mahajana.KUMARAS

    def test_get_position_by_index_invalid(self) -> None:
        """get_position_by_index raises for invalid index."""
        import pytest

        with pytest.raises(ValueError):
            get_position_by_index(16)

    def test_get_position_by_guardian(self) -> None:
        """get_position_by_guardian finds position."""
        pos = get_position_by_guardian(Mahajana.NARADA)
        assert pos.index == 2

    def test_get_position_by_opcode(self) -> None:
        """get_position_by_opcode finds position."""
        pos = get_position_by_opcode(MantraOpCode.AUDIT_SEAL)
        assert pos.index == 15

    def test_get_positions_by_quarter(self) -> None:
        """get_positions_by_quarter returns 4 positions."""
        genesis = get_positions_by_quarter(Quarter.GENESIS)
        assert len(genesis) == 4
        for pos in genesis:
            assert pos.quarter == Quarter.GENESIS

    def test_get_head_position(self) -> None:
        """get_head_position returns HEAD for quarter."""
        head = get_head_position(Quarter.KARMA)
        assert head.index == 8
        assert head.is_head
        assert head.guardian == Avatara.PARASHURAMA

    def test_get_worker_positions(self) -> None:
        """get_worker_positions returns 3 workers per quarter."""
        workers = get_worker_positions(Quarter.MOKSHA)
        assert len(workers) == 3
        for pos in workers:
            assert not pos.is_head
            assert pos.quarter == Quarter.MOKSHA
