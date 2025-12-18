"""
OPUS-101: Test Action - VEDA-4 Compliant Test Execution.

This wraps TestCortex in a BaseAction interface for auto-discovery.

Karmendriya: PAYU (Elimination) - The ability to validate/verify/eliminate bugs.

Handled Intent Types:
- run_smoke_test: Quick validation
- run_tests: Run pytest
- run_unit_tests: Run unit tests
- run_integration_tests: Run integration tests
- get_test_summary: Get test status
- run_playbook: Execute test playbook

CRITICAL: This is how MANAS verifies its own integrity.
The system that cannot test itself cannot trust itself.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/test.py
    required: true
wiring:
  - pattern: "class TestAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
  - pattern: "handled_intent_types.*run_smoke_test"
    in: vibe_core/plugins/opus_assistant/manas/cortex/test_action.py
-->
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction
from .test import TestCortex, TestCortexResult, TestScope

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Test")


class TestAction(BaseAction):
    """
    Test Action - Execute and validate tests.

    Wraps TestCortex in BaseAction interface for ActionLoader discovery.

    "PAYU (Elimination) - The validator that eliminates uncertainty."

    CRITICAL: This enables MANAS to verify its own integrity.
    Without testing, MANAS cannot trust its own modifications.
    """

    # OPUS-101: VEDA-4 auto-discovery
    name = "test_action"

    # Intent types this action handles
    handled_intent_types: Set[str] = {
        # Quick tests (safe, auto-execute)
        "run_smoke_test",
        "smoke_test",
        "get_test_summary",
        "test_summary",
        # Unit tests
        "run_tests",
        "run_unit_tests",
        "unit_tests",
        "pytest",
        # Integration tests (requires approval)
        "run_integration_tests",
        "integration_tests",
        # Full suite
        "run_all_tests",
        "full_tests",
        # Playbook
        "run_playbook",
        "test_playbook",
        # Specific file/pattern
        "test_file",
        "test_pattern",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Test Action.

        Args:
            workspace: Workspace root
            config: Configuration dict
        """
        super().__init__(workspace, config)
        self._test_cortex = TestCortex(workspace=self._workspace)
        logger.info("[TEST_ACTION] Initialized - PAYU (The Validator)")

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a test-related intent.

        Routes to appropriate TestCortex method based on intent type.

        Args:
            intent: The intent to execute

        Returns:
            ActionResult with execution status
        """
        intent_type = intent.type
        params = intent.params or {}

        try:
            # Smoke test (always safe)
            if intent_type in ("run_smoke_test", "smoke_test"):
                return self._handle_smoke_test(intent)

            # Test summary (always safe)
            elif intent_type in ("get_test_summary", "test_summary"):
                return self._handle_summary(intent)

            # Unit tests
            elif intent_type in ("run_tests", "run_unit_tests", "unit_tests", "pytest"):
                return self._handle_pytest(intent, params, TestScope.UNIT)

            # Integration tests (requires approval)
            elif intent_type in ("run_integration_tests", "integration_tests"):
                return self._handle_pytest(intent, params, TestScope.INTEGRATION)

            # Full suite (requires approval)
            elif intent_type in ("run_all_tests", "full_tests"):
                return self._handle_pytest(intent, params, TestScope.FULL)

            # Playbook (requires approval)
            elif intent_type in ("run_playbook", "test_playbook"):
                return self._handle_playbook(intent, params)

            # Specific file/pattern
            elif intent_type in ("test_file", "test_pattern"):
                return self._handle_specific(intent, params)

            else:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent_type,
                    error=f"Unknown intent type for TestAction: {intent_type}",
                )

        except Exception as e:
            logger.error(f"[TEST_ACTION] Error handling {intent_type}: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=str(e),
            )

    def _handle_smoke_test(self, intent: "Intent") -> ActionResult:
        """Handle smoke test (always safe)."""
        result = self._test_cortex.run_smoke_test()
        return self._test_result_to_action_result(result, intent.type)

    def _handle_summary(self, intent: "Intent") -> ActionResult:
        """Handle test summary request."""
        result = self._test_cortex.get_test_summary()
        return self._test_result_to_action_result(result, intent.type)

    def _handle_pytest(self, intent: "Intent", params: Dict, scope: TestScope) -> ActionResult:
        """Handle pytest execution."""
        path = params.get("path", "tests")
        markers = params.get("markers") or params.get("marker")
        approval_token = params.get("approval_token", "")

        # Check if scope requires approval
        needs_approval = scope in (TestScope.INTEGRATION, TestScope.FULL)

        if needs_approval and not approval_token:
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.type,
                result={
                    "status": "needs_approval",
                    "scope": scope.value,
                    "path": path,
                    "markers": markers,
                },
                metadata={"approval_required": True, "scope": scope.value},
            )

        # Auto-execute for unit tests or if approval given
        result = self._test_cortex.run_pytest(
            path=path,
            markers=markers,
            approval_token=approval_token if needs_approval else "auto_safe",
        )
        return self._test_result_to_action_result(result, intent.type)

    def _handle_playbook(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle test playbook execution (requires approval)."""
        playbook_name = params.get("playbook") or params.get("name")
        approval_token = params.get("approval_token", "")

        if not playbook_name:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing playbook name parameter",
            )

        if not approval_token:
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.type,
                result={
                    "status": "needs_approval",
                    "playbook": playbook_name,
                },
                metadata={"approval_required": True},
            )

        result = self._test_cortex.run_playbook(
            playbook_name=playbook_name,
            approval_token=approval_token,
        )
        return self._test_result_to_action_result(result, intent.type)

    def _handle_specific(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle testing specific file or pattern."""
        target = params.get("file") or params.get("pattern") or params.get("path")

        if not target:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing file/pattern parameter",
            )

        # Run pytest on specific target (safe operation)
        result = self._test_cortex.run_pytest(
            path=target,
            approval_token="auto_specific",
        )
        return self._test_result_to_action_result(result, intent.type)

    def _test_result_to_action_result(self, test_result: TestCortexResult, intent_type: str) -> ActionResult:
        """Convert TestCortexResult to ActionResult."""
        return ActionResult(
            success=test_result.success and not test_result.blocked,
            action_name=self.name,
            intent_type=intent_type,
            result={
                "operation": test_result.operation,
                "exit_code": test_result.exit_code,
                "summary": test_result.summary,
                "passed": test_result.passed,
                "failed": test_result.failed,
                "duration_ms": test_result.duration_ms,
                "blocked": test_result.blocked,
            },
            error=test_result.error,
            metadata={
                "output_length": len(test_result.output) if test_result.output else 0,
            },
        )
