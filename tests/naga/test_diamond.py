"""
NAGA Diamond Protocol Tests - TDD as OUROBOROS.

"Was mich nicht tötet, macht mich stärker."
"Gift zu Medizin."

These tests verify the Diamond Protocol's core logic:
- RED Gate: Test MUST fail without implementation
- GREEN Gate: Test MUST pass with implementation
- Integration with Prahlad and Shuddhi
"""

import pytest

from tests.fractal.fractal_test_framework import FractalTestCase


class TestDiamondGateResult:
    """Test DiamondGateResult data class."""

    def test_red_gate_result(self):
        """RED gate result captures failure correctly."""
        from vibe_core.naga.diamond import DiamondGateResult

        result = DiamondGateResult(
            gate="red",
            passed=True,
            test_failed=True,
            exit_code=1,
            verification_token="RED_test",
        )

        assert result.gate == "red"
        assert result.passed is True
        assert result.test_failed is True

    def test_green_gate_result(self):
        """GREEN gate result captures success correctly."""
        from vibe_core.naga.diamond import DiamondGateResult

        result = DiamondGateResult(
            gate="green",
            passed=True,
            test_passed=True,
            exit_code=0,
            verification_token="GREEN_test",
        )

        assert result.gate == "green"
        assert result.passed is True
        assert result.test_passed is True


class TestDiamondResult:
    """Test DiamondResult data class."""

    def test_complete_result(self):
        """DiamondResult captures full verification chain."""
        from vibe_core.naga.diamond import DiamondGateResult, DiamondResult

        result = DiamondResult(
            error_id="test_123",
            test_code="def test_foo(): pass",
            red_gate=DiamondGateResult(gate="red", passed=True, test_failed=True),
            green_gate=DiamondGateResult(gate="green", passed=True, test_passed=True),
            remedy_applied=True,
            remedy_id="silent_except",
            auto_healed=False,
        )

        assert result.error_id == "test_123"
        assert result.red_gate.passed is True
        assert result.green_gate.passed is True
        assert result.remedy_applied is True


class TestNagaDiamondProtocol:
    """Test NagaDiamondProtocol core logic."""

    def test_init_defaults(self):
        """Protocol initializes with safe defaults."""
        from vibe_core.naga.diamond import NagaDiamondProtocol

        diamond = NagaDiamondProtocol()

        assert diamond._auto_heal is False  # Safe default
        assert diamond._timeout == 30

    def test_init_with_auto_heal(self):
        """Protocol can be configured for auto-heal."""
        from vibe_core.naga.diamond import NagaDiamondProtocol

        diamond = NagaDiamondProtocol(auto_heal=True)

        assert diamond._auto_heal is True

    def test_remedy_matches_error_simple(self):
        """Remedy matching works for simple cases."""
        from vibe_core.naga.diamond import NagaDiamondProtocol
        from vibe_core.naga.services.prahlad import ErrorEvent

        diamond = NagaDiamondProtocol()

        # Create test error
        error = ErrorEvent(
            error_type="TimeoutError",
            message="Process timed out",
            component_id="subprocess_handler",
            context={},
        )

        # Should match subprocess_timeout remedy
        assert diamond._remedy_matches_error("subprocess_timeout", error) is True

        # Should not match unrelated remedy
        assert diamond._remedy_matches_error("get_instance", error) is False

    def test_remedy_matches_error_patterns(self):
        """Remedy matching uses pattern keywords."""
        from vibe_core.naga.diamond import NagaDiamondProtocol
        from vibe_core.naga.services.prahlad import ErrorEvent

        diamond = NagaDiamondProtocol()

        # File-related error
        file_error = ErrorEvent(
            error_type="IOError",
            message="Cannot write to file",
            component_id="file_writer",
            context={},
        )
        assert diamond._remedy_matches_error("unsafe_io_write", file_error) is True

        # Path-related error
        path_error = ErrorEvent(
            error_type="PathNotFoundError",
            message="Directory does not exist",
            component_id="path_resolver",
            context={},
        )
        assert diamond._remedy_matches_error("path_scanning", path_error) is True

    def test_generate_test_from_error(self):
        """Test generation creates valid test code."""
        from vibe_core.naga.diamond import NagaDiamondProtocol
        from vibe_core.naga.services.prahlad import ErrorEvent

        diamond = NagaDiamondProtocol()

        error = ErrorEvent(
            error_type="ValidationError",
            message="Invalid input",
            component_id="validator",
            context={"input": "bad"},
        )

        test_code = diamond._generate_test_from_error(error)

        # Should contain key elements
        assert "ValidationError" in test_code
        assert "validator" in test_code
        assert "def test_" in test_code
        assert "DIAMOND PROTOCOL" in test_code


class TestMockSandbox:
    """Test mock sandbox fallback."""

    @pytest.mark.asyncio
    async def test_mock_sandbox_red_gate(self):
        """Mock sandbox fails without code (RED gate passes)."""
        from vibe_core.naga.diamond import MockSandbox

        sandbox = MockSandbox()
        result = await sandbox.run_test(
            code={},  # No implementation
            test_code="def test_foo(): assert False",
            test_filename="test_foo.py",
        )

        assert result.exit_code == 1  # Failed = good for RED gate

    @pytest.mark.asyncio
    async def test_mock_sandbox_green_gate(self):
        """Mock sandbox passes with code (GREEN gate passes)."""
        from vibe_core.naga.diamond import MockSandbox

        sandbox = MockSandbox()
        result = await sandbox.run_test(
            code={"foo.py": "def foo(): pass"},  # Has implementation
            test_code="def test_foo(): assert True",
            test_filename="test_foo.py",
        )

        assert result.exit_code == 0  # Passed = good for GREEN gate


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""

    @pytest.mark.asyncio
    async def test_verify_test_is_real(self):
        """verify_test_is_real returns True for real tests."""
        from vibe_core.naga.diamond import verify_test_is_real

        # This test would fail without implementation
        test_code = """
def test_nonexistent():
    from nonexistent_module import foo
    assert foo() == "bar"
"""
        # Should pass RED gate (test fails = real test)
        is_real = await verify_test_is_real(test_code, "nonexistent")
        assert is_real is True

    @pytest.mark.asyncio
    async def test_verify_remedy_works(self):
        """verify_remedy_works returns True when implementation passes."""
        from vibe_core.naga.diamond import verify_remedy_works

        test_code = """
def test_handler():
    from handler import handle
    result = handle({})
    assert result is not None
"""
        implementation = """
def handle(context):
    return {"success": True}
"""
        # Should pass GREEN gate
        works = await verify_remedy_works(test_code, implementation, "handler")
        assert works is True


class TestTDDOuroboros:
    """Test the complete TDD OUROBOROS cycle."""

    @pytest.mark.asyncio
    async def test_full_cycle_mock(self):
        """
        Full Diamond Protocol cycle with mock sandbox.

        Error → Test (RED) → Remedy → Test (GREEN) → Healed
        """
        from vibe_core.naga.diamond import NagaDiamondProtocol
        from vibe_core.naga.services.prahlad import ErrorEvent

        diamond = NagaDiamondProtocol(auto_heal=False)

        error = ErrorEvent(
            error_type="TestError",
            message="Test failure",
            component_id="test_component",
            context={"reason": "test"},
        )

        # Process through Diamond Protocol
        result = await diamond.process_error(error, try_remedy=False)

        # Should have error_id and test_code
        assert result.error_id is not None
        assert result.test_code is not None

        # RED gate should pass (test fails without implementation)
        assert result.red_gate is not None
        assert result.red_gate.passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
