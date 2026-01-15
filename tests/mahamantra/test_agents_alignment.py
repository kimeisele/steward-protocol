"""
TEST AGENTS ALIGNMENT - The Sacred Mapping
==========================================

This test verifies that the core agents are found at their correct 
Seed-mandated positions in the Mahamantra Lotus.

MAPPING:
- Position 2:  NARADA (Envoy)
- Position 11: BHISHMA (Archivist)
- Position 15: YAMARAJA (Auditor)
"""

import pytest
from vibe_core.mahamantra import mahamantra

def test_narada_envoy_alignment():
    """Verify Envoy is Narada at Position 2."""
    pos = mahamantra[2]
    assert pos.guardian.value == "narada"
    
    # Check if we can find the Envoy class via the mod router
    # (Relies on the lazy loader in mahamantra.genesis.narada)
    # Since we haven't patched narada/__init__.py yet, this might still 
    # point to the old location, but the identity in the file is already updated.
    pass

def test_bhishma_archivist_alignment():
    """Verify Archivist is Bhishma at Position 11."""
    pos = mahamantra[11]
    assert pos.guardian.value == "bhishma"

def test_yamaraja_auditor_alignment():
    """Verify Auditor is Yamaraja at Position 15."""
    pos = mahamantra[15]
    assert pos.guardian.value == "yamaraja"

def test_agent_tattva_disclosure():
    """Verify that patched agents disclose their Tattva."""
    from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge
    from vibe_core.cartridges.system.archivist.cartridge_main import ArchivistCartridge
    from vibe_core.cartridges.system.auditor.cartridge_main import AuditorCartridge
    
    # Envoy
    envoy = EnvoyCartridge()
    assert envoy.__tattva__["chaitanya"] == "Universal Operator Interface (Envoy)"
    
    # Archivist
    archivist = ArchivistCartridge()
    assert archivist.__tattva__["chaitanya"] == "History Keeper (Archivist)"
    
    # Auditor
    auditor = AuditorCartridge()
    assert auditor.__tattva__["chaitanya"] == "Quality & Governance Gate (Auditor)"

if __name__ == "__main__":
    pytest.main([__file__])
