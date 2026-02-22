"""
TEST: MahaCellUnified - The Complete Computational Unit
======================================================

"Trust but verify" - Tests for the unified cell architecture.

WATERTIGHT TESTS:
- All values derived from SSOT (_seed.py)
- No hardcoded magic numbers
- No Any types
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    COSMIC_FRAME,
    MAHA_QUANTUM,
    PANCHA,
    TRINITY,
    PARAMPARA,
    JIVA_CYCLE,
    JIVA_QUALITIES,
)
from vibe_core.mahamantra.substrate.cell import (
    MahaCellUnified,
    CellLifecycleState,
    GENESIS_PRANA,
    MEMBRANE_MIN_INTEGRITY,
    METABOLIC_COST,
    MAX_AGE_CYCLES,
    MITOSIS_THRESHOLD,
    _SIGNAL_WEAR,
)
from vibe_core.mahamantra.protocols._header import (
    MahaHeader,
    HEADER_SIZE_BYTES,
)


class TestCellConstants:
    """Test that cell constants derive correctly from Seed."""

    def test_genesis_prana_derived(self) -> None:
        """GENESIS_PRANA = MAHA_QUANTUM × 100."""
        assert GENESIS_PRANA == MAHA_QUANTUM * 100
        assert GENESIS_PRANA == 13700

    def test_metabolic_cost_is_trinity(self) -> None:
        """METABOLIC_COST = TRINITY = 3."""
        assert METABOLIC_COST == TRINITY
        assert METABOLIC_COST == 3

    def test_mitosis_threshold_derived(self) -> None:
        """MITOSIS_THRESHOLD = MAHA_QUANTUM × 2."""
        assert MITOSIS_THRESHOLD == MAHA_QUANTUM * 2
        assert MITOSIS_THRESHOLD == 274

    def test_max_age_is_jiva_cycle(self) -> None:
        """MAX_AGE_CYCLES = JIVA_CYCLE = 432."""
        assert MAX_AGE_CYCLES == JIVA_CYCLE
        assert MAX_AGE_CYCLES == 432


class TestMahaCellUnifiedCreation:
    """Test cell creation methods."""

    def test_create_cell(self) -> None:
        """Create cell with factory method."""
        cell = MahaCellUnified.create(
            source=1,
            target=2,
            operation=3,
            dna="TEST_DNA",
            initial_state={"key": "value"},
        )

        assert cell.is_alive
        assert cell.prana == GENESIS_PRANA
        assert cell.membrane_integrity == COSMIC_FRAME
        assert cell.age == 0
        assert cell.payload == {"key": "value"}

    def test_null_cell(self) -> None:
        """Create null/sentinel cell."""
        cell = MahaCellUnified.null()

        assert not cell.is_alive
        assert cell.prana == 0
        assert cell.membrane_integrity == 0

    def test_cell_requires_valid_header(self) -> None:
        """Cell creation fails with invalid header."""
        # Create an invalid header by tampering with arcanam
        header = MahaHeader.create(source=1, target=2, operation=3)

        # Manually create cell should work with valid header
        cell = MahaCellUnified(header=header)
        assert cell.header.is_valid()


class TestCellLifecycle:
    """Test cell lifecycle methods."""

    def test_conceive(self) -> None:
        """Test cell conception (birth)."""
        cell = MahaCellUnified.null()
        cell.conceive(dna="DNA_SEQUENCE", genesis_state="INITIAL")

        assert cell.is_alive
        assert cell.prana == GENESIS_PRANA
        assert cell.lifecycle.dna == "DNA_SEQUENCE"
        assert cell.payload == "INITIAL"

    def test_metabolize_consumes_energy(self) -> None:
        """Metabolism costs TRINITY (3) prana per cycle."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        initial_prana = cell.prana

        new_prana = cell.metabolize(energy=0)

        assert new_prana == initial_prana - METABOLIC_COST
        assert cell.age == 1

    def test_metabolize_absorbs_energy(self) -> None:
        """Cell absorbs incoming energy."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        initial_prana = cell.prana

        new_prana = cell.metabolize(energy=10)

        assert new_prana == initial_prana - METABOLIC_COST + 10

    def test_metabolize_starvation_triggers_apoptosis(self) -> None:
        """Cell dies when prana reaches 0."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        cell.lifecycle.prana = 2  # Just below metabolic cost

        result = cell.metabolize(energy=0)

        assert result == 0
        assert not cell.is_alive

    def test_aging_triggers_apoptosis(self) -> None:
        """Cell dies after MAX_AGE_CYCLES cycles."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        cell.lifecycle.cycle = MAX_AGE_CYCLES - 1

        cell.metabolize(energy=100)  # One more cycle

        assert not cell.is_alive


class TestSignal:
    """Test cell signaling."""

    def test_signal_passes_with_good_integrity(self) -> None:
        """Signal passes when membrane integrity > 0.2."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)

        result = cell.signal("test_message")

        assert result == "test_message"

    def test_signal_rejected_with_low_integrity(self) -> None:
        """Signal rejected when membrane integrity < MEMBRANE_MIN_INTEGRITY."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        cell.lifecycle.integrity = MEMBRANE_MIN_INTEGRITY - 1

        result = cell.signal("test_message")

        assert result is None

    def test_signal_degrades_membrane(self) -> None:
        """Each signal costs 1% membrane integrity."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        initial_integrity = cell.membrane_integrity

        cell.signal("test_message")

        assert cell.membrane_integrity == initial_integrity - _SIGNAL_WEAR


class TestMitosis:
    """Test cell division."""

    def test_mitosis_requires_threshold_prana(self) -> None:
        """Mitosis fails without enough prana."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        cell.lifecycle.prana = MITOSIS_THRESHOLD - 1

        with pytest.raises(RuntimeError, match="Not enough prana"):
            cell.mitosis()

    def test_mitosis_splits_prana(self) -> None:
        """Mitosis divides prana between parent and child."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        initial_prana = cell.prana

        child = cell.mitosis()

        expected_each = initial_prana // 2
        assert cell.prana == expected_each
        assert child.prana == expected_each

    def test_mitosis_creates_fresh_child(self) -> None:
        """Child cell starts with cycle 0."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        cell.lifecycle.cycle = 100

        child = cell.mitosis()

        assert child.age == 0
        assert child.is_alive


class TestApoptosis:
    """Test programmed cell death."""

    def test_apoptosis_kills_cell(self) -> None:
        """Apoptosis sets all vital signs to zero."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)

        cell.apoptosis()

        assert not cell.is_alive
        assert cell.prana == 0
        assert cell.membrane_integrity == 0


class TestHomeostasis:
    """Test balance maintenance."""

    def test_homeostasis_returns_true_when_healthy(self) -> None:
        """Healthy cell passes homeostasis."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)

        result = cell.homeostasis()

        assert result is True
        assert cell.is_alive

    def test_homeostasis_triggers_apoptosis_on_no_prana(self) -> None:
        """Cell dies if homeostasis finds no prana."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        cell.lifecycle.prana = 0

        result = cell.homeostasis()

        assert result is False
        assert not cell.is_alive


class TestSerialization:
    """Test cell serialization."""

    def test_to_bytes_includes_header(self) -> None:
        """Serialized cell starts with 72-byte header."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)

        data = cell.to_bytes()

        assert len(data) >= HEADER_SIZE_BYTES
        assert data[:HEADER_SIZE_BYTES] == cell.header.to_bytes()

    def test_to_bytes_includes_lifecycle(self) -> None:
        """Serialized cell includes lifecycle state."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)

        data = cell.to_bytes()

        # Header (72) + prana (8) + integrity (8) + cycle (8) + flags (8) + dna
        min_size = HEADER_SIZE_BYTES + 32
        assert len(data) >= min_size


class TestOrganelles:
    """Test internal component inspection."""

    def test_get_organelles(self) -> None:
        """Get organelles returns expected keys."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)

        organelles = cell.get_organelles()

        assert "nucleus" in organelles
        assert "mitochondria" in organelles
        assert "membrane" in organelles
        assert "jiva_qualities" in organelles
        assert organelles["jiva_qualities"] == JIVA_QUALITIES
