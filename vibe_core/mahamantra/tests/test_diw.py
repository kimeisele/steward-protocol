"""
DIW — Divine Instruction Word Tests
=====================================

Tests the 19-bit DIW protocol:
- pack/unpack roundtrip integrity
- Bit field isolation (VENU/VAMSI/MURALI)
- THE_FLUTE_CYCLE static LUT
- 32-bit transport word (pack_full)
- VenuOrchestrator step/cycle
"""

import pytest

from vibe_core.mahamantra.protocols.diw import (
    DIW,
    DIW_MASK,
    MURALI_MASK,
    MURALI_SHIFT,
    SUNYA_MASK,
    VAMSI_MASK,
    VAMSI_SHIFT,
    VENU_MASK,
    VENU_SHIFT,
    extract_core,
    is_sunya,
    pack,
    pack_full,
    unpack,
)


class TestDIWConstants:
    """Bit layout constants must match the 19-bit spec."""

    def test_shifts(self):
        assert VENU_SHIFT == 0
        assert VAMSI_SHIFT == 6
        assert MURALI_SHIFT == 15

    def test_masks(self):
        assert VENU_MASK == 0x3F  # 6 bits
        assert VAMSI_MASK == 0x1FF  # 9 bits
        assert MURALI_MASK == 0xF  # 4 bits

    def test_diw_mask(self):
        """Total DIW = 19 bits."""
        assert DIW_MASK == 0x7FFFF
        assert DIW_MASK == (1 << 19) - 1

    def test_sunya_mask(self):
        """Sunya (silence) is bit 31."""
        assert SUNYA_MASK == 0x80000000


class TestPackUnpack:
    """pack/unpack must be perfect inverses."""

    def test_roundtrip_zero(self):
        word = pack(0, 0, 0)
        result = unpack(word)
        assert result.venu == 0
        assert result.vamsi == 0
        assert result.murali == 0

    def test_roundtrip_max(self):
        """Maximum values for each field."""
        word = pack(VENU_MASK, VAMSI_MASK, MURALI_MASK)
        result = unpack(word)
        assert result.venu == VENU_MASK  # 63
        assert result.vamsi == VAMSI_MASK  # 511
        assert result.murali == MURALI_MASK  # 15

    def test_roundtrip_specific(self):
        """Known values roundtrip."""
        word = pack(5, 170, 3)
        result = unpack(word)
        assert result.venu == 5
        assert result.vamsi == 170
        assert result.murali == 3

    def test_field_isolation_venu(self):
        """VENU changes don't affect VAMSI/MURALI."""
        w1 = pack(0, 100, 2)
        w2 = pack(63, 100, 2)
        r1, r2 = unpack(w1), unpack(w2)
        assert r1.vamsi == r2.vamsi == 100
        assert r1.murali == r2.murali == 2

    def test_field_isolation_vamsi(self):
        """VAMSI changes don't affect VENU/MURALI."""
        w1 = pack(10, 0, 3)
        w2 = pack(10, 511, 3)
        r1, r2 = unpack(w1), unpack(w2)
        assert r1.venu == r2.venu == 10
        assert r1.murali == r2.murali == 3

    def test_field_isolation_murali(self):
        """MURALI changes don't affect VENU/VAMSI."""
        w1 = pack(10, 200, 0)
        w2 = pack(10, 200, 15)
        r1, r2 = unpack(w1), unpack(w2)
        assert r1.venu == r2.venu == 10
        assert r1.vamsi == r2.vamsi == 200

    def test_diw_is_namedtuple(self):
        result = unpack(pack(1, 2, 3))
        assert isinstance(result, DIW)
        assert hasattr(result, "venu")
        assert hasattr(result, "vamsi")
        assert hasattr(result, "murali")

    @pytest.mark.parametrize(
        "venu,vamsi,murali",
        [
            (0, 0, 0),
            (1, 1, 1),
            (32, 256, 8),
            (63, 511, 15),
            (42, 170, 3),
            (7, 340, 11),
        ],
    )
    def test_roundtrip_parametric(self, venu, vamsi, murali):
        word = pack(venu, vamsi, murali)
        r = unpack(word)
        assert (r.venu, r.vamsi, r.murali) == (venu, vamsi, murali)

    def test_packed_within_19_bits(self):
        """All packed values must fit in 19 bits."""
        for v in range(0, 64, 7):
            for vs in range(0, 512, 51):
                for m in range(0, 16, 3):
                    assert pack(v, vs, m) <= DIW_MASK


class TestPackFull:
    """32-bit transport word tests."""

    def test_core_preserved(self):
        core = pack(5, 170, 3)
        full = pack_full(5, 170, 3)
        assert extract_core(full) == core


# ============================================================================
# VenuOrchestrator — THE_FLUTE_CYCLE
# ============================================================================


class TestVenuOrchestrator:
    """The orchestrator that produces DIW from the Mahamantra."""

    def test_flute_cycle_length(self):
        """THE_FLUTE_CYCLE has exactly 16 entries (WORDS)."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import THE_FLUTE_CYCLE

        assert len(THE_FLUTE_CYCLE) == 16

    def test_flute_cycle_entries_are_valid_diw(self):
        """Every entry in THE_FLUTE_CYCLE must be a valid 19-bit DIW."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import THE_FLUTE_CYCLE

        for i, entry in enumerate(THE_FLUTE_CYCLE):
            assert entry <= DIW_MASK, f"Entry {i} exceeds 19-bit DIW: {entry:#x}"
            r = unpack(entry)
            assert 0 <= r.venu <= VENU_MASK
            assert 0 <= r.vamsi <= VAMSI_MASK
            assert 0 <= r.murali <= MURALI_MASK

    def test_flute_cycle_no_duplicates(self):
        """All 16 entries should be unique."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import THE_FLUTE_CYCLE

        assert len(set(THE_FLUTE_CYCLE)) == 16

    def test_orchestrator_step(self):
        """step() returns a valid DIW and advances position."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import VenuOrchestrator

        orch = VenuOrchestrator()
        diw = orch.step()
        assert isinstance(diw, int)
        assert extract_core(diw) <= DIW_MASK

    def test_orchestrator_full_cycle(self):
        """cycle() runs all 16 steps."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import VenuOrchestrator

        orch = VenuOrchestrator()
        result = orch.cycle()
        assert isinstance(result, int)

    def test_orchestrator_verify_divinity(self):
        """LUT structural integrity check."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import VenuOrchestrator

        orch = VenuOrchestrator()
        assert orch.verify_divinity() is True

    def test_orchestrator_reset(self):
        """reset() returns to initial state."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import VenuOrchestrator

        orch = VenuOrchestrator()
        orch.step()
        orch.step()
        orch.reset()
        # After reset, first step should give same result as fresh orchestrator
        fresh = VenuOrchestrator()
        assert orch.step() == fresh.step()

    def test_orchestrator_persistence(self):
        """to_bytes / from_bytes roundtrip."""
        from vibe_core.mahamantra.substrate.vm.venu_orchestrator import VenuOrchestrator

        orch = VenuOrchestrator()
        for _ in range(5):
            orch.step()
        data = orch.to_bytes()
        assert isinstance(data, bytes)
        assert len(data) == 24

        restored = VenuOrchestrator()
        restored.from_bytes(data)
        assert orch.step() == restored.step()

    def test_sunya_flag(self):
        word = pack_full(0, 0, 0, sunya=True)
        assert is_sunya(word) is True
        word_normal = pack_full(0, 0, 0, sunya=False)
        assert is_sunya(word_normal) is False

    def test_extract_core_strips_upper_bits(self):
        full = pack_full(5, 170, 3, velocity=7, cluster=3)
        core = extract_core(full)
        assert core <= DIW_MASK
        r = unpack(core)
        assert r.venu == 5
        assert r.vamsi == 170
        assert r.murali == 3
