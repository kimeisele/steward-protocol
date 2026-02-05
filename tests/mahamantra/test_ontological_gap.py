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
    
    # 1. Check for Expansion Identity
    try:
        # This SHOULD fail in current architecture
        assert hasattr(Quarter.GENESIS, "expansion"), "Quarter lacks 'expansion' attribute"
        expansion = Quarter.GENESIS.expansion
        
        # If attribute exists, is it correct?
        # Note: We don't even have the Enum for Vasudeva yet
        assert expansion == "VASUDEVA", f"Expected Vasudeva, got {expansion}"
        
    except AttributeError as e:
        pytest.fail(f"ONTOLOGICAL GAP CONFIRMED: Quarter system is hollow. Missing Chatur-vyuha linkage. Error: {e}")

def test_subtle_element_mapping():
    """
    Verify that Quarters govern their subtle element (Tattva).
    
    Theology:
        Genesis -> Citta (Consciousness)
    """
    try:
        # This SHOULD fail
        assert hasattr(Quarter.GENESIS, "tattva"), "Quarter lacks 'tattva' attribute"
        tattva = Quarter.GENESIS.tattva
        assert tattva == "CITTA", f"Expected CITTA, got {tattva}"
        
    except AttributeError as e:
        pytest.fail(f"ONTOLOGICAL GAP CONFIRMED: No Subtle Element (Tattva) mapping in Quarter. Error: {e}")
