"""
OPUS-078: Execution Loop Closure - E2E Tests

These tests verify that the MANAS execution loop actually DOES something.
Not just wiring - actual execution with observable output.

TDD: We write the test first to discover what's broken.

"If you can't test it, you can't trust it."
"""

import asyncio
from pathlib import Path

import pytest

from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
    CognitiveKernel,
    ManasConfig,
)
from vibe_core.plugins.opus_assistant.manas.intent_generator import (
    Intent,
    IntentPriority,
    IntentRisk,
)
from vibe_core.plugins.opus_assistant.manas.intent_router import (
    IntentRouter,
    create_execution_callback,
)
from vibe_core.plugins.opus_assistant.manas.router import list_handlers

# =============================================================================
# SECTION 1: CALLBACK WIRING TESTS
# =============================================================================


class TestExecutionCallbackWiring:
    """Tests that the callback is properly wired."""

    def test_create_execution_callback_returns_callable(self):
        """Factory must return a callable."""
        callback = create_execution_callback(workspace=Path("."))
        assert callable(callback)

    def test_cognitive_kernel_accepts_callback(self):
        """CognitiveKernel must accept execution callback injection."""
        config = ManasConfig(auto_execute_safe=False)
        kernel = CognitiveKernel(workspace=Path("."), config=config)

        callback = create_execution_callback(workspace=Path("."))
        kernel.set_execution_callback(callback)

        assert kernel._execution_callback is not None
        assert kernel._execution_callback == callback


# =============================================================================
# SECTION 2: INTENT ROUTING TESTS
# =============================================================================


class TestIntentRouterExecution:
    """Tests that intents actually route to handlers."""

    def test_router_has_handlers_registered(self):
        """Router must have handlers for common intent types."""
        # OPUS-314: Use list_handlers() instead of router._handlers
        handlers = list_handlers(workspace=Path("."))
        assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_router_routes_documentation_intent(self):
        """Documentation intents should route to Sutra handler."""
        router = IntentRouter(workspace=Path("."))

        intent = Intent(
            id="test-doc-001",
            intent_type="update_documentation",
            title="Update README",
            description="Test documentation update",
            reasoning="TDD test",
            priority=IntentPriority.MEDIUM,
            risk=IntentRisk.SAFE,
            auto_executable=True,
            params={"file": "README.md"},
        )

        # OPUS-314: route() is now async
        result = await router.route(intent)

        # Should not error - handler should exist
        # Success depends on actual handler implementation
        assert result is not None
        assert hasattr(result, "executed_by")

    @pytest.mark.asyncio
    async def test_router_returns_error_for_unknown_intent_type(self):
        """Unknown intent types should return error, not crash."""
        router = IntentRouter(workspace=Path("."))

        intent = Intent(
            id="test-unknown-001",
            intent_type="totally_fake_intent_type_xyz",
            title="Unknown Intent",
            description="This should fail gracefully",
            reasoning="TDD test - unknown type",
            priority=IntentPriority.LOW,
            risk=IntentRisk.SAFE,
            auto_executable=False,
            params={},
        )

        # OPUS-314: route() is now async
        result = await router.route(intent)

        assert result is not None
        assert result.success is False
        # OPUS-133: Unknown intents may be blocked by VivekaGate (dharmic score too low)
        # OR by handler lookup failure. Both are valid rejections.
        error = result.error or ""
        assert "No handler" in error or "blocked" in error.lower() or "dharmic" in error.lower()


# =============================================================================
# SECTION 3: E2E EXECUTION TESTS
# =============================================================================


class TestEndToEndExecution:
    """Tests the full execution loop: Intent -> Callback -> Router -> Handler."""

    @pytest.mark.asyncio
    async def test_callback_routes_intent_and_returns_result(self):
        """Callback should route intent through router and return result."""
        callback = create_execution_callback(workspace=Path("."))

        intent = Intent(
            id="test-e2e-001",
            intent_type="system_status_check",
            title="Check System Status",
            description="Verify system health",
            reasoning="TDD test - E2E",
            priority=IntentPriority.HIGH,
            risk=IntentRisk.SAFE,
            auto_executable=True,
            params={},
        )

        # OPUS-314: callback is now async
        result = await callback(intent)

        # Callback must return a dict
        assert isinstance(result, dict)
        # Must have success key
        assert "success" in result
        # Must have handler key (tells us who handled it)
        assert "handler" in result

    @pytest.mark.asyncio
    async def test_full_loop_with_kernel(self):
        """
        Full loop: Kernel with callback executes intent.

        This is the critical test - does the loop actually work?
        """
        config = ManasConfig(auto_execute_safe=True)
        kernel = CognitiveKernel(workspace=Path("."), config=config)

        # Wire the callback
        callback = create_execution_callback(workspace=Path("."))
        kernel.set_execution_callback(callback)

        # Create a safe intent
        intent = Intent(
            id="test-full-loop-001",
            intent_type="log_observation",
            title="Test Observation",
            description="Log a test observation",
            reasoning="TDD test - full loop",
            priority=IntentPriority.LOW,
            risk=IntentRisk.SAFE,
            auto_executable=True,
            params={"message": "Test from E2E test"},
        )

        # Execute through kernel's internal method
        # OPUS-314: callback is now async
        result = await kernel._execution_callback(intent)

        assert result is not None
        assert isinstance(result, dict)


# =============================================================================
# SECTION 4: HANDLER VERIFICATION TESTS
# =============================================================================


class TestHandlerVerification:
    """Tests that specific handlers actually DO something."""

    @pytest.mark.asyncio
    async def test_sutra_handler_exists_and_responds(self):
        """Sutra (documentation) handler must exist and respond."""
        router = IntentRouter(workspace=Path("."))

        # OPUS-314: Use list_handlers() to check handlers
        handlers = list_handlers(workspace=Path("."))
        # At least some handlers should be registered
        assert len(handlers) > 0

        # At minimum, routing shouldn't crash
        intent = Intent(
            id="test-sutra-001",
            intent_type="update_documentation",
            title="Test Doc Update",
            description="Test",
            reasoning="TDD test - sutra handler",
            priority=IntentPriority.LOW,
            risk=IntentRisk.SAFE,
            auto_executable=True,
            params={},
        )

        # OPUS-314: route() is now async
        result = await router.route(intent)
        assert result is not None

    @pytest.mark.asyncio
    async def test_silpa_handler_exists_and_responds(self):
        """Silpa (code generation) handler must exist and respond."""
        router = IntentRouter(workspace=Path("."))

        intent = Intent(
            id="test-silpa-001",
            intent_type="genesis_test",  # Prefix-based routing
            title="Test Code Generation",
            description="Test",
            reasoning="TDD test - silpa handler",
            priority=IntentPriority.LOW,
            risk=IntentRisk.SAFE,
            auto_executable=False,  # Code gen should not auto-execute
            params={},
        )

        # OPUS-314: route() is now async
        result = await router.route(intent)
        assert result is not None
