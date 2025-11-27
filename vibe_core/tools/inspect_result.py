"""
InspectResultTool - Agent tool for querying task results from ledger (ARCH-026 Phase 4).

This module provides a Tool that agents can use to query the results of
previously submitted tasks. This is the "Missing Link" for Result Retrieval.

When an agent delegates a task to another agent, it gets a task_id back.
But how does it find the result? This tool answers that question.

Design:
- Works with the kernel's ledger to fetch task records
- Returns structured result information (status, output, error)
- Useful for synchronization workflows ("wait for result, then continue")
- Works standalone or integrated with ToolRegistry

Example:
    >>> # Agent submits task
    >>> task = Task(agent_id="specialist-planning", payload={...})
    >>> task_id = kernel.submit(task)
    >>>
    >>> # Later, agent queries the result
    >>> tool = InspectResultTool(kernel)
    >>> result = tool.execute({"task_id": task_id})
    >>> print(result.output["status"])  # "COMPLETED"
"""

from typing import Any

from vibe_core.tools.tool_protocol import Tool, ToolResult


class InspectResultTool(Tool):
    """
    Tool for querying task results from the kernel's ledger (ARCH-026 Phase 4).

    This enables agents to:
    1. Submit a task to another agent
    2. Get a task_id back
    3. Use this tool to poll for results
    4. Continue based on result status

    Design:
    - Queries kernel.ledger.get_task(task_id)
    - Returns structured result information
    - Safe to use (handles missing tasks gracefully)
    - Useful for synchronization/orchestration workflows

    Example:
        >>> from vibe_core.kernel import VibeKernel
        >>> kernel = VibeKernel(":memory:")
        >>> tool = InspectResultTool(kernel)
        >>>
        >>> # Suppose task-123 was executed
        >>> result = tool.execute({"task_id": "task-123"})
        >>>
        >>> if result.success:
        ...     print(result.output["status"])  # "COMPLETED"
        ...     print(result.output["output"])  # Agent's response
    """

    def __init__(self, kernel):
        """
        Initialize the tool with a kernel reference.

        Args:
            kernel: VibeKernel instance to query results from

        Example:
            >>> kernel = VibeKernel()
            >>> tool = InspectResultTool(kernel)
        """
        self.kernel = kernel

    @property
    def name(self) -> str:
        """Return the tool name."""
        return "inspect_result"

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return (
            "Query the result of a task from the kernel ledger. "
            "Use this after submitting a task to another agent "
            "to check if it has completed and retrieve the result."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """
        Return JSON Schema for the tool's parameters.

        Returns:
            dict: JSON Schema describing the tool's input parameters
        """
        return {
            "task_id": {
                "type": "string",
                "required": True,
                "description": "The task ID to query (returned from kernel.submit())",
            },
            "include_input": {
                "type": "boolean",
                "required": False,
                "default": False,
                "description": "If True, include the original task input payload",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate tool parameters.

        Args:
            parameters: Tool parameters dict

        Raises:
            ValueError: If required parameters missing or invalid
            TypeError: If parameters have wrong type
        """
        if "task_id" not in parameters:
            raise ValueError("Missing required parameter: task_id")

        task_id = parameters["task_id"]
        if not isinstance(task_id, str) or not task_id.strip():
            raise TypeError("task_id must be a non-empty string")

        # Validate optional include_input parameter
        if "include_input" in parameters:
            include_input = parameters["include_input"]
            if not isinstance(include_input, bool):
                raise TypeError("include_input must be a boolean")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute the tool: query a task result from the ledger.

        Parameters:
        - task_id (required): The task ID to look up
        - include_input (optional): If True, include the original task input (default: False)

        Returns:
            ToolResult with success=True and output containing:
            - task_id: The queried task ID
            - status: COMPLETED, FAILED, STARTED, or NOT_FOUND
            - output: Agent's response (if COMPLETED)
            - error: Error message (if FAILED)
            - timestamp: When the task was recorded
            - input_payload: Original task input (if include_input=True)

        Example:
            >>> result = tool.execute({"task_id": "task-123"})
            >>> if result.success and result.output["status"] == "COMPLETED":
            ...     print(result.output["output"])
        """
        try:
            # Validate parameters first
            self.validate(parameters)

            # Extract parameters
            task_id = parameters.get("task_id")
            include_input = parameters.get("include_input", False)

            # Query the ledger
            record = self.kernel.ledger.get_task(task_id)

            if record is None:
                return ToolResult(
                    success=True,
                    output={
                        "task_id": task_id,
                        "status": "NOT_FOUND",
                        "error": f"No task record found for task_id={task_id}",
                    },
                )

            # Build result output
            output = {
                "task_id": task_id,
                "status": record.get("status"),
                "timestamp": record.get("timestamp"),
            }

            # Add result data based on status
            if record.get("status") == "COMPLETED":
                output["output"] = record.get("output_result")
            elif record.get("status") == "FAILED":
                output["error"] = record.get("error_message")
            elif record.get("status") == "STARTED":
                output["message"] = "Task is still executing"

            # Optionally include input
            if include_input:
                output["input_payload"] = record.get("input_payload")

            return ToolResult(success=True, output=output)

        except (ValueError, TypeError) as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Invalid parameters: {e}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Error querying task result: {e}",
            )
