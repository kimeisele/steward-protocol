"""
DIAMOND PROTOCOL HANDLERS - The Iron Grip
=========================================
OPUS-037: TDD Enforcement for Capability Genesis

"RED before GREEN. Test before Code. No exceptions." - DIAMOND LAW

This module implements the enforcement layer for the Diamond Protocol:

1. diamond_generate_test: Generate test BEFORE implementation
2. diamond_red_gate: Verify test FAILS (proves non-trivial)
3. diamond_green_gate: Verify test PASSES (proves implementation works)

Philosophy:
    A law without enforcement is a wish.
    These handlers are the "police" of TDD.
    The system cannot physically cheat the process.

Architecture:
    ┌─────────────────────────────────────────────────────────────────┐
    │  capability_genesis.yaml (The Law)                             │
    │    target: "opus.diamond_red_gate"                             │
    │                      │                                          │
    │                      ▼                                          │
    │  diamond_handlers.py (The Enforcement)                         │
    │    DiamondHandlers.red_gate() → Sandbox.run_test()             │
    │                      │                                          │
    │                      ▼                                          │
    │  SandboxResult.exit_code == 1? → SUCCESS (RED verified)        │
    │  SandboxResult.exit_code == 0? → FAILURE (trivial test!)       │
    └─────────────────────────────────────────────────────────────────┘

The Diamond is forged under pressure.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x9e377172"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DIAMOND.Handlers")


@dataclass
class DiamondResult:
    """Result from a Diamond Protocol gate."""

    success: bool
    gate: str  # "red" or "green"
    test_failed: bool = False  # For RED gate
    test_passed: bool = False  # For GREEN gate
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    verification_token: Optional[str] = None  # Proof of gate passage

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for circuit consumption."""
        return {
            "success": self.success,
            "gate": self.gate,
            "test_failed": self.test_failed,
            "test_passed": self.test_passed,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "verification_token": self.verification_token,
        }


class DiamondHandlers:
    """
    The Iron Grip - TDD Enforcement Handlers.

    These handlers implement the Diamond Protocol's enforcement layer.
    They integrate with the existing Sandbox infrastructure from VIDYA.

    The key insight: RED gate inverts the success condition.
    - Normal testing: pass = good, fail = bad
    - RED gate: pass = BAD (trivial test), fail = GOOD (real test)
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize Diamond Handlers.

        Args:
            workspace: Workspace root for test execution
        """
        self._workspace = workspace or Path.cwd()

    async def generate_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate test code for a capability BEFORE implementation.

        This is the first step of TDD - write the test first.

        Target: opus.diamond_generate_test

        Params:
            capability_name: str - Name of the capability
            capability_type: str - Type (syscall, analyzer, formatter)
            description: str - What the capability should do
            syscall_name: str - The syscall name (e.g., HELLO_WORLD)
            parameters: List[Dict] - Parameter specifications
            research_insights: str - Insights from research phase

        Returns:
            Dict with generated test code
        """
        capability_name = params.get("capability_name", "unknown")
        capability_type = params.get("capability_type", "syscall")
        description = params.get("description", "")
        syscall_name = params.get("syscall_name", capability_name.upper())
        parameters = params.get("parameters", [])
        research_insights = params.get("research_insights", "")

        logger.info(f"💎 DIAMOND: Generating test for {capability_name}")

        try:
            # Generate test code based on capability spec
            test_code = self._generate_test_code(
                capability_name=capability_name,
                capability_type=capability_type,
                description=description,
                syscall_name=syscall_name,
                parameters=parameters,
                research_insights=research_insights,
            )

            return {
                "success": True,
                "test_code": test_code,
                "test_filename": f"test_{capability_name}.py",
                "capability_name": capability_name,
            }

        except Exception as e:
            logger.error(f"💎❌ Test generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _generate_test_code(
        self,
        capability_name: str,
        capability_type: str,
        description: str,
        syscall_name: str,
        parameters: List[Dict],
        research_insights: str,
    ) -> str:
        """
        Generate pytest-compatible test code.

        The test is designed to:
        1. Import the capability (will fail in RED phase - module doesn't exist)
        2. Test the capability's behavior
        3. Validate the output matches expectations

        Important: The test MUST fail when the implementation doesn't exist.
        This proves the test is not trivially true.
        """
        # Build parameter signature
        param_args = []
        param_values = []
        for p in parameters:
            name = p.get("name", "arg")
            ptype = p.get("type", "str")
            default = p.get("default")
            if default is not None:
                param_values.append(f'"{default}"' if ptype == "str" else str(default))
            else:
                # Use sensible test defaults
                if ptype == "str":
                    param_values.append('"test_value"')
                elif ptype == "int":
                    param_values.append("42")
                elif ptype == "bool":
                    param_values.append("True")
                else:
                    param_values.append("None")
            param_args.append(name)

        call_args = ", ".join(param_values) if param_values else ""

        # Generate test based on type
        if capability_type == "syscall":
            test_code = f'''"""
Test for {capability_name} capability.

DIAMOND PROTOCOL: This test was generated BEFORE the implementation.
It MUST fail in RED phase (proves test is non-trivial).
It MUST pass in GREEN phase (proves implementation works).

Description: {description}
"""
import pytest


class Test{capability_name.title().replace("_", "")}:
    """Tests for {syscall_name} syscall."""

    def test_module_exists(self):
        """Verify the capability module can be imported."""
        # This import MUST fail in RED phase (module doesn't exist yet)
        from {capability_name} import {capability_name}
        assert {capability_name} is not None, "Capability should be importable"

    def test_callable(self):
        """Verify the capability is callable."""
        from {capability_name} import {capability_name}
        assert callable({capability_name}), "Capability should be callable"

    def test_returns_result(self):
        """Verify the capability returns a result."""
        from {capability_name} import {capability_name}
        result = {capability_name}({call_args})
        assert result is not None, "Capability should return a result"

    def test_result_has_success_field(self):
        """Verify the result has a success indicator."""
        from {capability_name} import {capability_name}
        result = {capability_name}({call_args})
        # Result should be a dict with 'success' key or a value
        if isinstance(result, dict):
            assert "success" in result or "result" in result or "output" in result
        else:
            # Non-dict results are acceptable (simple return values)
            assert result is not None
'''

        elif capability_type == "analyzer":
            test_code = f'''"""
Test for {capability_name} analyzer.

DIAMOND PROTOCOL: This test was generated BEFORE the implementation.
"""
import pytest


class Test{capability_name.title().replace("_", "")}Analyzer:
    """Tests for {capability_name} analyzer."""

    def test_module_exists(self):
        """Verify the analyzer module can be imported."""
        from {capability_name} import {capability_name.title().replace("_", "")}Analyzer
        assert {capability_name.title().replace("_", "")}Analyzer is not None

    def test_has_analyze_method(self):
        """Verify the analyzer has an analyze method."""
        from {capability_name} import {capability_name.title().replace("_", "")}Analyzer
        analyzer = {capability_name.title().replace("_", "")}Analyzer()
        assert hasattr(analyzer, "analyze"), "Analyzer should have analyze method"

    def test_analyze_returns_list(self):
        """Verify analyze returns a list of findings."""
        from {capability_name} import {capability_name.title().replace("_", "")}Analyzer
        analyzer = {capability_name.title().replace("_", "")}Analyzer()
        result = analyzer.analyze({{}})  # Empty context
        assert isinstance(result, list), "analyze() should return a list"
'''

        else:
            # Generic test for other types
            test_code = f'''"""
Test for {capability_name} capability.

DIAMOND PROTOCOL: This test was generated BEFORE the implementation.
"""
import pytest


class Test{capability_name.title().replace("_", "")}:
    """Tests for {capability_name}."""

    def test_module_exists(self):
        """Verify the module can be imported."""
        import {capability_name}
        assert {capability_name} is not None

    def test_has_main_function(self):
        """Verify the module has a main entry point."""
        from {capability_name} import {capability_name}
        assert callable({capability_name})
'''

        return test_code

    async def red_gate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        RED Gate - Verify test FAILS without implementation.

        This is the critical innovation of the Diamond Protocol:
        - Normal testing: pass = success
        - RED gate: FAIL = success (proves test is real)

        If the test passes without implementation, it means either:
        1. The test is trivially true (bad test)
        2. The capability already exists (no work needed)

        Target: opus.diamond_red_gate

        Params:
            test_code: str - The generated test code
            capability_name: str - Name of the capability
            timeout_seconds: int - Timeout for test execution

        Returns:
            Dict with test_failed: bool (True = RED gate passed)
        """
        test_code = params.get("test_code", "")
        capability_name = params.get("capability_name", "unknown")
        timeout_seconds = params.get("timeout_seconds", 30)

        logger.info(f"💎🔴 RED GATE: Testing {capability_name} (expecting FAILURE)")

        try:
            from vibe_core.plugins.opus_assistant.vidya.sandbox import Sandbox

            sandbox = Sandbox(
                timeout_seconds=int(timeout_seconds),
                workspace=self._workspace,
            )

            # Run test WITHOUT implementation (empty code dict)
            # The test SHOULD fail because the module doesn't exist
            result = await sandbox.run_test(
                code={},  # No implementation yet!
                test_code=test_code,
                test_filename=f"test_{capability_name}.py",
            )

            # INVERTED LOGIC: Failure is success for RED gate
            test_failed = result.exit_code != 0

            if test_failed:
                logger.info(f"💎✅ RED GATE PASSED: Test failed as expected for {capability_name}")
                verification_token = f"RED_VERIFIED_{capability_name}_{result.exit_code}"
            else:
                logger.warning(f"💎🚫 RED GATE VIOLATED: Test passed without implementation for {capability_name}")
                verification_token = None

            return DiamondResult(
                success=test_failed,  # Inverted!
                gate="red",
                test_failed=test_failed,
                stdout=result.stdout,
                stderr=result.stderr,
                verification_token=verification_token,
                error=None if test_failed else "Test passed without implementation - trivially true test",
            ).to_dict()

        except Exception as e:
            logger.error(f"💎❌ RED GATE ERROR: {e}")
            return DiamondResult(
                success=False,
                gate="red",
                test_failed=False,
                error=str(e),
            ).to_dict()

    async def green_gate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        GREEN Gate - Verify test PASSES with implementation.

        The test that failed in RED phase MUST now pass.
        This proves the implementation actually works.

        Target: opus.diamond_green_gate

        Params:
            test_code: str - The test code (same as RED phase)
            implementation_code: str - The generated implementation
            capability_name: str - Name of the capability
            timeout_seconds: int - Timeout for test execution

        Returns:
            Dict with test_passed: bool (True = GREEN gate passed)
        """
        test_code = params.get("test_code", "")
        implementation_code = params.get("implementation_code", "")
        capability_name = params.get("capability_name", "unknown")
        timeout_seconds = params.get("timeout_seconds", 30)

        logger.info(f"💎🟢 GREEN GATE: Testing {capability_name} (expecting SUCCESS)")

        try:
            from vibe_core.plugins.opus_assistant.vidya.sandbox import Sandbox

            sandbox = Sandbox(
                timeout_seconds=int(timeout_seconds),
                workspace=self._workspace,
            )

            # Run test WITH implementation
            result = await sandbox.run_test(
                code={f"{capability_name}.py": implementation_code},
                test_code=test_code,
                test_filename=f"test_{capability_name}.py",
            )

            # NORMAL LOGIC: Pass is success for GREEN gate
            test_passed = result.exit_code == 0

            if test_passed:
                logger.info(f"💎✅ GREEN GATE PASSED: Test passed for {capability_name}")
                verification_token = f"GREEN_VERIFIED_{capability_name}_SUCCESS"
            else:
                logger.warning(f"💎❌ GREEN GATE FAILED: Test still fails for {capability_name}")
                verification_token = None

            return DiamondResult(
                success=test_passed,
                gate="green",
                test_passed=test_passed,
                stdout=result.stdout,
                stderr=result.stderr,
                verification_token=verification_token,
                error=None if test_passed else f"Implementation failed tests: {result.stderr[:500]}",
            ).to_dict()

        except Exception as e:
            logger.error(f"💎❌ GREEN GATE ERROR: {e}")
            return DiamondResult(
                success=False,
                gate="green",
                test_passed=False,
                error=str(e),
            ).to_dict()


# Singleton instance for kernel integration
_diamond_handlers: Optional[DiamondHandlers] = None


def get_diamond_handlers(workspace: Optional[Path] = None) -> DiamondHandlers:
    """Get or create the singleton DiamondHandlers instance."""
    global _diamond_handlers
    if _diamond_handlers is None:
        _diamond_handlers = DiamondHandlers(workspace=workspace)
    return _diamond_handlers
