"""
MAHAJANA ROUTER TESTS
=====================

"The Mahamantra sequence ITSELF determines routing."

Tests that the router correctly maps:
- 16 OpCodes → 12 Mahajanas
- 12 Mahajanas → Their OpCodes
- The sequence is complete and correct
"""

import pytest
from vibe_core.protocols.mahajanas import (
    Mahajana,
    MahajanaRoute,
    get_router,
    route,
    get_opcodes,
    verify_router,
)
from vibe_core.protocols.universal.mantra import MantraOpCode


class TestMahajanaRouter:
    """Tests for the OpCode → Mahajana router."""

    def test_01_router_is_complete(self) -> None:
        """All 16 OpCodes must be mapped."""
        verify_router()  # Raises if incomplete

    def test_02_all_opcodes_routable(self) -> None:
        """Every OpCode routes to a Mahajana."""
        for opcode in MantraOpCode:
            mahajana = route(opcode)
            assert isinstance(mahajana, Mahajana), f"{opcode} must route to Mahajana"

    def test_03_shambhu_owns_garbage_collect(self) -> None:
        """SHAMBHU owns GARBAGE_COLLECT (Bit 7)."""
        assert route(MantraOpCode.GARBAGE_COLLECT) == Mahajana.SHAMBHU

    def test_04_bali_owns_yield_cpu(self) -> None:
        """BALI owns YIELD_CPU (Bit 15)."""
        assert route(MantraOpCode.YIELD_CPU) == Mahajana.BALI

    def test_05_yamaraja_owns_assert_truth(self) -> None:
        """YAMARAJA owns ASSERT_TRUTH (Bit 5)."""
        assert route(MantraOpCode.ASSERT_TRUTH) == Mahajana.YAMARAJA

    def test_06_brahma_owns_creation_opcodes(self) -> None:
        """BRAHMA owns SYS_WAKE, LOAD_ROOT, ALLOC_MEM."""
        brahma_opcodes = get_opcodes(Mahajana.BRAHMA)
        assert MantraOpCode.SYS_WAKE in brahma_opcodes
        assert MantraOpCode.LOAD_ROOT in brahma_opcodes
        assert MantraOpCode.ALLOC_MEM in brahma_opcodes
        assert len(brahma_opcodes) == 3

    def test_07_kapila_owns_analysis_opcodes(self) -> None:
        """KAPILA owns RESOLVE_REQ, OPTIMIZE."""
        kapila_opcodes = get_opcodes(Mahajana.KAPILA)
        assert MantraOpCode.RESOLVE_REQ in kapila_opcodes
        assert MantraOpCode.OPTIMIZE in kapila_opcodes
        assert len(kapila_opcodes) == 2

    def test_08_manu_owns_law_opcodes(self) -> None:
        """MANU owns BIND_CTX, CHECK_DHARMA."""
        manu_opcodes = get_opcodes(Mahajana.MANU)
        assert MantraOpCode.BIND_CTX in manu_opcodes
        assert MantraOpCode.CHECK_DHARMA in manu_opcodes
        assert len(manu_opcodes) == 2

    def test_09_sequence_has_16_steps(self) -> None:
        """The Mahamantra sequence is exactly 16 steps."""
        router = get_router()
        sequence = router.chant_sequence()
        assert len(sequence) == 16

    def test_10_sequence_positions_are_1_to_16(self) -> None:
        """Positions are 1 through 16, no gaps."""
        router = get_router()
        sequence = router.chant_sequence()
        positions = [r.position for r in sequence]
        assert positions == list(range(1, 17))

    def test_11_four_quarters(self) -> None:
        """Each quarter has 4 steps."""
        router = get_router()
        for q in range(1, 5):
            quarter_routes = router.get_quarter(q)
            assert len(quarter_routes) == 4, f"Quarter {q} must have 4 steps"

    def test_12_mahajana_enum_has_12_members(self) -> None:
        """Mahajana enum has exactly 12 members."""
        assert len(Mahajana) == 12


class TestMahajanaRouteData:
    """Tests for MahajanaRoute dataclass."""

    def test_route_is_immutable(self) -> None:
        """Routes are frozen (immutable)."""
        router = get_router()
        route_obj = router.get_route(MantraOpCode.SYS_WAKE)

        with pytest.raises(Exception):  # FrozenInstanceError
            route_obj.position = 999  # type: ignore

    def test_route_has_all_fields(self) -> None:
        """Route has opcode, mahajana, quarter, position."""
        router = get_router()
        route_obj = router.get_route(MantraOpCode.GARBAGE_COLLECT)

        assert route_obj.opcode == MantraOpCode.GARBAGE_COLLECT
        assert route_obj.mahajana == Mahajana.SHAMBHU
        assert route_obj.quarter == 2
        assert route_obj.position == 7
