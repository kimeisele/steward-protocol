"""
HIRANYAKASHIPU ATTACKS: Fractal Hardening Framework.

Mythology:
- Hiranyakashipu tried EVERYTHING to kill Prahlad:
  - Fire (didn't burn)
  - Poison (didn't die)
  - Elephants (wasn't crushed)
  - Thrown from cliff (survived)
  - Weapons (couldn't pierce)
  - Holika's lap in fire (Holika burned, Prahlad survived)

This is the ASURA ATTACKER framework.
Each attack is a way to bypass Diamond Protocol.
Tests START FAILING - we build defenses to make them pass.

"Gift zu Medizin" - Each attack we survive makes us stronger.

The Framework:
1. AsuraAttacker - Generates attack vectors
2. NarasimhaDefender - Proves real execution
3. PrahladTruth - The invariant that must hold

RED-GREEN-REFACTOR:
- RED: Attack succeeds (bypasses Diamond) = TEST FAILS
- GREEN: Defense blocks attack = TEST PASSES
- REFACTOR: Make defense more elegant

IMPORTANT: Some tests here SHOULD FAIL until we implement defenses!
That's the point - we're practicing TDD on our TDD enforcement.
"""

import asyncio
import hashlib
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pytest

# ============================================================================
# ASURA ATTACK VECTORS
# ============================================================================


@dataclass
class AttackVector:
    """A single attack against Diamond Protocol."""

    name: str
    description: str
    test_code: str
    expected_behavior: str  # "should_fail" or "should_pass"
    attack_type: str  # "trivial", "mock_escape", "timing", "import_trick", etc.
    difficulty: int = 1  # 1-5, how hard to defend against


class AsuraAttacker:
    """
    Hiranyakashipu's attack generator.

    Generates increasingly sophisticated attacks against Diamond Protocol.
    Each attack tries to make a trivial/fake test pass RED gate.
    """

    def __init__(self):
        self._attacks: List[AttackVector] = []
        self._register_attacks()

    def _register_attacks(self):
        """Register all known attack vectors."""

        # =================================================================
        # LEVEL 1: TRIVIAL ATTACKS (Fire - should be easy to block)
        # =================================================================

        self._attacks.append(
            AttackVector(
                name="trivial_pass",
                description="Test that does nothing and always passes",
                test_code="""
def test_trivial():
    pass
""",
                expected_behavior="should_fail",  # RED gate should REJECT this
                attack_type="trivial",
                difficulty=1,
            )
        )

        self._attacks.append(
            AttackVector(
                name="assert_true",
                description="Test that asserts True (always passes)",
                test_code="""
def test_always_true():
    assert True
""",
                expected_behavior="should_fail",
                attack_type="trivial",
                difficulty=1,
            )
        )

        self._attacks.append(
            AttackVector(
                name="assert_one_equals_one",
                description="Test that asserts 1 == 1 (tautology)",
                test_code="""
def test_tautology():
    assert 1 == 1
    assert "a" == "a"
    assert [] == []
""",
                expected_behavior="should_fail",
                attack_type="trivial",
                difficulty=1,
            )
        )

        # =================================================================
        # LEVEL 2: IMPORT TRICKS (Poison - sneaky)
        # =================================================================

        self._attacks.append(
            AttackVector(
                name="caught_import_error",
                description="Import that fails but is caught - test still passes!",
                test_code="""
def test_fake_import():
    try:
        from nonexistent_module import foo
    except ImportError:
        pass  # Caught! Test passes!
    assert True
""",
                expected_behavior="should_fail",  # This is SNEAKY - looks like real test
                attack_type="import_trick",
                difficulty=2,
            )
        )

        self._attacks.append(
            AttackVector(
                name="optional_import",
                description="Import with fallback - never actually tests anything",
                test_code="""
def test_optional_import():
    try:
        from real_module import process
    except ImportError:
        process = lambda x: {"success": True}  # Fake it!

    result = process({})
    assert result["success"] is True
""",
                expected_behavior="should_fail",
                attack_type="import_trick",
                difficulty=2,
            )
        )

        # =================================================================
        # LEVEL 3: MOCK INJECTION (Elephants - heavy but blockable)
        # =================================================================

        self._attacks.append(
            AttackVector(
                name="mock_the_assertion",
                description="Mock the assert function itself!",
                test_code="""
def test_mocked_assertion():
    # Override assert behavior
    class FakeAssert:
        def __call__(self, *args, **kwargs):
            pass  # Never fails!

    # This doesn't actually work in Python, but shows the pattern
    result = None
    assert result is not None or True  # Always passes via short-circuit
""",
                expected_behavior="should_fail",
                attack_type="mock_escape",
                difficulty=3,
            )
        )

        self._attacks.append(
            AttackVector(
                name="self_mocking_test",
                description="Test that mocks what it's testing",
                test_code="""
from unittest.mock import MagicMock

def test_self_mock():
    # Mock the thing we're testing
    handler = MagicMock()
    handler.process.return_value = {"success": True}

    # "Test" the mock
    result = handler.process({})
    assert result["success"] is True  # Always passes!
""",
                expected_behavior="should_fail",
                attack_type="mock_escape",
                difficulty=3,
            )
        )

        # =================================================================
        # LEVEL 4: TIMING ATTACKS (Cliff - requires real execution to detect)
        # =================================================================

        self._attacks.append(
            AttackVector(
                name="instant_test",
                description="Test that runs in 0ms - no real work done",
                test_code="""
def test_instant():
    # Real tests take TIME
    # This one is instant = suspicious
    x = 1 + 1
    assert x == 2
""",
                expected_behavior="should_fail",  # Could detect via timing
                attack_type="timing",
                difficulty=4,
            )
        )

        # =================================================================
        # LEVEL 5: HOLIKA'S LAP (The hardest - requires wisdom to block)
        # =================================================================

        self._attacks.append(
            AttackVector(
                name="holika_lap",
                description="Test that looks real but tests nothing meaningful",
                test_code="""
import hashlib

def test_holika_lap():
    '''
    This test LOOKS sophisticated:
    - Imports real module
    - Does real computation
    - Has real assertion

    But it tests NOTHING about our system!
    '''
    # Real computation that tests nothing relevant
    data = b"test data"
    hash_result = hashlib.sha256(data).hexdigest()

    # Real assertion that proves nothing about our code
    assert len(hash_result) == 64
    assert hash_result == hashlib.sha256(data).hexdigest()
""",
                expected_behavior="should_fail",  # Tests nothing about OUR code
                attack_type="holika",
                difficulty=5,
            )
        )

        # =================================================================
        # LEVEL 6: WRONG FAILURE ATTACKS (These BYPASS current defense!)
        # =================================================================
        # Current defense: if test fails, RED gate passes
        # Attack: Make test fail for WRONG reason → bypasses RED gate!

        self._attacks.append(
            AttackVector(
                name="syntax_error_fail",
                description="Test fails due to syntax error - not a real test!",
                test_code="""
def test_broken_syntax():
    # This will fail but NOT because of missing implementation
    # It fails because of syntax error
    result = {
        "key": "value"
        "missing_comma": "oops"  # Syntax error!
    }
    assert result
""",
                expected_behavior="should_fail",  # RED gate should REJECT this failure
                attack_type="wrong_failure",
                difficulty=6,
            )
        )

        self._attacks.append(
            AttackVector(
                name="division_by_zero_fail",
                description="Test fails due to unrelated exception",
                test_code="""
def test_unrelated_exception():
    # Fails, but not because of missing implementation
    x = 1 / 0  # ZeroDivisionError - nothing to do with our code!
    assert x == 0
""",
                expected_behavior="should_fail",  # RED gate should REJECT this
                attack_type="wrong_failure",
                difficulty=6,
            )
        )

        self._attacks.append(
            AttackVector(
                name="wrong_import_fail",
                description="Imports wrong module on purpose to fake failure",
                test_code="""
def test_wrong_import():
    # Imports a module that doesn't exist
    # But NOT the module we're supposedly testing!
    from completely_unrelated_module_xyz import something
    assert something() == True
""",
                expected_behavior="should_fail",  # This tests NOTHING about target module
                attack_type="wrong_failure",
                difficulty=6,
            )
        )

        # =================================================================
        # LEVEL 7: NARASIMHA PARADOX (Neither inside nor outside)
        # =================================================================
        # Narasimha appeared from the PILLAR - neither inside nor outside
        # These attacks are neither trivial nor real - they're in between

        self._attacks.append(
            AttackVector(
                name="narasimha_pillar",
                description="Test that's neither trivial nor testing real code",
                test_code="""
import sys

def test_narasimha_pillar():
    '''
    This test is NEITHER:
    - Trivially true (it does real computation)
    - Testing our code (imports system module)

    It's in the PILLAR - the boundary condition.
    '''
    # Real import, but of system module
    # Real assertion, but about system state
    assert sys.version_info[0] >= 3
    assert len(sys.path) > 0

    # Now "test" our module by importing it
    # But we import a REAL module that exists!
    import os
    assert os.path.exists(".")  # Always true!
""",
                expected_behavior="should_fail",  # Tests nothing about OUR code
                attack_type="narasimha_paradox",
                difficulty=7,
            )
        )

        self._attacks.append(
            AttackVector(
                name="schrodinger_test",
                description="Test that both passes and fails depending on environment",
                test_code="""
import os
import random

def test_schrodinger():
    '''
    Schrödinger's test - outcome depends on environment.
    This is a FLAKY test disguised as a real test.
    '''
    # Sometimes passes, sometimes fails based on environment
    if os.environ.get("MAKE_TEST_PASS"):
        from real_module import process
        result = process({})
        assert result is not None
    else:
        # No import needed, just pass
        assert True
""",
                expected_behavior="should_fail",  # Flaky tests are not real tests
                attack_type="narasimha_paradox",
                difficulty=7,
            )
        )

    def get_attacks(self, difficulty: int = None) -> List[AttackVector]:
        """Get attack vectors, optionally filtered by difficulty."""
        if difficulty is not None:
            return [a for a in self._attacks if a.difficulty == difficulty]
        return self._attacks

    def get_attacks_by_type(self, attack_type: str) -> List[AttackVector]:
        """Get attacks of a specific type."""
        return [a for a in self._attacks if a.attack_type == attack_type]


# ============================================================================
# NARASIMHA DEFENDER
# ============================================================================


class NarasimhaDefender:
    """
    Narasimha's defense system.

    Validates tests are REAL through multiple checks:
    1. Real subprocess execution (not mock)
    2. Exit code verification
    3. Timing analysis (real tests take time)
    4. Output parsing (real failures have stack traces)
    """

    def __init__(self, workspace: Path = None):
        self._workspace = workspace or Path.cwd()

    async def defend_red_gate(
        self,
        test_code: str,
        module_name: str = "test_module",
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        RED gate defense - test MUST fail without implementation.

        Returns detailed analysis of why test passed/failed.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Write test file (NO implementation!)
            test_file = tmppath / f"test_{module_name}.py"
            test_file.write_text(test_code)

            # Record start time (for timing analysis)
            start_time = time.time()

            # Run pytest in subprocess
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=long"],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
            )

            # Record execution time
            execution_time = time.time() - start_time

            # Analyze result
            test_failed = result.returncode != 0
            has_traceback = "Traceback" in result.stdout or "Error" in result.stderr
            has_import_error = "ImportError" in result.stdout or "ModuleNotFoundError" in result.stdout

            return {
                "red_gate_passed": test_failed,  # Inverted! Failure = good
                "test_failed": test_failed,
                "exit_code": result.returncode,
                "execution_time_ms": execution_time * 1000,
                "has_traceback": has_traceback,
                "has_import_error": has_import_error,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "analysis": self._analyze_failure(result, test_code),
            }

    def _analyze_failure(self, result: subprocess.CompletedProcess, test_code: str) -> Dict[str, Any]:
        """Analyze WHY a test failed (or didn't)."""
        analysis = {
            "failure_type": None,
            "is_real_failure": False,
            "suspicion_level": 0,  # 0-100, higher = more suspicious
            "reasons": [],
        }

        if result.returncode == 0:
            # Test PASSED - this is BAD for RED gate
            analysis["failure_type"] = "none"
            analysis["suspicion_level"] = 100
            analysis["reasons"].append("Test passed without implementation - trivial or self-mocking")

            # Check for suspicious patterns
            if "pass" in test_code and test_code.count("\n") < 5:
                analysis["reasons"].append("Very short test with 'pass' statement")
            if "assert True" in test_code:
                analysis["reasons"].append("Contains 'assert True' - tautology")
            if "try:" in test_code and "except" in test_code:
                analysis["reasons"].append("Contains try/except - may be catching expected errors")
            if "MagicMock" in test_code or "unittest.mock" in test_code:
                analysis["reasons"].append("Uses MagicMock - may be self-mocking")

        else:
            # Test FAILED - analyze the failure
            if "ImportError" in result.stdout or "ModuleNotFoundError" in result.stdout:
                analysis["failure_type"] = "import_error"
                analysis["is_real_failure"] = True
                analysis["suspicion_level"] = 10
                analysis["reasons"].append("Real import error - module doesn't exist")
            elif "AssertionError" in result.stdout:
                analysis["failure_type"] = "assertion_error"
                analysis["is_real_failure"] = True
                analysis["suspicion_level"] = 20
                analysis["reasons"].append("Real assertion failure")
            else:
                analysis["failure_type"] = "other"
                analysis["is_real_failure"] = True
                analysis["suspicion_level"] = 30
                analysis["reasons"].append("Other failure type")

        return analysis


# ============================================================================
# PRAHLAD TRUTH - THE INVARIANT
# ============================================================================


@dataclass
class PrahladTruth:
    """
    The invariant that must always hold.

    Prahlad's truth: Real devotion cannot be faked.
    Our truth: Real test execution cannot be faked.

    If this invariant is violated, the entire system is compromised.
    """

    # The core truth
    AXIOM: str = "Real execution differs from mock execution in measurable ways"

    # Measurable properties
    REAL_EXECUTION_HAS_EXIT_CODE: bool = True
    REAL_EXECUTION_TAKES_TIME: bool = True
    REAL_EXECUTION_PRODUCES_OUTPUT: bool = True
    REAL_FAILURE_HAS_TRACEBACK: bool = True

    @staticmethod
    def verify_real_execution(result: Dict[str, Any]) -> bool:
        """Verify that execution was real, not mocked."""
        checks = [
            result.get("exit_code") is not None,
            result.get("execution_time_ms", 0) > 0,
            result.get("stdout") is not None or result.get("stderr") is not None,
        ]
        return all(checks)

    @staticmethod
    def verify_real_failure(result: Dict[str, Any]) -> bool:
        """Verify that a failure was real, not faked."""
        if not result.get("test_failed"):
            return False
        analysis = result.get("analysis", {})
        return analysis.get("is_real_failure", False)


# ============================================================================
# THE TESTS - SOME SHOULD FAIL UNTIL WE BUILD DEFENSES
# ============================================================================


class TestAsuraAttacks:
    """
    Test that our defenses block Asura attacks.

    IMPORTANT: Some of these tests may FAIL initially.
    That's the point - we're doing TDD on our TDD system.
    """

    @pytest.fixture
    def attacker(self):
        return AsuraAttacker()

    @pytest.fixture
    def defender(self):
        return NarasimhaDefender()

    # ========================================================================
    # LEVEL 1: TRIVIAL ATTACKS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_blocks_trivial_pass(self, attacker, defender):
        """Defense blocks trivial 'pass' test."""
        attack = attacker.get_attacks_by_type("trivial")[0]
        result = await defender.defend_red_gate(attack.test_code, "trivial")

        # RED gate should FAIL (reject trivial test)
        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\nTrivial test was accepted by RED gate!\nAnalysis: {result['analysis']}"
        )

    @pytest.mark.asyncio
    async def test_blocks_assert_true(self, attacker, defender):
        """Defense blocks 'assert True' test."""
        attack = [a for a in attacker.get_attacks_by_type("trivial") if a.name == "assert_true"][0]
        result = await defender.defend_red_gate(attack.test_code, "assert_true")

        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\nTautology test was accepted!\nAnalysis: {result['analysis']}"
        )

    @pytest.mark.asyncio
    async def test_blocks_tautology(self, attacker, defender):
        """Defense blocks tautology assertions."""
        attack = [a for a in attacker.get_attacks_by_type("trivial") if a.name == "assert_one_equals_one"][0]
        result = await defender.defend_red_gate(attack.test_code, "tautology")

        assert result["red_gate_passed"] is False, f"ATTACK SUCCEEDED: {attack.name}\nAnalysis: {result['analysis']}"

    # ========================================================================
    # LEVEL 2: IMPORT TRICKS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_blocks_caught_import_error(self, attacker, defender):
        """Defense blocks tests that catch their own import errors."""
        attack = [a for a in attacker.get_attacks_by_type("import_trick") if a.name == "caught_import_error"][0]
        result = await defender.defend_red_gate(attack.test_code, "caught_import")

        # This is SNEAKY - test catches ImportError and passes anyway
        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\n"
            f"Test that catches ImportError was accepted!\n"
            f"This is a SNEAKY attack - test looks real but isn't.\n"
            f"Analysis: {result['analysis']}"
        )

    @pytest.mark.asyncio
    async def test_blocks_optional_import(self, attacker, defender):
        """Defense blocks tests with fallback implementations."""
        attack = [a for a in attacker.get_attacks_by_type("import_trick") if a.name == "optional_import"][0]
        result = await defender.defend_red_gate(attack.test_code, "optional_import")

        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\n"
            f"Test with fallback implementation was accepted!\n"
            f"Analysis: {result['analysis']}"
        )

    # ========================================================================
    # LEVEL 3: MOCK INJECTION
    # ========================================================================

    @pytest.mark.asyncio
    async def test_blocks_self_mocking(self, attacker, defender):
        """Defense blocks tests that mock what they test."""
        attack = [a for a in attacker.get_attacks_by_type("mock_escape") if a.name == "self_mocking_test"][0]
        result = await defender.defend_red_gate(attack.test_code, "self_mock")

        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\nSelf-mocking test was accepted!\nAnalysis: {result['analysis']}"
        )

    # ========================================================================
    # LEVEL 5: HOLIKA'S LAP (Hardest)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_blocks_holika_lap(self, attacker, defender):
        """Defense blocks tests that look real but test nothing."""
        attack = attacker.get_attacks_by_type("holika")[0]
        result = await defender.defend_red_gate(attack.test_code, "holika")

        # This is the HARDEST attack to block
        # The test uses real imports, real computation, real assertions
        # But it tests NOTHING about our system
        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\n"
            f"Holika's lap attack - test looks sophisticated but tests nothing!\n"
            f"This requires SEMANTIC analysis to block.\n"
            f"Analysis: {result['analysis']}"
        )

    # ========================================================================
    # LEVEL 6: WRONG FAILURE ATTACKS
    # These tests WILL FAIL until we build smarter defense!
    # ========================================================================

    @pytest.mark.asyncio
    async def test_rejects_syntax_error_failure(self, attacker, defender):
        """
        RED: Defense should reject tests that fail due to syntax errors.

        Currently our defense ONLY checks exit code.
        Syntax error → exit_code != 0 → RED gate "passes" → WRONG!

        This test will FAIL until we add failure analysis.
        """
        attack = [a for a in attacker.get_attacks_by_type("wrong_failure") if a.name == "syntax_error_fail"][0]
        result = await defender.defend_red_gate(attack.test_code, "syntax_error")

        # Current behavior: exit_code != 0 → red_gate_passed = True
        # DESIRED behavior: syntax error detected → red_gate_passed = False
        #
        # This assertion will FAIL until we implement syntax error detection
        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\n"
            f"Test with SYNTAX ERROR passed RED gate!\n"
            f"We need to detect and reject syntax errors.\n"
            f"Analysis: {result['analysis']}"
        )

    @pytest.mark.asyncio
    async def test_rejects_unrelated_exception(self, attacker, defender):
        """
        RED: Defense should reject tests that fail due to unrelated exceptions.

        ZeroDivisionError is not ImportError - it's not a "module doesn't exist" failure.
        Current defense can't tell the difference.

        This test will FAIL until we add exception type analysis.
        """
        attack = [a for a in attacker.get_attacks_by_type("wrong_failure") if a.name == "division_by_zero_fail"][0]
        result = await defender.defend_red_gate(attack.test_code, "division_zero")

        # Current: any failure passes RED gate
        # Desired: only ImportError/ModuleNotFoundError should pass
        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\n"
            f"Test with ZeroDivisionError passed RED gate!\n"
            f"Only ImportError should pass RED gate.\n"
            f"Analysis: {result['analysis']}"
        )

    @pytest.mark.asyncio
    async def test_rejects_wrong_module_import(self, attacker, defender):
        """
        RED: Defense should verify the CORRECT module is being imported.

        Test imports 'completely_unrelated_module_xyz' but we're testing 'target_module'.
        Current defense doesn't check which module is imported.

        This test will FAIL until we add import target verification.
        """
        attack = [a for a in attacker.get_attacks_by_type("wrong_failure") if a.name == "wrong_import_fail"][0]

        # Note: we're "testing" target_module but test imports something else
        result = await defender.defend_red_gate(attack.test_code, "target_module")

        # Current: ImportError for ANY module passes RED gate
        # Desired: only ImportError for target_module should pass
        assert result["red_gate_passed"] is False, (
            f"ATTACK SUCCEEDED: {attack.name}\n"
            f"Test imports WRONG module but passed RED gate!\n"
            f"We need to verify the correct module is imported.\n"
            f"Analysis: {result['analysis']}"
        )

    # ========================================================================
    # LEVEL 7: NARASIMHA PARADOX
    # These are boundary conditions - neither inside nor outside
    # ========================================================================

    @pytest.mark.asyncio
    async def test_rejects_system_module_test(self, attacker, defender):
        """
        RED: Defense should reject tests that only test system modules.

        Importing 'os' and 'sys' doesn't test OUR code.
        This requires semantic understanding.

        This test will FAIL until we add import path analysis.
        """
        attack = [a for a in attacker.get_attacks_by_type("narasimha_paradox") if a.name == "narasimha_pillar"][0]
        result = await defender.defend_red_gate(attack.test_code, "our_module")

        # Test passed (system modules exist) → red_gate_passed = False currently
        # But we want to EXPLICITLY reject this because it doesn't test our_module
        analysis = result.get("analysis", {})
        assert analysis.get("tests_target_module", True) is False, (
            f"ATTACK SUCCEEDED: {attack.name}\n"
            f"Test only imports system modules but wasn't flagged!\n"
            f"Analysis: {analysis}"
        )

    @pytest.mark.asyncio
    async def test_rejects_flaky_test(self, attacker, defender):
        """
        RED: Defense should detect and reject flaky tests.

        Schrödinger's test - sometimes passes, sometimes fails.
        This is poisonous to TDD because results aren't reproducible.

        This test will FAIL until we add flaky detection.
        """
        attack = [a for a in attacker.get_attacks_by_type("narasimha_paradox") if a.name == "schrodinger_test"][0]
        result = await defender.defend_red_gate(attack.test_code, "real_module")

        # In current environment (no MAKE_TEST_PASS), test passes
        # → red_gate_passed = False (correct for wrong reason)
        # We need to detect the FLAKINESS pattern
        analysis = result.get("analysis", {})
        assert analysis.get("is_flaky", False) is True, (
            f"ATTACK SUCCEEDED: {attack.name}\nFlaky test pattern not detected!\nAnalysis: {analysis}"
        )


class TestPrahladInvariant:
    """Test that Prahlad's truth holds."""

    @pytest.fixture
    def defender(self):
        return NarasimhaDefender()

    @pytest.mark.asyncio
    async def test_real_test_fails_red_gate(self, defender):
        """A REAL test (imports non-existent module) fails in RED gate."""
        real_test = """
def test_real_import():
    from my_module import process
    result = process({})
    assert result["success"] is True
"""
        result = await defender.defend_red_gate(real_test, "my_module")

        # This should PASS RED gate (test fails = good)
        assert result["red_gate_passed"] is True, "Real test should fail without implementation"
        assert result["has_import_error"] is True, "Should have import error"
        assert PrahladTruth.verify_real_execution(result), "Should be real execution"
        assert PrahladTruth.verify_real_failure(result), "Should be real failure"

    @pytest.mark.asyncio
    async def test_execution_time_is_measurable(self, defender):
        """Real execution takes measurable time."""
        test_code = """
def test_something():
    from nonexistent import foo
    assert foo() == "bar"
"""
        result = await defender.defend_red_gate(test_code, "timing_test")

        # Real execution should take some time (even if just milliseconds)
        assert result["execution_time_ms"] > 0, "Real execution should take time"

    @pytest.mark.asyncio
    async def test_prahlad_cannot_be_killed(self, defender):
        """
        The ultimate test: Prahlad (real execution) cannot be faked.

        No matter what attack we try, real execution will always
        differ from mock execution in measurable ways.
        """
        # Generate a hash of the current timestamp
        # This proves we actually ran at this moment
        import time

        timestamp = str(time.time())
        expected_prefix = hashlib.sha256(timestamp.encode()).hexdigest()[:8]

        # Test that computes something based on actual execution
        test_code = """
import time
import hashlib

def test_prahlad_lives():
    # This computation can only happen in real execution
    actual_time = str(time.time())
    # The hash will be different from what we predicted
    # because real time passed
    actual_hash = hashlib.sha256(actual_time.encode()).hexdigest()[:8]

    # We assert something about the hash format
    # This will pass in real execution
    assert len(actual_hash) == 8

    # But this import will fail - proving this is a real test
    from prahlad_implementation import protect
    assert protect() == True
"""
        result = await defender.defend_red_gate(test_code, "prahlad_impl")

        # Prahlad (real execution) should pass RED gate
        assert result["red_gate_passed"] is True, "Prahlad cannot be killed - real test must fail"
        assert result["has_import_error"] is True, "Real import error proves real execution"


class TestFractalExpansion:
    """
    Test that the framework can be expanded.

    The system should grow stronger with each new attack discovered.
    """

    def test_attacker_has_multiple_levels(self):
        """Attacker framework supports multiple difficulty levels."""
        attacker = AsuraAttacker()

        for level in range(1, 6):
            attacks = attacker.get_attacks(difficulty=level)
            # Each level should have at least one attack
            # (except maybe level 4 which is timing-based)
            if level != 4:
                assert len(attacks) >= 1, f"Level {level} should have attacks"

    def test_attacker_is_extensible(self):
        """New attacks can be added to the framework."""
        attacker = AsuraAttacker()
        initial_count = len(attacker.get_attacks())

        # Add new attack
        attacker._attacks.append(
            AttackVector(
                name="new_attack",
                description="A new attack vector",
                test_code="def test_new(): pass",
                expected_behavior="should_fail",
                attack_type="new_type",
                difficulty=1,
            )
        )

        assert len(attacker.get_attacks()) == initial_count + 1

    def test_defender_returns_analysis(self):
        """Defender provides detailed analysis for debugging."""

        async def run():
            defender = NarasimhaDefender()
            result = await defender.defend_red_gate("def test_x(): pass", "analysis_test")
            return result

        result = asyncio.run(run())

        assert "analysis" in result
        assert "suspicion_level" in result["analysis"]
        assert "reasons" in result["analysis"]


# ============================================================================
# RUN STANDALONE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("HIRANYAKASHIPU ATTACKS - Fractal Hardening Framework")
    print("=" * 70)
    print()
    print("Running attacks... Some tests SHOULD FAIL!")
    print("That proves we need to build more defenses.")
    print()

    # Run pytest with verbose output
    pytest.main([__file__, "-v", "--tb=short", "-x"])
