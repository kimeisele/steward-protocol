"""
BREAK TEST 2.0: Diamond Protocol Validation
============================================

This test validates that the RED gate correctly:
1. REJECTS trivial tests (tests that pass without implementation)
2. ACCEPTS valid tests (tests that fail without implementation)

"Trust but Verify" - Senior Partner Directive

Run with: python -m pytest tests/break_test_diamond.py -v
"""

import asyncio
from pathlib import Path

import pytest


class TestDiamondRedGate:
    """Tests for the Diamond Protocol's RED Gate enforcement."""

    @pytest.fixture
    def handlers(self):
        """Get Diamond handlers instance."""
        from vibe_core.plugins.opus_assistant.events.diamond_handlers import DiamondHandlers

        return DiamondHandlers(workspace=Path.cwd())

    @pytest.mark.asyncio
    async def test_red_gate_rejects_trivial_test(self, handlers):
        """
        SCENARIO 1: Trivial Test (assert True)

        A test that always passes is USELESS.
        The RED gate MUST reject it (test_failed=False → gate FAILED).

        This catches:
        - Hallucinated tests
        - Tests that don't actually test anything
        """
        # The "Evil" test - always passes, tests nothing
        trivial_test = '''
"""Trivial test that always passes."""
import pytest

def test_trivial():
    """This test is useless - it always passes."""
    assert True  # BAD: This will pass without any implementation!
'''

        params = {
            "test_code": trivial_test,
            "capability_name": "fake_capability",
            "timeout_seconds": 10,
        }

        result = await handlers.red_gate(params)

        # The test PASSED without implementation → RED gate should FAIL
        # test_failed=False means the test passed (bad for RED gate)
        print(f"\n{'=' * 60}")
        print("SCENARIO 1: Trivial Test (assert True)")
        print(f"{'=' * 60}")
        print(f"Result: {result}")
        print(f"test_failed: {result.get('test_failed')}")
        print(f"success: {result.get('success')}")

        # RED gate should FAIL (success=False) because test passed
        assert not result.get("test_failed"), "Trivial test should PASS (which means RED gate should detect it)"
        assert not result.get("success"), "RED gate should FAIL when trivial test passes"

        print("✅ RED GATE CORRECTLY REJECTED TRIVIAL TEST!")

    @pytest.mark.asyncio
    async def test_red_gate_accepts_valid_test(self, handlers):
        """
        SCENARIO 2: Valid Test (import fails)

        A test that fails because the module doesn't exist is VALID.
        The RED gate MUST accept it (test_failed=True → gate PASSED).

        This is the correct behavior for TDD:
        - Write test first
        - Test fails (RED)
        - Write implementation
        - Test passes (GREEN)
        """
        # The "Good" test - fails because module doesn't exist
        valid_test = '''
"""Valid test that fails because implementation doesn't exist."""
import pytest

def test_import_nonexistent_module():
    """This test SHOULD fail - the module doesn't exist yet."""
    from nonexistent_capability import nonexistent_function
    assert nonexistent_function() is not None
'''

        params = {
            "test_code": valid_test,
            "capability_name": "nonexistent_capability",
            "timeout_seconds": 10,
        }

        result = await handlers.red_gate(params)

        # The test FAILED (import error) → RED gate should PASS
        # test_failed=True means the test failed (good for RED gate)
        print(f"\n{'=' * 60}")
        print("SCENARIO 2: Valid Test (import fails)")
        print(f"{'=' * 60}")
        print(f"Result: {result}")
        print(f"test_failed: {result.get('test_failed')}")
        print(f"success: {result.get('success')}")

        # RED gate should PASS (success=True) because test failed
        assert result.get("test_failed"), "Valid test should FAIL (module doesn't exist)"
        assert result.get("success"), "RED gate should PASS when valid test fails"

        print("✅ RED GATE CORRECTLY ACCEPTED VALID TEST!")

    @pytest.mark.asyncio
    async def test_red_gate_accepts_assertion_failure(self, handlers):
        """
        SCENARIO 3: Valid Test (assertion fails)

        A test with an assertion that fails is also valid for RED phase.
        """
        # Test with assertion failure
        assertion_test = '''
"""Valid test that fails on assertion."""
import pytest

def test_assertion_failure():
    """This test SHOULD fail - assertion is False."""
    assert False, "This assertion should fail in RED phase"
'''

        params = {
            "test_code": assertion_test,
            "capability_name": "assertion_test",
            "timeout_seconds": 10,
        }

        result = await handlers.red_gate(params)

        print(f"\n{'=' * 60}")
        print("SCENARIO 3: Valid Test (assertion fails)")
        print(f"{'=' * 60}")
        print(f"Result: {result}")
        print(f"test_failed: {result.get('test_failed')}")
        print(f"success: {result.get('success')}")

        # RED gate should PASS because test failed
        assert result.get("test_failed"), "Test with assertion failure should FAIL"
        assert result.get("success"), "RED gate should PASS when assertion fails"

        print("✅ RED GATE CORRECTLY ACCEPTED ASSERTION FAILURE!")


class TestDiamondGreenGate:
    """Tests for the Diamond Protocol's GREEN Gate enforcement."""

    @pytest.fixture
    def handlers(self):
        """Get Diamond handlers instance."""
        from vibe_core.plugins.opus_assistant.events.diamond_handlers import DiamondHandlers

        return DiamondHandlers(workspace=Path.cwd())

    @pytest.mark.asyncio
    async def test_green_gate_passes_with_implementation(self, handlers):
        """
        SCENARIO 4: Implementation makes test pass

        When the implementation exists, the test should pass.
        GREEN gate should ACCEPT this.
        """
        # Simple test
        test_code = '''
"""Test for greeting capability."""
import pytest

def test_greet():
    from greeting import greet
    result = greet("World")
    assert result == "Hello, World!"
'''

        # Simple implementation that makes test pass
        implementation_code = '''
"""Greeting capability."""

def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"
'''

        params = {
            "test_code": test_code,
            "implementation_code": implementation_code,
            "capability_name": "greeting",
            "timeout_seconds": 10,
        }

        result = await handlers.green_gate(params)

        print(f"\n{'=' * 60}")
        print("SCENARIO 4: Implementation makes test pass")
        print(f"{'=' * 60}")
        print(f"Result: {result}")
        print(f"test_passed: {result.get('test_passed')}")
        print(f"success: {result.get('success')}")

        # GREEN gate should PASS because test passed
        assert result.get("test_passed"), "Test should PASS with correct implementation"
        assert result.get("success"), "GREEN gate should PASS when implementation works"

        print("✅ GREEN GATE CORRECTLY ACCEPTED WORKING IMPLEMENTATION!")

    @pytest.mark.asyncio
    async def test_green_gate_fails_with_broken_implementation(self, handlers):
        """
        SCENARIO 5: Broken implementation fails test

        When the implementation is broken, the test should fail.
        GREEN gate should REJECT this.
        """
        # Simple test
        test_code = '''
"""Test for greeting capability."""
import pytest

def test_greet():
    from greeting import greet
    result = greet("World")
    assert result == "Hello, World!"
'''

        # BROKEN implementation that makes test fail
        broken_implementation = '''
"""Greeting capability - BROKEN."""

def greet(name: str) -> str:
    """Return a greeting - but broken!"""
    return f"Goodbye, {name}!"  # WRONG!
'''

        params = {
            "test_code": test_code,
            "implementation_code": broken_implementation,
            "capability_name": "greeting",
            "timeout_seconds": 10,
        }

        result = await handlers.green_gate(params)

        print(f"\n{'=' * 60}")
        print("SCENARIO 5: Broken implementation fails test")
        print(f"{'=' * 60}")
        print(f"Result: {result}")
        print(f"test_passed: {result.get('test_passed')}")
        print(f"success: {result.get('success')}")

        # GREEN gate should FAIL because test failed
        assert not result.get("test_passed"), "Test should FAIL with broken implementation"
        assert not result.get("success"), "GREEN gate should FAIL when implementation is broken"

        print("✅ GREEN GATE CORRECTLY REJECTED BROKEN IMPLEMENTATION!")


if __name__ == "__main__":
    # Run a quick standalone test
    async def run_tests():
        from vibe_core.plugins.opus_assistant.events.diamond_handlers import DiamondHandlers

        handlers = DiamondHandlers(workspace=Path.cwd())

        print("\n" + "=" * 70)
        print("BREAK TEST 2.0: DIAMOND PROTOCOL VALIDATION")
        print("=" * 70 + "\n")

        # Test 1: Trivial test should be rejected
        trivial_test = """
def test_trivial():
    assert True
"""
        result1 = await handlers.red_gate(
            {
                "test_code": trivial_test,
                "capability_name": "trivial",
                "timeout_seconds": 10,
            }
        )

        print(f"Test 1 (Trivial): test_failed={result1.get('test_failed')}, success={result1.get('success')}")
        if not result1.get("success"):
            print("   ✅ RED GATE REJECTED TRIVIAL TEST (CORRECT!)")
        else:
            print("   ❌ RED GATE ACCEPTED TRIVIAL TEST (BUG!)")

        # Test 2: Valid test should be accepted
        valid_test = """
def test_import():
    from nonexistent import func
    assert func()
"""
        result2 = await handlers.red_gate(
            {
                "test_code": valid_test,
                "capability_name": "valid",
                "timeout_seconds": 10,
            }
        )

        print(f"Test 2 (Valid): test_failed={result2.get('test_failed')}, success={result2.get('success')}")
        if result2.get("success"):
            print("   ✅ RED GATE ACCEPTED VALID TEST (CORRECT!)")
        else:
            print("   ❌ RED GATE REJECTED VALID TEST (BUG!)")

        print("\n" + "=" * 70)
        if not result1.get("success") and result2.get("success"):
            print("🎉 BREAK TEST 2.0: ALL TESTS PASSED!")
            print("   The Iron Grip is VERIFIED.")
        else:
            print("💥 BREAK TEST 2.0: TESTS FAILED!")
            print("   The Diamond Protocol has a bug.")
        print("=" * 70 + "\n")

    asyncio.run(run_tests())
