"""
THE GREAT PURGE - SWEEP-004: ToolProtocol Tests
===============================================

Tests for vibe_core/tools/tool_protocol.py

"The Contract of the System - if it fails, nothing speaks the same language."

Run with: pytest tests/tools/test_tool_protocol.py -v
"""

import pytest

from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult


class TestToolCall:
    """Tests for ToolCall dataclass."""

    def test_basic_creation(self):
        """Test creating a basic ToolCall."""
        call = ToolCall(tool_name="test_tool", parameters={"key": "value"})

        assert call.tool_name == "test_tool"
        assert call.parameters == {"key": "value"}
        assert call.call_id is None
        assert call.caller_agent_id is None

    def test_with_optional_fields(self):
        """Test creating ToolCall with optional fields."""
        call = ToolCall(
            tool_name="test_tool",
            parameters={"key": "value"},
            call_id="call-123",
            caller_agent_id="agent-456",
        )

        assert call.call_id == "call-123"
        assert call.caller_agent_id == "agent-456"

    def test_repr(self):
        """Test string representation."""
        call = ToolCall(tool_name="read_file", parameters={"path": "/tmp/test.txt"})

        repr_str = repr(call)

        assert "ToolCall" in repr_str
        assert "read_file" in repr_str
        assert "path" in repr_str

    def test_empty_parameters(self):
        """Test ToolCall with empty parameters."""
        call = ToolCall(tool_name="no_params", parameters={})

        assert call.parameters == {}


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_success_result(self):
        """Test creating a successful result."""
        result = ToolResult(success=True, output="Operation completed")

        assert result.success is True
        assert result.output == "Operation completed"
        assert result.error is None
        assert result.metadata is None

    def test_failure_result(self):
        """Test creating a failure result."""
        result = ToolResult(success=False, error="Something went wrong")

        assert result.success is False
        assert result.output is None
        assert result.error == "Something went wrong"

    def test_with_metadata(self):
        """Test result with metadata."""
        result = ToolResult(success=True, output="OK", metadata={"duration_ms": 42})

        assert result.metadata == {"duration_ms": 42}

    def test_repr_success(self):
        """Test string representation for success."""
        result = ToolResult(success=True, output="data")

        repr_str = repr(result)

        assert "success=True" in repr_str
        assert "data" in repr_str

    def test_repr_failure(self):
        """Test string representation for failure."""
        result = ToolResult(success=False, error="error message")

        repr_str = repr(result)

        assert "success=False" in repr_str
        assert "error message" in repr_str

    def test_output_can_be_any_type(self):
        """Test that output can be any type."""
        # Dict
        result1 = ToolResult(success=True, output={"key": "value"})
        assert result1.output == {"key": "value"}

        # List
        result2 = ToolResult(success=True, output=[1, 2, 3])
        assert result2.output == [1, 2, 3]

        # None
        result3 = ToolResult(success=True, output=None)
        assert result3.output is None


class TestToolABC:
    """Tests for Tool abstract base class."""

    def test_cannot_instantiate_directly(self):
        """Test that Tool cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Tool()

    def test_subclass_must_implement_abstract_methods(self):
        """Test that subclass must implement all abstract methods."""

        class IncompleteTool(Tool):
            @property
            def name(self) -> str:
                return "incomplete"

            # Missing: description, parameters_schema, validate, execute

        with pytest.raises(TypeError):
            IncompleteTool()

    def test_complete_implementation(self):
        """Test that a complete implementation can be instantiated."""

        class CompleteTool(Tool):
            @property
            def name(self) -> str:
                return "complete"

            @property
            def description(self) -> str:
                return "A complete tool"

            @property
            def parameters_schema(self) -> dict:
                return {"param": {"type": "string"}}

            def validate(self, parameters: dict) -> None:
                pass

            def execute(self, parameters: dict) -> ToolResult:
                return ToolResult(success=True, output="OK")

        tool = CompleteTool()
        assert tool.name == "complete"
        assert tool.description == "A complete tool"

    def test_to_llm_description(self):
        """Test the to_llm_description method."""

        class DescTool(Tool):
            @property
            def name(self) -> str:
                return "desc_tool"

            @property
            def description(self) -> str:
                return "Tool for descriptions"

            @property
            def parameters_schema(self) -> dict:
                return {"input": {"type": "string", "required": True}}

            def validate(self, parameters: dict) -> None:
                pass

            def execute(self, parameters: dict) -> ToolResult:
                return ToolResult(success=True)

        tool = DescTool()
        desc = tool.to_llm_description()

        assert desc["name"] == "desc_tool"
        assert desc["description"] == "Tool for descriptions"
        assert desc["parameters"] == {"input": {"type": "string", "required": True}}

    def test_repr(self):
        """Test string representation."""

        class ReprTool(Tool):
            @property
            def name(self) -> str:
                return "repr_test"

            @property
            def description(self) -> str:
                return "Test"

            @property
            def parameters_schema(self) -> dict:
                return {}

            def validate(self, parameters: dict) -> None:
                pass

            def execute(self, parameters: dict) -> ToolResult:
                return ToolResult(success=True)

        tool = ReprTool()
        repr_str = repr(tool)

        assert "ReprTool" in repr_str
        assert "repr_test" in repr_str


class TestToolProtocolIntegration:
    """Integration tests for the tool protocol."""

    def test_tool_execution_workflow(self):
        """Test the complete tool execution workflow."""

        class EchoTool(Tool):
            @property
            def name(self) -> str:
                return "echo"

            @property
            def description(self) -> str:
                return "Echoes input"

            @property
            def parameters_schema(self) -> dict:
                return {"message": {"type": "string", "required": True}}

            def validate(self, parameters: dict) -> None:
                if "message" not in parameters:
                    raise ValueError("Missing message")
                if not isinstance(parameters["message"], str):
                    raise TypeError("message must be string")

            def execute(self, parameters: dict) -> ToolResult:
                return ToolResult(success=True, output=parameters["message"])

        tool = EchoTool()

        # Create tool call
        call = ToolCall(tool_name="echo", parameters={"message": "Hello!"})

        # Validate
        tool.validate(call.parameters)  # Should not raise

        # Execute
        result = tool.execute(call.parameters)

        assert result.success is True
        assert result.output == "Hello!"

    def test_validation_raises_on_invalid_params(self):
        """Test that validation properly raises errors."""

        class StrictTool(Tool):
            @property
            def name(self) -> str:
                return "strict"

            @property
            def description(self) -> str:
                return "Strict validation"

            @property
            def parameters_schema(self) -> dict:
                return {"required_field": {"type": "string", "required": True}}

            def validate(self, parameters: dict) -> None:
                if "required_field" not in parameters:
                    raise ValueError("Missing required_field")

            def execute(self, parameters: dict) -> ToolResult:
                return ToolResult(success=True)

        tool = StrictTool()

        with pytest.raises(ValueError):
            tool.validate({})

    def test_tool_can_return_complex_output(self):
        """Test that tools can return complex data structures."""

        class ComplexTool(Tool):
            @property
            def name(self) -> str:
                return "complex"

            @property
            def description(self) -> str:
                return "Returns complex data"

            @property
            def parameters_schema(self) -> dict:
                return {}

            def validate(self, parameters: dict) -> None:
                pass

            def execute(self, parameters: dict) -> ToolResult:
                return ToolResult(
                    success=True,
                    output={
                        "items": [1, 2, 3],
                        "nested": {"key": "value"},
                        "count": 42,
                    },
                    metadata={"processed_at": "2024-01-01"},
                )

        tool = ComplexTool()
        result = tool.execute({})

        assert result.success is True
        assert result.output["items"] == [1, 2, 3]
        assert result.output["nested"]["key"] == "value"
        assert result.metadata["processed_at"] == "2024-01-01"
