import pytest
import time
from vibe_core.protocols.naga.prahlad import PrahladMemory
from vibe_core.protocols.substrate.byte import MantraByte, HolyName

def test_prahlad_immunity():
    """
    Proves that PrahladMemory protects data against Entropy (Hiranyakashipu).
    """
    memory = PrahladMemory()
    key = "bhakti_seed"
    value = "Premanjana"
    
    # 1. Create a Strong Mantra (Shield)
    shield = MantraByte.standard_16()
    
    # 2. Store Data (Smaranam)
    success = memory.remember(key, value, shield)
    assert success, "Prahlad should accept protected memory."
    
    # 3. Simulate Time Attack (Hiranyakashipu)
    # Intensity=10.0, Decay=0.1 -> 1.0 integrity loss per second approx?
    # Logic: decay = (delta * 10.0) * 0.1 = delta
    # So 1 second of time = 1.0 integrity loss.
    # Initial integrity = 1.08.
    # So it survives 1.08 seconds.
    
    # Small attack (0.5s) -> Should Survive
    memory.force_entropy_attack(key, 0.5)
    result = memory.recall(key, shield)
    assert result == value, "Memory should survive minor entropy attack."
    
    # 4. Massive Attack (2.0s) -> Should Die
    memory.force_entropy_attack(key, 2.0)
    result = memory.recall(key, shield)
    assert result is None, "Memory should perish under massive entropy without refresh."

def test_mayavad_rejection():
    """
    Proves that Weak Mantra fails to even store data.
    """
    memory = PrahladMemory()
    key = "illusion"
    value = "maya"
    
    # Weak Mantra (Chaos)
    # Using 'VOID' or just repeating one name to ruin coherence
    # Actually, let's use a very short mantra which might fail coherence check?
    # Coherence math: 1 - exp(-5 * ratio).
    # If we use a single RAMA, ratio against standard (HARE...) is 0 (RAMA != HARE).
    # Ratio 0 -> Coherence 0.
    weak_shield = MantraByte.from_string("RAMA") 
    
    success = memory.remember(key, value, weak_shield)
    assert not success, "Prahlad must reject weak mantra."
    
    # Double check recall
    assert memory.recall(key, weak_shield) is None

def test_smaranam_refresh():
    """
    Proves that constant Remembrance (Smaranam) keeps data alive forever.
    """
    memory = PrahladMemory()
    key = "eternal_service"
    value = "Seva"
    shield = MantraByte.standard_16()
    
    memory.remember(key, value, shield)
    
    # Attack -> Refresh -> Attack -> Refresh
    for _ in range(5):
        memory.force_entropy_attack(key, 0.8) # Drain 0.8 integrity (Leaves 0.28)
        assert memory.recall(key, shield) == value # Still alive
        memory.remember(key, value, shield) # Refresh back to 1.08
        
    print("\n🕉️  PRAHLAD PROOF: Smaranam conquers Time.")
