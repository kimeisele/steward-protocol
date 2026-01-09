import pytest
from dataclasses import dataclass, field
from typing import List, Any
from vibe_core.protocols.testable import Testable, TestableType, TestCase
from vibe_core.protocols.governance.dwarapala import DwarapalaGatekeeper, CommitIntent

@dataclass
class MockComponent(Testable):
    id: str
    pass_test: bool = True
    has_fast_test: bool = True

    def get_testable_id(self) -> str:
        return self.id

    def get_testable_type(self) -> TestableType:
        return TestableType.PLUGIN

    def get_test_cases(self) -> List[TestCase]:
        if not self.has_fast_test:
            return []
        
        tags = ["fast"]
        def mock_test(kernel: Any, target: Any) -> bool:
            return self.pass_test

        return [TestCase(name="mock_check", description="Mock", tags=tags, test_func=mock_test)]

    def evaluate_life(self, result: Any, gene: Any) -> str:
        return "GREEN"


@dataclass
class MockIntent(CommitIntent):
    author: str
    changes: List[Testable]
    message: str

def test_dwarapala_gatekeeper():
    gate = DwarapalaGatekeeper()

    # 1. Block Cowardice (No Tests)
    coward = MockComponent(id="coward", has_fast_test=False)
    intent1 = MockIntent("User", [coward], "feat: bad code")
    allowed, msg = gate.inspect_commit(intent1)
    
    assert not allowed
    assert "Cowardice" in msg

    # 2. Block Failure (Test Fails)
    failure = MockComponent(id="failure", pass_test=False)
    intent2 = MockIntent("User", [failure], "feat: broken code")
    allowed, msg = gate.inspect_commit(intent2)
    
    assert not allowed
    assert "BLOCK" in msg

    # 3. Allow Victory (Test Passes)
    hero = MockComponent(id="hero", pass_test=True)
    intent3 = MockIntent("User", [hero], "feat: good code")
    allowed, msg = gate.inspect_commit(intent3)
    
    assert allowed
    assert "Access Granted" in msg
