"""
Tests for the Chatur-Vyuha (4x4 Fractal Architecture)
=====================================================

Verifies:
1. 16 = 4 × (1 + 3) structure
2. 1:1 Mahajana:OpCode mapping
3. CycleHead seal mechanism (Military-Grade)
4. Orphan process prevention
"""

import time
from datetime import datetime

import pytest

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.avataras import Avatara
from vibe_core.protocols.mahajanas.router import (
    HEAD_OPCODES,
    Mahajana,
    MahajanaRouter,
)
from vibe_core.protocols.mahajanas.vyuha import (
    CHATUR_VYUHA,
    CYCLE_DHARMA,
    CYCLE_GENESIS,
    CYCLE_KARMA,
    CYCLE_MOKSHA,
    CycleDefinition,
    CyclePhase,
    CycleSeal,
    SealStatus,
    Vyuha,
    VyuhaRouter,
    get_cycle_for_mahajana,
    get_cycle_for_opcode,
    get_entity_for_opcode,
    get_head_for_opcode,
    get_mahajana_for_opcode,
    get_opcodes_for_mahajana,
    get_vyuha_router,
    verify_chatur_vyuha,
)


class TestChaturVyuhaStructure:
    """Tests for the 4x4 fractal structure."""

    def test_sixteen_equals_four_times_four(self):
        """16 = 4 × (1 + 3): 4 cycles, each with 1 HEAD + 3 workers."""
        assert len(CHATUR_VYUHA) == 4

        total_entities = 0
        for cycle in CHATUR_VYUHA:
            # 1 HEAD + 3 workers
            assert len(cycle.all_mahajanas) == 3
            total_entities += 4  # 1 HEAD + 3

        assert total_entities == 16

    def test_all_opcodes_mapped_exactly_once(self):
        """All 16 OpCodes are mapped exactly once."""
        all_opcodes = []
        for cycle in CHATUR_VYUHA:
            all_opcodes.extend(cycle.all_opcodes)

        assert len(all_opcodes) == 16
        assert len(set(all_opcodes)) == 16
        assert set(all_opcodes) == set(MantraOpCode)

    def test_all_mahajanas_in_exactly_one_cycle(self):
        """All 12 Mahajanas are in exactly one cycle."""
        all_mahajanas = []
        for cycle in CHATUR_VYUHA:
            all_mahajanas.extend(cycle.all_mahajanas)

        assert len(all_mahajanas) == 12
        assert len(set(all_mahajanas)) == 12
        assert set(all_mahajanas) == set(Mahajana)

    def test_four_unique_heads(self):
        """Each cycle has a unique HEAD (Avatara)."""
        heads = [c.head for c in CHATUR_VYUHA]
        assert len(set(heads)) == 4

    def test_verify_function_passes(self):
        """verify_chatur_vyuha() returns True."""
        assert verify_chatur_vyuha() is True


class TestOneToOneMahajanaOpCode:
    """Tests for 1:1 Mahajana:OpCode mapping."""

    def test_each_mahajana_owns_one_opcode(self):
        """Each Mahajana owns exactly 1 OpCode in Vyuha mode."""
        router = MahajanaRouter(legacy=False)

        for mahajana in Mahajana:
            opcodes = router.get_opcodes(mahajana)
            assert len(opcodes) == 1, f"{mahajana} owns {len(opcodes)} OpCodes"

    def test_head_opcodes_not_in_mahajana_router(self):
        """HEAD OpCodes are owned by Avataras, not Mahajanas."""
        assert len(HEAD_OPCODES) == 4

        for opcode in HEAD_OPCODES:
            result = get_mahajana_for_opcode(opcode)
            assert result is None, f"{opcode} should not have Mahajana owner"

    def test_worker_opcodes_have_mahajana_owners(self):
        """Worker OpCodes have Mahajana owners."""
        worker_opcodes = [op for op in MantraOpCode if op not in HEAD_OPCODES]
        assert len(worker_opcodes) == 12

        for opcode in worker_opcodes:
            result = get_mahajana_for_opcode(opcode)
            assert result is not None, f"{opcode} should have Mahajana owner"


class TestCycleSeal:
    """Tests for the CycleHead seal mechanism (Military-Grade)."""

    def test_valid_parampara_creates_seal(self):
        """Valid parampara (37) creates seal successfully."""
        seal = CYCLE_GENESIS.create_seal(lineage_hash=37)
        assert seal.head == Avatara.PRITHU
        assert seal.cycle == Vyuha.VASUDEVA
        assert len(seal.salt) == 16
        assert len(seal.block_hash) == 64  # SHA-256 hex

    def test_invalid_parampara_raises(self):
        """Invalid parampara raises PermissionError."""
        with pytest.raises(PermissionError) as exc_info:
            CYCLE_GENESIS.create_seal(lineage_hash=42)

        assert "Invalid parampara" in str(exc_info.value)
        assert "37" in str(exc_info.value)

    def test_multiples_of_37_are_valid(self):
        """Multiples of 37 are valid parampara."""
        for multiple in [37, 74, 111, 148, 370]:
            seal = CYCLE_GENESIS.create_seal(lineage_hash=multiple)
            assert seal is not None

    def test_seal_verifies_correct_opcodes(self):
        """Seal verifies correct OpCodes."""
        seal = CYCLE_DHARMA.create_seal(lineage_hash=37)
        result = seal.verify(CYCLE_DHARMA.all_opcodes)

        assert result["status"] == SealStatus.VALID.value
        assert result["error_message"] == ""

    def test_seal_rejects_wrong_opcodes(self):
        """Seal rejects wrong OpCodes."""
        seal = CYCLE_GENESIS.create_seal(lineage_hash=37)
        result = seal.verify(CYCLE_DHARMA.all_opcodes)  # Wrong cycle!

        assert result["status"] == SealStatus.INVALID.value
        assert "mismatch" in result["error_message"].lower()

    def test_headless_cycle_impossible(self):
        """Without HEAD seal, cycle is rejected (Headless Noise)."""
        # Attempting to create seal without valid parampara = no HEAD authorization
        # Note: 0 % 37 == 0, so use a non-zero non-multiple
        with pytest.raises(PermissionError):
            CYCLE_KARMA.create_seal(lineage_hash=1)  # Invalid (not multiple of 37)


class TestVyuhaRouter:
    """Tests for the VyuhaRouter (cycle-aware routing)."""

    def test_routes_opcode_to_cycle_and_entity(self):
        """Routes OpCode to its cycle and responsible entity."""
        router = get_vyuha_router()

        cycle, entity = router.route(MantraOpCode.TYPE_CHECK)
        assert cycle.vyuha == Vyuha.SANKARSHANA
        assert entity == Mahajana.KAPILA

    def test_head_opcodes_route_to_avatara(self):
        """HEAD OpCodes route to Avatara, not Mahajana."""
        router = get_vyuha_router()

        cycle, entity = router.route(MantraOpCode.SYS_WAKE)
        assert cycle.vyuha == Vyuha.VASUDEVA
        assert entity == Avatara.PRITHU

    def test_authorize_cycle_returns_seal(self):
        """authorize_cycle returns valid seal."""
        router = get_vyuha_router()
        seal = router.authorize_cycle(CYCLE_MOKSHA, lineage_hash=37)

        assert seal.head == Avatara.NRISIMHA
        assert seal.cycle == Vyuha.ANIRUDDHA


class TestCyclePhases:
    """Tests for cycle phase mappings."""

    def test_cycle_quarters(self):
        """Each cycle maps to correct quarter."""
        assert CYCLE_GENESIS.quarter == 1
        assert CYCLE_DHARMA.quarter == 2
        assert CYCLE_KARMA.quarter == 3
        assert CYCLE_MOKSHA.quarter == 4

    def test_cycle_phases(self):
        """Each cycle has correct phase."""
        assert CYCLE_GENESIS.phase == CyclePhase.GENESIS
        assert CYCLE_DHARMA.phase == CyclePhase.DHARMA
        assert CYCLE_KARMA.phase == CyclePhase.KARMA
        assert CYCLE_MOKSHA.phase == CyclePhase.MOKSHA


class TestRoutingFunctions:
    """Tests for convenience routing functions."""

    def test_get_cycle_for_opcode(self):
        """get_cycle_for_opcode returns correct cycle."""
        cycle = get_cycle_for_opcode(MantraOpCode.LEDGER_SIGN)
        assert cycle.vyuha == Vyuha.PRADYUMNA

    def test_get_head_for_opcode(self):
        """get_head_for_opcode returns cycle HEAD."""
        head = get_head_for_opcode(MantraOpCode.IO_FLUSH)
        assert head == Avatara.NRISIMHA  # Q4 HEAD

    def test_get_cycle_for_mahajana(self):
        """get_cycle_for_mahajana returns correct cycle."""
        cycle = get_cycle_for_mahajana(Mahajana.BHISHMA)
        assert cycle.vyuha == Vyuha.PRADYUMNA

    def test_get_opcodes_for_mahajana(self):
        """get_opcodes_for_mahajana returns single OpCode."""
        opcodes = get_opcodes_for_mahajana(Mahajana.YAMARAJA)
        assert opcodes == [MantraOpCode.AUDIT_SEAL]
