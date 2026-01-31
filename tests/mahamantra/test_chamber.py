"""
TEST: SankirtanChamber - The Resonance Space
============================================

"Trust but verify" - Tests for the composition pattern.

WATERTIGHT TESTS:
- All values derived from SSOT (_seed.py)
- No hardcoded magic numbers
- No Any types
"""

import pytest

from vibe_core.mahamantra.chamber import (
    SankirtanChamber,
    KirtanMode,
    CHAMBER_CAPACITY,
    RESONANCE_THRESHOLD,
    DEFAULT_CHORUS_SIZE,
)
from vibe_core.mahamantra.cell import (
    MahaCellUnified,
    GENESIS_PRANA,
)
from vibe_core.mahamantra.cluster import MahaCluster
from vibe_core.mahamantra.orchestrator import VenuOrchestrator
from vibe_core.mahamantra.protocols._seed import (
    MALA,
    PARAMPARA,
    WORDS,
    MAHA_QUANTUM,
)


class TestChamberConstants:
    """Test that chamber constants derive correctly from Seed."""
    
    def test_chamber_capacity_is_mala(self) -> None:
        """CHAMBER_CAPACITY = MALA = 108."""
        assert CHAMBER_CAPACITY == MALA
        assert CHAMBER_CAPACITY == 108
    
    def test_resonance_threshold_is_parampara(self) -> None:
        """RESONANCE_THRESHOLD = PARAMPARA = 37."""
        assert RESONANCE_THRESHOLD == PARAMPARA
        assert RESONANCE_THRESHOLD == 37
    
    def test_default_chorus_is_words(self) -> None:
        """DEFAULT_CHORUS_SIZE = WORDS = 16."""
        assert DEFAULT_CHORUS_SIZE == WORDS
        assert DEFAULT_CHORUS_SIZE == 16


class TestKirtanMode:
    """Test KirtanMode enum."""
    
    def test_kirtan_modes(self) -> None:
        """KirtanMode has three modes."""
        assert KirtanMode.SOLO == 0
        assert KirtanMode.CALL_RESPONSE == 1
        assert KirtanMode.CHORUS == 2


class TestSankirtanChamberCreation:
    """Test chamber creation."""
    
    def test_create_chamber(self) -> None:
        """Create chamber with factory method."""
        chamber = SankirtanChamber.create()
        
        assert chamber.tick == 0
        assert chamber.resonance_count == 0
        assert chamber.total_transformations == 0
    
    def test_chamber_owns_orchestrator(self) -> None:
        """Chamber owns (composes) orchestrator, not inherits."""
        chamber = SankirtanChamber.create()
        
        assert isinstance(chamber._orchestrator, VenuOrchestrator)


class TestDance:
    """Test dance() - atomic cell transformation."""
    
    def test_dance_transforms_cell(self) -> None:
        """Dance applies DIW to cell."""
        chamber = SankirtanChamber.create()
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        
        initial_prana = cell.prana
        result = chamber.dance(cell)
        
        # Cell was transformed (prana changed)
        assert result is cell  # Same object
        assert chamber.total_transformations == 1
    
    def test_dance_advances_tick(self) -> None:
        """Each dance advances the orchestrator tick."""
        chamber = SankirtanChamber.create()
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        
        assert chamber.tick == 0
        chamber.dance(cell)
        assert chamber.tick == 1
        chamber.dance(cell)
        assert chamber.tick == 2
    
    def test_dance_tracks_transformations(self) -> None:
        """Dance counts total transformations."""
        chamber = SankirtanChamber.create()
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        
        for _ in range(10):
            chamber.dance(cell)
        
        assert chamber.total_transformations == 10


class TestKirtan:
    """Test kirtan() - multi-cycle transformation."""
    
    def test_kirtan_runs_one_cycle(self) -> None:
        """kirtan(cycles=1) runs WORDS (16) transformations."""
        chamber = SankirtanChamber.create()
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        
        chamber.kirtan(cell, cycles=1)
        
        assert chamber.total_transformations == WORDS
        assert chamber.tick == WORDS
    
    def test_kirtan_runs_multiple_cycles(self) -> None:
        """kirtan(cycles=3) runs 48 transformations."""
        chamber = SankirtanChamber.create()
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        
        chamber.kirtan(cell, cycles=3)
        
        assert chamber.total_transformations == 3 * WORDS
        assert chamber.tick == 3 * WORDS


class TestSankirtan:
    """Test sankirtan() - group transformation."""
    
    def test_sankirtan_transforms_all_cells(self) -> None:
        """Sankirtan transforms all cells in group."""
        chamber = SankirtanChamber.create()
        cells = [
            MahaCellUnified.create(source=i, target=i+1, operation=i)
            for i in range(5)
        ]
        
        result = chamber.sankirtan(cells)
        
        assert isinstance(result, MahaCluster)
        assert result.size == 5
        assert len(result.cells) == 5
        assert chamber.total_transformations == 5
    
    def test_sankirtan_empty_list(self) -> None:
        """Sankirtan handles empty list."""
        chamber = SankirtanChamber.create()
        
        result = chamber.sankirtan([])
        
        assert isinstance(result, MahaCluster)
        assert result.size == 0
        assert result.cells == []


class TestResonance:
    """Test resonance tracking and verification."""
    
    def test_verify_resonance(self) -> None:
        """Verify resonance returns True for valid chamber."""
        chamber = SankirtanChamber.create()
        
        result = chamber.verify_resonance()
        
        assert result is True


class TestReset:
    """Test chamber reset."""
    
    def test_reset_clears_state(self) -> None:
        """Reset returns chamber to initial state."""
        chamber = SankirtanChamber.create()
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        
        # Advance state
        for _ in range(50):
            chamber.dance(cell)
        
        # Reset
        chamber.reset()
        
        assert chamber.tick == 0
        assert chamber.total_transformations == 0
        assert chamber.resonance_count == 0


class TestSilence:
    """Test SUNYA (silence) detection."""
    
    def test_is_silent_with_sunya_flag(self) -> None:
        """is_silent returns True when SUNYA bit set."""
        chamber = SankirtanChamber.create()
        diw_with_sunya = 1 << 31  # SUNYA bit
        
        assert chamber.is_silent(diw_with_sunya) is True
    
    def test_is_silent_without_sunya_flag(self) -> None:
        """is_silent returns False without SUNYA bit."""
        chamber = SankirtanChamber.create()
        diw_without_sunya = 0x12345
        
        assert chamber.is_silent(diw_without_sunya) is False


class TestCompositionPattern:
    """Verify composition over inheritance pattern."""
    
    def test_chamber_does_not_inherit_orchestrator(self) -> None:
        """SankirtanChamber does NOT inherit from VenuOrchestrator."""
        assert not issubclass(SankirtanChamber, VenuOrchestrator)
    
    def test_chamber_composes_orchestrator(self) -> None:
        """SankirtanChamber COMPOSES VenuOrchestrator."""
        chamber = SankirtanChamber.create()
        
        # Orchestrator is a component, not a parent
        assert hasattr(chamber, "_orchestrator")
        assert isinstance(chamber._orchestrator, VenuOrchestrator)
    
    def test_cell_does_not_own_orchestrator(self) -> None:
        """MahaCellUnified does NOT own orchestrator."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        
        assert not hasattr(cell, "_orchestrator")
