#!/usr/bin/env python3
"""
BaseSpecialist - Abstract Base Class for HAP (Hierarchical Agent Pattern)
ARCH-005: Design BaseSpecialist Interface

This module defines the contract that all specialist agents must implement.
Specialists are phase-specific agents that handle distinct SDLC phases:
    - PlanningSpecialist (PLANNING phase)
    - CodingSpecialist (CODING phase)
    - TestingSpecialist (TESTING phase)
    - DeploymentSpecialist (DEPLOYMENT phase)
    - MaintenanceSpecialist (MAINTENANCE phase)

Architecture Alignment (4D Hypercube):
    - **GAD (Global)**: Specialists implement specific pillar capabilities
    - **LAD (Layer)**: Specialists adapt behavior based on infrastructure layer
    - **VAD (Verification)**: Specialists validate preconditions/postconditions
    - **PAD (Playbook)**: Specialists follow phase-specific workflow choreography

Design Principles:
    1. **Explicit over Implicit**: All dependencies injected in __init__
    2. **Fail Fast**: validate_preconditions() must be called before execute()
    3. **Persistent State**: All decisions logged to SQLite for auditability
    4. **Tool Safety**: All tool calls guarded by ToolSafetyGuard
    5. **Playbook-Driven**: Workflow logic loaded from playbook YAML files

See: docs/architecture/SPECIALIST_AGENT_CONTRACT.md for implementation guide
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


@dataclass
class MissionContext:
    """
    Immutable context passed to specialist for execution.

    Contains all information needed to execute a phase-specific workflow:
        - mission_id: Database primary key
        - mission_uuid: External UUID identifier
        - phase: Current SDLC phase (PLANNING, CODING, etc.)
        - project_root: Path to project workspace
        - metadata: Additional phase-specific data
    """

    mission_id: int
    mission_uuid: str
    phase: str
    project_root: Path
    metadata: dict[str, Any]


@dataclass
class SpecialistResult:
    """
    Result of specialist execution.

    Returned by execute() to communicate outcome to orchestrator:
        - success: Whether execution completed successfully
        - next_phase: Recommended next SDLC phase (or None to stay)
        - artifacts: List of generated artifact paths
        - decisions: Key decisions made during execution
        - error: Error message if success=False
    """

    success: bool
    next_phase: str | None = None
    artifacts: list[str] = None
    decisions: list[dict[str, Any]] = None
    error: str | None = None

    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.artifacts is None:
            self.artifacts = []
        if self.decisions is None:
            self.decisions = []


class BaseSpecialist(ABC):
    """
    Abstract base class for all specialist agents (HAP pattern).

    Responsibilities:
        1. Execute phase-specific SDLC workflows (PLANNING, CODING, etc.)
        2. Validate preconditions before execution
        3. Persist state and decisions to SQLite
        4. Load state for crash recovery
        5. Enforce tool safety via ToolSafetyGuard
        6. Load playbook-driven workflow logic

    Lifecycle:
        1. __init__() - Inject dependencies (SQLiteStore, ToolSafetyGuard)
        2. load_state() - Restore from crash/previous session
        3. validate_preconditions() - Check if phase can execute
        4. on_start() - Setup hook before execution
        5. execute() - Main workflow logic (MUST BE IMPLEMENTED)
        6. persist_state() - Save decisions/artifacts to DB
        7. on_complete() - Cleanup hook after success
        8. on_error() - Error recovery hook

    Example:
        >>> class PlanningSpecialist(BaseSpecialist):
        ...     def execute(self, context: MissionContext) -> SpecialistResult:
        ...         # Planning workflow logic here
        ...         return SpecialistResult(success=True, next_phase="CODING")
        ...
        >>> store = SQLiteStore(".vibe/state/vibe_agency.db")
        >>> guard = ToolSafetyGuard()
        >>> specialist = PlanningSpecialist("PLANNING", mission_id=1, store, guard)
        >>> context = MissionContext(...)
        >>> if specialist.validate_preconditions(context):
        ...     result = specialist.execute(context)
    """

    def __init__(
        self,
        role: str,
        mission_id: int,
        sqlite_store: SQLiteStore,
        tool_safety_guard: ToolSafetyGuard,
        playbook_root: Path | None = None,
    ):
        """
        Initialize specialist with required dependencies.

        Args:
            role: Specialist role (e.g., "PLANNING", "CODING")
            mission_id: Database primary key for current mission
            sqlite_store: SQLite persistence layer (REQUIRED)
            tool_safety_guard: Tool safety enforcement layer (REQUIRED)
            playbook_root: Path to playbook directory (auto-detected if None)

        Raises:
            ValueError: If role is empty or mission_id is invalid
        """
        if not role:
            raise ValueError("role is REQUIRED and cannot be empty")
        if mission_id <= 0:
            raise ValueError(f"mission_id must be positive, got: {mission_id}")

        self.role = role
        self.mission_id = mission_id
        self.sqlite_store = sqlite_store
        self.tool_safety_guard = tool_safety_guard

        # Auto-detect playbook root if not provided
        if playbook_root is None:
            playbook_root = self._detect_playbook_root()
        self.playbook_root = playbook_root

        # Lifecycle tracking
        self.state: dict[str, Any] = {}
        self.started_at: str | None = None
        self.completed_at: str | None = None

        logger.info(f"Initialized {self.__class__.__name__} (role={role}, mission_id={mission_id})")

    def _detect_playbook_root(self) -> Path:
        """
        Auto-detect playbook directory.

        Searches for:
            1. agency_os/playbooks/ (project structure)
            2. playbooks/ (workspace root)

        Returns:
            Path to playbook directory or a default placeholder if not found.
            (Playbooks are optional - some specialists may not need them)
        """
        # Try project structure first
        current = Path(__file__).resolve()
        for parent in [current.parent, *current.parents]:
            candidate = parent / "agency_os" / "playbooks"
            if candidate.exists():
                return candidate

        # Try workspace root
        workspace_playbooks = Path.cwd() / "playbooks"
        if workspace_playbooks.exists():
            return workspace_playbooks

        # Fallback: Return a path that may not exist (some specialists don't need playbooks)
        # This allows specialists to initialize without failing, but _load_playbook will fail
        # if actually called on a specialist that needs playbooks
        logger.debug("Playbook directory not found. Using fallback (playbooks may not be required)")
        return Path.cwd() / "playbooks"

    # ========================================================================
    # ABSTRACT METHODS - MUST BE IMPLEMENTED BY SUBCLASSES
    # ========================================================================

    @abstractmethod
    def execute(self, context: MissionContext) -> SpecialistResult:
        """
        Execute the specialist's phase-specific workflow.

        This is the main entry point for specialist logic. Must be implemented
        by all concrete specialists (PlanningSpecialist, CodingSpecialist, etc.).

        Workflow:
            1. Load playbook for current phase
            2. Execute workflow steps (call tools, make decisions)
            3. Log decisions to SQLite via _log_decision()
            4. Generate artifacts (code, docs, configs)
            5. Return result with success status and next phase

        Args:
            context: Immutable mission context (mission_id, phase, metadata)

        Returns:
            SpecialistResult with success status, artifacts, decisions

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute(context)")

    @abstractmethod
    def validate_preconditions(self, context: MissionContext) -> bool:
        """
        Validate that preconditions are met before execution.

        This method MUST be called before execute(). It checks:
            - Required files exist
            - Dependencies are installed
            - Previous phase completed successfully
            - Budget constraints are satisfied

        Args:
            context: Mission context with phase and metadata

        Returns:
            True if preconditions met, False otherwise

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement validate_preconditions(context)"
        )

    # ========================================================================
    # PERSISTENCE - IMPLEMENTED WITH SENSIBLE DEFAULTS
    # ========================================================================

    def persist_state(self) -> None:
        """
        Persist specialist state to SQLite.

        Default implementation stores:
            - self.state dict as JSON in decisions table
            - Completion timestamp
            - Role and mission_id

        Override to add specialist-specific state (e.g., intermediate artifacts).
        """
        if not self.state:
            logger.debug(f"{self.role}: No state to persist (state dict is empty)")
            return

        # Log state as a decision (generic persistence)
        self._log_decision(
            decision_type="STATE_CHECKPOINT",
            rationale="Specialist state persisted",
            data=self.state,
        )

        logger.info(f"{self.role}: State persisted to SQLite (mission_id={self.mission_id})")

    def load_state(self) -> dict[str, Any]:
        """
        Load specialist state from SQLite (crash recovery).

        Default implementation loads most recent STATE_CHECKPOINT decision.
        Override to implement custom state recovery logic.

        Returns:
            State dict (empty dict if no saved state)
        """
        try:
            # Query most recent STATE_CHECKPOINT decision
            decisions = self.sqlite_store.get_decisions_for_mission(self.mission_id)

            # Filter for STATE_CHECKPOINT decisions, most recent first
            checkpoints = [d for d in decisions if d.get("decision_type") == "STATE_CHECKPOINT"]

            if not checkpoints:
                logger.info(f"{self.role}: No saved state found (clean start)")
                return {}

            # Load most recent checkpoint
            latest = checkpoints[-1]  # Assuming chronological order
            state_data = latest.get("context", {})

            self.state = state_data
            logger.info(f"{self.role}: State loaded from SQLite (mission_id={self.mission_id})")

            return state_data

        except Exception as e:
            logger.warning(f"{self.role}: Failed to load state (proceeding with clean state): {e}")
            return {}

    # ========================================================================
    # LIFECYCLE HOOKS - OVERRIDE TO CUSTOMIZE BEHAVIOR
    # ========================================================================

    def on_start(self, context: MissionContext) -> None:
        """
        Hook called before execute() begins.

        Use for:
            - Logging start event
            - Initializing resources
            - Recording start timestamp

        Args:
            context: Mission context
        """
        self.started_at = datetime.utcnow().isoformat() + "Z"
        logger.info(
            f"{self.role}: Starting execution (mission_id={self.mission_id}, phase={context.phase})"
        )

    def on_complete(self, context: MissionContext, result: SpecialistResult) -> None:
        """
        Hook called after successful execute().

        Use for:
            - Logging completion event
            - Cleaning up resources
            - Recording completion timestamp
            - Persisting final state

        Args:
            context: Mission context
            result: Execution result from execute()
        """
        self.completed_at = datetime.utcnow().isoformat() + "Z"
        duration = self._calculate_duration()

        logger.info(
            f"{self.role}: Execution complete "
            f"(mission_id={self.mission_id}, duration={duration}s, "
            f"next_phase={result.next_phase})"
        )

        # Auto-persist state on completion
        self.persist_state()

    def on_error(self, context: MissionContext, error: Exception) -> SpecialistResult:
        """
        Hook called when execute() raises an exception.

        Use for:
            - Logging error details
            - Persisting partial state for recovery
            - Cleaning up resources
            - Returning error result

        Args:
            context: Mission context
            error: Exception that was raised

        Returns:
            SpecialistResult with success=False and error message
        """
        logger.error(
            f"{self.role}: Execution failed (mission_id={self.mission_id}): {error}",
            exc_info=True,
        )

        # Persist partial state for crash recovery
        self.state["error"] = str(error)
        self.state["failed_at"] = datetime.utcnow().isoformat() + "Z"
        self.persist_state()

        return SpecialistResult(success=False, error=f"{self.__class__.__name__} failed: {error}")

    # ========================================================================
    # SHARED UTILITY METHODS
    # ========================================================================

    def _log_decision(
        self, decision_type: str, rationale: str, data: dict[str, Any] | None = None
    ) -> None:
        """
        Log a decision to SQLite for audit trail.

        All significant decisions (architecture choices, tool calls, etc.)
        should be logged using this method for:
            - Debugging ("why did the agent do X?")
            - Auditability (compliance, post-mortems)
            - Learning (training data for future agents)

        Args:
            decision_type: Type of decision (e.g., "ARCHITECTURE_CHOICE", "TOOL_CALL")
            rationale: Human-readable explanation of why decision was made
            data: Additional structured data (optional)
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        self.sqlite_store.record_decision(
            mission_id=self.mission_id,
            decision_type=decision_type,
            rationale=rationale,
            timestamp=timestamp,
            agent_name=self.__class__.__name__,
            context=data or {},
        )

    def _load_playbook(self, playbook_name: str) -> dict[str, Any]:
        """
        Load playbook YAML file for phase-specific workflow.

        Playbooks define time-ordered workflows (PAD - Playbook Architecture).
        They specify:
            - Steps to execute
            - Tools allowed for each step
            - Success criteria
            - Error handling

        Args:
            playbook_name: Playbook filename (e.g., "planning.yaml")

        Returns:
            Parsed playbook dict

        Raises:
            FileNotFoundError: If playbook not found
        """
        playbook_path = self.playbook_root / playbook_name

        if not playbook_path.exists():
            raise FileNotFoundError(f"Playbook not found: {playbook_path}")

        # Import yaml only if needed (not in stdlib)
        try:
            import yaml

            with open(playbook_path) as f:
                playbook = yaml.safe_load(f)

            logger.debug(f"{self.role}: Loaded playbook: {playbook_name}")
            return playbook

        except ImportError:
            # Fallback to JSON if YAML not available
            logger.warning(f"{self.role}: PyYAML not installed, trying JSON fallback")

            json_path = playbook_path.with_suffix(".json")
            if not json_path.exists():
                raise FileNotFoundError(
                    f"Playbook not found (tried .yaml and .json): {playbook_path}"
                )

            with open(json_path) as f:
                return json.load(f)

    def _calculate_duration(self) -> float:
        """
        Calculate execution duration in seconds.

        Returns:
            Duration in seconds (or 0.0 if not started)
        """
        if not self.started_at:
            return 0.0

        if not self.completed_at:
            # Still running - calculate elapsed time
            end = datetime.utcnow()
        else:
            # Completed - calculate total duration
            end = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))

        start = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
        return (end - start).total_seconds()

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    def get_mission_data(self) -> dict[str, Any]:
        """
        Get full mission data from SQLite.

        Returns:
            Mission dict with all fields (phase, status, metadata, etc.)
        """
        mission = self.sqlite_store.get_mission(self.mission_id)
        if not mission:
            raise ValueError(f"Mission not found in database: mission_id={self.mission_id}")
        return mission

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"{self.__class__.__name__}(role={self.role!r}, mission_id={self.mission_id})"

    # ========================================================================
    # LLM INVOCATION UTILITY (ARCH-010: For repair loop and code generation)
    # ========================================================================

    def _invoke_llm(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> str:
        """
        Invoke LLM for code generation, patch generation, or analysis.

        This is a lightweight utility for specialists to call LLM without
        instantiating SimpleLLMAgent. Used by repair loop, code generation, etc.

        Args:
            prompt: Input prompt for LLM
            model: Model to use (default: Claude 3.5 Sonnet)
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Returns:
            LLM response content as string

        Raises:
            Exception: If LLM invocation fails
        """
        try:
            # Import locally to avoid circular imports
            from vibe_core.runtime.llm_client import LLMClient
            from vibe_core.runtime.providers import get_default_provider

            # Get default provider (respects environment variables)
            provider = get_default_provider()

            # Create LLM client with provider
            llm_client = LLMClient(provider=provider)

            # Invoke LLM
            response = llm_client.invoke(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            logger.info(f"LLM invocation successful: {model}")
            return response.content

        except ImportError as e:
            logger.error(f"Failed to import LLM utilities: {e}")
            raise

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise
