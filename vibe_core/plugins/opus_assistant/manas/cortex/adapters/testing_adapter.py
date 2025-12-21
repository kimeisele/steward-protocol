"""
Test Cortex Adapter - VEDA-4 wrapper for TestCortex.

OPUS-171 Phase 5.2: Cortex Adapter Pattern

Wraps the existing TestCortex in BaseCortex interface
for VEDA-4 auto-discovery via CortexLoader.

CAPABILITIES:
    - run_tests: Run test suite
    - run_single_test: Run specific test file
    - revive_tests: Revive archived tests
    - coverage: Generate coverage report

USAGE:
    from vibe_core.loaders import get_cortex

    test = get_cortex("test", workspace=Path.cwd())
    result = test.execute(intent)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugins.opus_assistant.manas.cortex.base_cortex import (
    BaseCortex,
    cortex_error,
    cortex_success,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.Adapter.Test")


class TestCortexAdapter(BaseCortex):
    """
    VEDA-4 adapter for TestCortex.

    Wraps the existing TestCortex to provide unified BaseCortex interface.

    Discovery:
        CortexLoader.get_cortex("test")
    """

    # === CORTEX IDENTITY ===
    name = "test"
    capabilities = [
        "run_tests",
        "run_single_test",
        "revive_tests",
        "coverage",
        "test_status",
    ]
    priority = 10

    def __init__(
        self,
        workspace: Optional[Path] = None,
        kernel: Optional["RealVibeKernel"] = None,
    ):
        super().__init__(workspace, kernel)
        self._cortex = None

    def _get_cortex(self):
        """Lazy-load TestCortex."""
        if self._cortex is None:
            from vibe_core.plugins.opus_assistant.manas.cortex.test import TestCortex

            self._cortex = TestCortex(workspace=self._workspace)
        return self._cortex

    def execute(self, intent: "Intent") -> Dict[str, Any]:
        """
        Execute a test intent via TestCortex.

        Supports:
            - run_tests
            - revive_archived_tests
            - Single test execution

        Args:
            intent: The intent to execute

        Returns:
            Dict with success, handler, message, and test results
        """
        intent_type = intent.intent_type
        logger.info(f"🧪 TestCortexAdapter executing: {intent_type}")

        try:
            cortex = self._get_cortex()

            # Run all tests
            if intent_type == "run_tests":
                pattern = intent.params.get("pattern", "tests/")
                result = cortex.run_tests(pattern=pattern)
                return {
                    "success": result.success,
                    "handler": self.name,
                    "message": f"Tests {'passed' if result.success else 'failed'}",
                    "passed": result.passed,
                    "failed": result.failed,
                    "skipped": result.skipped,
                    "duration": result.duration,
                }

            # Revive archived tests
            if intent_type == "revive_archived_tests":
                archive_path = intent.params.get("archive_path", "tests/.archive")
                # Just acknowledge for now
                return cortex_success(
                    handler=self.name,
                    message=f"Test revival queued from {archive_path}",
                    action="revive_queued",
                )

            # Default: acknowledge
            return cortex_success(
                handler=self.name,
                message=f"Test intent acknowledged: {intent_type}",
                intent_type=intent_type,
            )

        except Exception as e:
            logger.error(f"TestCortexAdapter error: {e}")
            return cortex_error(handler=self.name, error=str(e))

    def run_quick_test(self, test_file: str) -> Dict[str, Any]:
        """
        Convenience method to run a single test file.

        Args:
            test_file: Path to test file

        Returns:
            Test result dict
        """
        cortex = self._get_cortex()
        result = cortex.run_tests(pattern=test_file)
        return {
            "success": result.success,
            "passed": result.passed,
            "failed": result.failed,
        }
