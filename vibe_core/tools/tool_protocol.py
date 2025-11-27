"""
Tool Protocol for vibe-agency OS (ARCH-027)

Defines the clean interface that all tools must implement.
This enables LLM agents to perform actions safely and extensibly.

Design Principles:
- NO exec() or eval() - all tools implement explicit protocol
- Type-safe parameters via structured data
- Explicit error handling
- Auditability (all tool calls can be logged)
- Extensibility (easy to add new tools)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    """
    Represents a request to execute a tool.

    This is the data structure that LLM agents emit when they want
    to perform an action.

    Expected format from LLM:
    {
        "tool": "write_file",
        "parameters": {
            "path": "/tmp/hello.txt",
            "content": "Hello, world!"
        }
    }
    """

    tool_name: str
    parameters: dict[str, Any]
    call_id: str | None = None  # For tracking in logs

    def __repr__(self) -> str:
        """String representation for debugging"""
        params_str = ", ".join(f"{k}={v!r}" for k, v in self.parameters.items())
        return f"ToolCall({self.tool_name}({params_str}))"


@dataclass
class ToolResult:
    """
    Result of tool execution.

    Returned by Tool.execute() to communicate outcome to agent.

    Fields:
        success: Whether tool execution succeeded
        output: Tool output (file content, API response, etc.)
        error: Error message if success=False
        metadata: Additional info (execution time, resource usage, etc.)
    """

    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def __repr__(self) -> str:
        """String representation for debugging"""
        if self.success:
            return f"ToolResult(success=True, output={self.output!r})"
        else:
            return f"ToolResult(success=False, error={self.error!r})"


class Tool(ABC):
    """
    Abstract base class for all tools.

    Tools are actions that agents can perform (read files, make API calls,
    run commands, etc.). Each tool implements this protocol to ensure
    safe, auditable, type-safe execution.

    Lifecycle:
        1. Agent emits ToolCall with tool name and parameters
        2. ToolRegistry looks up Tool instance by name
        3. Tool.validate(parameters) checks parameter validity
        4. Tool.execute(parameters) performs the action
        5. Returns ToolResult with success/output/error

    Example:
        >>> class EchoTool(Tool):
        ...     @property
        ...     def name(self) -> str:
        ...         return "echo"
        ...
        ...     @property
        ...     def description(self) -> str:
        ...         return "Echoes back the input message"
        ...
        ...     @property
        ...     def parameters_schema(self) -> Dict[str, Any]:
        ...         return {"message": {"type": "string", "required": True}}
        ...
        ...     def validate(self, parameters: Dict[str, Any]) -> None:
        ...         if "message" not in parameters:
        ...             raise ValueError("Missing required parameter: message")
        ...
        ...     def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        ...         message = parameters["message"]
        ...         return ToolResult(success=True, output=message)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name of this tool.

        This name is used by agents to call the tool.
        Must be lowercase with underscores (e.g., "read_file", "make_api_call").

        Returns:
            str: Tool name
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Return a human-readable description of what this tool does.

        This description is shown to LLM agents in their system prompt
        so they understand when to use this tool.

        Returns:
            str: Tool description
        """
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """
        Return the JSON schema for tool parameters.

        Defines what parameters this tool accepts and their types.
        Used for documentation and validation.

        Returns:
            dict: JSON schema describing parameters

        Example:
            {
                "path": {"type": "string", "required": True},
                "content": {"type": "string", "required": True}
            }
        """
        pass

    @abstractmethod
    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate that parameters meet requirements.

        Called before execute() to ensure parameters are valid.
        Should raise ValueError or TypeError if validation fails.

        Args:
            parameters: Tool parameters from ToolCall

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type

        Example:
            >>> def validate(self, parameters):
            ...     if "path" not in parameters:
            ...         raise ValueError("Missing required parameter: path")
            ...     if not isinstance(parameters["path"], str):
            ...         raise TypeError("path must be a string")
        """
        pass

    @abstractmethod
    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given parameters.

        This is the main entry point for tool execution. Should:
        1. Perform the requested action (read file, make API call, etc.)
        2. Return ToolResult with success=True and output
        3. If error occurs, catch exception and return ToolResult with success=False

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult: Execution result

        Example:
            >>> def execute(self, parameters):
            ...     try:
            ...         path = parameters["path"]
            ...         content = open(path).read()
            ...         return ToolResult(success=True, output=content)
            ...     except Exception as e:
            ...         return ToolResult(success=False, error=str(e))

        Notes:
            - This method should NEVER raise exceptions (catch and return error)
            - Long-running operations should consider timeout handling
            - Resource cleanup should be in finally blocks
        """
        pass

    def to_llm_description(self) -> dict[str, Any]:
        """
        Convert tool to LLM-friendly description.

        This format is included in the LLM system prompt so agents
        understand how to use this tool.

        Returns:
            dict: Tool description for LLM

        Example output:
            {
                "name": "read_file",
                "description": "Read content from a file",
                "parameters": {
                    "path": {"type": "string", "required": True}
                }
            }
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
        }

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"{self.__class__.__name__}(name={self.name!r})"
