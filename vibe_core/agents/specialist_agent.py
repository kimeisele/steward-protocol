"""
SpecialistAgent Adapter - Bridge between Kernel and Specialists (ARCH-026)

This module implements the adapter pattern that allows BaseSpecialist
subclasses to work with the VibeKernel dispatch mechanism.

Architecture:
- Wraps BaseSpecialist to implement VibeAgent protocol
- Converts Task → MissionContext (for specialist execution)
- Converts SpecialistResult → Task result (for kernel recording)
- Manages specialist lifecycle: on_start(), execute(), on_complete(), on_error()
- Validates preconditions before execution

This enables the Hybrid Agent Pattern:
    Kernel → SpecialistAgent (adapter) → BaseSpecialist (workflow executor)

All specialists (Planning, Coding, Testing, Deployment, Maintenance) can now
be orchestrated by the Kernel using the same dispatch mechanism as LLM agents.
"""

import logging
from pathlib import Path

from vibe_core.agent_protocol import AgentResponse, VibeAgent
from vibe_core.scheduling import Task
from vibe_core.specialists.base_specialist import BaseSpecialist, MissionContext, SpecialistResult

logger = logging.getLogger(__name__)


class SpecialistAgent(VibeAgent):
    """
    Adapter that wraps BaseSpecialist to implement VibeAgent protocol.

    This enables specialists to be dispatched by the Kernel alongside
    LLM agents, creating a unified hybrid agent system.

    Architecture:
    - Implements VibeAgent (agent_id property + process method)
    - Wraps a BaseSpecialist instance
    - Converts Task payload → MissionContext
    - Converts SpecialistResult → dict result
    - Handles lifecycle: preconditions, start, execute, complete/error

    Example:
        >>> from vibe_core.specialists.planning import PlanningSpecialist
        >>> from vibe_core.store.sqlite_store import SQLiteStore
        >>> from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
        >>>
        >>> store = SQLiteStore(":memory:")
        >>> guard = ToolSafetyGuard()
        >>> specialist = PlanningSpecialist("PLANNING", mission_id=1, store, guard)
        >>> agent = SpecialistAgent(specialist)
        >>>
        >>> # Register with kernel
        >>> kernel.register_agent(agent)
        >>>
        >>> # Submit task
        >>> task = Task(
        ...     agent_id="specialist-planning",
        ...     payload={
        ...         "mission_id": 1,
        ...         "mission_uuid": "abc-123",
        ...         "phase": "PLANNING",
        ...         "project_root": "/path/to/project",
        ...         "metadata": {}
        ...     }
        ... )
        >>> result = kernel.submit(task)
        >>> kernel.tick()  # Dispatches to SpecialistAgent → PlanningSpecialist
    """

    def __init__(self, specialist: BaseSpecialist):
        """
        Initialize the adapter with a specialist instance.

        Args:
            specialist: BaseSpecialist subclass instance to wrap
                        (PlanningSpecialist, CodingSpecialist, etc.)

        Example:
            >>> specialist = PlanningSpecialist(...)
            >>> agent = SpecialistAgent(specialist)
            >>> print(agent.agent_id)  # "specialist-planning"
        """
        if not isinstance(specialist, BaseSpecialist):
            raise TypeError(
                f"specialist must be a BaseSpecialist instance, got {type(specialist).__name__}"
            )

        self.specialist = specialist

        logger.info(
            f"SpecialistAgent: Wrapped {specialist.__class__.__name__} "
            f"(role={specialist.role}, agent_id={self.agent_id})"
        )

    @property
    def agent_id(self) -> str:
        """
        Return the agent ID for kernel registration.

        Format: "specialist-{role}" (lowercase)
        Examples:
            - PlanningSpecialist → "specialist-planning"
            - CodingSpecialist → "specialist-coding"
            - TestingSpecialist → "specialist-testing"

        Returns:
            str: Unique agent identifier
        """
        return f"specialist-{self.specialist.role.lower()}"

    @property
    def capabilities(self) -> list[str]:
        """
        Return list of capabilities provided by this specialist.

        Specialists describe what they do via their role and lifecycle:
        - The role defines the primary capability (e.g., "planning", "coding")
        - Additional capabilities can include workflow phases or domain actions

        For now, capabilities are derived from the specialist's role.
        Future: can be extended to include sub-capabilities from metadata.

        Returns:
            list[str]: List of capability names

        Example:
            >>> specialist = PlanningSpecialist(...)
            >>> agent = SpecialistAgent(specialist)
            >>> print(agent.capabilities)  # ["planning"]

            >>> specialist = CodingSpecialist(...)
            >>> agent = SpecialistAgent(specialist)
            >>> print(agent.capabilities)  # ["coding"]
        """
        return [self.specialist.role.lower()]

    def process(self, task: Task) -> AgentResponse:
        """
        Process a task by executing the wrapped specialist.

        Workflow:
            1. Convert Task payload → MissionContext
            2. Validate preconditions (fail fast if not met)
            3. Call specialist.on_start(context)
            4. Execute specialist.execute(context)
            5. Call specialist.on_complete(context, result) if successful
            6. Call specialist.on_error(context, error) if failed
            7. Convert SpecialistResult → AgentResponse result for kernel

        Expected task payload format:
        {
            "mission_id": int,           # Required: mission database ID
            "mission_uuid": str,         # Required: mission UUID
            "phase": str,                # Required: SDLC phase (PLANNING, CODING, etc.)
            "project_root": str,         # Optional: project directory path
            "metadata": dict             # Optional: additional context
        }

        Args:
            task: Task submitted to kernel

        Returns:
            AgentResponse: Standardized response with:
                agent_id: This specialist agent's ID
                task_id: The task ID
                success: Whether execution succeeded
                output: Contains next_phase, artifacts, decisions, specialist, role
                error: Error message if success is False

        Raises:
            ValueError: If task payload is invalid or preconditions not met
            Exception: If specialist execution fails (propagated from specialist)

        Example:
            >>> task = Task(
            ...     agent_id="specialist-planning",
            ...     payload={"mission_id": 1, "phase": "PLANNING", ...}
            ... )
            >>> result = agent.process(task)
            >>> print(result.success)  # True
            >>> print(result.output["next_phase"])  # "CODING"
        """
        # Step 1: Convert Task → MissionContext
        try:
            context = self._task_to_context(task)
        except KeyError as e:
            error_msg = f"Invalid task payload: missing required field {e}"
            logger.error(f"SpecialistAgent: {error_msg} (task_id={task.id})")
            raise ValueError(error_msg) from e

        logger.info(
            f"SpecialistAgent: Processing task {task.id} with "
            f"{self.specialist.__class__.__name__} (phase={context.phase})"
        )

        # Step 2: Validate preconditions
        if not self.specialist.validate_preconditions(context):
            error_msg = (
                f"Preconditions not met for {self.specialist.__class__.__name__} "
                f"(phase={context.phase}, mission_id={context.mission_id})"
            )
            logger.error(f"SpecialistAgent: {error_msg}")

            # Return error result (don't raise - let kernel record it)
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=False,
                output={
                    "next_phase": None,
                    "artifacts": [],
                    "decisions": [],
                    "specialist": self.specialist.__class__.__name__,
                    "role": self.specialist.role,
                },
                error=error_msg,
            )

        # Step 3: Execute lifecycle
        self.specialist.on_start(context)

        try:
            # Step 4: Execute specialist workflow
            result = self.specialist.execute(context)

            # Step 5: Complete successfully
            self.specialist.on_complete(context, result)

            logger.info(
                f"SpecialistAgent: Task {task.id} completed successfully "
                f"(next_phase={result.next_phase}, artifacts={len(result.artifacts)})"
            )

            # Convert SpecialistResult → AgentResponse
            return self._result_to_response(task, result)

        except Exception as e:
            # Step 6: Handle error
            logger.error(
                f"SpecialistAgent: Task {task.id} failed with {type(e).__name__}: {e}",
                exc_info=True,
            )

            # Let specialist handle error (for cleanup/logging)
            self.specialist.on_error(context, e)

            # Return AgentResponse with failure status instead of raising
            error_msg = f"{type(e).__name__}: {e}"
            return AgentResponse(
                agent_id=self.agent_id,
                task_id=task.id,
                success=False,
                output={
                    "next_phase": None,
                    "artifacts": [],
                    "decisions": [],
                    "specialist": self.specialist.__class__.__name__,
                    "role": self.specialist.role,
                },
                error=error_msg,
                metadata={"error_type": type(e).__name__},
            )

    def _task_to_context(self, task: Task) -> MissionContext:
        """
        Convert Task payload to MissionContext.

        Args:
            task: Task with payload dict

        Returns:
            MissionContext: Context for specialist execution

        Raises:
            KeyError: If required field missing in payload
            TypeError: If payload is not a dict
        """
        payload = task.payload

        if not isinstance(payload, dict):
            raise TypeError(f"Task payload must be a dict, got {type(payload).__name__}")

        # Extract required fields (will raise KeyError if missing)
        mission_id = payload["mission_id"]
        mission_uuid = payload["mission_uuid"]
        phase = payload["phase"]

        # Extract optional fields
        project_root_str = payload.get("project_root", ".")
        metadata = payload.get("metadata", {})

        # Convert to MissionContext
        return MissionContext(
            mission_id=mission_id,
            mission_uuid=mission_uuid,
            phase=phase,
            project_root=Path(project_root_str),
            metadata=metadata,
        )

    def _result_to_response(self, task: Task, result: SpecialistResult) -> AgentResponse:
        """
        Convert SpecialistResult to AgentResponse for kernel recording.

        Args:
            task: The task being processed
            result: SpecialistResult from specialist.execute()

        Returns:
            AgentResponse: Result in kernel-compatible standardized format
        """
        return AgentResponse(
            agent_id=self.agent_id,
            task_id=task.id,
            success=result.success,
            output={
                "next_phase": result.next_phase,
                "artifacts": result.artifacts,
                "decisions": result.decisions,
                "specialist": self.specialist.__class__.__name__,
                "role": self.specialist.role,
            },
            error=result.error,
        )

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"SpecialistAgent(agent_id={self.agent_id!r}, "
            f"specialist={self.specialist.__class__.__name__})"
        )
