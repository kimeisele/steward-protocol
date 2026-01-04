"""
Tool Registry for vibe-agency OS (ARCH-027 + ARCH-029)

Manages available tools and provides lookup/execution functionality.
Integrates Soul Governance (ARCH-029) for security by design.

SECURITY (ARCH-HARDENING):
- Capability-based access control for tools
- Caller identity verification via caller_agent_id
- No tool execution without proper authorization
"""

import logging
from typing import TYPE_CHECKING, Callable, Optional

from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

# Import Soul Governance (ARCH-029)
try:
    from vibe_core.governance import InvariantChecker, SoulResult
except ImportError:
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
    - Plugin hooks for tool execution (on_tool_execute, on_tool_executed)

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

    def __init__(
        self,
        invariant_checker: Optional["InvariantChecker"] = None,  # type: ignore
        capability_checker: Optional[Callable[[str, str], bool]] = None,
        kernel: Optional["RealVibeKernel"] = None,  # type: ignore
    ):
        """
        Initialize tool registry with optional Soul Governance and capability checking.

        Args:
            invariant_checker: Optional InvariantChecker for Soul Governance (ARCH-029).
                              If None, tools execute without governance checks.
            capability_checker: Optional callback (agent_id, capability) -> bool
                              Returns True if agent has the capability.
                              SECURITY: If set, all tool calls MUST have caller_agent_id.
            kernel: Optional kernel reference for plugin hooks.
                   If set, on_tool_execute and on_tool_executed hooks are called.

        Example:
            >>> # With governance (recommended for production)
            >>> from vibe_core.governance import InvariantChecker
            >>> checker = InvariantChecker("config/soul.yaml")
            >>> registry = ToolRegistry(invariant_checker=checker)
            >>>
            >>> # With capability checking (production)
            >>> def check_cap(agent_id, cap):
            ...     return cap in agent_capabilities.get(agent_id, [])
            >>> registry = ToolRegistry(capability_checker=check_cap)
        """
        self.tools: dict[str, Tool] = {}
        self._invariant_checker = invariant_checker
        self._capability_checker = capability_checker
        self._kernel = kernel
        # Map tool_name -> required capability (default: tool name itself)
        self._tool_capabilities: dict[str, str] = {}

        if invariant_checker:
            # Get rule count safely (some invariant checkers may not have this attribute)
            rule_count = getattr(invariant_checker, "rule_count", "unknown")
            logger.info(f"🛡️ ToolRegistry initialized with Soul Governance ({rule_count} rules)")
        else:
            logger.debug("ToolRegistry: Initialized (no governance)")

        if capability_checker:
            logger.info("🔐 ToolRegistry: Capability enforcement ENABLED")

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
            raise ValueError(f"Tool '{tool_name}' is already registered. Cannot register duplicate tool names.")

        self.tools[tool_name] = tool
        # Default: tool requires capability matching its name
        self._tool_capabilities[tool_name] = tool_name
        logger.info(f"ToolRegistry: Registered tool '{tool_name}'")

    def set_tool_capability(self, tool_name: str, required_capability: str) -> None:
        """
        Set the required capability for a tool.

        SECURITY: Tools require capabilities to execute. By default,
        a tool requires a capability matching its name.

        Args:
            tool_name: Name of the tool
            required_capability: Capability required to use this tool

        Example:
            >>> registry.register(WriteFileTool())
            >>> registry.set_tool_capability("write_file", "filesystem_write")
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
        self._tool_capabilities[tool_name] = required_capability
        logger.info(f"ToolRegistry: Tool '{tool_name}' requires capability '{required_capability}'")

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
        caller_agent_id = tool_call.caller_agent_id

        # Step 1: Look up tool
        tool = self.get(tool_name)
        if tool is None:
            error_msg = f"Tool '{tool_name}' not found in registry. Available tools: {self.list_tools()}"
            logger.error(f"ToolRegistry: {error_msg}")
            return ToolResult(success=False, error=error_msg)

        logger.info(f"ToolRegistry: Executing {tool_call}")

        # Step 1.5: 🔐 CAPABILITY CHECK (ARCH-HARDENING)
        if self._capability_checker is not None:
            # If capability checking is enabled, caller_agent_id is REQUIRED
            if not caller_agent_id:
                error_msg = (
                    f"CAPABILITY_BYPASS_BLOCKED: Tool '{tool_name}' requires caller_agent_id. "
                    "Anonymous tool calls are not allowed."
                )
                logger.warning(f"⛔ {error_msg}")
                return ToolResult(
                    success=False,
                    error=error_msg,
                    metadata={"blocked_by": "capability_enforcement", "reason": "missing_caller_id"},
                )

            required_cap = self._tool_capabilities.get(tool_name, tool_name)
            has_capability = self._capability_checker(caller_agent_id, required_cap)

            if not has_capability:
                error_msg = (
                    f"CAPABILITY_DENIED: Agent '{caller_agent_id}' lacks capability '{required_cap}' "
                    f"required for tool '{tool_name}'."
                )
                logger.warning(f"⛔ {error_msg}")
                return ToolResult(
                    success=False,
                    error=error_msg,
                    metadata={
                        "blocked_by": "capability_enforcement",
                        "agent_id": caller_agent_id,
                        "required_capability": required_cap,
                    },
                )

            logger.debug(f"✅ Capability check passed: {caller_agent_id} has '{required_cap}'")

        # Step 2: 🛡️ Soul Governance Check (ARCH-029)
        if self._invariant_checker and hasattr(self._invariant_checker, "check_tool_call"):
            soul_check: SoulResult = self._invariant_checker.check_tool_call(  # type: ignore
                tool_name, tool_call.parameters, caller_agent_id
            )
            if not soul_check.allowed:
                logger.warning(f"⛔ SOUL BLOCKED {tool_name}: {soul_check.reason}")
                return ToolResult(
                    success=False,
                    error=f"Governance Violation: {soul_check.reason}",
                    metadata={
                        "blocked_by_soul": True,
                        "rule_reason": soul_check.reason,
                    },
                )

        # Step 2.5: 🔌 PLUGIN HOOK: on_tool_execute (TOOL GATE)
        # Any plugin can veto tool execution
        if self._kernel and hasattr(self._kernel, "_plugins"):
            for plugin in self._kernel._plugins:
                try:
                    result = plugin.on_tool_execute(
                        self._kernel, caller_agent_id or "anonymous", tool_name, tool_call.parameters
                    )
                    if result is False:
                        logger.info(f"🚫 Tool VETOED by plugin '{plugin.plugin_id}': {tool_name}")
                        return ToolResult(
                            success=False,
                            error=f"Tool execution blocked by plugin '{plugin.plugin_id}'",
                            metadata={"blocked_by_plugin": plugin.plugin_id},
                        )
                except Exception as e:
                    logger.warning(f"⚠️ Plugin {plugin.plugin_id} on_tool_execute error: {e}")

        # Step 3: Validate parameters
        try:
            tool.validate(tool_call.parameters)
        except (ValueError, TypeError) as e:
            error_msg = f"Parameter validation failed: {e!s}"
            logger.error(f"ToolRegistry: {error_msg} (tool={tool_name})")
            return ToolResult(success=False, error=error_msg)

        # Step 3.5: 🛡️ VFS INJECTION (SANDBOX)
        # Inject VFS from the calling agent's sandbox if provided
        if tool_call.vfs and hasattr(tool, "vfs"):
            tool.vfs = tool_call.vfs
            logger.debug(f"✅ VFS injected into tool '{tool_name}'")

        # Step 4: Execute tool
        try:
            result = tool.execute(tool_call.parameters)
            logger.info(f"ToolRegistry: Tool '{tool_name}' completed (success={result.success})")

            # Step 5: 🔌 PLUGIN HOOK: on_tool_executed (post-execution)
            if self._kernel and hasattr(self._kernel, "_plugins"):
                for plugin in self._kernel._plugins:
                    try:
                        plugin.on_tool_executed(
                            self._kernel,
                            caller_agent_id or "anonymous",
                            tool_name,
                            tool_call.parameters,
                            result.output if result.success else result.error,
                            result.success,
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Plugin {plugin.plugin_id} on_tool_executed error: {e}")

            return result
        except Exception as e:
            # Fallback error handling (tools should catch their own exceptions)
            error_msg = f"Tool execution failed: {type(e).__name__}: {e!s}"
            logger.error(f"ToolRegistry: {error_msg} (tool={tool_name})", exc_info=True)

            # Step 5b: PLUGIN HOOK for failures too
            if self._kernel and hasattr(self._kernel, "_plugins"):
                for plugin in self._kernel._plugins:
                    try:
                        plugin.on_tool_executed(
                            self._kernel,
                            caller_agent_id or "anonymous",
                            tool_name,
                            tool_call.parameters,
                            error_msg,
                            False,
                        )
                    except Exception as hook_err:
                        logger.warning(f"⚠️ Plugin {plugin.plugin_id} on_tool_executed error: {hook_err}")

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
