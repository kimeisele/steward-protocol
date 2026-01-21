"""
TESTS: guna.py - The Three Modes of Material Nature
====================================================

"sattvam rajas tama iti gunah prakriti-sambhavah"

REAL TESTS for:
1. Guna enum (SATTVA, RAJAS, TAMAS)
2. Vishuddha Sattva (transcendental)
3. OpCode to Guna mapping
4. GunaQoS (Quality of Service)
"""

import pytest
from vibe_core.mahamantra.substrate.guna import (
    Guna,
    VISHUDDHA_SATTVA,
    is_vishuddha,
    SATTVA_OPCODES,
    RAJAS_OPCODES,
    TAMAS_OPCODES,
    OPCODE_GUNA,
    get_guna,
    get_guna_by_position,
    is_sattva,
    is_rajas,
    is_tamas,
    GunaQoS,
)
from vibe_core.mahamantra.substrate.opcode import MantraOpCode


# =============================================================================
# Guna Enum Tests
# =============================================================================


class TestGunaEnum:
    """Test Guna IntEnum."""

    def test_exactly_3_gunas(self):
        """Must have exactly 3 gunas (BG 14.5)."""
        assert len(Guna) == 3

    def test_sattva_is_0(self):
        """SATTVA = 0 (Goodness)."""
        assert Guna.SATTVA.value == 0

    def test_rajas_is_1(self):
        """RAJAS = 1 (Passion)."""
        assert Guna.RAJAS.value == 1

    def test_tamas_is_2(self):
        """TAMAS = 2 (Ignorance)."""
        assert Guna.TAMAS.value == 2

    def test_guna_names(self):
        """Guna names match BG 14."""
        assert Guna.SATTVA.name == "SATTVA"
        assert Guna.RAJAS.name == "RAJAS"
        assert Guna.TAMAS.name == "TAMAS"


# =============================================================================
# Vishuddha Sattva Tests
# =============================================================================


class TestVishuddhasSattva:
    """Test transcendental mode (above three gunas)."""

    def test_vishuddha_constant(self):
        """VISHUDDHA_SATTVA is 'vishuddha'."""
        assert VISHUDDHA_SATTVA == "vishuddha"

    def test_is_vishuddha_chant(self):
        """'chant' is vishuddha (transcendental)."""
        assert is_vishuddha("chant") is True
        assert is_vishuddha("CHANT") is True
        assert is_vishuddha("Chant") is True

    def test_is_vishuddha_tick(self):
        """'tick' is vishuddha (transcendental)."""
        assert is_vishuddha("tick") is True

    def test_is_vishuddha_mahamantra(self):
        """'mahamantra' is vishuddha (transcendental)."""
        assert is_vishuddha("mahamantra") is True

    def test_regular_ops_not_vishuddha(self):
        """Regular operations are NOT vishuddha."""
        assert is_vishuddha("read") is False
        assert is_vishuddha("write") is False
        assert is_vishuddha("delete") is False
        assert is_vishuddha("execute") is False


# =============================================================================
# OpCode to Guna Mapping Tests
# =============================================================================


class TestOpCodeSets:
    """Test OpCode classification sets."""

    def test_sattva_opcodes_count(self):
        """SATTVA_OPCODES has 4 opcodes."""
        assert len(SATTVA_OPCODES) == 4

    def test_rajas_opcodes_count(self):
        """RAJAS_OPCODES has 9 opcodes."""
        assert len(RAJAS_OPCODES) == 9

    def test_tamas_opcodes_count(self):
        """TAMAS_OPCODES has 3 opcodes."""
        assert len(TAMAS_OPCODES) == 3

    def test_total_opcodes_is_16(self):
        """Total mapped opcodes = 16 (all positions)."""
        total = len(SATTVA_OPCODES) + len(RAJAS_OPCODES) + len(TAMAS_OPCODES)
        assert total == 16

    def test_sets_are_disjoint(self):
        """Sets have no overlap."""
        assert len(SATTVA_OPCODES & RAJAS_OPCODES) == 0
        assert len(SATTVA_OPCODES & TAMAS_OPCODES) == 0
        assert len(RAJAS_OPCODES & TAMAS_OPCODES) == 0

    def test_opcode_guna_dict_complete(self):
        """OPCODE_GUNA has all 16 opcodes."""
        assert len(OPCODE_GUNA) == 16


class TestSattvaOpcodes:
    """Test SATTVA opcodes (read-only, observation)."""

    def test_type_check_is_sattva(self):
        """TYPE_CHECK (Kapila) is SATTVA."""
        assert MantraOpCode.TYPE_CHECK in SATTVA_OPCODES

    def test_dharma_test_is_sattva(self):
        """DHARMA_TEST (Manu) is SATTVA."""
        assert MantraOpCode.DHARMA_TEST in SATTVA_OPCODES

    def test_log_emit_is_sattva(self):
        """LOG_EMIT (Shuka) is SATTVA."""
        assert MantraOpCode.LOG_EMIT in SATTVA_OPCODES

    def test_audit_seal_is_sattva(self):
        """AUDIT_SEAL (Yamaraja) is SATTVA."""
        assert MantraOpCode.AUDIT_SEAL in SATTVA_OPCODES


class TestRajasOpcodes:
    """Test RAJAS opcodes (write, modification)."""

    def test_sys_wake_is_rajas(self):
        """SYS_WAKE (Prithu) is RAJAS."""
        assert MantraOpCode.SYS_WAKE in RAJAS_OPCODES

    def test_load_root_is_rajas(self):
        """LOAD_ROOT (Brahma) is RAJAS."""
        assert MantraOpCode.LOAD_ROOT in RAJAS_OPCODES

    def test_exec_op_is_rajas(self):
        """EXEC_OP (Parashurama) is RAJAS."""
        assert MantraOpCode.EXEC_OP in RAJAS_OPCODES

    def test_ledger_sign_is_rajas(self):
        """LEDGER_SIGN (Bhishma) is RAJAS."""
        assert MantraOpCode.LEDGER_SIGN in RAJAS_OPCODES


class TestTamasOpcodes:
    """Test TAMAS opcodes (destruction, cleanup)."""

    def test_init_thread_is_tamas(self):
        """INIT_THREAD (Shambhu) is TAMAS."""
        assert MantraOpCode.INIT_THREAD in TAMAS_OPCODES

    def test_yield_cpu_is_tamas(self):
        """YIELD_CPU (Nrisimha) is TAMAS."""
        assert MantraOpCode.YIELD_CPU in TAMAS_OPCODES

    def test_io_flush_is_tamas(self):
        """IO_FLUSH (Bali) is TAMAS."""
        assert MantraOpCode.IO_FLUSH in TAMAS_OPCODES


# =============================================================================
# get_guna Function Tests
# =============================================================================


class TestGetGuna:
    """Test get_guna function."""

    def test_get_guna_sattva(self):
        """get_guna returns SATTVA for sattva opcodes."""
        assert get_guna(MantraOpCode.TYPE_CHECK) == Guna.SATTVA
        assert get_guna(MantraOpCode.AUDIT_SEAL) == Guna.SATTVA

    def test_get_guna_rajas(self):
        """get_guna returns RAJAS for rajas opcodes."""
        assert get_guna(MantraOpCode.SYS_WAKE) == Guna.RAJAS
        assert get_guna(MantraOpCode.EXEC_OP) == Guna.RAJAS

    def test_get_guna_tamas(self):
        """get_guna returns TAMAS for tamas opcodes."""
        assert get_guna(MantraOpCode.INIT_THREAD) == Guna.TAMAS
        assert get_guna(MantraOpCode.YIELD_CPU) == Guna.TAMAS


class TestGetGunaByPosition:
    """Test get_guna_by_position function."""

    def test_position_0_is_rajas(self):
        """Position 0 (SYS_WAKE) is RAJAS."""
        assert get_guna_by_position(0) == Guna.RAJAS

    def test_position_6_is_sattva(self):
        """Position 6 (TYPE_CHECK) is SATTVA."""
        assert get_guna_by_position(6) == Guna.SATTVA

    def test_position_3_is_tamas(self):
        """Position 3 (INIT_THREAD) is TAMAS."""
        assert get_guna_by_position(3) == Guna.TAMAS

    def test_position_15_is_sattva(self):
        """Position 15 (AUDIT_SEAL) is SATTVA."""
        assert get_guna_by_position(15) == Guna.SATTVA

    def test_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            get_guna_by_position(16)
        with pytest.raises(ValueError):
            get_guna_by_position(-1)


# =============================================================================
# Predicate Function Tests
# =============================================================================


class TestGunaPredicates:
    """Test is_sattva, is_rajas, is_tamas functions."""

    def test_is_sattva(self):
        """is_sattva returns True for sattva opcodes."""
        assert is_sattva(MantraOpCode.TYPE_CHECK) is True
        assert is_sattva(MantraOpCode.AUDIT_SEAL) is True
        assert is_sattva(MantraOpCode.SYS_WAKE) is False

    def test_is_rajas(self):
        """is_rajas returns True for rajas opcodes."""
        assert is_rajas(MantraOpCode.SYS_WAKE) is True
        assert is_rajas(MantraOpCode.EXEC_OP) is True
        assert is_rajas(MantraOpCode.TYPE_CHECK) is False

    def test_is_tamas(self):
        """is_tamas returns True for tamas opcodes."""
        assert is_tamas(MantraOpCode.INIT_THREAD) is True
        assert is_tamas(MantraOpCode.YIELD_CPU) is True
        assert is_tamas(MantraOpCode.SYS_WAKE) is False


# =============================================================================
# GunaQoS Tests
# =============================================================================


class TestGunaQoS:
    """Test GunaQoS class."""

    def test_sattva_latency_is_1(self):
        """SATTVA latency is 1.0 (fast)."""
        assert GunaQoS.SATTVA_LATENCY == 1.0

    def test_rajas_latency_is_1_5(self):
        """RAJAS latency is 1.5 (normal)."""
        assert GunaQoS.RAJAS_LATENCY == 1.5

    def test_tamas_latency_is_3(self):
        """TAMAS latency is 3.0 (slow, intentional)."""
        assert GunaQoS.TAMAS_LATENCY == 3.0

    def test_get_latency_multiplier(self):
        """get_latency_multiplier returns correct values."""
        assert GunaQoS.get_latency_multiplier(Guna.SATTVA) == 1.0
        assert GunaQoS.get_latency_multiplier(Guna.RAJAS) == 1.5
        assert GunaQoS.get_latency_multiplier(Guna.TAMAS) == 3.0

    def test_sattva_allows_parallel(self):
        """SATTVA allows parallel execution."""
        assert GunaQoS.allows_parallel(Guna.SATTVA) is True
        assert GunaQoS.SATTVA_PARALLEL is True

    def test_rajas_not_parallel(self):
        """RAJAS does not allow parallel."""
        assert GunaQoS.allows_parallel(Guna.RAJAS) is False
        assert GunaQoS.RAJAS_PARALLEL is False

    def test_tamas_not_parallel(self):
        """TAMAS does not allow parallel."""
        assert GunaQoS.allows_parallel(Guna.TAMAS) is False
        assert GunaQoS.TAMAS_PARALLEL is False

    def test_tamas_requires_confirmation(self):
        """TAMAS requires confirmation."""
        assert GunaQoS.requires_confirmation(Guna.TAMAS) is True
        assert GunaQoS.TAMAS_CONFIRM is True

    def test_sattva_no_confirmation(self):
        """SATTVA does not require confirmation."""
        assert GunaQoS.requires_confirmation(Guna.SATTVA) is False
        assert GunaQoS.SATTVA_CONFIRM is False

    def test_rajas_no_confirmation(self):
        """RAJAS does not require confirmation."""
        assert GunaQoS.requires_confirmation(Guna.RAJAS) is False
        assert GunaQoS.RAJAS_CONFIRM is False
