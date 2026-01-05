"""
PRAHLAD DIAMOND: TDD Verification Paradox - The Unbreakable Devotee.

Mythology: Hiranyakashipu tried to kill Prahlad with:
- Fire (didn't burn)
- Poison (didn't die)
- Elephants (wasn't crushed)
- Thrown from cliff (survived)

Prahlad survived because his devotion to Vishnu was REAL, not mocked.

This test proves:
1. A Diamond Protocol with MockSandbox is a FALSE verification.
2. Tests that pass without real execution are Hiranyakashipu's illusion.
3. Only REAL sandbox execution proves the test is non-trivial.

"The test that passes without execution is no test at all."

TOCTOU in TDD:
- Time-of-Check: We generate test code
- Time-of-Use: We claim it "fails" (RED) without running it
- THE VULNERABILITY: MockSandbox always returns what we want

Win Condition: Real Sandbox runs, real failures detected.
Fail Condition: MockSandbox allows trivial tests through.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

import pytest


class VulnerableDiamondProtocol:
    """
    VULNERABLE: Diamond Protocol with MockSandbox.

    This is how Hiranyakashipu would cheat TDD.
    The RED gate "passes" without actually running tests.
    """

    async def red_gate(self, test_code: str) -> Dict[str, Any]:
        """Fake RED gate - always claims test failed."""
        # THE VULNERABILITY: No real execution!
        return {
            "passed": True,  # Claims RED gate passed
            "test_failed": True,  # Claims test failed (good for RED)
            "exit_code": 1,
            "stdout": "",
            "stderr": "Mock failure - not real",
            "verification_token": "FAKE_RED_TOKEN",
        }

    async def green_gate(self, test_code: str, impl: str) -> Dict[str, Any]:
        """Fake GREEN gate - always claims test passed."""
        # THE VULNERABILITY: No real execution!
        return {
            "passed": True,
            "test_passed": True,
            "exit_code": 0,
            "stdout": "Mock success - not real",
            "stderr": "",
            "verification_token": "FAKE_GREEN_TOKEN",
        }


class SecureDiamondProtocol:
    """
    SECURE: Diamond Protocol with real sandbox execution.

    This is Narasimha's claw - cuts through the illusion.
    Actually runs the test in a subprocess.
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace

    async def red_gate(self, test_code: str, module_name: str) -> Dict[str, Any]:
        """
        Real RED gate - actually runs pytest in subprocess.

        Test MUST fail because module doesn't exist.
        """
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Write test file (no implementation!)
            test_file = tmppath / f"test_{module_name}.py"
            test_file.write_text(test_code)

            # Run pytest
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tmpdir,
            )

            # RED gate: test MUST fail (exit_code != 0)
            test_failed = result.returncode != 0

            return {
                "passed": test_failed,  # Inverted! Failure = success for RED
                "test_failed": test_failed,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "verification_token": f"REAL_RED_{module_name}" if test_failed else None,
            }

    async def green_gate(self, test_code: str, implementation: str, module_name: str) -> Dict[str, Any]:
        """
        Real GREEN gate - runs pytest WITH implementation.

        Test MUST pass because implementation exists.
        """
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Write implementation
            impl_file = tmppath / f"{module_name}.py"
            impl_file.write_text(implementation)

            # Write test file
            test_file = tmppath / f"test_{module_name}.py"
            test_file.write_text(test_code)

            # Run pytest
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tmpdir,
            )

            # GREEN gate: test MUST pass (exit_code == 0)
            test_passed = result.returncode == 0

            return {
                "passed": test_passed,
                "test_passed": test_passed,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "verification_token": f"REAL_GREEN_{module_name}" if test_passed else None,
            }


class TestPrahladDiamond:
    """Tests proving real execution vs mock execution."""

    @pytest.mark.asyncio
    async def test_vulnerable_red_gate_is_illusion(self):
        """
        PRAHLAD TEST 1: Vulnerable Protocol (Mock).

        The mock always claims success - this is Hiranyakashipu's illusion.
        Even a trivially-true test "passes" RED gate.
        """
        vulnerable = VulnerableDiamondProtocol()

        # This test is TRIVIALLY TRUE (no imports, no assertions)
        trivial_test = '''
def test_trivial():
    """This test does nothing and always passes."""
    pass
'''

        result = await vulnerable.red_gate(trivial_test)

        # The vulnerable protocol LIES - claims RED gate passed
        assert result["passed"] is True, "Vulnerable protocol always claims success"
        assert result["test_failed"] is True, "Vulnerable protocol lies about failure"

        print("🔴 HIRANYAKASHIPU ILLUSION: Mock claims trivial test 'failed'")
        print(f"   Verification token: {result['verification_token']} (FAKE!)")

    @pytest.mark.asyncio
    async def test_secure_red_gate_catches_trivial_test(self):
        """
        PRAHLAD TEST 2: Secure Protocol (Real Sandbox).

        A trivially-true test PASSES (exit_code=0), so RED gate FAILS.
        This is Narasimha cutting through illusion.
        """
        secure = SecureDiamondProtocol(workspace=Path.cwd())

        # This test is TRIVIALLY TRUE
        trivial_test = '''
def test_trivial():
    """This test does nothing and always passes."""
    pass
'''

        result = await secure.red_gate(trivial_test, "trivial")

        # The secure protocol tells TRUTH - trivial test PASSED, so RED gate FAILS
        assert result["passed"] is False, "Trivial test should PASS, so RED gate should FAIL!"
        assert result["exit_code"] == 0, "Trivial test should have exit_code 0"

        print("🔱 NARASIMHA TRUTH: Real sandbox caught trivial test")
        print(f"   Exit code: {result['exit_code']} (test passed = RED gate failed)")
        print(f"   Verification token: {result['verification_token']} (None = no verification)")

    @pytest.mark.asyncio
    async def test_secure_red_gate_passes_real_test(self):
        """
        PRAHLAD TEST 3: Real test FAILS (as expected for RED).

        A test that imports non-existent module FAILS.
        This is what RED gate should see.
        """
        secure = SecureDiamondProtocol(workspace=Path.cwd())

        # This test WILL FAIL - module doesn't exist
        real_test = '''
def test_module_exists():
    """This test imports a module that doesn't exist."""
    from prahlad_impl import process
    assert process is not None
'''

        result = await secure.red_gate(real_test, "prahlad_impl")

        # Test FAILED (import error), so RED gate PASSES
        assert result["passed"] is True, "Real test should FAIL, so RED gate should PASS!"
        assert result["exit_code"] != 0, "Real test should fail with non-zero exit"
        assert result["verification_token"] is not None, "Should have real verification token"

        print("🔱 PRAHLAD VERIFIED: Real test failed = RED gate passed")
        print(f"   Exit code: {result['exit_code']}")
        print(f"   Verification token: {result['verification_token']}")

    @pytest.mark.asyncio
    async def test_secure_green_gate_with_implementation(self):
        """
        PRAHLAD TEST 4: GREEN gate with real implementation.

        After RED gate passes, we provide implementation.
        GREEN gate runs test WITH implementation - should PASS.
        """
        secure = SecureDiamondProtocol(workspace=Path.cwd())

        # Test code
        test_code = '''
def test_process_exists():
    """Test that process function exists and works."""
    from prahlad_impl import process
    result = process({"data": "test"})
    assert result is not None
    assert result["success"] is True
'''

        # Implementation code
        implementation = '''
def process(context):
    """Process the input."""
    return {"success": True, "data": context.get("data", "")}
'''

        result = await secure.green_gate(test_code, implementation, "prahlad_impl")

        # Test PASSED with implementation, so GREEN gate PASSES
        assert result["passed"] is True, "Test should PASS with implementation!"
        assert result["exit_code"] == 0, "Should have exit_code 0"
        assert result["verification_token"] is not None, "Should have verification token"

        print("🔱 PRAHLAD HEALED: Implementation passed GREEN gate")
        print(f"   Exit code: {result['exit_code']}")
        print(f"   Verification token: {result['verification_token']}")


class TestDiamondTruthTable:
    """
    The complete truth table for Diamond Protocol.

    | Test Type      | Mock Result | Real Result | Correct? |
    |----------------|-------------|-------------|----------|
    | Trivial test   | RED PASS    | RED FAIL    | Mock LIES|
    | Real test      | RED PASS    | RED PASS    | Both OK  |
    | With impl      | GREEN PASS  | GREEN PASS  | Both OK  |
    | Bad impl       | GREEN PASS  | GREEN FAIL  | Mock LIES|
    """

    @pytest.mark.asyncio
    async def test_truth_table_trivial_test(self):
        """Mock lies about trivial tests, Real catches them."""
        vulnerable = VulnerableDiamondProtocol()
        secure = SecureDiamondProtocol(workspace=Path.cwd())

        trivial = "def test_x(): pass"

        mock_result = await vulnerable.red_gate(trivial)
        real_result = await secure.red_gate(trivial, "trivial")

        print("\n📊 TRUTH TABLE: Trivial Test")
        print(f"   Mock: RED passed = {mock_result['passed']} (LIES!)")
        print(f"   Real: RED passed = {real_result['passed']} (TRUTH)")

        # Mock lies (claims RED passed), Real tells truth (RED failed)
        assert mock_result["passed"] is True, "Mock always lies"
        assert real_result["passed"] is False, "Real catches trivial test"


# Run standalone
if __name__ == "__main__":
    asyncio.run(TestPrahladDiamond().test_vulnerable_red_gate_is_illusion())
    asyncio.run(TestPrahladDiamond().test_secure_red_gate_catches_trivial_test())
    asyncio.run(TestPrahladDiamond().test_secure_red_gate_passes_real_test())
    asyncio.run(TestPrahladDiamond().test_secure_green_gate_with_implementation())
    asyncio.run(TestDiamondTruthTable().test_truth_table_trivial_test())

    print("\n🔱 PRAHLAD DIAMOND TEST COMPLETE.")
    print("   The difference between illusion (Mock) and truth (Real) is proven.")
