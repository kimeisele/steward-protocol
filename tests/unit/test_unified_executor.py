"""
Unit tests for UnifiedExecutor (OPUS Phase 2).

Tests execution paths, result formats, and error handling.
"""

import asyncio
from unittest.mock import MagicMock

import pytest

from vibe_core.runtime.unified_execution import (
    ExecutionPath,
    ExecutionRequest,
    ExecutionStatus,
    UnifiedExecutor,
)


@pytest.fixture
def mock_kernel():
    """Create a mock kernel for testing."""
    kernel = MagicMock()
    kernel.envoy = MagicMock()
    kernel.envoy._ephemeral = None
    return kernel


def test_executor_eager_initialization(mock_kernel):
    """Executor should initialize eagerly (no lazy loading)."""
    executor = UnifiedExecutor(mock_kernel)

    # Executor should be initialized
    assert executor is not None
    assert executor._kernel == mock_kernel


def test_executor_returns_structured_result(mock_kernel):
    """Executor should return ExecutionResult with consistent structure."""

    async def test_async():
        executor = UnifiedExecutor(mock_kernel)

        request = ExecutionRequest(
            user_input="test",
            execution_path=ExecutionPath.FALLBACK,
            target_id="SIMPLE_QUERY",
        )

        result = await executor.execute(request)

        assert hasattr(result, "status")
        assert hasattr(result, "response")
        assert hasattr(result, "execution_path")
        assert hasattr(result, "target_id")
        assert hasattr(result, "request_id")

    asyncio.run(test_async())


def test_executor_handles_fallback_path(mock_kernel):
    """Executor should handle fallback execution path."""

    async def test_async():
        executor = UnifiedExecutor(mock_kernel)

        request = ExecutionRequest(
            user_input="unknown command",
            execution_path=ExecutionPath.FALLBACK,
            target_id="SIMPLE_QUERY",
        )

        result = await executor.execute(request)

        assert result.status == "completed"
        assert "Unknown command" in result.response

    asyncio.run(test_async())


def test_executor_marks_request_status(mock_kernel):
    """Executor should update request status during execution."""

    async def test_async():
        executor = UnifiedExecutor(mock_kernel)

        request = ExecutionRequest(
            user_input="test",
            execution_path=ExecutionPath.FALLBACK,
            target_id="SIMPLE_QUERY",
        )

        # Initial status
        assert request.status == ExecutionStatus.PENDING

        # Execute
        await executor.execute(request)

        # Should be completed
        assert request.status == ExecutionStatus.COMPLETED
        assert request.started_at is not None
        assert request.completed_at is not None

    asyncio.run(test_async())


def test_executor_handles_errors_gracefully(mock_kernel):
    """Executor should handle errors and return failed result."""

    async def test_async():
        executor = UnifiedExecutor(mock_kernel)

        # Create request with invalid path to trigger error
        request = ExecutionRequest(
            user_input="test",
            execution_path="INVALID_PATH",  # This will cause error
            target_id="TEST",
        )

        result = await executor.execute(request)

        # Should fail gracefully
        assert result.status == "failed"
        assert result.error is not None

    asyncio.run(test_async())


def test_executor_tracks_duration(mock_kernel):
    """Executor should track execution duration."""

    async def test_async():
        executor = UnifiedExecutor(mock_kernel)

        request = ExecutionRequest(
            user_input="test",
            execution_path=ExecutionPath.FALLBACK,
            target_id="SIMPLE_QUERY",
        )

        result = await executor.execute(request)

        # Duration should be set
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0

    asyncio.run(test_async())
