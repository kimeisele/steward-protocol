# import pytest (Removed to allow standalone execution)
from vibe_core.mahamantra.namarupa.akshara import SyllableEngine, Akshara
from vibe_core.mahamantra.namarupa.atom import AtomicResonanceHash, IdentityRegistry
from vibe_core.reactor.matrix import Varga, Sthana
import sys

def test_syllable_splitting_physics():
    """Test FSM splitting based on Energy physics."""
    print("Testing Syllable Splitting...")
    engine = SyllableEngine()
    
    # "Govinda" -> Go - vi - nda (Strict Akshara / Maximum Onset)
    syllables = engine.analyze("Govinda")
    assert len(syllables) == 3, f"Govinda split fail: {syllables}"
    assert str(syllables[0]) == "Go"
    assert str(syllables[1]) == "vi"  # Was "vin"
    assert str(syllables[2]) == "nda" # Was "da"
    
    # "Hari" -> Ha - ri (Check 'h' as onset, 'a' as nucleus)
    s_hari = engine.analyze("Hari")
    assert len(s_hari) == 2, f"Hari split fail: {s_hari}"
    assert str(s_hari[0]) == "Ha"
    assert str(s_hari[1]) == "ri"
    
    # "Krishna" -> Kri - shna 
    # (K-r onset cluster)
    s_krishna = engine.analyze("Krishna")
    assert len(s_krishna) == 2, f"Krishna split fail: {s_krishna}"
    assert str(s_krishna[0]) == "Kri"
    assert str(s_krishna[1]) == "shna"
    print("PASS: Syllable Splitting")

def test_collision_fix_ga_vs_a():
    """Test 6-bit Resonance Hash solves Ga/A collision."""
    print("Testing Collision Fix (Ga vs A)...")
    hash_ga = AtomicResonanceHash.compute("Ga")
    hash_a = AtomicResonanceHash.compute("A")
    
    # They MUST be different
    assert hash_ga != hash_a, f"COLLISION DETECTED: Ga({hash_ga}) == A({hash_a})"
    print(f"PASS: Ga ({hash_ga}) != A ({hash_a})")
    
    # Verify bits manually?
    # Ga: KANTHYA(0) + GHOSHAVAT(2) + NotSvara = 000 10 = 2 -> Shifted
    # A:  KANTHYA(0) + GHOSHAVAT(2) + IsSvara  = 100 010 = 34 -> Shifted

def test_holographic_search_256bit():
    """Test Prefix Search in 256-bit space."""
    print("Testing 256-bit Holographic Search...")
    registry = IdentityRegistry()
    registry.register("Govindam", "Full Name")
    registry.register("Govinda", "Short Name")
    registry.register("Gopal", "Cowherd")
    
    # Search for "Govi" (Phonetically valid prefix)
    # Govinda: Go - vi - nda
    # Govindam: Go - vi - ndam
    # Govi: Go - vi
    # Should match botH
    results = registry.search("Govi")
    assert "Full Name" in results, "Govindam not found (Collision/Overwrite?)"
    assert "Short Name" in results, "Govinda not found"
    assert "Cowherd" not in results, "Gopal falsely matched" # Go-pal differs at syllable 2
    
    # Search for "Go" (Should find all)
    res_go = registry.search("Go")
    assert len(res_go) >= 3, f"Expected >=3 results for 'Go', got {len(res_go)}"
    print("PASS: Holographic Search")

def test_capacity_overflow():
    """Ensure extremely long names don't crash."""
    print("Testing Capacity/Overflow...")
    long_name = "SriKrishnaChaitanyaPrabhuNityanandaSriAdvaitaGadadharaSrivasadiGauraBhaktaVrinda"
    key = AtomicResonanceHash.compute(long_name)
    assert isinstance(key, int)
    assert key > 0
    print("PASS: Capacity OK")

if __name__ == "__main__":
    try:
        test_syllable_splitting_physics()
        test_collision_fix_ga_vs_a()
        test_holographic_search_256bit()
        test_capacity_overflow()
        print("\nALL SYSTEMS GO: ATOMIC NAMARUPA VERIFIED.")
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
