"""
Tool Registry for vibe-agency OS (ARCH-027 + ARCH-029)

Manages available tools and provides lookup/execution functionality.
Integrates Soul Governance (ARCH-029) for security by design.
"""

import logging
from typing import Optional

from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult

# Import Soul Governance (ARCH-029)
try:
    from vibe_core.governance.invariants import InvariantChecker, SoulResult
except ImportError:
    # Graceful fallback if governance not available
    InvariantChecker = None  # type: ignore
    SoulResult = None  # type: ignore

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for managing available tools.

    Provides:
    - Tool registration (add tools dynamically)
    - Tool lookup by name
    - Tool execution (validates + executes)
    - LLM-friendly tool descriptions

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(ReadFileTool())
        >>> registry.register(WriteFileTool())
        >>>
        >>> # Agent calls tool
        >>> call = ToolCall(tool_name="read_file", parameters={"path": "/tmp/test.txt"})
        >>> result = registry.execute(call)
        >>> print(result.output)  # File content
    """

    def __init__(self, invariant_checker: Optional["InvariantChecker"] = None):  # type: ignore
        """
        Initialize tool registry with optional Soul Governance.

        Args:
            invariant_checker: Optional InvariantChecker for Soul Governance (ARCH-029).
                              If None, tools execute without governance checks.

        Example:
            >>> # With governance (recommended for production)
            >>> from vibe_core.governance import InvariantChecker
            >>> checker = InvariantChecker("config/soul.yaml")
            >>> registry = ToolRegistry(invariant_checker=checker)
            >>>
            >>> # Without governance (testing only)
            >>> registry = ToolRegistry()
        """
        self.tools: dict[str, Tool] = {}
        self._invariant_checker = invariant_checker

        if invariant_checker:
            logger.info(
                f"🛡️ ToolRegistry initialized with Soul Governance ({invariant_checker.rule_count} rules)"
            )
        else:
            logger.debug("ToolRegistry: Initialized (no governance)")

    def register(self, tool: Tool) -> None:
        """
        Register a tool with the registry.

        Args:
            tool: Tool instance to register

        Raises:
            ValueError: If tool with same name already registered
            TypeError: If tool doesn't implement Tool protocol

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(ReadFileTool())
            >>> registry.register(WriteFileTool())
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"tool must be a Tool instance, got {type(tool).__name__}")

        tool_name = tool.name

        if tool_name in self.tools:
            raise ValueError(
                f"Tool '{tool_name}' is already registered. Cannot register duplicate tool names."
            )

        self.tools[tool_name] = tool
        logger.info(f"ToolRegistry: Registered tool '{tool_name}'")

    def get(self, tool_name: str) -> Tool | None:
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance if found, None otherwise

        Example:
            >>> tool = registry.get("read_file")
            >>> if tool:
            ...     result = tool.execute({"path": "/tmp/test.txt"})
        """
        return self.tools.get(tool_name)

    def has(self, tool_name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool registered, False otherwise

        Example:
            >>> if registry.has("read_file"):
            ...     print("Tool available")
        """
        return tool_name in self.tools

    def list_tools(self) -> list[str]:
        """
        Get list of all registered tool names.

        Returns:
            List of tool names

        Example:
            >>> print(registry.list_tools())
            ['read_file', 'write_file', 'make_api_call']
        """
        return list(self.tools.keys())

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call.

        Workflow:
            1. Look up tool by name
            2. Validate parameters
            3. Execute tool
            4. Return result

        Args:
            tool_call: ToolCall with tool name and parameters

        Returns:
            ToolResult: Execution result

        Example:
            >>> call = ToolCall(tool_name="write_file", parameters={
            ...     "path": "/tmp/hello.txt",
            ...     "content": "Hello, world!"
            ... })
            >>> result = registry.execute(call)
            >>> print(result.success)  # True
        """
        tool_name = tool_call.tool_name

        # Step 1: Look up tool
        tool = self.get(tool_name)
        if tool is None:
            error_msg = (
                f"Tool '{tool_name}' not found in registry. Available tools: {self.list_tools()}"
            )
            logger.error(f"ToolRegistry: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        logger.info(f"ToolRegistry: Executing {tool_call}")

        # Step 2: 🛡️ Soul Governance Check (ARCH-029)
        if self._invariant_checker:
            soul_check: SoulResult = self._invariant_checker.check_tool_call(  # type: ignore
                tool_name, tool_call.parameters
            )
            if not soul_check.allowed:
                logger.warning(f"⛔ SOUL BLOCKED {tool_name}: {soul_check.reason}")
                return ToolResult(
                    success=False,
                    error=f"Governance Violation: {soul_check.reason}",
                    metadata={"blocked_by_soul": True, "rule_reason": soul_check.reason},
                )

        # Step 3: Validate parameters
        try:
            tool.validate(tool_call.parameters)
        except (ValueError, TypeError) as e:
            error_msg = f"Parameter validation failed: {e!s}"
            logger.error(f"ToolRegistry: {error_msg} (tool={tool_name})")
            return ToolResult(success=False, error=error_msg)

        # Step 4: Execute tool
        try:
            result = tool.execute(tool_call.parameters)
            logger.info(f"ToolRegistry: Tool '{tool_name}' completed (success={result.success})")
            return result
        except Exception as e:
            # Fallback error handling (tools should catch their own exceptions)
            error_msg = f"Tool execution failed: {type(e).__name__}: {e!s}"
            logger.error(f"ToolRegistry: {error_msg} (tool={tool_name})", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def to_llm_prompt(self) -> str:
        """
        Generate LLM system prompt section describing available tools.

        This is included in the agent's system prompt so the LLM knows
        what tools it can use and how to call them.

        Returns:
            str: Formatted tool descriptions for LLM

        Example:
            >>> prompt = registry.to_llm_prompt()
            >>> print(prompt)
            Available tools:
            - read_file: Read content from a file
              Parameters: {"path": {"type": "string", "required": true}}
            - write_file: Write content to a file
              Parameters: {"path": {"type": "string", "required": true}, ...}
        """
        if not self.tools:
            return "No tools available."

        lines = ["Available tools:"]
        for tool in self.tools.values():
            desc = tool.to_llm_description()
            lines.append(f"- {desc['name']}: {desc['description']}")
            lines.append(f"  Parameters: {desc['parameters']}")

        lines.append("")
        lines.append("To use a tool, respond with JSON:")
        lines.append('{"tool": "tool_name", "parameters": {...}}')

        return "\n".join(lines)

    def get_tool_descriptions(self) -> list[dict]:
        """
        Get structured tool descriptions.

        Returns list of tool descriptions in JSON format.
        Useful for APIs, documentation, etc.

        Returns:
            List of tool description dicts

        Example:
            >>> descriptions = registry.get_tool_descriptions()
            >>> for desc in descriptions:
            ...     print(desc["name"], desc["description"])
        """
        return [tool.to_llm_description() for tool in self.tools.values()]

    def __len__(self) -> int:
        """Return number of registered tools"""
        return len(self.tools)

    def __repr__(self) -> str:
        """String representation for debugging"""
        tool_names = ", ".join(self.tools.keys())
        return f"ToolRegistry({len(self.tools)} tools: [{tool_names}])"
