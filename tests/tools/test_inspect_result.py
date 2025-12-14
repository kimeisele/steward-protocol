"""
THE GREAT PURGE - SWEEP-002: InspectResultTool Tests
====================================================

Tests for vibe_core/tools/inspect_result.py

"The Sensor of the System - if it fails, we are deaf."

Run with: pytest tests/tools/test_inspect_result.py -v
"""

from unittest.mock import MagicMock

import pytest

from vibe_core.tools.inspect_result import InspectResultTool


class TestInspectResultToolProperties:
    """Tests for InspectResultTool properties."""

    @pytest.fixture
    def tool(self):
        """Get tool instance with mock kernel."""
        mock_kernel = MagicMock()
        return InspectResultTool(mock_kernel)

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "inspect_result"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert len(tool.description) > 0
        assert "result" in tool.description.lower() or "task" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "task_id" in schema
        assert schema["task_id"]["type"] == "string"
        assert schema["task_id"]["required"] is True
        assert "include_input" in schema
        assert schema["include_input"]["required"] is False


class TestInspectResultToolValidation:
    """Tests for InspectResultTool validation."""

    @pytest.fixture
    def tool(self):
        """Get tool instance with mock kernel."""
        mock_kernel = MagicMock()
        return InspectResultTool(mock_kernel)

    def test_validate_missing_task_id(self, tool):
        """Test validation rejects missing task_id."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({})
        assert "task_id" in str(exc_info.value).lower()

    def test_validate_empty_task_id(self, tool):
        """Test validation rejects empty task_id."""
        with pytest.raises(TypeError):
            tool.validate({"task_id": "   "})

    def test_validate_non_string_task_id(self, tool):
        """Test validation rejects non-string task_id."""
        with pytest.raises(TypeError):
            tool.validate({"task_id": 123})

    def test_validate_invalid_include_input_type(self, tool):
        """Test validation rejects non-boolean include_input."""
        with pytest.raises(TypeError):
            tool.validate({"task_id": "task-123", "include_input": "yes"})

    def test_validate_valid_params(self, tool):
        """Test validation accepts valid parameters."""
        # Should not raise
        tool.validate({"task_id": "task-123"})
        tool.validate({"task_id": "task-456", "include_input": True})
        tool.validate({"task_id": "task-789", "include_input": False})


class TestInspectResultToolExecution:
    """Tests for InspectResultTool execution."""

    @pytest.fixture
    def mock_kernel(self):
        """Get mock kernel with ledger."""
        kernel = MagicMock()
        kernel.ledger = MagicMock()
        return kernel

    @pytest.fixture
    def tool(self, mock_kernel):
        """Get tool instance."""
        return InspectResultTool(mock_kernel)

    def test_execute_task_not_found(self, tool, mock_kernel):
        """Test querying a task that doesn't exist."""
        mock_kernel.ledger.get_task.return_value = None

        result = tool.execute({"task_id": "nonexistent"})

        assert result.success is True
        assert result.output["status"] == "NOT_FOUND"
        assert "nonexistent" in result.output["error"]

    def test_execute_task_completed(self, tool, mock_kernel):
        """Test querying a completed task."""
        mock_kernel.ledger.get_task.return_value = {
            "status": "COMPLETED",
            "output_result": "Task output data",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        result = tool.execute({"task_id": "task-123"})

        assert result.success is True
        assert result.output["status"] == "COMPLETED"
        assert result.output["output"] == "Task output data"
        assert "timestamp" in result.output

    def test_execute_task_failed(self, tool, mock_kernel):
        """Test querying a failed task."""
        mock_kernel.ledger.get_task.return_value = {
            "status": "FAILED",
            "error_message": "Something went wrong",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        result = tool.execute({"task_id": "task-456"})

        assert result.success is True
        assert result.output["status"] == "FAILED"
        assert result.output["error"] == "Something went wrong"

    def test_execute_task_started(self, tool, mock_kernel):
        """Test querying a task that is still running."""
        mock_kernel.ledger.get_task.return_value = {
            "status": "STARTED",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        result = tool.execute({"task_id": "task-789"})

        assert result.success is True
        assert result.output["status"] == "STARTED"
        assert "executing" in result.output["message"].lower()

    def test_execute_with_include_input(self, tool, mock_kernel):
        """Test querying with include_input=True."""
        mock_kernel.ledger.get_task.return_value = {
            "status": "COMPLETED",
            "output_result": "Output",
            "input_payload": {"key": "value"},
            "timestamp": "2024-01-01T12:00:00Z",
        }

        result = tool.execute({"task_id": "task-123", "include_input": True})

        assert result.success is True
        assert "input_payload" in result.output
        assert result.output["input_payload"] == {"key": "value"}

    def test_execute_without_include_input(self, tool, mock_kernel):
        """Test querying with include_input=False (default)."""
        mock_kernel.ledger.get_task.return_value = {
            "status": "COMPLETED",
            "output_result": "Output",
            "input_payload": {"key": "value"},
            "timestamp": "2024-01-01T12:00:00Z",
        }

        result = tool.execute({"task_id": "task-123"})

        assert result.success is True
        assert "input_payload" not in result.output

    def test_execute_handles_exception(self, tool, mock_kernel):
        """Test that exceptions are handled gracefully."""
        mock_kernel.ledger.get_task.side_effect = Exception("Database error")

        result = tool.execute({"task_id": "task-123"})

        assert result.success is False
        assert "error" in result.error.lower()

    def test_execute_handles_validation_error(self, tool, mock_kernel):
        """Test that validation errors return proper result."""
        result = tool.execute({})  # Missing task_id

        assert result.success is False
        assert "Invalid parameters" in result.error


class TestInspectResultToolIntegration:
    """Integration-style tests."""

    def test_tool_protocol_compliance(self):
        """Test that InspectResultTool implements Tool protocol."""
        from vibe_core.tools.tool_protocol import Tool

        mock_kernel = MagicMock()
        tool = InspectResultTool(mock_kernel)

        assert isinstance(tool, Tool)
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "parameters_schema")
        assert hasattr(tool, "validate")
        assert hasattr(tool, "execute")

    def test_to_llm_description(self):
        """Test LLM description generation."""
        mock_kernel = MagicMock()
        tool = InspectResultTool(mock_kernel)

        desc = tool.to_llm_description()

        assert desc["name"] == "inspect_result"
        assert "description" in desc
        assert "parameters" in desc
