"""
TEST PERSISTENCE - Operation ChamberState
=========================================

Verifies serialization and deserialization of the entire Mahamantra stack.
"""

import pytest
from vibe_core.mahamantra.cell import MahaCellUnified
from vibe_core.mahamantra.orchestrator import VenuOrchestrator
from vibe_core.mahamantra.substrate.registry import SiksastakamRegistry
from vibe_core.mahamantra.chamber import SankirtanChamber

class TestCellPersistence:
    def test_cell_cycle(self):
        """Test cell to_bytes and from_bytes."""
        cell = MahaCellUnified.create(source=1, target=2, operation=3)
        # Conceive FIRST (resets state)
        cell.conceive("AGCT", "InitialPayload".encode("utf-8"))
        
        # Then modify state
        cell.lifecycle.prana = 12345
        cell.lifecycle.integrity = 0.5
        
        data = cell.to_bytes()
        assert len(data) >= 104
        
        restored, consumed = MahaCellUnified.from_bytes(data)
        
        assert restored.header.sravanam == 1
        assert restored.lifecycle.prana == 12345
        assert restored.lifecycle.integrity == 0.5
        assert restored.lifecycle.dna == "AGCT"
        assert restored.lifecycle.is_active is True
        assert consumed == len(data)

class TestRegistryPersistence:
    def test_registry_cycle(self):
        """Test registry to_bytes and from_bytes."""
        registry = SiksastakamRegistry()
        
        # Populate some cells
        c1 = MahaCellUnified.create(source=10, target=20, operation=30)
        c1.conceive("DNA1", b"")
        registry.set(100, c1)
        
        c2 = MahaCellUnified.create(source=11, target=21, operation=31)
        c2.conceive("DNA2", b"")
        registry.set(200, c2)
        
        # Serialize
        data = registry.to_bytes()
        
        # Restore into new registry
        new_registry = SiksastakamRegistry()
        new_registry.from_bytes(data)
        
        # Verify
        assert len(new_registry.active_cells()) == 2
        
        r1 = new_registry.get(100)
        assert r1.header.sravanam == 10
        assert r1.lifecycle.dna == "DNA1"
        
        r2 = new_registry.get(200)
        assert r2.header.sravanam == 11
        
        r_empty = new_registry.get(0)
        assert not r_empty.lifecycle.is_active # Should be Null

class TestOrchestratorPersistence:
    def test_orch_cycle(self):
        orch = VenuOrchestrator()
        orch.step()
        orch.step()
        # Tick should be 2
        assert orch.tick == 2
        
        data = orch.to_bytes()
        assert len(data) == 24
        
        new_orch = VenuOrchestrator()
        new_orch.from_bytes(data)
        assert new_orch.tick == 2
        assert new_orch._prev_state == orch._prev_state

class TestChamberPersistence:
    def test_snapshot_restore(self):
        chamber = SankirtanChamber.create()
        
        # Run some steps
        seed = MahaCellUnified.create(source=1, target=2, operation=3)
        chamber.dance(seed)
        chamber.dance(seed) # Resonance?
        
        assert chamber.total_transformations == 2
        
        # Snapshot
        snap = chamber.snapshot()
        assert snap.startswith(b"OM!!")
        
        # Restore to new chamber
        new_chamber = SankirtanChamber.create()
        new_chamber.restore(snap)
        
        assert new_chamber.total_transformations == 2
        assert new_chamber._accumulated_diw == chamber._accumulated_diw
        
        # Verify Registry State
        active = new_chamber._registry.active_cells()
        assert len(active) > 0
