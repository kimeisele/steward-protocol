"""
Test Handler - Testing and code generation intent processing.

OPUS-171 Phase 5: Extracted from IntentRouter.

Handles:
- run_tests, revive_archived_tests (TestCortex)
- genesis_tests, create_tests (SILPA)
- contract violations routing
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Test")


@register_handler
class TestHandler(BaseHandler):
    """
    Handle test-related intents.

    Routes to TestCortex for test execution.
    """

    name = "test"
    intent_types = [
        "revive_archived_tests",
        "run_tests",
    ]
    agent_type = AgentType.TESTING
    priority = 15

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to TestCortex for test-related tasks."""
        from vibe_core.plugins.opus_assistant.manas.cortex.test import TestCortex

        logger.info(f"🧪 TestCortex handling: {intent.title}")

        try:
            test_cortex = TestCortex(workspace=self._workspace)
            if self._kernel:
                test_cortex.inject_kernel(self._kernel)

            result = test_cortex.run_smoke_test()

            return {
                "success": getattr(result, "success", True),
                "handler": self.name,
                "tests_passed": getattr(result, "tests_passed", getattr(result, "passed", 0)),
                "tests_failed": getattr(result, "tests_failed", getattr(result, "failed", 0)),
                "duration_ms": getattr(result, "duration_ms", getattr(result, "duration", 0)),
                "message": getattr(result, "message", f"Tests executed for: {intent.title}"),
            }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class SilpaHandler(BaseHandler):
    """
    Handle code generation and refactoring intents.

    OPUS-SILPA: Routes to SilpaArchitect.
    """

    name = "silpa"
    intent_types = [
        "genesis_tests",
        "create_tests",
    ]
    agent_type = AgentType.GENESIS
    priority = 12

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to SILPA for code generation/refactoring."""
        from vibe_core.plugins.opus_assistant.manas.cortex.silpa import SilpaArchitect

        logger.info(f"🏗️ SILPA handling: {intent.title}")

        try:
            architect = SilpaArchitect(workspace=self._workspace)

            return {
                "success": True,
                "handler": self.name,
                "action": "analysis_only",
                "message": f"SILPA analyzed intent: {intent.title}. Full execution requires approval.",
                "intent_params": intent.params,
            }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class ContractHandler(BaseHandler):
    """
    Handle contract violation intents.

    OPUS-SILPA: Routes contract violations to appropriate handlers.
    """

    name = "contract"
    intent_types = []  # Dynamic - checked via can_handle
    agent_type = AgentType.AUDIT
    priority = 8

    def can_handle(self, intent_type: str) -> bool:
        """Match any contract_* intent type."""
        return intent_type.startswith("contract_")

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route contract violations to appropriate handlers."""
        intent_type = intent.intent_type
        logger.info(f"📜 Contract handler: {intent_type}")

        try:
            # Documentation-related → SUTRA
            if "doc" in intent_type:
                from .sutra_handler import SutraHandler

                handler = SutraHandler(workspace=self._workspace, config=self._config)
                handler.inject_kernel(self._kernel)
                return handler.handle(intent)

            # Test-related → TestHandler
            if "test" in intent_type:
                handler = TestHandler(workspace=self._workspace, config=self._config)
                handler.inject_kernel(self._kernel)
                return handler.handle(intent)

            # Code fixes → SILPA
            if "fix" in intent_type or "create" in intent_type:
                handler = SilpaHandler(workspace=self._workspace, config=self._config)
                handler.inject_kernel(self._kernel)
                return handler.handle(intent)

            # Review requests → Acknowledge
            if "review" in intent_type:
                return {
                    "success": True,
                    "handler": self.name,
                    "action": "queued_for_review",
                    "message": f"Contract review queued: {intent.title}",
                    "details": intent.params,
                }

            # Fallback: route to SILPA
            handler = SilpaHandler(workspace=self._workspace, config=self._config)
            return handler.handle(intent)

        except Exception as e:
            logger.error(f"❌ Contract handler failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}
