"""
TEST ONTOLOGICAL GAP - The Chatur-vyuha Verification
=====================================================

"Proving what is missing through rigorous failure."

HYPOTHESIS:
    The current architecture maps Quarters (Genesis, Dharma, Karma, Moksha)
    only to functional phases, ignoring the psychophysical substrate
    (Chatur-vyuha: Vasudeva, Sankarsana, Pradyumna, Aniruddha).

THE RED TEST:
    This test attempts to access the 'psychic substrate' of a Quarter.
    It EXPECTS TO FAIL (AttributeError).
    
    If it runs, the architecture is complete.
    If it fails, the ontoligical gap is proven.
"""
import pytest
from vibe_core.mahamantra.substrate.mahajana import Quarter

@pytest.mark.xfail(reason="Ontological gap: Quarter lacks Chatur-vyuha expansion (not yet implemented)")
def test_chatur_vyuha_connection():
    """
    Verify that Quarters are connected to their Chatur-vyuha expansion.
    
    Theology (Hypothesis):
        Genesis -> Vasudeva (Citta/Consciousness)
        Dharma  -> Sankarsana (Ahankara/Ego)
        Karma   -> Pradyumna (Buddhi/Intelligence)
        Moksha  -> Aniruddha (Manas/Mind)
        
    Engineering Reality:
        Does Quarter.GENESIS know it is Vasudeva?
    """
    assert hasattr(Quarter.GENESIS, "expansion"), "Quarter lacks 'expansion' attribute"
    assert Quarter.GENESIS.expansion == "VASUDEVA", "Expected Vasudeva"

@pytest.mark.xfail(reason="Ontological gap: Quarter lacks Tattva mapping (not yet implemented)")
def test_subtle_element_mapping():
    """
    Verify that Quarters govern their subtle element (Tattva).
    
    Theology:
        Genesis -> Citta (Consciousness)
    """
    assert hasattr(Quarter.GENESIS, "tattva"), "Quarter lacks 'tattva' attribute"
    assert Quarter.GENESIS.tattva == "CITTA", "Expected CITTA"
