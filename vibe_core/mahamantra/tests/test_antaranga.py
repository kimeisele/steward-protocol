"""
ANTARANGA REGISTRY — Tests for the Inner Chamber (ctypes Zero-Copy)
====================================================================

Tests the 16 KB contiguous RAM chamber: slot read/write, collision logic
(PRESENCE vs RESONANCE), DIW application, query methods, clear/snapshot,
and ctypes overlay correctness.

All constants derived from SSOT (_seed.py). No hardcoding.
"""

import ctypes
import struct

import pytest

from vibe_core.mahamantra.substrate.cell_system.antaranga import (
    _SLOT_FMT,
    ANTARANGA_SLOTS,
    CHAMBER_BYTES,
    FLAG_ACTIVE,
    GENESIS_PRANA_U32,
    INTEGRITY_FULL,
    MAX_PRANA_U32,
    SLOT_BYTES,
    AntarangaRegistry,
    SlotView,
    _CSlot,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def reg():
    """Fresh AntarangaRegistry for each test."""
    return AntarangaRegistry()


# =============================================================================
# CONSTANTS SANITY
# =============================================================================


class TestConstants:
    """Verify SSOT-derived constants are consistent."""

    def test_slot_bytes(self):
        assert SLOT_BYTES == 32

    def test_chamber_bytes(self):
        assert CHAMBER_BYTES == ANTARANGA_SLOTS * SLOT_BYTES

    def test_antaranga_slots(self):
        assert ANTARANGA_SLOTS == 512

    def test_chamber_is_16kb(self):
        assert CHAMBER_BYTES == 16384

    def test_cslot_size_matches_struct(self):
        assert ctypes.sizeof(_CSlot) == struct.calcsize(_SLOT_FMT)

    def test_cslot_size_matches_slot_bytes(self):
        assert ctypes.sizeof(_CSlot) == SLOT_BYTES


# =============================================================================
# INIT & CLEAR
# =============================================================================


class TestInitAndClear:
    """Registry starts silent and can be wiped."""

    def test_init_all_zeros(self, reg):
        assert reg._mem == bytearray(CHAMBER_BYTES)

    def test_init_no_active_slots(self, reg):
        assert reg.active_count() == 0

    def test_init_zero_prana(self, reg):
        assert reg.total_prana() == 0

    def test_clear_wipes_state(self, reg):
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100, 50, 1)
        reg.clear()
        assert reg.active_count() == 0
        assert reg.total_prana() == 0
        assert reg._mem == bytearray(CHAMBER_BYTES)

    def test_size_bytes(self, reg):
        assert reg.size_bytes == CHAMBER_BYTES

    def test_repr_empty(self, reg):
        r = repr(reg)
        assert "0/512" in r
        assert "16384" in r


# =============================================================================
# GET / SET
# =============================================================================


class TestGetSet:
    """O(1) read/write via ctypes overlay + struct.pack_into."""

    def test_get_empty_slot(self, reg):
        sv = reg.get(0)
        assert isinstance(sv, SlotView)
        assert sv == SlotView(0, 0, 0, 0, 0, 0, 0, 0, 0)

    def test_set_and_get_roundtrip(self, reg):
        reg.set_slot(42, 100, 200, 300, 400, 500, FLAG_ACTIVE, 1000, 5000, 7)
        sv = reg.get(42)
        assert sv.source == 100
        assert sv.target == 200
        assert sv.operation == 300
        assert sv.arcanam == 400
        assert sv.atma_nivedanam == 500
        assert sv.flags == FLAG_ACTIVE
        assert sv.prana == 1000
        assert sv.integrity == 5000
        assert sv.cycle == 7

    def test_set_last_slot(self, reg):
        last = ANTARANGA_SLOTS - 1
        reg.set_slot(last, 1, 2, 3, 4, 5, FLAG_ACTIVE, 99, 88, 77)
        sv = reg.get(last)
        assert sv.source == 1
        assert sv.prana == 99
        assert sv.cycle == 77

    def test_set_overwrites(self, reg):
        reg.set_slot(10, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100, 50, 1)
        reg.set_slot(10, 9, 8, 7, 6, 5, FLAG_ACTIVE, 200, 60, 2)
        sv = reg.get(10)
        assert sv.source == 9
        assert sv.prana == 200

    def test_ctypes_overlay_reads_struct_writes(self, reg):
        """ctypes overlay and struct.pack_into share the same memory."""
        reg.set_slot(0, 0xDEAD, 0xBEEF, 0xCAFE, 0xF00D, 0xBABE, 1, 42, 7, 3)
        s = reg._slots[0]
        assert s.source == 0xDEAD
        assert s.target == 0xBEEF
        assert s.operation == 0xCAFE
        assert s.arcanam == 0xF00D
        assert s.atma == 0xBABE
        assert s.flags == 1
        assert s.prana == 42
        assert s.integrity == 7
        assert s.cycle == 3


# =============================================================================
# COLLISION (The Heart of Resonance)
# =============================================================================


class TestCollision:
    """PRESENCE (empty slot) vs RESONANCE (occupied slot)."""

    def test_presence_on_empty_slot(self, reg):
        result = reg.collide(0, 10, 20, 30, 40, 50, 100, 500, 1)
        assert result is False  # PRESENCE, not RESONANCE
        sv = reg.get(0)
        assert sv.source == 10
        assert sv.target == 20
        assert sv.prana == 100
        assert sv.integrity == 500
        assert sv.flags == FLAG_ACTIVE

    def test_resonance_on_occupied_slot(self, reg):
        # First: presence
        reg.collide(5, 1, 2, 3, 4, 5, 100, 1000, 1)
        # Second: resonance
        result = reg.collide(5, 9, 8, 7, 6, 5, 200, 2000, 2)
        assert result is True  # RESONANCE
        sv = reg.get(5)
        # Header unchanged (resident keeps identity)
        assert sv.source == 1
        assert sv.target == 2
        # Prana accumulated
        assert sv.prana == 300
        # Integrity averaged (HALVES = 2)
        assert sv.integrity == (1000 + 2000) // 2
        # Cycle unchanged (from resident)
        assert sv.cycle == 1

    def test_resonance_prana_clamped(self, reg):
        reg.collide(0, 1, 2, 3, 4, 5, MAX_PRANA_U32, INTEGRITY_FULL, 1)
        reg.collide(0, 9, 8, 7, 6, 5, MAX_PRANA_U32, INTEGRITY_FULL, 2)
        sv = reg.get(0)
        assert sv.prana == MAX_PRANA_U32  # Clamped, not overflowed

    def test_multiple_resonances_accumulate(self, reg):
        reg.collide(0, 1, 2, 3, 4, 5, 100, 1000, 1)
        for _ in range(10):
            reg.collide(0, 9, 8, 7, 6, 5, 50, 1000, 2)
        sv = reg.get(0)
        assert sv.prana == 100 + 10 * 50  # 600

    def test_presence_sets_flag_active(self, reg):
        reg.collide(0, 1, 2, 3, 4, 5, 100, 500, 1)
        sv = reg.get(0)
        assert sv.flags == FLAG_ACTIVE


# =============================================================================
# QUERY METHODS
# =============================================================================


class TestQueries:
    """is_alive, prana_at, active_count, total_prana."""

    def test_is_alive_empty(self, reg):
        assert reg.is_alive(0) is False

    def test_is_alive_after_set(self, reg):
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100, 50, 1)
        assert reg.is_alive(0) is True

    def test_is_alive_zero_prana(self, reg):
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, 0, 50, 1)
        assert reg.is_alive(0) is False

    def test_prana_at(self, reg):
        reg.set_slot(7, 1, 2, 3, 4, 5, FLAG_ACTIVE, 42, 50, 1)
        assert reg.prana_at(7) == 42

    def test_prana_at_empty(self, reg):
        assert reg.prana_at(0) == 0

    def test_active_count(self, reg):
        for i in range(10):
            reg.set_slot(i, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100 + i, 50, 1)
        assert reg.active_count() == 10

    def test_total_prana(self, reg):
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100, 50, 1)
        reg.set_slot(1, 1, 2, 3, 4, 5, FLAG_ACTIVE, 200, 50, 1)
        reg.set_slot(2, 1, 2, 3, 4, 5, FLAG_ACTIVE, 300, 50, 1)
        assert reg.total_prana() == 600


# =============================================================================
# APPLY DIW (The Reactor)
# =============================================================================


class TestApplyDiw:
    """DIW transforms lifecycle fields of active slots."""

    def test_diw_on_dead_slot_is_noop(self, reg):
        reg.apply_diw(0, 0x1234)
        sv = reg.get(0)
        assert sv.prana == 0  # Still dead

    def test_diw_changes_lifecycle(self, reg):
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, GENESIS_PRANA_U32, INTEGRITY_FULL, 0)
        before = reg.get(0)
        reg.apply_diw(0, 0x7FFFF)  # Max 19-bit DIW
        after = reg.get(0)
        # Header unchanged
        assert after.source == before.source
        assert after.target == before.target
        # Lifecycle changed (exact values depend on DIW decode)
        lifecycle_changed = (
            after.prana != before.prana or after.integrity != before.integrity or after.cycle != before.cycle
        )
        assert lifecycle_changed, "DIW should transform at least one lifecycle field"

    def test_diw_preserves_header(self, reg):
        reg.set_slot(0, 0xAAAA, 0xBBBB, 0xCCCC, 0xDDDD, 0xEEEE, FLAG_ACTIVE, GENESIS_PRANA_U32, INTEGRITY_FULL, 0)
        reg.apply_diw(0, 0x12345)
        sv = reg.get(0)
        assert sv.source == 0xAAAA
        assert sv.target == 0xBBBB
        assert sv.operation == 0xCCCC
        assert sv.arcanam == 0xDDDD
        assert sv.atma_nivedanam == 0xEEEE


# =============================================================================
# RAW MEMORY & SNAPSHOT
# =============================================================================


class TestRawMemory:
    """Direct memory access for snapshots and restore."""

    def test_raw_is_memoryview(self, reg):
        assert isinstance(reg.raw, memoryview)

    def test_raw_length(self, reg):
        assert len(reg.raw) == CHAMBER_BYTES

    def test_raw_reflects_writes(self, reg):
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100, 50, 1)
        raw_bytes = bytes(reg.raw[:SLOT_BYTES])
        # Unpack and verify
        values = struct.unpack_from(_SLOT_FMT, raw_bytes, 0)
        assert values[0] == 1  # source
        assert values[6] == 100  # prana

    def test_snapshot_and_restore(self, reg):
        # Write some state
        for i in range(5):
            reg.set_slot(i, i, i * 10, i * 100, 0, 0, FLAG_ACTIVE, (i + 1) * 100, 500, i)
        snapshot = bytes(reg.raw)

        # Clear and verify empty
        reg.clear()
        assert reg.active_count() == 0

        # Restore from snapshot
        reg._mem[:] = snapshot
        assert reg.active_count() == 5
        assert reg.get(0).prana == 100
        assert reg.get(4).prana == 500

    def test_ctypes_overlay_survives_clear(self, reg):
        """After clear(), the ctypes overlay still works (same buffer)."""
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100, 50, 1)
        reg.clear()
        reg.set_slot(0, 9, 8, 7, 6, 5, FLAG_ACTIVE, 200, 60, 2)
        sv = reg.get(0)
        assert sv.source == 9
        assert sv.prana == 200


# =============================================================================
# CTYPES ZERO-COPY CORRECTNESS
# =============================================================================


class TestCtypesOverlay:
    """Verify ctypes overlay is a true zero-copy view of _mem."""

    def test_slots_share_buffer(self, reg):
        """_slots and _mem point to the same memory."""
        reg._mem[0] = 0xFF
        assert reg._slots[0].source & 0xFF == 0xFF

    def test_struct_write_visible_via_ctypes(self, reg):
        offset = 10 * SLOT_BYTES
        struct.pack_into("<I", reg._mem, offset, 0xDEADBEEF)
        assert reg._slots[10].source == 0xDEADBEEF

    def test_ctypes_field_offsets(self):
        """Verify field offsets match the documented layout."""
        assert _CSlot.source.offset == 0
        assert _CSlot.target.offset == 4
        assert _CSlot.operation.offset == 8
        assert _CSlot.arcanam.offset == 12
        assert _CSlot.atma.offset == 16
        assert _CSlot.flags.offset == 20
        assert _CSlot.prana.offset == 24
        assert _CSlot.integrity.offset == 28
        assert _CSlot.cycle.offset == 30

    def test_collision_reads_via_ctypes(self, reg):
        """Collide reads resident prana via ctypes, not struct.unpack_from."""
        # Set up a resident via struct (set_slot)
        reg.set_slot(0, 1, 2, 3, 4, 5, FLAG_ACTIVE, 100, 1000, 1)
        # Verify ctypes sees it
        assert reg._slots[0].prana == 100
        # Collide (reads via ctypes internally)
        reg.collide(0, 9, 8, 7, 6, 5, 50, 2000, 2)
        # Verify result via ctypes
        assert reg._slots[0].prana == 150

    def test_all_512_slots_accessible(self, reg):
        """Every slot in the array is addressable."""
        for i in [0, 1, 255, 256, 511]:
            reg.set_slot(i, i, 0, 0, 0, 0, FLAG_ACTIVE, i + 1, 0, 0)
        for i in [0, 1, 255, 256, 511]:
            assert reg.prana_at(i) == i + 1
