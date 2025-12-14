"""
THE GREAT PURGE - SWEEP-003: DelegateTool Tests
===============================================

Tests for vibe_core/tools/delegate_tool.py

"The Router of the System - if it fails, no one receives orders."

Run with: pytest tests/tools/test_delegate_tool.py -v
"""

from unittest.mock import MagicMock

import pytest

from vibe_core.tools.delegate_tool import DelegateTool


class TestDelegateToolProperties:
    """Tests for DelegateTool properties."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return DelegateTool()

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "delegate_task"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert len(tool.description) > 0
        assert "delegate" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "agent_id" in schema
        assert schema["agent_id"]["required"] is True
        assert "payload" in schema
        assert schema["payload"]["required"] is True

    def test_init_without_kernel(self, tool):
        """Test that tool initializes without kernel (late binding)."""
        assert tool.kernel is None


class TestDelegateToolKernelInjection:
    """Tests for kernel injection (late binding)."""

    def test_set_kernel(self):
        """Test injecting kernel reference."""
        tool = DelegateTool()
        mock_kernel = MagicMock()

        tool.set_kernel(mock_kernel)

        assert tool.kernel is mock_kernel


class TestDelegateToolValidation:
    """Tests for DelegateTool validation."""

    @pytest.fixture
    def tool_with_kernel(self):
        """Get tool instance with mock kernel."""
        tool = DelegateTool()
        mock_kernel = MagicMock()
        mock_kernel.agent_registry = {
            "specialist-planning": MagicMock(),
            "specialist-coding": MagicMock(),
        }
        tool.set_kernel(mock_kernel)
        return tool

    def test_validate_missing_agent_id(self, tool_with_kernel):
        """Test validation rejects missing agent_id."""
        with pytest.raises(ValueError) as exc_info:
            tool_with_kernel.validate({"payload": {}})
        assert "agent_id" in str(exc_info.value).lower()

    def test_validate_invalid_agent_id_type(self, tool_with_kernel):
        """Test validation rejects non-string agent_id."""
        with pytest.raises(TypeError):
            tool_with_kernel.validate({"agent_id": 123, "payload": {}})

    def test_validate_empty_agent_id(self, tool_with_kernel):
        """Test validation rejects empty agent_id."""
        with pytest.raises(ValueError):
            tool_with_kernel.validate({"agent_id": "   ", "payload": {}})

    def test_validate_missing_payload(self, tool_with_kernel):
        """Test validation rejects missing payload."""
        with pytest.raises(ValueError) as exc_info:
            tool_with_kernel.validate({"agent_id": "specialist-planning"})
        assert "payload" in str(exc_info.value).lower()

    def test_validate_invalid_payload_type(self, tool_with_kernel):
        """Test validation rejects non-dict payload."""
        with pytest.raises(TypeError):
            tool_with_kernel.validate({"agent_id": "specialist-planning", "payload": "not a dict"})

    def test_validate_payload_missing_mission_id(self, tool_with_kernel):
        """Test validation rejects payload without mission_id."""
        with pytest.raises(ValueError) as exc_info:
            tool_with_kernel.validate(
                {
                    "agent_id": "specialist-planning",
                    "payload": {"mission_uuid": "abc", "phase": "PLANNING"},
                }
            )
        assert "mission_id" in str(exc_info.value)

    def test_validate_payload_missing_mission_uuid(self, tool_with_kernel):
        """Test validation rejects payload without mission_uuid."""
        with pytest.raises(ValueError) as exc_info:
            tool_with_kernel.validate(
                {
                    "agent_id": "specialist-planning",
                    "payload": {"mission_id": 1, "phase": "PLANNING"},
                }
            )
        assert "mission_uuid" in str(exc_info.value)

    def test_validate_payload_missing_phase(self, tool_with_kernel):
        """Test validation rejects payload without phase."""
        with pytest.raises(ValueError) as exc_info:
            tool_with_kernel.validate(
                {
                    "agent_id": "specialist-planning",
                    "payload": {"mission_id": 1, "mission_uuid": "abc"},
                }
            )
        assert "phase" in str(exc_info.value)

    def test_validate_invalid_mission_id_type(self, tool_with_kernel):
        """Test validation rejects non-integer mission_id."""
        with pytest.raises(TypeError):
            tool_with_kernel.validate(
                {
                    "agent_id": "specialist-planning",
                    "payload": {"mission_id": "not-int", "mission_uuid": "abc", "phase": "PLANNING"},
                }
            )

    def test_validate_unknown_agent_id(self, tool_with_kernel):
        """Test validation rejects unknown agent_id (security)."""
        with pytest.raises(ValueError) as exc_info:
            tool_with_kernel.validate(
                {
                    "agent_id": "unknown-agent",
                    "payload": {"mission_id": 1, "mission_uuid": "abc", "phase": "PLANNING"},
                }
            )
        assert "Unknown agent_id" in str(exc_info.value)

    def test_validate_valid_params(self, tool_with_kernel):
        """Test validation accepts valid parameters."""
        # Should not raise
        tool_with_kernel.validate(
            {
                "agent_id": "specialist-planning",
                "payload": {"mission_id": 1, "mission_uuid": "abc-123", "phase": "PLANNING"},
            }
        )


class TestDelegateToolExecution:
    """Tests for DelegateTool execution."""

    @pytest.fixture
    def tool_with_kernel(self):
        """Get tool instance with mock kernel."""
        tool = DelegateTool()
        mock_kernel = MagicMock()
        mock_kernel.agent_registry = {"specialist-planning": MagicMock()}
        mock_kernel.submit.return_value = "task-uuid-123"
        tool.set_kernel(mock_kernel)
        return tool

    def test_execute_success(self, tool_with_kernel):
        """Test successful task delegation."""
        result = tool_with_kernel.execute(
            {
                "agent_id": "specialist-planning",
                "payload": {"mission_id": 42, "mission_uuid": "m-123", "phase": "PLANNING"},
            }
        )

        assert result.success is True
        assert result.output["task_id"] == "task-uuid-123"
        assert result.output["agent_id"] == "specialist-planning"
        assert result.output["status"] == "delegated"

    def test_execute_metadata_contains_task_info(self, tool_with_kernel):
        """Test that metadata contains task information."""
        result = tool_with_kernel.execute(
            {
                "agent_id": "specialist-planning",
                "payload": {"mission_id": 42, "mission_uuid": "m-123", "phase": "PLANNING"},
            }
        )

        assert result.metadata is not None
        assert result.metadata["task_id"] == "task-uuid-123"
        assert result.metadata["agent_id"] == "specialist-planning"
        assert result.metadata["mission_id"] == 42
        assert result.metadata["phase"] == "PLANNING"

    def test_execute_calls_kernel_submit(self, tool_with_kernel):
        """Test that kernel.submit is called correctly."""
        tool_with_kernel.execute(
            {
                "agent_id": "specialist-planning",
                "payload": {"mission_id": 42, "mission_uuid": "m-123", "phase": "PLANNING"},
            }
        )

        tool_with_kernel.kernel.submit.assert_called_once()

    def test_execute_handles_exception(self, tool_with_kernel):
        """Test that exceptions are handled gracefully."""
        tool_with_kernel.kernel.submit.side_effect = Exception("Kernel error")

        result = tool_with_kernel.execute(
            {
                "agent_id": "specialist-planning",
                "payload": {"mission_id": 42, "mission_uuid": "m-123", "phase": "PLANNING"},
            }
        )

        assert result.success is False
        assert "Failed to delegate" in result.error


class TestDelegateToolIntegration:
    """Integration-style tests."""

    def test_tool_protocol_compliance(self):
        """Test that DelegateTool implements Tool protocol."""
        from vibe_core.tools.tool_protocol import Tool

        tool = DelegateTool()

        assert isinstance(tool, Tool)
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "parameters_schema")
        assert hasattr(tool, "validate")
        assert hasattr(tool, "execute")

    def test_to_llm_description(self):
        """Test LLM description generation."""
        tool = DelegateTool()

        desc = tool.to_llm_description()

        assert desc["name"] == "delegate_task"
        assert "description" in desc
        assert "parameters" in desc
