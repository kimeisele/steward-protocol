import pytest
from vibe_core.protocols.universal.ramanujan import RamanujanProtocol

def test_the_12th_mahajana_proof():
    """
    Executes the Ramanujan Protocol's 12th Test.
    This test passes ONLY if the Logic Fails (Necessity of Failure).
    """
    protocol = RamanujanProtocol()
    
    # Run the proof
    result = protocol.run_proof()
    
    # Assert that the proof validated the failure of logic
    assert result, "The System failed to realize its own mortality."
    print("\n🕉️  RAMANUJAN PROOF: VALIDATED.")

