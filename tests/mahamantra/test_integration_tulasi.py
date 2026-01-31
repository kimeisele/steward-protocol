"""
INTEGRATION TEST: TULASI GATE (Production)
==========================================

"ye yathā māṁ prapadyante..." (BG 4.11)

Verifies the production integration of TulasiGate into MahaModularSynth.
"""

import pytest
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
from vibe_core.mahamantra.adapters.tulasi_gate import TulasiGate
from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, HARE_COUNT

def test_production_integration():
    """
    Verify that the Synth happily accepts the Tulasi Gate
    and changes behavior based on the HasTulasi flag.
    """
    
    # 1. Setup with Gate
    gate = TulasiGate()
    synth = MahaModularSynth(default_preset="quantum", grace_gate=gate)
    
    # 2. Test Loop WITHOUT Tulasi (Should be Standard)
    # Using seed 137 which maps to 0 if mod 137
    # Note: purify_offering is NOT called if has_tulasi=False
    # So 137 % 137 = 0
    res_standard = synth.transform(seed=MAHA_QUANTUM, has_tulasi=False)
    
    # 3. Test Loop WITH Tulasi (Should be Expanded)
    # Seed 137 becomes: (137*8) + 108 = 1204
    # Mod Space becomes: 137 * 8 = 1096
    # 1204 % 1096 = 108
    # So the INITIAL value into the loop is 108.
    # The loop then runs.
    
    res_tulasi = synth.transform(seed=MAHA_QUANTUM, has_tulasi=True)
    
    print(f"\n[INTEGRATION] Standard Result (seed=137): {res_standard}")
    print(f"[INTEGRATION] Tulasi Result (seed=137): {res_tulasi}")
    
    # Assert they are DIFFERENT (Grace changes the outcome)
    assert res_standard != res_tulasi, "Tulasi had no effect!"
    
    # Assert Calculation Logic match
    # Since res_tulasi is likely > 137 (depending on loop), let's check input
    # If the synth loop creates large values, they should now be bounded by 1096, not 137
    
    # Let's try to verify if we can EXCEED 137 in the output
    # This requires a seed that produces a large value
    
    # Try a large seed
    large_seed = 10000
    res_large = synth.transform(seed=large_seed, has_tulasi=True)
    print(f"[INTEGRATION] Large Seed Result: {res_large}")
    
    # It is possible res_large < 137 just by modulo chance, 
    # but let's run a loop to find ONE value > 137
    
    found_expanded_value = False
    for i in range(100):
        val = synth.transform(seed=i, has_tulasi=True)
        if val > MAHA_QUANTUM:
            found_expanded_value = True
            print(f"[PROOF] Found value {val} > {MAHA_QUANTUM}")
            break
            
    assert found_expanded_value, "Even with Tulasi, we never exceeded 137! Mod expansion failed?"
    
    print("[CONCLUSION] Tulasi Gate is operational. Field is expanded.")

if __name__ == "__main__":
    test_production_integration()
