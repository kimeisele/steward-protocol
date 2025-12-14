"""
THE GREAT PURGE - SWEEP-001: ToolRegistry Tests
================================================

Tests for vibe_core/tools/tool_registry.py

"The Backbone of the System - if it fails, nothing works."

Run with: pytest tests/tools/test_tool_registry.py -v
"""

from unittest.mock import MagicMock

import pytest

from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult


class MockTool(Tool):
    """Mock tool for testing."""

    def __init__(self, name: str = "mock_tool", should_fail: bool = False):
        self._name = name
        self._should_fail = should_fail

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f"Mock tool: {self._name}"

    @property
    def parameters_schema(self) -> dict:
        return {"param": {"type": "string", "required": False}}

    def validate(self, parameters: dict) -> None:
        if "invalid" in parameters:
            raise ValueError("Invalid parameter")

    def execute(self, parameters: dict) -> ToolResult:
        if self._should_fail:
            return ToolResult(success=False, error="Mock failure")
        return ToolResult(success=True, output=f"Executed {self._name}")


class TestToolRegistryBasics:
    """Basic ToolRegistry tests."""

    @pytest.fixture
    def registry(self):
        """Get a fresh ToolRegistry instance."""
        from vibe_core.tools.tool_registry import ToolRegistry

        return ToolRegistry()

    def test_register_tool(self, registry):
        """Test registering a tool."""
        tool = MockTool("test_tool")
        registry.register(tool)

        assert registry.has("test_tool")
        assert len(registry) == 1

    def test_register_duplicate_raises(self, registry):
        """Test that registering duplicate tool name raises error."""
        tool1 = MockTool("same_name")
        tool2 = MockTool("same_name")

        registry.register(tool1)
        with pytest.raises(ValueError) as exc_info:
            registry.register(tool2)
        assert "already registered" in str(exc_info.value)

    def test_register_non_tool_raises(self, registry):
        """Test that registering non-Tool raises TypeError."""
        with pytest.raises(TypeError):
            registry.register("not a tool")

    def test_get_existing_tool(self, registry):
        """Test getting an existing tool."""
        tool = MockTool("get_test")
        registry.register(tool)

        result = registry.get("get_test")
        assert result is tool

    def test_get_nonexistent_tool(self, registry):
        """Test getting a tool that doesn't exist returns None."""
        result = registry.get("nonexistent")
        assert result is None

    def test_has_tool(self, registry):
        """Test has() method."""
        tool = MockTool("has_test")
        registry.register(tool)

        assert registry.has("has_test") is True
        assert registry.has("nonexistent") is False

    def test_list_tools(self, registry):
        """Test listing all tools."""
        registry.register(MockTool("tool_a"))
        registry.register(MockTool("tool_b"))
        registry.register(MockTool("tool_c"))

        tools = registry.list_tools()
        assert "tool_a" in tools
        assert "tool_b" in tools
        assert "tool_c" in tools
        assert len(tools) == 3

    def test_len(self, registry):
        """Test __len__ method."""
        assert len(registry) == 0
        registry.register(MockTool("t1"))
        assert len(registry) == 1
        registry.register(MockTool("t2"))
        assert len(registry) == 2

    def test_repr(self, registry):
        """Test __repr__ method."""
        registry.register(MockTool("repr_tool"))
        repr_str = repr(registry)
        assert "ToolRegistry" in repr_str
        assert "repr_tool" in repr_str


class TestToolRegistryExecution:
    """Tests for tool execution via registry."""

    @pytest.fixture
    def registry(self):
        """Get a fresh ToolRegistry instance."""
        from vibe_core.tools.tool_registry import ToolRegistry

        return ToolRegistry()

    def test_execute_success(self, registry):
        """Test successful tool execution."""
        registry.register(MockTool("exec_test"))
        call = ToolCall(tool_name="exec_test", parameters={})

        result = registry.execute(call)

        assert result.success is True
        assert "Executed" in result.output

    def test_execute_nonexistent_tool(self, registry):
        """Test executing a tool that doesn't exist."""
        call = ToolCall(tool_name="nonexistent", parameters={})

        result = registry.execute(call)

        assert result.success is False
        assert "not found" in result.error

    def test_execute_validation_failure(self, registry):
        """Test that validation failures are caught."""
        registry.register(MockTool("validate_fail"))
        call = ToolCall(tool_name="validate_fail", parameters={"invalid": True})

        result = registry.execute(call)

        assert result.success is False
        assert "validation failed" in result.error.lower()

    def test_execute_tool_failure(self, registry):
        """Test that tool execution failures are handled."""
        registry.register(MockTool("fail_tool", should_fail=True))
        call = ToolCall(tool_name="fail_tool", parameters={})

        result = registry.execute(call)

        assert result.success is False


class TestToolRegistryCapabilityEnforcement:
    """Tests for capability-based security."""

    @pytest.fixture
    def registry_with_capability_checker(self):
        """Get registry with capability checker."""
        from vibe_core.tools.tool_registry import ToolRegistry

        def checker(agent_id: str, capability: str) -> bool:
            # agent_1 has all capabilities, agent_2 has none
            return agent_id == "agent_1"

        return ToolRegistry(capability_checker=checker)

    def test_capability_check_missing_agent_id(self, registry_with_capability_checker):
        """Test that missing caller_agent_id is blocked."""
        registry = registry_with_capability_checker
        registry.register(MockTool("cap_tool"))

        call = ToolCall(tool_name="cap_tool", parameters={})  # No caller_agent_id

        result = registry.execute(call)

        assert result.success is False
        assert "caller_agent_id" in result.error.lower()
        assert result.metadata["blocked_by"] == "capability_enforcement"

    def test_capability_check_denied(self, registry_with_capability_checker):
        """Test that agent without capability is denied."""
        registry = registry_with_capability_checker
        registry.register(MockTool("cap_tool"))

        call = ToolCall(
            tool_name="cap_tool",
            parameters={},
            caller_agent_id="agent_2",  # Has no capabilities
        )

        result = registry.execute(call)

        assert result.success is False
        assert "CAPABILITY_DENIED" in result.error

    def test_capability_check_allowed(self, registry_with_capability_checker):
        """Test that agent with capability is allowed."""
        registry = registry_with_capability_checker
        registry.register(MockTool("cap_tool"))

        call = ToolCall(
            tool_name="cap_tool",
            parameters={},
            caller_agent_id="agent_1",  # Has capabilities
        )

        result = registry.execute(call)

        assert result.success is True

    def test_set_tool_capability(self):
        """Test setting custom capability for a tool."""
        from vibe_core.tools.tool_registry import ToolRegistry

        registry = ToolRegistry()
        registry.register(MockTool("custom_cap"))
        registry.set_tool_capability("custom_cap", "special_permission")

        assert registry._tool_capabilities["custom_cap"] == "special_permission"

    def test_set_tool_capability_unregistered_raises(self):
        """Test that setting capability for unregistered tool raises."""
        from vibe_core.tools.tool_registry import ToolRegistry

        registry = ToolRegistry()

        with pytest.raises(ValueError):
            registry.set_tool_capability("nonexistent", "capability")


class TestToolRegistryLLMIntegration:
    """Tests for LLM-related functionality."""

    @pytest.fixture
    def registry(self):
        """Get a fresh ToolRegistry instance."""
        from vibe_core.tools.tool_registry import ToolRegistry

        return ToolRegistry()

    def test_to_llm_prompt_empty(self, registry):
        """Test LLM prompt generation with no tools."""
        prompt = registry.to_llm_prompt()
        assert "No tools available" in prompt

    def test_to_llm_prompt_with_tools(self, registry):
        """Test LLM prompt generation with tools."""
        registry.register(MockTool("tool_a"))
        registry.register(MockTool("tool_b"))

        prompt = registry.to_llm_prompt()

        assert "Available tools" in prompt
        assert "tool_a" in prompt
        assert "tool_b" in prompt
        assert "tool" in prompt.lower()

    def test_get_tool_descriptions(self, registry):
        """Test getting structured tool descriptions."""
        registry.register(MockTool("desc_tool"))

        descriptions = registry.get_tool_descriptions()

        assert len(descriptions) == 1
        assert descriptions[0]["name"] == "desc_tool"
        assert "description" in descriptions[0]
        assert "parameters" in descriptions[0]


class TestToolRegistryPluginHooks:
    """Tests for plugin hook integration."""

    def test_on_tool_execute_hook_veto(self):
        """Test that plugins can veto tool execution."""
        from vibe_core.tools.tool_registry import ToolRegistry

        # Create mock kernel with mock plugin
        mock_kernel = MagicMock()
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = "veto_plugin"
        mock_plugin.on_tool_execute.return_value = False  # Veto!
        mock_kernel._plugins = [mock_plugin]

        registry = ToolRegistry(kernel=mock_kernel)
        registry.register(MockTool("veto_test"))

        call = ToolCall(tool_name="veto_test", parameters={})
        result = registry.execute(call)

        assert result.success is False
        assert "blocked by plugin" in result.error.lower()

    def test_on_tool_executed_hook_called(self):
        """Test that on_tool_executed hook is called after execution."""
        from vibe_core.tools.tool_registry import ToolRegistry

        mock_kernel = MagicMock()
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = "post_hook"
        mock_plugin.on_tool_execute.return_value = True  # Allow
        mock_kernel._plugins = [mock_plugin]

        registry = ToolRegistry(kernel=mock_kernel)
        registry.register(MockTool("hook_test"))

        call = ToolCall(tool_name="hook_test", parameters={}, caller_agent_id="test_agent")
        registry.execute(call)

        mock_plugin.on_tool_executed.assert_called_once()


class TestToolRegistrySoulGovernance:
    """Tests for Soul Governance integration (ARCH-029)."""

    def test_soul_governance_blocks(self):
        """Test that Soul Governance can block tool calls."""
        from vibe_core.tools.tool_registry import ToolRegistry

        # Create mock invariant checker
        mock_checker = MagicMock()
        mock_result = MagicMock()
        mock_result.allowed = False
        mock_result.reason = "Governance rule violated"
        mock_checker.check_tool_call.return_value = mock_result

        registry = ToolRegistry(invariant_checker=mock_checker)
        registry.register(MockTool("governed_tool"))

        call = ToolCall(tool_name="governed_tool", parameters={})
        result = registry.execute(call)

        assert result.success is False
        assert "Governance Violation" in result.error

    def test_soul_governance_allows(self):
        """Test that Soul Governance allows valid calls."""
        from vibe_core.tools.tool_registry import ToolRegistry

        mock_checker = MagicMock()
        mock_result = MagicMock()
        mock_result.allowed = True
        mock_checker.check_tool_call.return_value = mock_result

        registry = ToolRegistry(invariant_checker=mock_checker)
        registry.register(MockTool("governed_tool"))

        call = ToolCall(tool_name="governed_tool", parameters={})
        result = registry.execute(call)

        assert result.success is True
