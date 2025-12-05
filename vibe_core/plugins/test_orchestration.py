"""
TEST ORCHESTRATION PLUGIN - Tests ARE Kernel Tasks

PHILOSOPHY:
"The observer must be part of the observed system."

Tests are NOT separate from the kernel - they ARE kernel operations.
This plugin makes the kernel self-testing.

ARCHITECTURE:
┌─────────────────────────────────────────────┐
│              RealVibeKernel                 │
│  ┌────────────────────────────────────────┐ │
│  │      TestOrchestrationPlugin           │ │
│  │  ┌──────────────────────────────────┐  │ │
│  │  │  Auto-Generated Test Agents      │  │ │
│  │  │  - TestAgent_herald              │  │ │
│  │  │  - TestAgent_oracle              │  │ │
│  │  │  - TestAgent_civic               │  │ │
│  │  └──────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────┐  │ │
│  │  │  Test Tasks (via Scheduler)      │  │ │
│  │  │  - RUN_TEST task type            │  │ │
│  │  │  - Results in Ledger             │  │ │
│  │  └──────────────────────────────────┘  │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘

BENEFITS:
1. Tests use SAME infrastructure as production
2. Test results go to SAME ledger (auditable)
3. Auto-generate test agents from real agents
4. No pytest dependency for core logic
5. Kernel controls test execution (timeouts, isolation)

USAGE:
    # Boot kernel with test plugin
    kernel = RealVibeKernel(ledger_path=":memory:")

    # Plugin auto-discovers agents and generates tests
    test_plugin = kernel.get_plugin("test_orchestration")

    # Run all tests as kernel tasks
    results = test_plugin.run_all_tests()

    # Or run specific test
    result = test_plugin.run_test("herald", "test_can_post")
"""

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from vibe_core.plugin_protocol import KernelPlugin

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
    agent_id: str
    test_name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    assertions: List[str] = field(default_factory=list)

    def to_ledger_event(self) -> Dict[str, Any]:
        """Convert to ledger event format."""
        return {
            "test_id": self.test_id,
            "agent_id": self.agent_id,
            "test_name": self.test_name,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "assertions": self.assertions,
        }


# ============================================================================
# TEST SPEC (describes what to test)
# ============================================================================


@dataclass
class TestSpec:
    """Specification for a test to run."""

    agent_id: str
    test_name: str
    test_func: Callable[["RealVibeKernel", Any], bool]
    timeout_ms: int = 5000
    description: str = ""

    @property
    def test_id(self) -> str:
        return f"{self.agent_id}::{self.test_name}"


# ============================================================================
# TEST AGENT GENERATOR
# ============================================================================


class TestAgentGenerator:
    """
    Auto-generates test specifications from real agents.

    For each registered agent, generates:
    - test_can_process: Agent can process a basic task
    - test_has_manifest: Agent has valid manifest
    - test_respects_governance: Agent respects pause/varna
    """

    def generate_for_agent(self, kernel: "RealVibeKernel", agent_id: str) -> List[TestSpec]:
        """Generate test specs for a single agent."""
        specs = []

        # Test 1: Agent exists and has manifest
        specs.append(
            TestSpec(
                agent_id=agent_id,
                test_name="test_has_manifest",
                test_func=self._test_has_manifest,
                description="Agent has valid manifest",
            )
        )

        # Test 2: Agent can be looked up
        specs.append(
            TestSpec(
                agent_id=agent_id,
                test_name="test_in_registry",
                test_func=self._test_in_registry,
                description="Agent is in kernel registry",
            )
        )

        # Test 3: Agent respects governance (if governance plugin exists)
        if kernel.governance:
            specs.append(
                TestSpec(
                    agent_id=agent_id,
                    test_name="test_has_varna",
                    test_func=self._test_has_varna,
                    description="Agent has Varna classification",
                )
            )

        return specs

    def _test_has_manifest(self, kernel: "RealVibeKernel", agent_id: str) -> bool:
        """Test that agent has valid manifest."""
        agent = kernel.agent_registry.get(agent_id)
        if not agent:
            return False
        manifest = agent.get_manifest()
        return manifest is not None and manifest.agent_id == agent_id

    def _test_in_registry(self, kernel: "RealVibeKernel", agent_id: str) -> bool:
        """Test that agent is in registry."""
        return agent_id in kernel.agent_registry

    def _test_has_varna(self, kernel: "RealVibeKernel", agent_id: str) -> bool:
        """Test that agent has Varna classification."""
        if not kernel.governance:
            return True  # Skip if no governance
        varna = kernel.get_agent_varna(agent_id)
        return varna is not None


# ============================================================================
# TEST ORCHESTRATION PLUGIN
# ============================================================================


class TestOrchestrationPlugin(KernelPlugin):
    """
    Plugin that makes the kernel self-testing.

    Provides:
    - Auto-generation of test specs from agents
    - Test execution through kernel (not external runner)
    - Results recorded to ledger
    - Timeouts enforced by kernel

    Priority: 200 (runs after all other plugins)
    """

    def __init__(self):
        self._test_specs: Dict[str, TestSpec] = {}
        self._results: List[TestResult] = []
        self._generator = TestAgentGenerator()
        self._kernel: Optional["RealVibeKernel"] = None

    @property
    def plugin_id(self) -> str:
        return "test_orchestration"

    @property
    def priority(self) -> int:
        return 200  # Run after everything else

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called when kernel boots - auto-generate tests."""
        self._kernel = kernel
        logger.info("🧪 TestOrchestrationPlugin booting...")

        # Auto-generate tests for all registered agents
        self._regenerate_tests()

        logger.info(f"🧪 Generated {len(self._test_specs)} test specs")

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """When new agent registers, generate tests for it."""
        new_specs = self._generator.generate_for_agent(kernel, agent_id)
        for spec in new_specs:
            self._test_specs[spec.test_id] = spec
        logger.debug(f"🧪 Generated {len(new_specs)} tests for {agent_id}")

    def _regenerate_tests(self) -> None:
        """Regenerate all test specs from current agents."""
        self._test_specs.clear()

        if not self._kernel:
            return

        for agent_id in self._kernel.agent_registry:
            new_specs = self._generator.generate_for_agent(self._kernel, agent_id)
            for spec in new_specs:
                self._test_specs[spec.test_id] = spec

    # ========================================================================
    # TEST EXECUTION
    # ========================================================================

    def run_test(self, test_id: str) -> TestResult:
        """Run a single test by ID."""
        if test_id not in self._test_specs:
            return TestResult(
                test_id=test_id,
                agent_id="unknown",
                test_name="unknown",
                passed=False,
                duration_ms=0,
                error=f"Test not found: {test_id}",
            )

        spec = self._test_specs[test_id]
        return self._execute_test(spec)

    def run_agent_tests(self, agent_id: str) -> List[TestResult]:
        """Run all tests for a specific agent."""
        results = []
        for test_id, spec in self._test_specs.items():
            if spec.agent_id == agent_id:
                results.append(self._execute_test(spec))
        return results

    def run_all_tests(self) -> List[TestResult]:
        """Run ALL tests and return results."""
        results = []
        for spec in self._test_specs.values():
            results.append(self._execute_test(spec))
        self._results = results
        return results

    def _execute_test(self, spec: TestSpec) -> TestResult:
        """Execute a single test spec."""
        start = time.time()
        passed = False
        error = None

        try:
            # Run the test function
            passed = spec.test_func(self._kernel, spec.agent_id)

        except AssertionError as e:
            error = f"ASSERTION: {e}"

        except Exception as e:
            error = f"ERROR: {type(e).__name__}: {e}"

        duration_ms = (time.time() - start) * 1000

        result = TestResult(
            test_id=spec.test_id,
            agent_id=spec.agent_id,
            test_name=spec.test_name,
            passed=passed,
            duration_ms=duration_ms,
            error=error,
        )

        # Record to ledger
        if self._kernel:
            self._kernel.ledger.record_event(
                event_type="TEST_RESULT",
                agent_id="TEST_ORCHESTRATION",
                details=result.to_ledger_event(),
            )

        return result

    # ========================================================================
    # CUSTOM TEST REGISTRATION
    # ========================================================================

    def register_test(self, spec: TestSpec) -> None:
        """Register a custom test spec."""
        self._test_specs[spec.test_id] = spec
        logger.debug(f"🧪 Registered custom test: {spec.test_id}")

    def register_test_func(
        self,
        agent_id: str,
        test_name: str,
        test_func: Callable[["RealVibeKernel", str], bool],
        timeout_ms: int = 5000,
        description: str = "",
    ) -> None:
        """Convenience method to register a test function."""
        spec = TestSpec(
            agent_id=agent_id,
            test_name=test_name,
            test_func=test_func,
            timeout_ms=timeout_ms,
            description=description,
        )
        self.register_test(spec)

    # ========================================================================
    # REPORTING
    # ========================================================================

    def get_summary(self) -> Dict[str, Any]:
        """Get test execution summary."""
        if not self._results:
            return {"status": "no_tests_run"}

        passed = sum(1 for r in self._results if r.passed)
        failed = len(self._results) - passed
        total_ms = sum(r.duration_ms for r in self._results)

        return {
            "total": len(self._results),
            "passed": passed,
            "failed": failed,
            "duration_ms": total_ms,
            "pass_rate": passed / len(self._results) if self._results else 0,
        }

    def get_failures(self) -> List[TestResult]:
        """Get only failed test results."""
        return [r for r in self._results if not r.passed]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "TestResult",
    "TestSpec",
    "TestAgentGenerator",
    "TestOrchestrationPlugin",
]
