"""
OPUS-059: PRAMANA (The Valid Proof) - TestCortex

This is the sensory-motor interface for MANAS to execute tests.
MANAS can now validate its own environment through the test system.

SECURITY MODEL:
- SAFE operations: run_smoke_test, get_test_summary, run_pytest (read-only/validation)
- REQUIRES_APPROVAL: Running playbooks, full test suites
- All test executions are recorded to the core ledger (VAJRA binding)

"The system that cannot test itself cannot trust itself."
"""

import hashlib
import logging
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("MANAS.Cortex.Test")


class TestScope(Enum):
    """Scope classification for test operations."""

    SMOKE = "smoke"  # Quick sanity check - auto-execute
    UNIT = "unit"  # Unit tests - auto-execute
    INTEGRATION = "integration"  # Requires approval
    FULL = "full"  # Full suite - requires approval
    PLAYBOOK = "playbook"  # Requires approval


@dataclass
class TestCortexResult:
    """Result of a test cortex operation."""

    operation: str
    success: bool
    exit_code: int = 0
    summary: str = ""
    passed: int = 0
    failed: int = 0
    duration_ms: float = 0.0
    output: str = ""
    error: Optional[str] = None
    blocked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ledger/serialization."""
        return {
            "operation": self.operation,
            "success": self.success,
            "exit_code": self.exit_code,
            "summary": self.summary,
            "passed": self.passed,
            "failed": self.failed,
            "duration_ms": self.duration_ms,
            "output_length": len(self.output) if self.output else 0,
            "error": self.error,
            "blocked": self.blocked,
        }


class TestCortex:
    """
    Safe interface for MANAS to execute tests.

    OPUS-059 PRAMANA: The system that cannot test itself cannot trust itself.

    This cortex allows MANAS to:
    1. Run smoke tests to verify kernel integrity
    2. Run pytest suites with marker filtering
    3. Execute test playbooks
    4. Get test summaries

    All operations are recorded to the core ledger (VAJRA binding).

    Usage:
        cortex = TestCortex(workspace=Path("."))
        cortex.inject_kernel(kernel)

        # Safe operations (auto-execute)
        result = cortex.run_smoke_test()

        # Operations requiring approval
        result = cortex.run_pytest("tests", approval_token="human_approved")
    """

    # Operations that are safe to auto-execute
    SAFE_OPERATIONS = frozenset(
        {
            "smoke_test",
            "get_summary",
            "get_failures",
        }
    )

    # Operations requiring approval
    REQUIRES_APPROVAL_OPERATIONS = frozenset(
        {
            "pytest",
            "pytest_markers",
            "run_playbook",
            "run_all",
        }
    )

    # Default timeout in seconds
    DEFAULT_TIMEOUT = 300  # 5 minutes for test runs

    def __init__(
        self,
        workspace: Optional[Path] = None,
        timeout_seconds: Optional[int] = None,
    ):
        """
        Initialize TestCortex.

        Args:
            workspace: Working directory for test execution
            timeout_seconds: Test timeout (default: 300s / 5 min)
        """
        self._workspace = workspace or Path.cwd()
        self._timeout = timeout_seconds if timeout_seconds is not None else self.DEFAULT_TIMEOUT
        self._vibe_kernel: Optional["KernelProtocol"] = None
        self._test_orchestration_plugin = None

    # =========================================================================
    # ⚡ PRAMANA: KERNEL INTEGRATION (OPUS-059)
    # =========================================================================

    def inject_kernel(self, kernel: "KernelProtocol") -> None:
        """
        Inject the core VibeKernel for ledger access.

        OPUS-059 PRAMANA: Every test operation MUST be recorded.
        Without kernel injection, TestCortex operates in "shadow mode".

        Args:
            kernel: The RealVibeKernel instance
        """
        self._vibe_kernel = kernel
        logger.info("⚡ PRAMANA: TestCortex bound to core kernel")

        # Try to get test_orchestration plugin
        try:
            self._test_orchestration_plugin = kernel.get_plugin("test_orchestration")
            if self._test_orchestration_plugin:
                logger.info("⚡ PRAMANA: TestCortex connected to test_orchestration plugin")
        except Exception as e:
            logger.debug(f"Could not get test_orchestration plugin: {e}")

    def _record_to_ledger(
        self,
        event_type: str,
        operation: str,
        result: Optional["TestCortexResult"] = None,
    ) -> Optional[str]:
        """
        Record a test operation to the core ledger.

        OPUS-059 PRAMANA: Audit trail for all test actions.

        Args:
            event_type: Type of event (TEST_CORTEX_STARTED, TEST_CORTEX_COMPLETED, etc.)
            operation: The operation being performed
            result: Optional result after execution

        Returns:
            Event ID if recorded, None if no kernel available
        """
        if not self._vibe_kernel:
            logger.debug("⚠️ PRAMANA: No kernel - test operation not ledgered (shadow mode)")
            return None

        # Build operation hash for integrity
        op_hash = hashlib.sha256(operation.encode()).hexdigest()[:16]

        details = {
            "operation": operation,
            "operation_hash": op_hash,
            "workspace": str(self._workspace),
        }

        if result:
            details.update(result.to_dict())

        try:
            event_id = self._vibe_kernel.ledger.record_event(
                event_type=event_type,
                agent_id="test_cortex",
                details=details,
            )
            logger.debug(f"⚡ PRAMANA: {event_type} recorded → {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"⚡ PRAMANA: Failed to record {event_type}: {e}")
            return None

    # =========================================================================
    # SAFE OPERATIONS (Auto-execute)
    # =========================================================================

    def run_smoke_test(self) -> TestCortexResult:
        """
        Run the kernel smoke test to verify basic functionality.

        This is SAFE to auto-execute - it's a read-only sanity check.

        Returns:
            TestCortexResult with test outcome
        """
        operation = "smoke_test"
        self._record_to_ledger("TEST_CORTEX_STARTED", operation)

        start_time = time.time()

        try:
            # Run the smoke test script
            smoke_script = self._workspace / "scripts" / "smoke_test_kernel.py"

            if not smoke_script.exists():
                result = TestCortexResult(
                    operation=operation,
                    success=False,
                    error=f"Smoke test script not found: {smoke_script}",
                )
                self._record_to_ledger("TEST_CORTEX_ERROR", operation, result)
                return result

            proc = subprocess.run(
                ["python", str(smoke_script)],
                capture_output=True,
                text=True,
                timeout=self._timeout,
                cwd=str(self._workspace),
            )

            duration_ms = (time.time() - start_time) * 1000

            # Parse output for pass/fail counts
            passed = 0
            failed = 0
            for line in proc.stdout.splitlines():
                if "✅" in line or "PASS" in line:
                    passed += 1
                if "❌" in line or "FAIL" in line:
                    failed += 1

            result = TestCortexResult(
                operation=operation,
                success=proc.returncode == 0,
                exit_code=proc.returncode,
                summary=f"Smoke test {'PASSED' if proc.returncode == 0 else 'FAILED'}",
                passed=passed,
                failed=failed,
                duration_ms=duration_ms,
                output=proc.stdout,
                error=proc.stderr if proc.returncode != 0 else None,
            )

            event_type = "TEST_CORTEX_COMPLETED" if result.success else "TEST_CORTEX_FAILED"
            self._record_to_ledger(event_type, operation, result)

            return result

        except subprocess.TimeoutExpired:
            result = TestCortexResult(
                operation=operation,
                success=False,
                exit_code=124,
                error=f"Smoke test timed out after {self._timeout}s",
            )
            self._record_to_ledger("TEST_CORTEX_TIMEOUT", operation, result)
            return result
        except Exception as e:
            result = TestCortexResult(
                operation=operation,
                success=False,
                exit_code=1,
                error=str(e),
            )
            self._record_to_ledger("TEST_CORTEX_ERROR", operation, result)
            return result

    def get_test_summary(self) -> TestCortexResult:
        """
        Get a summary of discovered tests from test_orchestration.

        This is SAFE to auto-execute - read-only operation.

        Returns:
            TestCortexResult with test discovery summary
        """
        operation = "get_summary"

        if not self._test_orchestration_plugin:
            return TestCortexResult(
                operation=operation,
                success=False,
                error="test_orchestration plugin not available",
            )

        try:
            summary = self._test_orchestration_plugin.get_summary()
            return TestCortexResult(
                operation=operation,
                success=True,
                summary=str(summary),
                output=str(summary),
            )
        except Exception as e:
            return TestCortexResult(
                operation=operation,
                success=False,
                error=str(e),
            )

    # =========================================================================
    # OPERATIONS REQUIRING APPROVAL
    # =========================================================================

    def run_pytest(
        self,
        path: str = "tests",
        markers: Optional[str] = None,
        approval_token: Optional[str] = None,
    ) -> TestCortexResult:
        """
        Run pytest with optional markers.

        Requires approval token for full control.

        Args:
            path: Test path to run
            markers: Pytest markers to filter (e.g., "fast", "not slow")
            approval_token: Required approval token

        Returns:
            TestCortexResult with pytest outcome
        """
        operation = f"pytest:{path}:{markers or 'all'}"

        if not approval_token:
            result = TestCortexResult(
                operation=operation,
                success=False,
                blocked=True,
                error="Approval token required for pytest execution",
            )
            self._record_to_ledger("TEST_CORTEX_BLOCKED", operation, result)
            return result

        self._record_to_ledger("TEST_CORTEX_STARTED", operation)

        start_time = time.time()

        try:
            # Try to use test_orchestration plugin if available
            if self._test_orchestration_plugin:
                result_dict = self._test_orchestration_plugin.run_pytest(
                    markers=markers or "",
                    path=path,
                    verbose=False,
                )
                duration_ms = (time.time() - start_time) * 1000

                result = TestCortexResult(
                    operation=operation,
                    success=result_dict.get("success", False),
                    exit_code=result_dict.get("exit_code", 1),
                    summary=result_dict.get("summary", ""),
                    output=result_dict.get("output", ""),
                    duration_ms=duration_ms,
                )
            else:
                # Fallback to direct pytest invocation
                args = ["pytest", path, "-q"]
                if markers:
                    args.extend(["-m", markers])

                proc = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                    cwd=str(self._workspace),
                )

                duration_ms = (time.time() - start_time) * 1000

                # Parse summary line
                summary_line = ""
                for line in proc.stdout.splitlines():
                    if "passed" in line or "failed" in line:
                        summary_line = line

                result = TestCortexResult(
                    operation=operation,
                    success=proc.returncode == 0,
                    exit_code=proc.returncode,
                    summary=summary_line,
                    output=proc.stdout,
                    duration_ms=duration_ms,
                    error=proc.stderr if proc.returncode != 0 else None,
                )

            event_type = "TEST_CORTEX_COMPLETED" if result.success else "TEST_CORTEX_FAILED"
            self._record_to_ledger(event_type, operation, result)

            return result

        except subprocess.TimeoutExpired:
            result = TestCortexResult(
                operation=operation,
                success=False,
                exit_code=124,
                error=f"Pytest timed out after {self._timeout}s",
            )
            self._record_to_ledger("TEST_CORTEX_TIMEOUT", operation, result)
            return result
        except Exception as e:
            result = TestCortexResult(
                operation=operation,
                success=False,
                exit_code=1,
                error=str(e),
            )
            self._record_to_ledger("TEST_CORTEX_ERROR", operation, result)
            return result

    def run_playbook(
        self,
        playbook_id: str,
        inputs: Optional[Dict[str, Any]] = None,
        approval_token: Optional[str] = None,
    ) -> TestCortexResult:
        """
        Execute a test playbook.

        Requires approval token.

        Args:
            playbook_id: ID of the playbook to execute
            inputs: Input parameters for the playbook
            approval_token: Required approval token

        Returns:
            TestCortexResult with playbook outcome
        """
        operation = f"playbook:{playbook_id}"

        if not approval_token:
            result = TestCortexResult(
                operation=operation,
                success=False,
                blocked=True,
                error="Approval token required for playbook execution",
            )
            self._record_to_ledger("TEST_CORTEX_BLOCKED", operation, result)
            return result

        self._record_to_ledger("TEST_CORTEX_STARTED", operation)

        try:
            from vibe_core.plugins.test_orchestration.playbook_executor import (
                execute_playbook,
            )

            start_time = time.time()
            pb_result = execute_playbook(
                playbook_id,
                inputs or {},
                dry_run=False,
                kernel=self._vibe_kernel,
            )
            duration_ms = (time.time() - start_time) * 1000

            # Count passed/failed stages
            passed = sum(1 for s in pb_result.stages if s.status.value == "success")
            failed = sum(1 for s in pb_result.stages if s.status.value == "failed")

            result = TestCortexResult(
                operation=operation,
                success=pb_result.success,
                exit_code=0 if pb_result.success else 1,
                summary=f"Playbook {playbook_id}: {passed}/{len(pb_result.stages)} stages passed",
                passed=passed,
                failed=failed,
                duration_ms=duration_ms,
            )

            event_type = "TEST_CORTEX_COMPLETED" if result.success else "TEST_CORTEX_FAILED"
            self._record_to_ledger(event_type, operation, result)

            return result

        except Exception as e:
            result = TestCortexResult(
                operation=operation,
                success=False,
                exit_code=1,
                error=str(e),
            )
            self._record_to_ledger("TEST_CORTEX_ERROR", operation, result)
            return result


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TestCortex",
    "TestCortexResult",
    "TestScope",
]
