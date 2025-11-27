"""
Simple LLM-based agent for vibe-agency OS.

This module implements a generic agent that performs cognitive work
via an LLM provider (ARCH-025).

Updated in ARCH-027 to support tool-use capability.
"""

import json
import logging
from typing import Any, Optional

from vibe_core.agent_protocol import AgentResponse, VibeAgent
from vibe_core.llm import LLMProvider
from vibe_core.scheduling import Task

logger = logging.getLogger(__name__)


class SimpleLLMAgent(VibeAgent):
    """
    A simple LLM-based agent that processes tasks via an LLM provider.

    This is the "Hello World" of cognitive agents - it demonstrates
    the full stack: Kernel → Agent → LLM → Ledger.

    Architecture:
    - Implements VibeAgent protocol (works with kernel dispatch)
    - Uses LLMProvider for cognitive work
    - Extracts user_message from task payload
    - Returns LLM response as task result
    - Handles errors gracefully

    Design Principles:
    - Provider-agnostic (works with any LLMProvider)
    - Simple interface (minimal configuration)
    - Error handling (captures LLM failures)
    - Logging (tracks LLM interactions)

    Example:
        >>> from tests.mocks.llm import MockLLMProvider
        >>> provider = MockLLMProvider(mock_response="Hello, human!")
        >>> agent = SimpleLLMAgent(
        ...     agent_id="assistant",
        ...     provider=provider,
        ...     system_prompt="You are friendly."
        ... )
        >>> task = Task(
        ...     agent_id="assistant",
        ...     payload={"user_message": "Hi there!"}
        ... )
        >>> result = agent.process(task)
        >>> print(result["response"])  # "Hello, human!"
    """

    def __init__(
        self,
        agent_id: str,
        provider: LLMProvider,
        system_prompt: str | None = None,
        model: str | None = None,
        tool_registry: Optional["ToolRegistry"] = None,  # noqa: F821
    ):
        """
        Initialize the LLM agent.

        Args:
            agent_id: Unique identifier for this agent
            provider: LLMProvider instance to use for cognitive work
            system_prompt: System prompt to use (overrides provider default)
            model: Model identifier to pass to provider (e.g., "gpt-4")
            tool_registry: Optional ToolRegistry for tool-use capability

        Example:
            >>> from tests.mocks.llm import MockLLMProvider
            >>> from vibe_core.tools import ToolRegistry, ReadFileTool
            >>> provider = MockLLMProvider()
            >>> registry = ToolRegistry()
            >>> registry.register(ReadFileTool())
            >>> agent = SimpleLLMAgent(
            ...     agent_id="my-agent",
            ...     provider=provider,
            ...     system_prompt="Be concise.",
            ...     tool_registry=registry
            ... )
        """
        self._agent_id = agent_id
        self.provider = provider
        self._system_prompt = system_prompt or provider.system_prompt
        self.model = model
        self.tool_registry = tool_registry

        logger.info(
            f"AGENT: Initialized SimpleLLMAgent '{agent_id}' "
            f"(provider={provider.__class__.__name__}, model={model}, "
            f"tools={'enabled' if tool_registry else 'disabled'})"
        )

    @property
    def agent_id(self) -> str:
        """Return the agent's unique identifier."""
        return self._agent_id

    @property
    def capabilities(self) -> list[str]:
        """
        Return list of tool names available to this agent.

        If tool_registry is configured, returns the names of all registered tools.
        Otherwise returns empty list (LLM can think but not act).

        Returns:
            list[str]: Names of available tools or empty list

        Example:
            >>> agent = SimpleLLMAgent(...)  # without tools
            >>> print(agent.capabilities)  # []

            >>> registry = ToolRegistry()
            >>> registry.register(ReadFileTool())
            >>> registry.register(WriteFileTool())
            >>> agent = SimpleLLMAgent(..., tool_registry=registry)
            >>> print(agent.capabilities)  # ["read_file", "write_file"]
        """
        if not self.tool_registry:
            return []
        return self.tool_registry.list_tools()  # Returns list of tool names

    def process(self, task: Task) -> AgentResponse:
        """
        Process a task by sending it to the LLM provider.

        Expected task payload format:
        {
            "user_message": str,  # Required: the user's message
            "context": dict,      # Optional: additional context
            "model": str          # Optional: override default model
        }

        Args:
            task: The Task to process

        Returns:
            AgentResponse: Standardized response with structure:
                {
                    "agent_id": str,           # This agent's ID
                    "task_id": str,            # The task ID
                    "success": bool,           # Whether call succeeded
                    "output": dict,            # Contains response, model_used, provider, tool_call
                    "error": str | None        # Error message if failed
                }

        Raises:
            ValueError: If task payload is missing user_message
            LLMError: If LLM call fails (after recording attempt)

        Example:
            >>> task = Task(
            ...     agent_id="my-agent",
            ...     payload={"user_message": "What is 2+2?"}
            ... )
            >>> result = agent.process(task)
            >>> print(result.output["response"])  # LLM's answer
        """
        # Extract user message from payload
        payload = task.payload
        if not isinstance(payload, dict):
            raise ValueError(f"Task payload must be a dict, got {type(payload).__name__}")

        user_message = payload.get("user_message")
        if not user_message:
            raise ValueError(
                "Task payload must contain 'user_message' field. "
                f"Got payload keys: {list(payload.keys())}"
            )

        # Determine model to use
        model_to_use = payload.get("model") or self.model

        # Build message history
        messages = self._build_messages(user_message, payload.get("context"))

        # Log the interaction
        logger.info(
            f"AGENT: {self.agent_id} processing task {task.id} "
            f"(user_message length={len(user_message)}, model={model_to_use})"
        )
        logger.debug(f"AGENT: Messages to LLM: {messages}")

        try:
            # Call LLM provider
            response = self.provider.chat(messages, model=model_to_use)

            logger.info(f"AGENT: {self.agent_id} received LLM response (length={len(response)})")
            logger.debug(f"AGENT: LLM response: {response}")

            # Check if response contains tool call
            tool_result = None
            if self.tool_registry:
                tool_call_data = self._extract_tool_call(response)
                if tool_call_data:
                    logger.info(f"AGENT: {self.agent_id} detected tool call in response")
                    tool_result = self._execute_tool_call(tool_call_data)

            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=True,
                output={
                    "response": response,
                    "model_used": model_to_use or "default",
                    "provider": self.provider.__class__.__name__,
                    "tool_call": tool_result,  # None if no tool call
                },
            )

        except Exception as e:
            logger.error(f"AGENT: {self.agent_id} LLM call failed for task {task.id}: {e}")

            # Return AgentResponse with failure status instead of raising
            error_msg = f"LLM call failed: {e!s}"
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=False,
                output=None,
                error=error_msg,
                metadata={
                    "provider": self.provider.__class__.__name__,
                    "original_error_type": type(e).__name__,
                },
            )

    def _build_messages(
        self, user_message: str, context: dict | None = None
    ) -> list[dict[str, str]]:
        """
        Build the message list for the LLM provider.

        Args:
            user_message: The user's message
            context: Optional context to include in system message

        Returns:
            List of message dicts with 'role' and 'content' keys

        Example:
            >>> messages = agent._build_messages("Hello", {"mode": "friendly"})
            >>> print(messages[0]["role"])  # "system"
            >>> print(messages[1]["role"])  # "user"
        """
        messages = []

        # Add system message
        system_content = self._system_prompt

        # Add tool descriptions if tool registry available
        if self.tool_registry and len(self.tool_registry) > 0:
            tool_prompt = self.tool_registry.to_llm_prompt()
            system_content = f"{system_content}\n\n{tool_prompt}"

        if context:
            # Include context in system message
            context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
            system_content = f"{system_content}\n\nContext:\n{context_str}"

        messages.append({"role": "system", "content": system_content})

        # Add user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _extract_tool_call(self, response: str) -> dict[str, Any] | None:
        """
        Extract tool call from LLM response.

        Looks for JSON object with format: {"tool": "name", "parameters": {...}}

        Args:
            response: LLM response text

        Returns:
            dict with tool call data, or None if no tool call found

        Example:
            >>> response = '{"tool": "read_file", "parameters": {"path": "/tmp/test.txt"}}'
            >>> call = agent._extract_tool_call(response)
            >>> print(call["tool"])  # "read_file"
        """
        # Try to parse entire response as JSON first
        try:
            data = json.loads(response.strip())
            if isinstance(data, dict) and "tool" in data and "parameters" in data:
                return data
        except json.JSONDecodeError:
            pass

        # Fallback: Try to find JSON object with balanced braces
        brace_depth = 0
        json_start = -1

        for i, char in enumerate(response):
            if char == "{":
                if brace_depth == 0:
                    json_start = i
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth == 0 and json_start >= 0:
                    # Found complete JSON object
                    json_str = response[json_start : i + 1]
                    try:
                        data = json.loads(json_str)
                        if isinstance(data, dict) and "tool" in data and "parameters" in data:
                            return data
                    except json.JSONDecodeError:
                        pass
                    json_start = -1

        return None

    def _execute_tool_call(self, tool_call_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a tool call via the tool registry.

        Args:
            tool_call_data: {"tool": "name", "parameters": {...}}

        Returns:
            dict with tool execution result

        Example:
            >>> call_data = {"tool": "read_file", "parameters": {"path": "/tmp/test.txt"}}
            >>> result = agent._execute_tool_call(call_data)
            >>> print(result["success"])  # True
        """
        # Import here to avoid circular dependency
        from vibe_core.tools.tool_protocol import ToolCall

        tool_name = tool_call_data["tool"]
        parameters = tool_call_data["parameters"]

        logger.info(f"AGENT: {self.agent_id} executing tool call: {tool_name}")

        # Create ToolCall object
        tool_call = ToolCall(tool_name=tool_name, parameters=parameters)

        # Execute via registry
        result = self.tool_registry.execute(tool_call)

        logger.info(
            f"AGENT: {self.agent_id} tool call completed "
            f"(tool={tool_name}, success={result.success})"
        )

        # Convert ToolResult to dict
        return {
            "tool": tool_name,
            "parameters": parameters,
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata,
        }

    def update_system_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt for this agent.

        Args:
            new_prompt: New system prompt to use

        Example:
            >>> agent.update_system_prompt("You are now very formal.")
        """
        self._system_prompt = new_prompt
        logger.info(f"AGENT: Updated system prompt for {self.agent_id}")
