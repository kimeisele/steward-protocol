import pytest
import time
from typing import Set
from vibe_core.protocols.naga.prahlad import PrahladMemory
from vibe_core.protocols.substrate.byte import MantraByte, HolyName
from vibe_core.protocols.types import PersonProtocol, Capability
from tests.common.avatars import TestDevotee, TestService

# --- TESTS ---

def test_prahlad_immunity():
    """
    Proves that PrahladMemory protects data against Entropy (Hiranyakashipu).
    """
    memory = PrahladMemory()
    key = "bhakti_seed"
    value = "Premanjana"
    devotee = TestDevotee(name="Prahlad")
    
    # 1. Create a Strong Mantra (Shield)
    shield = MantraByte.standard_16()
    
    # 2. Store Data (Smaranam)
    success = memory.remember(devotee, key, value, shield)
    assert success, "Prahlad should accept protected memory."
    
    # 3. Simulate Time Attack
    # Small attack (0.5s) -> Should Survive
    memory.force_entropy_attack(key, 0.5)
    result = memory.recall(devotee, key, shield)
    assert result == value, "Memory should survive minor entropy attack."
    
    # 4. Massive Attack (2.0s) -> Should Die
    memory.force_entropy_attack(key, 2.0)
    result = memory.recall(devotee, key, shield)
    assert result is None, "Memory should perish under massive entropy without refresh."

def test_identity_enforcement():
    """
    Proves that only a Person can perform Smaranam.
    """
    memory = PrahladMemory()
    # TestService does NOT implement PersonProtocol (it is a Thing/Service)
    demon_service = TestService()
    shield = MantraByte.standard_16()
    
    # Demon (Service) trying to Remember -> TypeError
    with pytest.raises(TypeError) as excinfo:
        memory.remember(demon_service, "evil_plan", "destroy", shield) # type: ignore
    assert "Only a Person" in str(excinfo.value)
    
    # Demon (Service) trying to Recall -> Returns None (Silent Rejection)
    # First plant data with valid devotee
    devotee = TestDevotee(name="Prahlad")
    memory.remember(devotee, "divine_plan", "save", shield)
    
    result = memory.recall(demon_service, "divine_plan", shield) # type: ignore
    assert result is None

def test_mayavad_rejection():
    """
    Proves that Weak Mantra fails to even store data.
    """
    memory = PrahladMemory()
    key = "illusion"
    value = "maya"
    devotee = TestDevotee(name="Mayavadi")
    
    # Weak Mantra
    weak_shield = MantraByte.from_string("RAMA") 
    
    success = memory.remember(devotee, key, value, weak_shield)
    assert not success, "Prahlad must reject weak mantra."
    
    assert memory.recall(devotee, key, weak_shield) is None

def test_smaranam_refresh():
    """
    Proves that constant Remembrance (Smaranam) keeps data alive forever.
    """
    memory = PrahladMemory()
    key = "eternal_service"
    value = "Seva"
    shield = MantraByte.standard_16()
    devotee = TestDevotee(name="Hanuman")
    
    memory.remember(devotee, key, value, shield)
    
    # Attack -> Refresh -> Attack -> Refresh
    for _ in range(5):
        memory.force_entropy_attack(key, 0.8) 
        assert memory.recall(devotee, key, shield) == value 
        memory.remember(devotee, key, value, shield) 
        
    print("\n🕉️  PRAHLAD PROOF: Smaranam conquers Time.")
