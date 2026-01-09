"""
TEST: KALA VS NAMA (Entropy vs Grace)
=====================================

"Proof of Decay" - validating the thermodynamic laws of the Kernel.

Tests:
1. Kali Yuga Victory: Without Mantra, systems die.
2. Chaitanya Singularity: With Mantra, systems live.
"""

import time
import pytest
from vibe_core.protocols.science.entropy import (
    EntropyState, 
    KaliYugaEngine, 
    KalaProtocol
)

def test_kala_protocol_compliance():
    """Verify KaliYugaEngine implements KalaProtocol."""
    engine = KaliYugaEngine()
    assert isinstance(engine, KalaProtocol)

def test_kali_yuga_victory():
    """Beweist, dass ohne Mantra alles stirbt."""
    # High intensity for faster test execution
    engine = KaliYugaEngine(intensity=5.0) 
    
    start_time = time.time()
    obj_state = EntropyState(
        decay_rate=0.1, 
        integrity=1.0, 
        last_refresh=start_time
    )
    
    # Warte kurz (simulierte Zeit vergeht)
    time.sleep(0.5)
    
    # Check integrity BEFORE decay applied update
    # In reality, we just calculate it based on time delta
    integrity = engine.apply_decay(obj_state)
    
    # Expect significant decay
    # Delta ~0.5s * Intensity 5.0 * 0.1 = 0.25 decay
    # 1.0 - 0.25 = 0.75
    assert integrity < 0.95, "Objekt hätte verfallen müssen!"
    assert integrity > 0.0, "Objekt sollte noch nicht ganz tot sein"
    
    # Update state
    obj_state.integrity = integrity
    
    # Wait more
    time.sleep(0.5)
    integrity_2 = engine.apply_decay(obj_state)
    
    assert integrity_2 < integrity, "Entropie muss fortschreiten!"


def test_chaitanya_singularity():
    """Beweist, dass das Mantra die Entropie besiegt."""
    engine = KaliYugaEngine(intensity=5.0)
    obj_state = EntropyState(decay_rate=0.1, integrity=1.0, last_refresh=time.time())
    
    # Simulation des Mantra Loops (16 Schritte)
    for i in range(16): # 16 Worte (Hare Krishna...)
        time.sleep(0.05) # Kurze Zeit pro Wort
        
        # Bei 'Hare' (OpCode: Pulse aka Bit 8 approx) wird refreshed
        # Wir simulieren Injection bei Step 7
        if i == 7: 
            obj_state.last_refresh = time.time() # REFRESH!
            obj_state.integrity = 1.0 # GRACE!
            
    # Check decay after the loop
    # Time since last refresh (at step 7) to end (step 15) is small
    # (15-7) * 0.05 = 0.4s
    # Decay = 0.4 * 5.0 * 0.1 = 0.2
    # Integrity should be around 0.8
    
    integrity = engine.apply_decay(obj_state)
    
    # Ohne Mantra wäre es: 16 * 0.05 = 0.8s => 0.4 decay => 0.6 integrity
    # Mit Mantra Reset bei 50%: 0.2 decay => 0.8 integrity
    
    assert integrity > 0.7, "Mantra hat das Objekt nicht erhalten!"
    
    # Verify it's better than if we didn't refresh
    # Hypothetical calculation
    decay_without_grace = (0.8 * 5.0 * 0.1) # 0.4
    integrity_without_grace = 1.0 - decay_without_grace # 0.6
    
    assert integrity > integrity_without_grace, "Gnade muss besser sein als Karma!"
