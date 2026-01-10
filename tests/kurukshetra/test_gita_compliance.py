"""
TEST GITA COMPLIANCE - The Red & Green Suite (Hardened)
"""
import pytest
from typing import Dict, Any, List
from vibe_core.protocols.naga.base import NagaBase
from vibe_core.protocols.universal.gita import GitaProtocol
from vibe_core.protocols.universal.types import (
    SovereignContext, DivineCommand, SankhyaDualism, 
    KarmaCounter, VisvarupaSnapshot, TranscendentalQuality
)

class MockService(NagaBase):
    """A standard Naga (Snake). Fails because it ignores the Sovereign."""
    def serve(self, req): pass

class ArjunaCore:
    """
    A Divine Implementation.
    Follows Phase 25 (Strict Outputs) and Phase 26 (Sovereign Inputs).
    """
    @property
    def gita_library_hash(self) -> str: return "1972"

    def chapter_01_visada_yoga(self, sovereign: SovereignContext) -> str:
        return "I see omens."

    def chapter_02_sankhya_yoga(self, sovereign: SovereignContext) -> SankhyaDualism:
        return SankhyaDualism("PURUSHA_1", "ACTIVE", {"sattva": 1.0})

    def chapter_03_karma_yoga(self, sovereign: SovereignContext) -> KarmaCounter:
        return KarmaCounter(108, 0.0, 100.0, "Akarma")
        
    def chapter_04_jnana_yoga(self, sovereign: SovereignContext) -> str:
        return "Parampara-001"

    def chapter_11_visvarupa_yoga(self, sovereign: SovereignContext) -> VisvarupaSnapshot:
        return VisvarupaSnapshot("ROOT", TranscendentalQuality.EXISTENCE, {}, [])

    def chapter_18_moksha_sannyasa_yoga(self, cmd: DivineCommand) -> bool:
        return cmd.sovereign.identity_id == "KRISHNA"

def test_naga_is_NOT_divine():
    snake = MockService("Takshaka", ("bite",))
    assert not isinstance(snake, GitaProtocol)

def test_arjuna_IS_divine():
    arjuna = ArjunaCore()
    # This checks runtime Protocol compliance
    assert isinstance(arjuna, GitaProtocol)

def test_sankhya_properties():
    """Verify strict type properties on return value."""
    arjuna = ArjunaCore()
    # Mock sovereign
    sov = SovereignContext("Arjuna", "Sig", 0.0)
    
    sankhya = arjuna.chapter_02_sankhya_yoga(sov)
    assert sankhya.purusha_id == "PURUSHA_1"
    assert sankhya.guna_balance["sattva"] == 1.0
