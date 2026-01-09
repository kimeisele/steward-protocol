import pytest
from typing import Set
from vibe_core.protocols.types import PersonProtocol, ServiceProtocol, Capability
from vibe_core.protocols.governance.dwarapala import DwarapalaGate, AccessDenied
from tests.common.avatars import TestDevotee, TestService

# --- TESTS ---

def test_dwarapala_gate_access():
    gate = DwarapalaGate()
    
    # 1. Define Actors (Vidura & Civilians)
    user_arjuna = TestDevotee(name="Arjuna")
    user_arjuna.add_capability("read", risk=1)
    user_arjuna.add_capability("nuke", risk=10)
    
    user_civilian = TestDevotee(name="Civilian")
    user_civilian.add_capability("read", risk=1)
    
    service_bot = TestService()
    
    # CASE A: Authorized Person (Arjuna -> Nuke)
    # Should result in success (returns accessor)
    accessor = gate.verify_accessor(user_arjuna, "nuke")
    assert accessor == user_arjuna
    
    # CASE B: Unauthorized Person (Civilian -> Nuke)
    # Should raise AccessDenied (Adhikara Failure)
    with pytest.raises(AccessDenied) as excinfo:
        gate.verify_accessor(user_civilian, "nuke")
    assert "Adhikara Failure" in str(excinfo.value)
    
    # CASE C: Identity Crisis (Service -> Nuke)
    # Should raise AccessDenied (Identity Crisis)
    # ServiceBot is class TestService, which does NOT implement PersonProtocol
    with pytest.raises(AccessDenied) as excinfo:
        gate.verify_accessor(service_bot, "read") # type: ignore
    assert "Identity Crisis" in str(excinfo.value)

def test_gate_open():
    """Verify pass-through mechanism."""
    gate = DwarapalaGate()
    user = TestDevotee(name="User")
    user.add_capability("enter")
    
    resource = {"secret": "data"}
    
    # Open Gate
    result = gate.open_gate(user, resource)
    assert result == resource
