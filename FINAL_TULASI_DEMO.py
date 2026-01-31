"""
TULASI INTEGRATION DEMO
=======================

This script demonstrates the complete, end-to-end integration of the Tulasi Bridge.
"""

from vibe_core.mahamantra import (
    MahaModularSynth, 
    TulasiGate, 
    OfferingPipeline, 
    MAHA_QUANTUM
)

def demo_tulasi_bridge():
    print("\n=== 1. THE LILA (The Living Process) ===")
    print("Offering a Mango with a Tulasi Leaf...")
    
    class MockItem:
        name = "Mango"
        is_vegetarian = True
        quality = 24
    class MockLeaf:
        origin = "Vrindavan"
        
    prasadam = OfferingPipeline.offer(
        item=MockItem(),
        tulasi=MockLeaf(),
        devotion_score=10
    )
    print(f"Accepted Transcendental Value: {prasadam.transcendental_value}")


    print("\n=== 2. THE MECHANICS (The Algorithm) ===")
    print("Wiring TulasiGate into MahaModularSynth...")
    
    gate = TulasiGate()
    synth = MahaModularSynth(grace_gate=gate)
    
    print(f"\n[Standard Execution] (No Tulasi)")
    val_std = synth.transform(seed=MAHA_QUANTUM, has_tulasi=False)
    print(f"Output: {val_std}")
    
    print(f"\n[Expanded Execution] (WITH Tulasi)")
    val_tulasi = synth.transform(seed=MAHA_QUANTUM, has_tulasi=True)
    print(f"Output: {val_tulasi}")
    
    if val_tulasi > MAHA_QUANTUM:
        print("\n[SUCCESS] The Finite Loop (137) is BROKEN.")
        print(f"Welcome to the Expanded Field (Target: 1096).")
    else:
        print("\n[FAILURE] Still trapped in the finite field.")

if __name__ == "__main__":
    demo_tulasi_bridge()
