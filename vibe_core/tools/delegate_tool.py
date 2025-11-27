"""
DelegateTool - ARCH-037: Inter-Agent Communication

Allows the Operator to delegate tasks to specialist agents.

This is the "intercom" that enables the Commander (Operator) to assign
work to the Crew (Specialists). Without this, the Operator tries to do
everything itself instead of leveraging domain expertise.

Architecture:
- Operator sees "delegate_task" in its tool list
- Operator calls: {"tool": "delegate_task", "parameters": {"agent_id": "specialist-planning", ...}}
- DelegateTool calls: kernel.submit(agent_id, payload)
- Kernel dispatches to SpecialistFactoryAgent
- Factory creates Specialist instance with mission_id
- Specialist executes and returns result

Example Flow:
    User: "Plan a Python hello world project"
    Operator: "I'll delegate to specialist-planning"
    Operator calls: delegate_task(agent_id="specialist-planning", payload={...})
    DelegateTool: Submits task to kernel
    Kernel: Routes to planning factory
    PlanningSpecialist: Generates plan.json
    DelegateTool: Returns {"success": True, "task_id": "xyz"}
    Operator: "Task delegated successfully"

Why This Matters:
- Enables specialization (Planning vs Coding vs Testing)
- Reduces cognitive load on Operator (no need to be expert at everything)
- Enables parallel execution (future: delegate multiple tasks concurrently)
- Foundation for Mission Architecture (Phase 4)
"""

import logging
from typing import TYPE_CHECKING, Any

from vibe_core.scheduling import Task
from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.kernel import VibeKernel

logger = logging.getLogger(__name__)


class DelegateTool(Tool):
    """
    Tool for delegating tasks to other agents.

    This tool allows the Operator to submit tasks to specialists via
    the kernel's task dispatch system.

    Security:
    - Validates that agent_id exists in kernel registry
    - Requires mission_id in payload (prevents unbounded task creation)
    - Logs all delegations for audit trail

    Example:
        >>> kernel = boot_kernel()
        >>> tool = DelegateTool()
        >>> tool.set_kernel(kernel)
        >>> result = tool.execute({
        ...     "agent_id": "specialist-planning",
        ...     "payload": {
        ...         "mission_id": 42,
        ...         "mission_uuid": "abc-123",
        ...         "phase": "PLANNING",
        ...         "project_root": "/tmp/project",
        ...         "metadata": {}
        ...     }
        ... })
        >>> print(result.success)  # True
        >>> print(result.output["task_id"])  # Task ID in ledger
    """

    def __init__(self):
        """
        Initialize DelegateTool without kernel reference (Late Binding).

        The kernel is injected AFTER construction via set_kernel() to break
        the circular dependency:
        - Kernel needs Agent
        - Agent needs ToolRegistry
        - DelegateTool needs Kernel

        Solution: Tool initializes without kernel, then kernel is injected
        after kernel boot via set_kernel(kernel).
        """
        self.kernel: VibeKernel | None = None
        logger.info("DelegateTool: Initialized (kernel will be injected via set_kernel)")

    def set_kernel(self, kernel: "VibeKernel") -> None:
        """
        Inject kernel reference (Late Binding).

        This method is called after kernel boot to provide the kernel
        reference without creating circular dependencies.

        Args:
            kernel: VibeKernel instance (for task submission)
        """
        self.kernel = kernel
        logger.info("DelegateTool: Kernel injected successfully")

    @property
    def name(self) -> str:
        return "delegate_task"

    @property
    def description(self) -> str:
        return (
            "Delegate a task to another agent (specialist). "
            "Use this to assign work to domain experts like 'specialist-planning', "
            "'specialist-coding', or 'specialist-testing'. "
            "Returns task_id for tracking."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "agent_id": {
                "type": "string",
                "required": True,
                "description": "ID of agent to delegate to (e.g., 'specialist-planning')",
            },
            "payload": {
                "type": "object",
                "required": True,
                "description": (
                    "Task payload containing mission context. "
                    "Must include: mission_id, mission_uuid, phase, project_root"
                ),
                "properties": {
                    "mission_id": {
                        "type": "integer",
                        "required": True,
                        "description": "Mission database ID",
                    },
                    "mission_uuid": {
                        "type": "string",
                        "required": True,
                        "description": "Mission UUID",
                    },
                    "phase": {
                        "type": "string",
                        "required": True,
                        "description": "SDLC phase (PLANNING, CODING, TESTING, etc.)",
                    },
                    "project_root": {
                        "type": "string",
                        "required": False,
                        "description": "Project root directory (default: current directory)",
                    },
                    "metadata": {
                        "type": "object",
                        "required": False,
                        "description": "Additional mission metadata",
                    },
                },
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate delegation parameters.

        Checks:
        1. agent_id is present and is a string
        2. payload is present and is a dict
        3. payload contains required fields (mission_id, phase)
        4. agent_id exists in kernel registry (security: no delegation to unknown agents)

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        # Check agent_id
        if "agent_id" not in parameters:
            raise ValueError("Missing required parameter: agent_id")

        agent_id = parameters["agent_id"]
        if not isinstance(agent_id, str):
            raise TypeError(f"agent_id must be a string, got {type(agent_id).__name__}")

        if not agent_id.strip():
            raise ValueError("agent_id cannot be empty")

        # Check payload
        if "payload" not in parameters:
            raise ValueError("Missing required parameter: payload")

        payload = parameters["payload"]
        if not isinstance(payload, dict):
            raise TypeError(f"payload must be a dict, got {type(payload).__name__}")

        # Check required payload fields
        required_fields = ["mission_id", "mission_uuid", "phase"]
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"payload missing required field: {field}")

        # Validate mission_id type
        mission_id = payload["mission_id"]
        if not isinstance(mission_id, int):
            raise TypeError(
                f"payload.mission_id must be an integer, got {type(mission_id).__name__}"
            )

        # Security: Verify agent exists in kernel registry
        if agent_id not in self.kernel.agent_registry:
            available_agents = list(self.kernel.agent_registry.keys())
            raise ValueError(
                f"Unknown agent_id: {agent_id}. Available agents: {', '.join(available_agents)}"
            )

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute task delegation.

        Workflow:
        1. Extract agent_id and payload
        2. Create Task object
        3. Submit to kernel via kernel.submit()
        4. Return task_id for tracking

        Args:
            parameters: {
                "agent_id": "specialist-planning",
                "payload": {"mission_id": 42, "phase": "PLANNING", ...}
            }

        Returns:
            ToolResult with task_id or error

        Example:
            >>> result = tool.execute({
            ...     "agent_id": "specialist-planning",
            ...     "payload": {"mission_id": 42, "phase": "PLANNING"}
            ... })
            >>> if result.success:
            ...     print(f"Task delegated: {result.output['task_id']}")
        """
        agent_id = parameters["agent_id"]
        payload = parameters["payload"]

        try:
            # Create task
            task = Task(agent_id=agent_id, payload=payload)

            # Submit to kernel
            task_id = self.kernel.submit(task)

            logger.info(
                f"DelegateTool: Delegated task to {agent_id} "
                f"(task_id={task_id}, mission_id={payload.get('mission_id')})"
            )

            return ToolResult(
                success=True,
                output={
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "status": "delegated",
                    "message": f"Task delegated to {agent_id}",
                },
                metadata={
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "mission_id": payload.get("mission_id"),
                    "phase": payload.get("phase"),
                },
            )

        except Exception as e:
            error_msg = f"Failed to delegate task: {type(e).__name__}: {e!s}"
            logger.error(
                f"DelegateTool: {error_msg} (agent_id={agent_id}, payload={payload})",
                exc_info=True,
            )
            return ToolResult(success=False, error=error_msg)
