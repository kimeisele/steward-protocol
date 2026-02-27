"""
SANKIRTAN CHAMBER — Snapshot/Restore Roundtrip Tests
=====================================================

Verifies the binary snapshot format: length-prefixed orchestrator,
TLV registry, fixed-size antaranga tail.

All constants derived from SSOT (_seed.py). No hardcoding.
"""

import struct

import pytest

from vibe_core.mahamantra.protocols._seed import KSHETRA, QUARTERS
from vibe_core.mahamantra.substrate.cell_system.antaranga import CHAMBER_BYTES
from vibe_core.mahamantra.substrate.cell_system.cell import MahaCellUnified
from vibe_core.mahamantra.substrate.cell_system.chamber import SankirtanChamber


@pytest.fixture
def chamber():
    return SankirtanChamber.create()


@pytest.fixture
def cell():
    return MahaCellUnified.create(source=42, target=7, operation=3, dna="test")


class TestSnapshotFormat:
    """Verify the binary layout of snapshot bytes."""

    def test_magic_header(self, chamber):
        snap = chamber.snapshot()
        assert snap[:4] == b"OM!!"

    def test_orchestrator_length_prefix(self, chamber):
        snap = chamber.snapshot()
        # After magic (4) + metrics (24) = offset 28
        orch_size = struct.unpack("<I", snap[28:32])[0]
        assert orch_size == KSHETRA  # 24 bytes (3 × Q)

    def test_antaranga_is_last_16384_bytes(self, chamber):
        snap = chamber.snapshot()
        assert len(snap) >= CHAMBER_BYTES
        # Last CHAMBER_BYTES must equal the raw antaranga
        assert snap[-CHAMBER_BYTES:] == bytes(chamber._antaranga.raw)

    def test_minimum_snapshot_size(self, chamber):
        snap = chamber.snapshot()
        # 4 (magic) + 24 (metrics) + 4 (orch_len) + 24 (orch) + 4 (registry count=0) + 16384 (antaranga)
        expected_min = 4 + 24 + 4 + KSHETRA + QUARTERS + CHAMBER_BYTES
        assert len(snap) == expected_min


class TestRoundtrip:
    """Verify snapshot → restore produces identical state."""

    def test_empty_chamber_roundtrip(self, chamber):
        snap = chamber.snapshot()

        restored = SankirtanChamber.create()
        restored.restore(snap)

        assert restored._accumulated_diw == chamber._accumulated_diw
        assert restored._resonance_count == chamber._resonance_count
        assert restored._total_transformations == chamber._total_transformations
        assert restored._orchestrator.tick == chamber._orchestrator.tick
        assert restored._orchestrator.mode == chamber._orchestrator.mode

    def test_roundtrip_after_dance(self, chamber, cell):
        # Transform a cell to produce state
        chamber.dance(cell)
        chamber.dance(cell)
        chamber.dance(cell)

        snap = chamber.snapshot()

        restored = SankirtanChamber.create()
        restored.restore(snap)

        assert restored._accumulated_diw == chamber._accumulated_diw
        assert restored._resonance_count == chamber._resonance_count
        assert restored._total_transformations == chamber._total_transformations
        assert restored._orchestrator.tick == chamber._orchestrator.tick
        assert restored._orchestrator.mode == chamber._orchestrator.mode

    def test_roundtrip_preserves_antaranga(self, chamber, cell):
        chamber.dance(cell)

        snap = chamber.snapshot()
        restored = SankirtanChamber.create()
        restored.restore(snap)

        assert bytes(restored._antaranga.raw) == bytes(chamber._antaranga.raw)

    def test_roundtrip_after_mode_change(self, chamber, cell):
        chamber._orchestrator.set_mode(2)  # CHORUS
        for _ in range(5):
            chamber.dance(cell)

        snap = chamber.snapshot()
        restored = SankirtanChamber.create()
        restored.restore(snap)

        assert restored._orchestrator.mode == 2

    def test_double_roundtrip(self, chamber, cell):
        """snapshot → restore → snapshot must produce identical bytes."""
        chamber.dance(cell)

        snap1 = chamber.snapshot()
        restored = SankirtanChamber.create()
        restored.restore(snap1)
        snap2 = restored.snapshot()

        assert snap1 == snap2


class TestRestoreErrors:
    """Verify restore rejects invalid data."""

    def test_too_short(self, chamber):
        with pytest.raises(ValueError, match="too short"):
            chamber.restore(b"\x00" * 10)

    def test_bad_magic(self, chamber):
        bad = b"NOPE" + b"\x00" * 100
        with pytest.raises(ValueError, match="Invalid magic"):
            chamber.restore(bad)

    def test_truncated_orchestrator(self, chamber):
        # Valid header but orchestrator claims more bytes than available
        buf = bytearray()
        buf.extend(b"OM!!")
        buf.extend(struct.pack("<QQQ", 0, 0, 0))  # metrics
        buf.extend(struct.pack("<I", 9999))  # orch_size = absurd
        buf.extend(b"\x00" * 24)  # not enough
        with pytest.raises(ValueError, match="truncated"):
            chamber.restore(bytes(buf))
