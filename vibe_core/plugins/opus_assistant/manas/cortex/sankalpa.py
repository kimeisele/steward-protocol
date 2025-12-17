"""
OPUS-055: SANKALPA (The Will / The Vow) - Proactive Strategy Module.

Sanskrit: Sankalpa = Solemn vow, determination, will, intention to shape reality.
    "Sankalpa is the seed of action. Plant it with care, and the universe conspires."

SANKALPA transforms MANAS from reactive to proactive:
- Without SANKALPA: System waits for commands
- With SANKALPA: System has GOALS and acts to achieve them

Architecture:
    ┌───────────────────────────────────────────────────────────────┐
    │                    SANKALPA (The Will)                         │
    │                                                                │
    │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐        │
    │   │ Registry    │──▶│ Planner     │──▶│ Intents     │        │
    │   │ (Goals)     │   │ (Strategy)  │   │ (Actions)   │        │
    │   └─────────────┘   └─────────────┘   └─────────────┘        │
    │          │                                    │                │
    │          ▼                                    ▼                │
    │   ┌─────────────────────────────────────────────────────┐    │
    │   │  CognitiveKernel.think() → Proactive Intent Gen     │    │
    │   └─────────────────────────────────────────────────────┘    │
    └───────────────────────────────────────────────────────────────┘

Core Concepts:
    - Mission: High-level goal (e.g., "Maintain Code Health")
    - Strategy: How to achieve mission (e.g., "Weekly Refactor")
    - Trigger: When to act (e.g., "CI green + idle > 1h")
    - Campaign: A running instance of strategy execution

"Give the mind a purpose, and it becomes unstoppable."
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MANAS.Cortex.Sankalpa")


# =============================================================================
# SECTION 1: DATA MODELS
# =============================================================================


class MissionPriority(Enum):
    """Priority of a mission."""

    CRITICAL = "critical"  # Must be done (security, stability)
    HIGH = "high"  # Important for health
    MEDIUM = "medium"  # Nice to have
    LOW = "low"  # Optional improvement


class MissionStatus(Enum):
    """Status of a mission."""

    ACTIVE = "active"  # Mission is being pursued
    PAUSED = "paused"  # Temporarily paused
    COMPLETED = "completed"  # Goal achieved
    ABANDONED = "abandoned"  # Given up


class TriggerType(Enum):
    """Types of triggers that can activate a strategy."""

    TIME_BASED = "time_based"  # Cron-like (daily, weekly, etc.)
    EVENT_BASED = "event_based"  # On specific events
    CONDITION_BASED = "condition_based"  # When conditions met
    IDLE_BASED = "idle_based"  # When system is idle


class StrategyFrequency(Enum):
    """How often a strategy should run."""

    ONCE = "once"  # Run once when triggered
    HOURLY = "hourly"  # Every hour
    DAILY = "daily"  # Once per day
    WEEKLY = "weekly"  # Once per week
    CONTINUOUS = "continuous"  # Always active


@dataclass
class SankalpaTrigger:
    """
    Trigger condition for a strategy.

    Defines when a strategy should activate.
    """

    trigger_type: TriggerType
    # For time-based
    hour: Optional[int] = None  # Hour of day (0-23)
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    # For condition-based
    condition: Optional[str] = None  # Condition expression
    # For idle-based
    idle_minutes: int = 30  # Minimum idle time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_type": self.trigger_type.value,
            "hour": self.hour,
            "day_of_week": self.day_of_week,
            "condition": self.condition,
            "idle_minutes": self.idle_minutes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SankalpaTrigger":
        return cls(
            trigger_type=TriggerType(data.get("trigger_type", "condition_based")),
            hour=data.get("hour"),
            day_of_week=data.get("day_of_week"),
            condition=data.get("condition"),
            idle_minutes=data.get("idle_minutes", 30),
        )


@dataclass
class SankalpaStrategy:
    """
    Strategy for achieving a mission.

    A strategy defines HOW and WHEN to act toward a mission.
    """

    id: str
    name: str
    description: str
    trigger: SankalpaTrigger
    frequency: StrategyFrequency
    # What to do when triggered
    intent_type: str  # Type of intent to generate
    intent_template: Dict[str, Any]  # Template for intent params
    # Constraints
    requires_ci_green: bool = True
    requires_no_pending_intents: bool = True
    max_executions_per_day: int = 3
    # Tracking
    last_executed: Optional[str] = None
    execution_count_today: int = 0
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger": self.trigger.to_dict(),
            "frequency": self.frequency.value,
            "intent_type": self.intent_type,
            "intent_template": self.intent_template,
            "requires_ci_green": self.requires_ci_green,
            "requires_no_pending_intents": self.requires_no_pending_intents,
            "max_executions_per_day": self.max_executions_per_day,
            "last_executed": self.last_executed,
            "execution_count_today": self.execution_count_today,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SankalpaStrategy":
        return cls(
            id=data.get("id", "unknown"),
            name=data.get("name", "Unknown Strategy"),
            description=data.get("description", ""),
            trigger=SankalpaTrigger.from_dict(data.get("trigger", {})),
            frequency=StrategyFrequency(data.get("frequency", "daily")),
            intent_type=data.get("intent_type", "proactive_task"),
            intent_template=data.get("intent_template", {}),
            requires_ci_green=data.get("requires_ci_green", True),
            requires_no_pending_intents=data.get("requires_no_pending_intents", True),
            max_executions_per_day=data.get("max_executions_per_day", 3),
            last_executed=data.get("last_executed"),
            execution_count_today=data.get("execution_count_today", 0),
            enabled=data.get("enabled", True),
        )


@dataclass
class SankalpaMission:
    """
    A long-term goal for MANAS.

    Missions are the WHY - the purpose that drives action.
    Strategies are the HOW - the methods to achieve missions.
    """

    id: str
    name: str
    description: str
    priority: MissionPriority
    status: MissionStatus
    strategies: List[SankalpaStrategy] = field(default_factory=list)
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    owner: str = "MANAS"  # Who created this mission

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "strategies": [s.to_dict() for s in self.strategies],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "owner": self.owner,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SankalpaMission":
        strategies = [SankalpaStrategy.from_dict(s) for s in data.get("strategies", [])]
        return cls(
            id=data.get("id", "unknown"),
            name=data.get("name", "Unknown Mission"),
            description=data.get("description", ""),
            priority=MissionPriority(data.get("priority", "medium")),
            status=MissionStatus(data.get("status", "active")),
            strategies=strategies,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            completed_at=data.get("completed_at"),
            owner=data.get("owner", "MANAS"),
        )


@dataclass
class SankalpaIntent:
    """
    An intent generated by SANKALPA.

    This is what gets sent to CognitiveKernel for execution.
    """

    id: str
    mission_id: str
    strategy_id: str
    title: str
    description: str
    intent_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "strategy_id": self.strategy_id,
            "title": self.title,
            "description": self.description,
            "intent_type": self.intent_type,
            "params": self.params,
            "priority": self.priority,
            "created_at": self.created_at,
        }


# =============================================================================
# SECTION 2: SANKALPA REGISTRY - Mission Storage
# =============================================================================


class SankalpaRegistry:
    """
    Registry of missions and strategies.

    Persists to .opus_state/sankalpa.json
    Provides CRUD operations and query methods.

    "The registry is the scroll of vows - written in fire, bound by honor."
    """

    DEFAULT_MISSIONS = [
        {
            "id": "mission_code_health",
            "name": "Maintain Code Health",
            "description": "Keep the codebase clean, tested, and well-documented",
            "priority": "high",
            "status": "active",
            "owner": "MANAS",
            "strategies": [
                {
                    "id": "strategy_daily_hygiene",
                    "name": "Daily Hygiene",
                    "description": "Run lint, format check, and basic tests",
                    "trigger": {
                        "trigger_type": "idle_based",
                        "idle_minutes": 60,
                    },
                    "frequency": "daily",
                    "intent_type": "hygiene_check",
                    "intent_template": {
                        "title": "Daily Hygiene Check",
                        "actions": ["lint", "format", "test_quick"],
                    },
                    "requires_ci_green": False,  # Can run even if CI is red
                    "max_executions_per_day": 1,
                    "enabled": True,
                },
                {
                    "id": "strategy_weekly_audit",
                    "name": "Weekly Architecture Audit",
                    "description": "Run DHARMA drift detection and report",
                    "trigger": {
                        "trigger_type": "time_based",
                        "day_of_week": 0,  # Monday
                        "hour": 9,
                    },
                    "frequency": "weekly",
                    "intent_type": "architecture_audit",
                    "intent_template": {
                        "title": "Weekly Architecture Audit",
                        "actions": ["dharma_check", "report"],
                    },
                    "requires_ci_green": True,
                    "max_executions_per_day": 1,
                    "enabled": True,
                },
            ],
        },
        {
            "id": "mission_self_improvement",
            "name": "Continuous Self-Improvement",
            "description": "Learn from past actions and improve autonomy",
            "priority": "medium",
            "status": "active",
            "owner": "MANAS",
            "strategies": [
                {
                    "id": "strategy_memory_review",
                    "name": "Memory Review",
                    "description": "Analyze recent memories and identify patterns",
                    "trigger": {
                        "trigger_type": "idle_based",
                        "idle_minutes": 120,
                    },
                    "frequency": "daily",
                    "intent_type": "memory_review",
                    "intent_template": {
                        "title": "Review Recent Memories",
                        "actions": ["analyze_patterns", "update_success_rate"],
                    },
                    "requires_ci_green": False,
                    "max_executions_per_day": 1,
                    "enabled": True,
                },
            ],
        },
    ]

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize the registry.

        Args:
            workspace: Workspace path for persistence
        """
        self._workspace = workspace or Path.cwd()
        self._missions: Dict[str, SankalpaMission] = {}
        self._load()

    def _get_registry_file(self) -> Path:
        """Get path to registry file."""
        return self._workspace / ".opus_state" / "sankalpa.json"

    def _load(self) -> None:
        """Load missions from disk."""
        try:
            registry_file = self._get_registry_file()
            if registry_file.exists():
                data = json.loads(registry_file.read_text())
                for mission_data in data.get("missions", []):
                    mission = SankalpaMission.from_dict(mission_data)
                    self._missions[mission.id] = mission
                logger.debug(f"SANKALPA: Loaded {len(self._missions)} missions")
            else:
                # Initialize with defaults
                self._init_defaults()
        except Exception as e:
            logger.warning(f"SANKALPA: Could not load registry: {e}")
            self._init_defaults()

    def _init_defaults(self) -> None:
        """Initialize with default missions."""
        for mission_data in self.DEFAULT_MISSIONS:
            mission = SankalpaMission.from_dict(mission_data)
            self._missions[mission.id] = mission
        logger.info(f"SANKALPA: Initialized with {len(self._missions)} default missions")
        self._save()

    def _save(self) -> None:
        """Save missions to disk."""
        try:
            registry_file = self._get_registry_file()
            registry_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "missions": [m.to_dict() for m in self._missions.values()],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            temp_file = registry_file.with_suffix(".tmp")
            temp_file.write_text(json.dumps(data, indent=2))
            temp_file.replace(registry_file)

        except Exception as e:
            logger.warning(f"SANKALPA: Could not save registry: {e}")

    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------

    def get_mission(self, mission_id: str) -> Optional[SankalpaMission]:
        """Get a mission by ID."""
        return self._missions.get(mission_id)

    def get_all_missions(self) -> List[SankalpaMission]:
        """Get all missions."""
        return list(self._missions.values())

    def get_active_missions(self) -> List[SankalpaMission]:
        """Get all active missions."""
        return [m for m in self._missions.values() if m.status == MissionStatus.ACTIVE]

    def add_mission(self, mission: SankalpaMission) -> None:
        """Add a new mission."""
        self._missions[mission.id] = mission
        self._save()
        logger.info(f"SANKALPA: Added mission '{mission.name}'")

    def update_mission(self, mission: SankalpaMission) -> None:
        """Update an existing mission."""
        if mission.id in self._missions:
            self._missions[mission.id] = mission
            self._save()

    def remove_mission(self, mission_id: str) -> bool:
        """Remove a mission."""
        if mission_id in self._missions:
            del self._missions[mission_id]
            self._save()
            return True
        return False

    def get_strategy(self, mission_id: str, strategy_id: str) -> Optional[SankalpaStrategy]:
        """Get a specific strategy."""
        mission = self.get_mission(mission_id)
        if mission:
            for strategy in mission.strategies:
                if strategy.id == strategy_id:
                    return strategy
        return None

    def update_strategy(self, mission_id: str, strategy: SankalpaStrategy) -> None:
        """Update a strategy within a mission."""
        mission = self.get_mission(mission_id)
        if mission:
            for i, s in enumerate(mission.strategies):
                if s.id == strategy.id:
                    mission.strategies[i] = strategy
                    self._save()
                    return

    def get_all_strategies(self) -> List[tuple]:
        """Get all strategies with their mission IDs."""
        result = []
        for mission in self._missions.values():
            for strategy in mission.strategies:
                result.append((mission.id, strategy))
        return result


# =============================================================================
# SECTION 3: SANKALPA PLANNER - Proactive Intent Generation
# =============================================================================


class SankalpaPlanner:
    """
    The Strategic Planner - evaluates missions and generates proactive intents.

    This is the heart of SANKALPA: it decides WHEN and WHAT to do based on:
    - Current system state
    - Mission priorities
    - Strategy triggers
    - Constraints (CI status, pending intents, etc.)

    "The planner sees the path; the kernel walks it."
    """

    def __init__(self, registry: SankalpaRegistry, workspace: Optional[Path] = None):
        """
        Initialize the planner.

        Args:
            registry: The mission registry
            workspace: Workspace path
        """
        self._registry = registry
        self._workspace = workspace or Path.cwd()
        self._last_daily_reset: Optional[str] = None

    def evaluate(
        self,
        context: Optional[Dict[str, Any]] = None,
        idle_minutes: int = 0,
        pending_intents: int = 0,
    ) -> List[SankalpaIntent]:
        """
        Evaluate all strategies and generate intents for those that should fire.

        Args:
            context: System context (CI status, health, etc.)
            idle_minutes: How long the system has been idle
            pending_intents: Number of pending intents in buffer

        Returns:
            List of SankalpaIntent objects to be executed
        """
        context = context or {}
        generated_intents: List[SankalpaIntent] = []

        # Reset daily counters if new day
        self._check_daily_reset()

        # Get CI status from context
        ci_green = self._is_ci_green(context)

        # Evaluate each active mission
        for mission in self._registry.get_active_missions():
            for strategy in mission.strategies:
                if not strategy.enabled:
                    continue

                # Check if strategy should fire
                if self._should_fire(strategy, context, idle_minutes, pending_intents, ci_green):
                    intent = self._create_intent(mission, strategy)
                    if intent:
                        generated_intents.append(intent)
                        # Update execution tracking
                        strategy.execution_count_today += 1
                        strategy.last_executed = datetime.now(timezone.utc).isoformat()
                        self._registry.update_strategy(mission.id, strategy)

        if generated_intents:
            logger.info(f"SANKALPA: Generated {len(generated_intents)} proactive intents")

        return generated_intents

    def _check_daily_reset(self) -> None:
        """Reset daily counters if a new day has started."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if self._last_daily_reset != today:
            self._last_daily_reset = today
            # Reset all strategy counters
            for mission_id, strategy in self._registry.get_all_strategies():
                if strategy.execution_count_today > 0:
                    strategy.execution_count_today = 0
                    self._registry.update_strategy(mission_id, strategy)
            logger.debug("SANKALPA: Daily counters reset")

    def _is_ci_green(self, context: Dict[str, Any]) -> bool:
        """Check if CI is green from context."""
        ci_status = context.get("ci", {}).get("status", "unknown")
        return ci_status in ("success", "passing", "green", "unknown")

    def _should_fire(
        self,
        strategy: SankalpaStrategy,
        context: Dict[str, Any],
        idle_minutes: int,
        pending_intents: int,
        ci_green: bool,
    ) -> bool:
        """
        Determine if a strategy should fire.

        Args:
            strategy: The strategy to evaluate
            context: System context
            idle_minutes: Current idle time
            pending_intents: Number of pending intents
            ci_green: Whether CI is green

        Returns:
            True if strategy should fire
        """
        # Check constraints
        if strategy.requires_ci_green and not ci_green:
            return False

        if strategy.requires_no_pending_intents and pending_intents > 0:
            return False

        if strategy.execution_count_today >= strategy.max_executions_per_day:
            return False

        # Check trigger
        trigger = strategy.trigger

        if trigger.trigger_type == TriggerType.IDLE_BASED:
            return idle_minutes >= trigger.idle_minutes

        elif trigger.trigger_type == TriggerType.TIME_BASED:
            return self._check_time_trigger(trigger, strategy)

        elif trigger.trigger_type == TriggerType.CONDITION_BASED:
            return self._check_condition_trigger(trigger, context)

        elif trigger.trigger_type == TriggerType.EVENT_BASED:
            # Event-based triggers are handled by event system
            return False

        return False

    def _check_time_trigger(self, trigger: SankalpaTrigger, strategy: SankalpaStrategy) -> bool:
        """Check if time-based trigger should fire."""
        now = datetime.now(timezone.utc)

        # Check day of week if specified
        if trigger.day_of_week is not None:
            if now.weekday() != trigger.day_of_week:
                return False

        # Check hour if specified
        if trigger.hour is not None:
            if now.hour != trigger.hour:
                return False

        # Check if already executed today/this week
        if strategy.last_executed:
            last = datetime.fromisoformat(strategy.last_executed.replace("Z", "+00:00"))
            if strategy.frequency == StrategyFrequency.DAILY:
                if last.date() >= now.date():
                    return False
            elif strategy.frequency == StrategyFrequency.WEEKLY:
                # Check if same week
                if last.isocalendar()[1] >= now.isocalendar()[1]:
                    return False

        return True

    def _check_condition_trigger(self, trigger: SankalpaTrigger, context: Dict[str, Any]) -> bool:
        """Check if condition-based trigger should fire."""
        if not trigger.condition:
            return True

        # Simple condition evaluation (can be extended)
        condition = trigger.condition.lower()

        if "ci_red" in condition:
            return not self._is_ci_green(context)
        elif "ci_green" in condition:
            return self._is_ci_green(context)
        elif "has_drift" in condition:
            return context.get("drift", {}).get("has_violations", False)

        return True

    def _create_intent(self, mission: SankalpaMission, strategy: SankalpaStrategy) -> SankalpaIntent:
        """Create an intent from a strategy."""
        import uuid

        intent_id = f"sankalpa_{uuid.uuid4().hex[:8]}"

        # Build intent from template
        template = strategy.intent_template
        title = template.get("title", strategy.name)
        description = f"[SANKALPA] {strategy.description}\nMission: {mission.name}"

        return SankalpaIntent(
            id=intent_id,
            mission_id=mission.id,
            strategy_id=strategy.id,
            title=title,
            description=description,
            intent_type=strategy.intent_type,
            params=template,
            priority=mission.priority.value,
        )


# =============================================================================
# SECTION 4: SANKALPA ORCHESTRATOR - Main Entry Point
# =============================================================================


class SankalpaOrchestrator:
    """
    Orchestrates the SANKALPA system.

    Provides a unified interface for:
    - Managing missions and strategies
    - Evaluating and generating proactive intents
    - Integrating with CognitiveKernel

    "The orchestrator is the conductor of will."
    """

    def __init__(self, workspace: Optional[Path] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator.

        Args:
            workspace: Workspace path
            config: Optional config dict from config/manas.yaml (sankalpa section)
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or {}  # Store config for future use
        self._registry = SankalpaRegistry(workspace=self._workspace)
        self._planner = SankalpaPlanner(self._registry, workspace=self._workspace)

    @property
    def registry(self) -> SankalpaRegistry:
        """Access the mission registry."""
        return self._registry

    @property
    def planner(self) -> SankalpaPlanner:
        """Access the strategy planner."""
        return self._planner

    def think(
        self,
        context: Optional[Dict[str, Any]] = None,
        idle_minutes: int = 0,
        pending_intents: int = 0,
    ) -> List[SankalpaIntent]:
        """
        Perform a strategic thinking cycle.

        Called by CognitiveKernel during its think() cycle.

        Args:
            context: System context
            idle_minutes: System idle time
            pending_intents: Number of pending intents

        Returns:
            List of proactive intents
        """
        return self._planner.evaluate(
            context=context,
            idle_minutes=idle_minutes,
            pending_intents=pending_intents,
        )

    def get_status(self) -> Dict[str, Any]:
        """Get SANKALPA status for display."""
        missions = self._registry.get_all_missions()
        active = [m for m in missions if m.status == MissionStatus.ACTIVE]

        total_strategies = sum(len(m.strategies) for m in missions)
        enabled_strategies = sum(len([s for s in m.strategies if s.enabled]) for m in missions)

        return {
            "total_missions": len(missions),
            "active_missions": len(active),
            "total_strategies": total_strategies,
            "enabled_strategies": enabled_strategies,
            "missions": [
                {
                    "id": m.id,
                    "name": m.name,
                    "priority": m.priority.value,
                    "status": m.status.value,
                    "strategies": len(m.strategies),
                }
                for m in missions
            ],
        }


# =============================================================================
# SECTION 5: JNANA INTEGRATION - Chat Interface
# =============================================================================


def handle_sankalpa_query(content: str, workspace: Optional[Path] = None) -> str:
    """
    Handle sankalpa-related queries from JNANA chat.

    Args:
        content: User's query content
        workspace: Optional workspace path

    Returns:
        Response string
    """
    content_lower = content.lower()
    orchestrator = SankalpaOrchestrator(workspace=workspace)

    # List missions
    if any(word in content_lower for word in ["list", "show", "missions", "ziele"]):
        status = orchestrator.get_status()
        lines = [
            "🔥 **SANKALPA** - Active Missions",
            "",
        ]

        for m in status["missions"]:
            status_emoji = "✅" if m["status"] == "active" else "⏸️"
            priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(m["priority"], "⚪")
            lines.append(f"{status_emoji} {priority_emoji} **{m['name']}** ({m['strategies']} strategies)")

        return "\n".join(lines)

    # Show specific mission
    if "mission" in content_lower:
        # Try to extract mission name
        missions = orchestrator.registry.get_all_missions()
        for mission in missions:
            if mission.name.lower() in content_lower or mission.id in content_lower:
                return _format_mission_detail(mission)

    # Status
    return get_sankalpa_for_chat(workspace)


def _format_mission_detail(mission: SankalpaMission) -> str:
    """Format a mission for detailed display."""
    lines = [
        f"🔥 **Mission: {mission.name}**",
        f"*{mission.description}*",
        "",
        f"**Priority:** {mission.priority.value.upper()}",
        f"**Status:** {mission.status.value}",
        f"**Owner:** {mission.owner}",
        "",
        "**Strategies:**",
    ]

    for strategy in mission.strategies:
        enabled = "✅" if strategy.enabled else "❌"
        freq = strategy.frequency.value
        last = strategy.last_executed or "never"
        lines.append(f"  {enabled} {strategy.name} ({freq})")
        lines.append(f"      Last run: {last}")

    return "\n".join(lines)


def get_sankalpa_for_chat(workspace: Optional[Path] = None) -> str:
    """
    Get SANKALPA status for chat display.

    Args:
        workspace: Optional workspace path

    Returns:
        Status string
    """
    orchestrator = SankalpaOrchestrator(workspace=workspace)
    status = orchestrator.get_status()

    return f"""🔥 **SANKALPA** (Proactive Strategy)
├─ Missions: {status["active_missions"]}/{status["total_missions"]} active
├─ Strategies: {status["enabled_strategies"]}/{status["total_strategies"]} enabled
└─ Status: {"ACTIVE" if status["active_missions"] > 0 else "IDLE"}

**Commands:**
- "list missions" - Show all missions
- "show mission <name>" - Mission details

**Active Missions:**
{chr(10).join(f"  • {m['name']} ({m['priority']})" for m in status["missions"] if m["status"] == "active")}
"""


# =============================================================================
# SECTION 6: SINGLETON ACCESS
# =============================================================================


_sankalpa_orchestrator: Optional[SankalpaOrchestrator] = None


def get_sankalpa_orchestrator(workspace: Optional[Path] = None) -> SankalpaOrchestrator:
    """Get or create the global SANKALPA orchestrator."""
    global _sankalpa_orchestrator
    if _sankalpa_orchestrator is None:
        _sankalpa_orchestrator = SankalpaOrchestrator(workspace)
    return _sankalpa_orchestrator
