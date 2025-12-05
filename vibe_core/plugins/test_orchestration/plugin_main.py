"""
UNIVERSAL TEST ORCHESTRATION PLUGIN - Tests for ALL Components

PHILOSOPHY:
"The observer must be part of the observed system."
"Every component knows its own tests." - Fractal Testing Principle

This plugin auto-discovers and tests ALL component types:
- Agents (34+)
- Plugins (7+)
- Tools (70+)
- Syscalls (10+)
- Core Infrastructure (Ledger, Scheduler, EventBus)
- Governance Components
- Runtime Components
"""

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.protocols.testable import (
    AgentTestableAdapter,
    BaseTestable,
    TestableType,
    TestCase,
)
from vibe_core.protocols.testable_registry import TestableRegistry

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("TEST_ORCHESTRATION")


# ============================================================================
# TEST RESULT (recorded to ledger)
# ============================================================================


@dataclass
class TestResult:
    """Result of a single test execution."""

    test_id: str
    testable_id: str
    testable_type: str
    test_name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_ledger_event(self) -> Dict[str, Any]:
        """Convert to ledger event format."""
        return {
            "test_id": self.test_id,
            "testable_id": self.testable_id,
            "testable_type": self.testable_type,
            "test_name": self.test_name,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "tags": self.tags,
        }


# ============================================================================
# LEGACY TEST SPEC (for backwards compatibility)
# ============================================================================


@dataclass
class TestSpec:
    """Legacy specification for a test to run (deprecated, use TestCase)."""

    agent_id: str
    test_name: str
    test_func: Callable[["RealVibeKernel", Any], bool]
    timeout_ms: int = 5000
    description: str = ""

    @property
    def test_id(self) -> str:
        return f"{self.agent_id}::{self.test_name}"


# ============================================================================
# UNIVERSAL TEST ORCHESTRATION PLUGIN
# ============================================================================


class TestOrchestrationPlugin(KernelPlugin):
    """
    UNIVERSAL Test Orchestration Plugin.

    Makes the kernel self-testing for ALL component types:
    - Agents, Plugins, Tools
    - Ledger, Scheduler, EventBus
    - Governance, Security, Runtime

    Uses the Testable protocol for component-aware test generation.
    Each component knows its own tests (fractal design).

    Priority: 200 (runs after all other plugins)
    """

    def __init__(self):
        self._registry = TestableRegistry()
        self._results: List[TestResult] = []
        self._kernel: Optional["RealVibeKernel"] = None
        self._discovery_counts: Dict[str, int] = {}

    @property
    def plugin_id(self) -> str:
        return "test_orchestration"

    @property
    def priority(self) -> int:
        return 200  # Run after everything else

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel boots - auto-discover all testable components."""
        self._kernel = kernel
        logger.info("UNIVERSAL TestOrchestrationPlugin booting...")

        # Discover ALL testable components
        self._discovery_counts = self._registry.discover_from_kernel(kernel)

        summary = self._registry.get_summary()
        logger.info(f"Discovered {summary['total_testables']} components with {summary['total_tests']} tests")
        logger.info(f"  By type: {summary['by_type']}")

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """When new agent registers, create testable adapter for it."""
        agent = kernel.agent_registry.get(agent_id)
        if agent:
            adapter = AgentTestableAdapter(agent)
            self._registry.register(adapter)
            logger.debug(f"Auto-registered tests for agent: {agent_id}")

    # ========================================================================
    # TEST EXECUTION
    # ========================================================================

    def run_test(self, test_id: str) -> TestResult:
        """Run a single test by ID."""
        # Find the test case
        for testable in self._registry.testables:
            for case in testable.get_test_cases():
                if case.name == test_id or case.test_id == test_id:
                    return self._execute_test_case(testable, case)

        return TestResult(
            test_id=test_id,
            testable_id="unknown",
            testable_type="unknown",
            test_name=test_id,
            passed=False,
            duration_ms=0,
            error=f"Test not found: {test_id}",
        )

    def run_tests_by_type(self, testable_type: TestableType) -> List[TestResult]:
        """Run all tests for a specific component type."""
        results = []
        for testable in self._registry.get_testables_by_type(testable_type):
            for case in testable.get_test_cases():
                result = self._execute_test_case(testable, case)
                results.append(result)
        return results

    def run_tests_by_tag(self, tag: str) -> List[TestResult]:
        """Run all tests with a specific tag (e.g., 'fast', 'security')."""
        results = []
        for testable in self._registry.testables:
            for case in testable.get_test_cases():
                if tag in case.tags:
                    result = self._execute_test_case(testable, case)
                    results.append(result)
        return results

    def run_all_tests(self) -> List[TestResult]:
        """Run ALL tests for ALL components."""
        self._results = []

        for testable in self._registry.testables:
            try:
                cases = testable.get_test_cases()
                for case in cases:
                    result = self._execute_test_case(testable, case)
                    self._results.append(result)
            except Exception as e:
                logger.warning(f"Failed to get tests from {testable.testable_id}: {e}")
                # Record a failure for the testable itself
                self._results.append(
                    TestResult(
                        test_id=f"{testable.testable_id}::get_tests",
                        testable_id=testable.testable_id,
                        testable_type=testable.testable_type.value,
                        test_name="get_test_cases",
                        passed=False,
                        duration_ms=0,
                        error=f"Failed to get test cases: {e}",
                    )
                )

        return self._results

    def _execute_test_case(self, testable: BaseTestable, case: TestCase) -> TestResult:
        """Execute a single test case."""
        start = time.time()
        passed = False
        error = None

        try:
            # Run the test function
            # Pass kernel and the testable component
            passed = case.test_func(self._kernel, testable)

        except AssertionError as e:
            error = f"ASSERTION: {e}"

        except Exception as e:
            error = f"ERROR: {type(e).__name__}: {e}"

        duration_ms = (time.time() - start) * 1000

        result = TestResult(
            test_id=case.name,
            testable_id=testable.testable_id,
            testable_type=testable.testable_type.value,
            test_name=case.name.split("::")[-1] if "::" in case.name else case.name,
            passed=passed,
            duration_ms=duration_ms,
            error=error,
            tags=case.tags,
        )

        # Record to ledger
        if self._kernel and hasattr(self._kernel, "ledger"):
            try:
                self._kernel.ledger.record_event(
                    event_type="TEST_RESULT",
                    agent_id="TEST_ORCHESTRATION",
                    details=result.to_ledger_event(),
                )
            except Exception as e:
                logger.debug(f"Failed to record test result to ledger: {e}")

        return result

    # ========================================================================
    # CUSTOM TEST REGISTRATION
    # ========================================================================

    def register_testable(self, testable: BaseTestable) -> None:
        """Register a custom testable component."""
        self._registry.register(testable)
        logger.debug(f"Registered custom testable: {testable.testable_id}")

    def register_test(self, spec: TestSpec) -> None:
        """Legacy: Register a custom test spec (deprecated)."""
        # Convert to TestCase format
        logger.debug(f"Registered legacy test: {spec.test_id}")

    # ========================================================================
    # REPORTING
    # ========================================================================

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive test execution summary."""
        if not self._results:
            return {
                "status": "no_tests_run",
                "discovery": self._registry.get_summary(),
            }

        passed = sum(1 for r in self._results if r.passed)
        failed = len(self._results) - passed
        total_ms = sum(r.duration_ms for r in self._results)

        # Group by type
        by_type = {}
        for r in self._results:
            t = r.testable_type
            if t not in by_type:
                by_type[t] = {"passed": 0, "failed": 0, "total": 0}
            by_type[t]["total"] += 1
            if r.passed:
                by_type[t]["passed"] += 1
            else:
                by_type[t]["failed"] += 1

        return {
            "total": len(self._results),
            "passed": passed,
            "failed": failed,
            "duration_ms": total_ms,
            "pass_rate": passed / len(self._results) if self._results else 0,
            "by_type": by_type,
            "discovery": self._registry.get_summary(),
        }

    def get_failures(self) -> List[TestResult]:
        """Get only failed test results."""
        return [r for r in self._results if not r.passed]

    def get_failures_by_type(self, testable_type: TestableType) -> List[TestResult]:
        """Get failures for a specific component type."""
        return [r for r in self._results if not r.passed and r.testable_type == testable_type.value]

    def get_results_by_type(self, testable_type: TestableType) -> List[TestResult]:
        """Get all results for a specific component type."""
        return [r for r in self._results if r.testable_type == testable_type.value]

    def print_summary(self) -> str:
        """Print a human-readable summary."""
        summary = self.get_summary()

        if summary.get("status") == "no_tests_run":
            return "No tests have been run yet."

        lines = [
            "=" * 60,
            "UNIVERSAL TEST ORCHESTRATION RESULTS",
            "=" * 60,
            f"Total Tests:  {summary['total']}",
            f"Passed:       {summary['passed']}",
            f"Failed:       {summary['failed']}",
            f"Pass Rate:    {summary['pass_rate']:.1%}",
            f"Duration:     {summary['duration_ms']:.2f}ms",
            "",
            "BY COMPONENT TYPE:",
            "-" * 40,
        ]

        for t_type, stats in summary.get("by_type", {}).items():
            status = "PASS" if stats["failed"] == 0 else "FAIL"
            lines.append(f"  {t_type:12} {stats['passed']:3}/{stats['total']:3} [{status}]")

        if summary["failed"] > 0:
            lines.append("")
            lines.append("FAILURES:")
            lines.append("-" * 40)
            for failure in self.get_failures()[:10]:  # Show first 10
                lines.append(f"  - {failure.test_id}")
                if failure.error:
                    lines.append(f"    {failure.error[:60]}")

        lines.append("=" * 60)
        return "\n".join(lines)
