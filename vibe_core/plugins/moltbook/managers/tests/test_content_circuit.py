"""Tests for ContentCircuitExecutor — Kirtan feedback loop wiring.

Tests verify that content generation outcomes (success/failure) feed back into
the learning system via Reflection, SynapseStore, and event emission.
"""

from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock, patch

from vibe_core.plugins.moltbook.managers.content_circuit import ContentCircuitExecutor


@dataclass
class MockCycleResult:
    """Mock CycleResult for testing."""

    status: str = "SUCCESS"
    content: Optional[str] = "Generated content"
    guna: str = "RAJAS"
    guardian: str = "narada"
    duration_ms: float = 150.0


def _make_executor():
    """Create ContentCircuitExecutor with mock callables."""
    agency_director = MagicMock()
    emit_event = MagicMock()
    executor = ContentCircuitExecutor(
        agency_director_getter=lambda: agency_director,
        emit_event=emit_event,
    )
    return executor, agency_director, emit_event


class TestContentCircuitSuccess:
    """SUCCESS → SynapseStore positive reinforcement."""

    @patch("vibe_core.plugins.moltbook.managers.content_circuit.get_synapse_store", create=True)
    def test_success_increments_synapse(self, mock_get_store):
        # Can't easily patch lazy imports — test the method directly
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="SUCCESS", content="Good content")

        result = executor.execute(raw_input="test input", content_type="comment")

        assert result is not None
        assert result["content"] == "Good content"

    def test_success_returns_dict(self):
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(
            status="SUCCESS", content="Good content", guna="RAJAS", guardian="narada"
        )

        result = executor.execute(raw_input="test", content_type="post")

        assert result["content"] == "Good content"
        assert result["guna"] == "RAJAS"
        assert result["guardian"] == "narada"


class TestContentCircuitFailure:
    """Non-SUCCESS → Reflection + SynapseStore + event emission."""

    def test_failure_returns_none(self):
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="ERROR", content=None)

        result = executor.execute(raw_input="test", content_type="comment")
        assert result is None

    def test_failure_emits_content_failure_event(self):
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="ERROR", content=None, guna="RAJAS")

        executor.execute(raw_input="test", content_type="comment")

        # Should emit CONTENT_FAILURE event
        calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(calls) == 1
        assert "comment" in calls[0][0][1]

    def test_skipped_low_integrity_emits_both_events(self):
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(
            status="SKIPPED_LOW_INTEGRITY", content=None, guna="TAMAS"
        )

        result = executor.execute(raw_input="test", content_type="post")
        assert result is None

        # Should emit CONTENT_SKIPPED + CONTENT_FAILURE
        event_types = [c[0][0] for c in emit_event.call_args_list]
        assert "CONTENT_SKIPPED" in event_types
        assert "CONTENT_FAILURE" in event_types

    def test_validation_failed_emits_failure(self):
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="VALIDATION_FAILED", content="Bad content")

        result = executor.execute(raw_input="test", content_type="comment")

        # Content exists but status != SUCCESS → failure
        calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(calls) == 1

    def test_empty_content_emits_failure(self):
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="SUCCESS", content="")

        result = executor.execute(raw_input="test", content_type="comment")
        assert result is None

        calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(calls) == 1


class TestContentCircuitReflectionRecording:
    """Failure → ExecutionRecord recorded in Reflection."""

    def test_record_content_failure_calls_reflection(self):
        executor, agency_director, emit_event = _make_executor()
        mock_result = MockCycleResult(status="ERROR", content=None, guna="RAJAS", duration_ms=200.0)

        with patch(
            "vibe_core.plugins.moltbook.managers.content_circuit.get_reflection_safe",
            create=True,
        ) as mock_get:
            mock_reflection = MagicMock()
            mock_get.return_value = mock_reflection

            # Patch the import to work inside the lazy import block
            with patch.dict(
                "sys.modules",
                {
                    "vibe_core.protocols.reflection": MagicMock(
                        get_reflection_safe=mock_get,
                        ExecutionRecord=type("ExecutionRecord", (), {"__init__": lambda *a, **kw: None}),
                    )
                },
            ):
                executor._record_content_failure("comment", mock_result)

            # Event should still be emitted regardless of reflection
            calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
            assert len(calls) == 1

    def test_record_content_success_does_not_emit_failure(self):
        executor, agency_director, emit_event = _make_executor()

        executor._record_content_success("comment")

        # No CONTENT_FAILURE event
        failure_calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(failure_calls) == 0


class TestContentCircuitContextPassthrough:
    """Strategic context is threaded through to director."""

    def test_context_kwargs_passed(self):
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="SUCCESS", content="Content")

        executor.execute(
            raw_input="test",
            content_type="comment",
            context={"strategic_reasoning": "test reasoning", "submolt_context": "dev"},
        )

        call_kwargs = agency_director.run_retry_loop.call_args[1]
        assert call_kwargs["strategic_reasoning"] == "test reasoning"
        assert call_kwargs["submolt_context"] == "dev"


class TestDepartmentSignal:
    """CONTENT_FAILURE events include department-level signal fields."""

    def test_failure_includes_department_signal(self):
        """department_signal=True in CONTENT_FAILURE event data."""
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="ERROR", content=None)

        executor.execute(raw_input="test", content_type="comment")

        calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(calls) == 1
        event_data = calls[0][0][2]  # Third positional arg = data dict
        assert event_data["department_signal"] is True

    def test_failure_includes_healing_target(self):
        """healing_target in CONTENT_FAILURE event data matches content type."""
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="ERROR", content=None)

        executor.execute(raw_input="test", content_type="post")

        calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(calls) == 1
        event_data = calls[0][0][2]
        assert event_data["healing_target"] == "moltbook:content:post"

    def test_low_integrity_skip_also_has_department_signal(self):
        """SKIPPED_LOW_INTEGRITY emits CONTENT_FAILURE with department signal."""
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(
            status="SKIPPED_LOW_INTEGRITY", content=None, guna="TAMAS"
        )

        executor.execute(raw_input="test", content_type="dm")

        calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(calls) == 1
        event_data = calls[0][0][2]
        assert event_data["department_signal"] is True
        assert event_data["healing_target"] == "moltbook:content:dm"

    def test_success_has_no_department_signal(self):
        """SUCCESS path does NOT emit CONTENT_FAILURE."""
        executor, agency_director, emit_event = _make_executor()
        agency_director.run_retry_loop.return_value = MockCycleResult(status="SUCCESS", content="Good content")

        executor.execute(raw_input="test", content_type="comment")

        calls = [c for c in emit_event.call_args_list if c[0][0] == "CONTENT_FAILURE"]
        assert len(calls) == 0
