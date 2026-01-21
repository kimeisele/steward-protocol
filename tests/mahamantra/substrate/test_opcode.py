"""
TEST OPCODE - substrate/opcode.py
=================================

Tests for the 16 OpCodes (SSOT).
"""

from vibe_core.mahamantra.substrate import (
    MantraOpCode,
    OPCODE_NAMES,
    MAHAJANA_OPCODES,
    GENESIS_OPCODES,
    DHARMA_OPCODES,
    KARMA_OPCODES,
    MOKSHA_OPCODES,
    Quarter,
    get_opcode,
    get_opcode_name,
    get_mahajana_opcode,
    get_opcode_quarter,
    get_quarter_opcodes,
    OPCODE_PARAMPARA,
    get_opcode_parampara,
    verify_opcode_parampara,
)


class TestMantraOpCode:
    """Test MantraOpCode enum."""

    def test_has_16_opcodes(self) -> None:
        """Must have exactly 16 opcodes."""
        assert len(MantraOpCode) == 16

    def test_opcodes_are_0_to_15(self) -> None:
        """OpCode values must be 0-15."""
        values = [op.value for op in MantraOpCode]
        assert values == list(range(16))

    def test_genesis_opcodes(self) -> None:
        """Genesis quarter has positions 0-3."""
        genesis = [MantraOpCode.SYS_WAKE, MantraOpCode.LOAD_ROOT, MantraOpCode.ALLOC_MEM, MantraOpCode.INIT_THREAD]
        for op in genesis:
            assert op.value < 4

    def test_dharma_opcodes(self) -> None:
        """Dharma quarter has positions 4-7."""
        dharma = [MantraOpCode.COMPILE_AST, MantraOpCode.BIND_SYMBOL, MantraOpCode.TYPE_CHECK, MantraOpCode.DHARMA_TEST]
        for op in dharma:
            assert 4 <= op.value < 8

    def test_karma_opcodes(self) -> None:
        """Karma quarter has positions 8-11."""
        karma = [MantraOpCode.EXEC_OP, MantraOpCode.EXTEND_CAP, MantraOpCode.STATE_SYNC, MantraOpCode.LEDGER_SIGN]
        for op in karma:
            assert 8 <= op.value < 12

    def test_moksha_opcodes(self) -> None:
        """Moksha quarter has positions 12-15."""
        moksha = [MantraOpCode.YIELD_CPU, MantraOpCode.IO_FLUSH, MantraOpCode.LOG_EMIT, MantraOpCode.AUDIT_SEAL]
        for op in moksha:
            assert 12 <= op.value < 16


class TestOpCodeLookup:
    """Test opcode lookup functions."""

    def test_get_opcode_valid(self) -> None:
        """get_opcode returns correct opcode for position."""
        assert get_opcode(0) == MantraOpCode.SYS_WAKE
        assert get_opcode(15) == MantraOpCode.AUDIT_SEAL

    def test_get_opcode_invalid_raises(self) -> None:
        """get_opcode raises for invalid position."""
        import pytest

        with pytest.raises(ValueError):
            get_opcode(16)
        with pytest.raises(ValueError):
            get_opcode(-1)

    def test_get_opcode_name(self) -> None:
        """get_opcode_name returns name string."""
        assert get_opcode_name(0) == "SYS_WAKE"
        assert get_opcode_name(15) == "AUDIT_SEAL"

    def test_get_mahajana_opcode(self) -> None:
        """get_mahajana_opcode maps name to opcode."""
        assert get_mahajana_opcode("brahma") == MantraOpCode.LOAD_ROOT
        assert get_mahajana_opcode("yamaraja") == MantraOpCode.AUDIT_SEAL

    def test_get_opcode_quarter(self) -> None:
        """get_opcode_quarter returns correct quarter."""
        assert get_opcode_quarter(MantraOpCode.SYS_WAKE) == Quarter.GENESIS
        assert get_opcode_quarter(MantraOpCode.COMPILE_AST) == Quarter.DHARMA
        assert get_opcode_quarter(MantraOpCode.EXEC_OP) == Quarter.KARMA
        assert get_opcode_quarter(MantraOpCode.YIELD_CPU) == Quarter.MOKSHA


class TestOpCodeParampara:
    """Test opcode parampara vectors."""

    def test_all_opcodes_have_parampara(self) -> None:
        """Every opcode has a parampara vector."""
        for op in MantraOpCode:
            assert op in OPCODE_PARAMPARA

    def test_parampara_formula(self) -> None:
        """Parampara vector = (position + 1) * 37."""
        for op in MantraOpCode:
            expected = (op.value + 1) * 37
            assert OPCODE_PARAMPARA[op] == expected

    def test_verify_parampara(self) -> None:
        """verify_opcode_parampara validates correctly."""
        for op in MantraOpCode:
            vector = get_opcode_parampara(op)
            assert verify_opcode_parampara(op, vector)
            assert not verify_opcode_parampara(op, vector + 1)


class TestQuarterGroupings:
    """Test quarter opcode groupings."""

    def test_genesis_has_4(self) -> None:
        """Genesis quarter has 4 opcodes."""
        assert len(GENESIS_OPCODES) == 4

    def test_dharma_has_4(self) -> None:
        """Dharma quarter has 4 opcodes."""
        assert len(DHARMA_OPCODES) == 4

    def test_karma_has_4(self) -> None:
        """Karma quarter has 4 opcodes."""
        assert len(KARMA_OPCODES) == 4

    def test_moksha_has_4(self) -> None:
        """Moksha quarter has 4 opcodes."""
        assert len(MOKSHA_OPCODES) == 4

    def test_no_overlap(self) -> None:
        """Quarter groups don't overlap."""
        all_ops = GENESIS_OPCODES | DHARMA_OPCODES | KARMA_OPCODES | MOKSHA_OPCODES
        assert len(all_ops) == 16

    def test_get_quarter_opcodes(self) -> None:
        """get_quarter_opcodes returns correct set."""
        assert get_quarter_opcodes(Quarter.GENESIS) == GENESIS_OPCODES
        assert get_quarter_opcodes(Quarter.MOKSHA) == MOKSHA_OPCODES
