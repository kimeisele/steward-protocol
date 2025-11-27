"""
SpecialistFactoryAgent - ARCH-036 (Crew Assembly)
===================================================

Factory agent that creates Specialists on-demand for each task.

Problem:
- Specialists require mission_id and orchestrator at __init__
- We want to register agents at boot time (no mission yet)
- Solution: Factory pattern - create specialist instances per task

Architecture:
- FactoryAgent implements VibeAgent protocol
- Registered once at boot (agent_id = "specialist-planning", etc.)
- Creates fresh Specialist instance for each task
- Specialist is short-lived (task-scoped, not boot-scoped)

Example:
    >>> factory = SpecialistFactoryAgent(
    ...     specialist_class=PlanningSpecialist,
    ...     role="planning",
    ...     sqlite_store=store,
    ...     tool_safety_guard=guard
    ... )
    >>> kernel.register_agent(factory)  # Boot-time registration
    >>> # Later, when task arrives:
    >>> task = Task(agent_id="specialist-planning", payload={...})
    >>> result = kernel.submit(task)
    >>> kernel.tick()  # Factory creates PlanningSpecialist and executes
"""

import logging
from pathlib import Path
from typing import Any

from vibe_core.agent_protocol import VibeAgent
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.scheduling import Task
from vibe_core.specialists.base_specialist import BaseSpecialist
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class SpecialistFactoryAgent(VibeAgent):
    """
    Factory agent that creates Specialists on-demand.

    This agent is registered once at boot and creates fresh Specialist
    instances for each task that arrives.

    Lifecycle:
        1. Boot: Register factory in kernel (no specialist instance yet)
        2. Task arrives: Extract mission_id from payload
        3. Create fresh specialist instance with mission_id
        4. Wrap specialist in SpecialistAgent adapter
        5. Execute specialist.process(task)
        6. Return result
        7. Discard specialist (task-scoped lifetime)

    Why Factory Pattern:
        - Specialists are mission-specific (need mission_id)
        - Kernel needs agents at boot time (no mission yet)
        - Factory bridges the gap: registered early, instantiates late
    """

    def __init__(
        self,
        specialist_class: type[BaseSpecialist],
        role: str,
        sqlite_store: SQLiteStore,
        tool_safety_guard: ToolSafetyGuard,
        playbook_root: Path | None = None,
        orchestrator=None,  # Optional: for specialists that still need it
    ):
        """
        Initialize factory agent.

        Args:
            specialist_class: BaseSpecialist subclass to instantiate
                              (PlanningSpecialist, CodingSpecialist, etc.)
            role: Specialist role ("planning", "coding", etc.)
            sqlite_store: SQLite persistence layer (shared across specialists)
            tool_safety_guard: Safety guard (shared across specialists)
            playbook_root: Playbook directory (optional)
            orchestrator: Legacy orchestrator (optional, for transition period)

        Example:
            >>> factory = SpecialistFactoryAgent(
            ...     specialist_class=PlanningSpecialist,
            ...     role="planning",
            ...     sqlite_store=store,
            ...     tool_safety_guard=guard
            ... )
        """
        if not issubclass(specialist_class, BaseSpecialist):
            raise TypeError(
                f"specialist_class must be a BaseSpecialist subclass, "
                f"got {specialist_class.__name__}"
            )

        self.specialist_class = specialist_class
        self.role = role.lower()
        self.sqlite_store = sqlite_store
        self.tool_safety_guard = tool_safety_guard
        self.playbook_root = playbook_root
        self.orchestrator = orchestrator

        logger.info(
            f"SpecialistFactoryAgent: Initialized factory for "
            f"{specialist_class.__name__} (agent_id={self.agent_id})"
        )

    @property
    def agent_id(self) -> str:
        """
        Return agent ID for kernel registration.

        Format: "specialist-{role}" (lowercase)
        Examples:
            - planning → "specialist-planning"
            - coding → "specialist-coding"
            - testing → "specialist-testing"

        Returns:
            str: Unique agent identifier
        """
        return f"specialist-{self.role}"

    @property
    def capabilities(self) -> list[str]:
        """
        Return the capabilities of this specialist factory.

        The factory provides capabilities based on the specialist class it creates.
        For example:
        - PlanningSpecialist → ["planning", "analysis"]
        - CodingSpecialist → ["coding", "implementation"]
        - TestingSpecialist → ["testing", "validation"]

        Returns:
            list[str]: List of capability names this specialist provides
        """
        # Return the role as the primary capability
        # Additional capabilities could be inferred from specialist_class
        return [self.role]

    def process(self, task: Task) -> dict[str, Any]:
        """
        Process task by creating and executing a Specialist.

        Workflow:
            1. Extract mission_id from task payload
            2. Create fresh specialist instance with mission_id
            3. Wrap specialist in SpecialistAgent adapter
            4. Execute specialist.process(task)
            5. Return result

        Expected task payload:
        {
            "mission_id": int,           # Required
            "mission_uuid": str,         # Required
            "phase": str,                # Required (PLANNING, CODING, etc.)
            "project_root": str,         # Optional
            "metadata": dict             # Optional
        }

        Args:
            task: Task with mission context in payload

        Returns:
            dict: Result from specialist execution

        Raises:
            ValueError: If mission_id missing from payload
            Exception: If specialist execution fails

        Example:
            >>> task = Task(
            ...     agent_id="specialist-planning",
            ...     payload={"mission_id": 42, "phase": "PLANNING", ...}
            ... )
            >>> result = factory.process(task)
            >>> print(result["success"])  # True
        """
        # Step 1: Extract mission_id from payload
        payload = task.payload
        if not isinstance(payload, dict):
            raise TypeError(f"Task payload must be a dict, got {type(payload).__name__}")

        mission_id = payload.get("mission_id")
        if not mission_id:
            raise ValueError(
                f"Task payload missing required field 'mission_id' "
                f"(needed to instantiate {self.specialist_class.__name__})"
            )

        logger.info(
            f"SpecialistFactoryAgent: Creating {self.specialist_class.__name__} "
            f"for mission_id={mission_id} (task_id={task.id})"
        )

        # Step 2: Create fresh specialist instance
        # Note: This specialist is task-scoped (will be discarded after execution)
        specialist = self.specialist_class(
            mission_id=mission_id,
            sqlite_store=self.sqlite_store,
            tool_safety_guard=self.tool_safety_guard,
            orchestrator=self.orchestrator,  # May be None (transitional)
            playbook_root=self.playbook_root,
        )

        # Step 3: Wrap specialist in SpecialistAgent adapter
        # Import here to avoid circular dependency
        from vibe_core.agents.specialist_agent import SpecialistAgent

        specialist_agent = SpecialistAgent(specialist)

        # Step 4: Execute specialist
        logger.debug(
            f"SpecialistFactoryAgent: Delegating to {specialist_agent.agent_id} "
            f"(specialist={self.specialist_class.__name__})"
        )

        result = specialist_agent.process(task)

        logger.info(
            f"SpecialistFactoryAgent: Task {task.id} completed "
            f"(success={result.get('success', False)}, specialist={self.specialist_class.__name__})"
        )

        return result

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"SpecialistFactoryAgent(agent_id={self.agent_id!r}, "
            f"specialist_class={self.specialist_class.__name__})"
        )
