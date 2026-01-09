import pytest
import time
from typing import List
from vibe_core.protocols.universal.yamaraja import secure_contract, YamarajaProtocol

# 1. MOCK FUNCTION: FAST (Should Pass)
@secure_contract(baseline_metric=100.0)
def fast_function():
    # Very fast
    return "Fast"

# 2. MOCK FUNCTION: SLOW (Should Fail)
@secure_contract(baseline_metric=10000000.0) # Impossible baseline
def slow_function():
    time.sleep(0.01) # Deliberate slowdown
    return "Slow"

# 3. TYPE SAFETY TEST
@secure_contract(baseline_metric=0.0) # Baseline 0 always passes
def typed_function(data: List[str]) -> str:
    return "".join(data)

def test_contract_enforcement():
    """
    Test that Yamaraja allows efficient code and kills inefficient code.
    """
    # 1. Valid Execution
    try:
        res = fast_function()
        assert res == "Fast"
    except SystemError:
        pytest.fail("Yamaraja killed a valid fast function!")

    # 2. Invalid Execution (The Danda)
    with pytest.raises(SystemError) as excinfo:
        slow_function()
    
    assert "YAMARAJA PROTOCOL VIOLATION" in str(excinfo.value)
    assert "stagnating" in str(excinfo.value)

def test_typing_integrity():
    """
    Test Step 3: Verify Type Hints (Runtime check only here, static analysis assumed checked by linter)
    """
    # At runtime, we just check it runs correctly.
    # The Decorator ParamSpec ensures tools like MyPy would be happy.
    val: str = typed_function(["Hara", "Krishna"])
    assert val == "HaraKrishna"
    
def test_mock_judgment():
    """
    Directly test the logic.
    """
    # 100 baseline, 150 current -> 1.5x -> Pass
    j = YamarajaProtocol.evaluate("test", 100.0, 150.0)
    assert j.verdict == "allow"
    
    # 100 baseline, 105 current -> 1.05x -> Fail (< 1.08)
    j2 = YamarajaProtocol.evaluate("test", 100.0, 105.0)
    assert j2.verdict == "deny"
