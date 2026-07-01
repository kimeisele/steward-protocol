"""
SANKALPA WILL - The Orchestrator of Dharmic Action.

"Sankalpa is the seed of action. Plant it with care, and the universe conspires."

This module evaluates missions and generates intents based on Shastra (strategy),
not ego (Ahankara). It is NISHKAMA KARMA - action without attachment.

ADVAITA PRINCIPLE:
All execution goes through ChatProtocol. No bypass. No special paths.
Internal voice (Sankalpa) and external voice (User) enter the same gate.
"""

from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA, NAVA, TEN, TRINITY

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = NAVA
__genesis__ = "0xebbc13e9"  # GenesisByte: parampara % 37 == 0

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from vibe_core.mahamantra.protocols.sankalpa.types import (
    ASHRAMA_PERMISSIONS,
    INTENT_PERMISSION_MAP,
    # Conscience types (extracted from DharmaSense)
    Ashrama,
    ConscienceVerdict,
    GunaState,
    # Mission types
    MissionPriority,
    MissionStatus,
    SankalpaIntent,
    SankalpaMission,
    SankalpaResult,
    SankalpaStatus,
    SankalpaStrategy,
    SankalpaTrigger,
    StrategyFrequency,
    TriggerType,
)

logger = logging.getLogger("SANKALPA")


# =============================================================================
# DEFAULT MISSIONS (Shastra-defined, not arbitrary)
# =============================================================================

DEFAULT_MISSIONS: List[dict] = [
    {
        "id": "mission_code_health",
        "name": "Maintain Code Health",
        "description": "Keep the codebase clean, tested, and well-documented",
        "priority": "high",
        "status": "active",
        "strategies": [
            {
                "id": "strategy_daily_hygiene",
                "name": "Daily Hygiene",
                "description": "Run lint, format check, and basic tests",
                "trigger": {"trigger_type": "idle_based", "idle_minutes": 60},
                "frequency": "daily",
                "intent_type": "hygiene_check",
                "intent_template": {"actions": ["lint", "format", "test_quick"]},
                "requires_ci_green": False,
                "max_executions_per_day": KSETRAJNA,
            },
        ],
    },
]


# =============================================================================
# REGISTRY - Mission Storage (Persistent)
# =============================================================================


class SankalpaRegistry:
    """
    Registry of missions and strategies.
    Persists to .vibe/state/sankalpa.json (NOT in plugins folder!)
    """

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._missions: dict[str, SankalpaMission] = {}
        self._load()

    def _get_state_file(self) -> Path:
        """State file in .vibe/state/ (core location, not plugin)."""
        state_dir = self._workspace / ".vibe" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / "sankalpa.json"

    def _load(self) -> None:
        """Load missions from disk."""
        state_file = self._get_state_file()
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                for m_data in data.get("missions", []):
                    mission = self._parse_mission(m_data)
                    self._missions[mission.id] = mission
                logger.debug(f"SANKALPA: Loaded {len(self._missions)} missions")
            except Exception as e:
                logger.warning(f"SANKALPA: Load failed, using defaults: {e}")
                self._init_defaults()
        else:
            self._init_defaults()

    def _init_defaults(self) -> None:
        """Initialize with default Shastra-defined missions."""
        for m_data in DEFAULT_MISSIONS:
            mission = self._parse_mission(m_data)
            self._missions[mission.id] = mission
        self._save()
        logger.info(f"SANKALPA: Initialized {len(self._missions)} default missions")

    def _save(self) -> None:
        """Persist missions to disk (atomic write)."""
        state_file = self._get_state_file()
        data = {
            "missions": [self._serialize_mission(m) for m in self._missions.values()],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        temp = state_file.with_suffix(".tmp")
        temp.write_text(json.dumps(data, indent=HALVES, default=str))
        temp.replace(state_file)

    def _parse_mission(self, data: dict) -> SankalpaMission:
        """Parse dict to SankalpaMission."""
        strategies = [self._parse_strategy(s) for s in data.get("strategies", [])]
        return SankalpaMission(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            priority=MissionPriority(data.get("priority", "medium")),
            status=MissionStatus(data.get("status", "active")),
            strategies=strategies,
            owner=data.get("owner", "dharma"),
        )

    def _parse_strategy(self, data: dict) -> SankalpaStrategy:
        """Parse dict to SankalpaStrategy."""
        trigger_data = data.get("trigger", {})
        trigger = SankalpaTrigger(
            trigger_type=TriggerType(trigger_data.get("trigger_type", "idle_based")),
            hour=trigger_data.get("hour"),
            day_of_week=trigger_data.get("day_of_week"),
            condition=trigger_data.get("condition"),
            idle_minutes=trigger_data.get("idle_minutes", 30),
        )
        return SankalpaStrategy(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            trigger=trigger,
            frequency=StrategyFrequency(data.get("frequency", "daily")),
            intent_type=data.get("intent_type", "task"),
            intent_template=data.get("intent_template", {}),
            requires_ci_green=data.get("requires_ci_green", True),
            requires_no_pending_intents=data.get("requires_no_pending_intents", True),
            max_executions_per_day=data.get("max_executions_per_day", TRINITY),
            enabled=data.get("enabled", True),
        )

    def _serialize_mission(self, mission: SankalpaMission) -> dict:
        """Serialize SankalpaMission to dict."""
        return {
            "id": mission.id,
            "name": mission.name,
            "description": mission.description,
            "priority": mission.priority.value,
            "status": mission.status.value,
            "strategies": [self._serialize_strategy(s) for s in mission.strategies],
            "owner": mission.owner,
        }

    def _serialize_strategy(self, strategy: SankalpaStrategy) -> dict:
        """Serialize SankalpaStrategy to dict."""
        return {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "trigger": {
                "trigger_type": strategy.trigger.trigger_type.value,
                "hour": strategy.trigger.hour,
                "day_of_week": strategy.trigger.day_of_week,
                "condition": strategy.trigger.condition,
                "idle_minutes": strategy.trigger.idle_minutes,
            },
            "frequency": strategy.frequency.value,
            "intent_type": strategy.intent_type,
            "intent_template": strategy.intent_template,
            "requires_ci_green": strategy.requires_ci_green,
            "requires_no_pending_intents": strategy.requires_no_pending_intents,
            "max_executions_per_day": strategy.max_executions_per_day,
            "last_executed": strategy.last_executed.isoformat() if strategy.last_executed else None,
            "execution_count_today": strategy.execution_count_today,
            "enabled": strategy.enabled,
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def add_mission(self, mission: SankalpaMission) -> None:
        """Add a mission to the registry and persist."""
        self._missions[mission.id] = mission
        self._save()

    def get_active_missions(self) -> List[SankalpaMission]:
        """Get all active missions."""
        return [m for m in self._missions.values() if m.status == MissionStatus.ACTIVE]

    def get_all_missions(self) -> List[SankalpaMission]:
        """Get all missions."""
        return list(self._missions.values())

    def list_missions(self, status: str | None = None) -> List[SankalpaMission]:
        """List missions, optionally filtered by status value.

        Args:
            status: Filter by status string (e.g. "active", "completed").
                    None returns all missions.
        """
        if status is None:
            return list(self._missions.values())
        return [m for m in self._missions.values() if m.status.value == status]

    def update_strategy(self, mission_id: str, strategy: SankalpaStrategy) -> None:
        """Update a strategy within a mission."""
        if mission_id in self._missions:
            mission = self._missions[mission_id]
            for i, s in enumerate(mission.strategies):
                if s.id == strategy.id:
                    mission.strategies[i] = strategy
                    self._save()
                    return


# =============================================================================
# PLANNER - Evaluates strategies, generates intents
# =============================================================================


class SankalpaPlanner:
    """
    The Strategic Planner - evaluates missions and generates intents.
    Decides WHEN and WHAT based on Shastra (strategy), not ego.
    """

    def __init__(self, registry: SankalpaRegistry):
        self._registry = registry
        self._last_daily_reset: Optional[str] = None

    def evaluate(
        self,
        idle_minutes: int = 0,
        pending_intents: int = 0,
        ci_green: bool = True,
        is_stagnating: bool = False,
    ) -> List[SankalpaIntent]:
        """
        Evaluate all strategies and generate intents for those that should fire.
        """
        self._check_daily_reset()
        intents: List[SankalpaIntent] = []

        for mission in self._registry.get_active_missions():
            for strategy in mission.strategies:
                if not strategy.enabled:
                    continue

                if self._should_fire(strategy, idle_minutes, pending_intents, ci_green, is_stagnating):
                    intent = self._create_intent(mission, strategy)
                    intents.append(intent)

                    # Update tracking
                    strategy.execution_count_today += KSETRAJNA
                    strategy.last_executed = datetime.now(timezone.utc)
                    self._registry.update_strategy(mission.id, strategy)

        if intents:
            logger.info(f"SANKALPA: Generated {len(intents)} intents")

        return intents

    def _check_daily_reset(self) -> None:
        """Reset daily counters if new day."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._last_daily_reset != today:
            self._last_daily_reset = today
            for mission in self._registry.get_active_missions():
                for strategy in mission.strategies:
                    if strategy.execution_count_today > 0:
                        strategy.execution_count_today = 0
                        self._registry.update_strategy(mission.id, strategy)

    def _should_fire(
        self,
        strategy: SankalpaStrategy,
        idle_minutes: int,
        pending_intents: int,
        ci_green: bool,
        is_stagnating: bool = False,
    ) -> bool:
        """Determine if a strategy should fire."""
        # Constraints
        if strategy.requires_ci_green and not ci_green:
            return False
        if strategy.requires_no_pending_intents and pending_intents > 0:
            return False
        if strategy.execution_count_today >= strategy.max_executions_per_day:
            return False

        # Trigger check
        trigger = strategy.trigger
        if trigger.trigger_type == TriggerType.IDLE_BASED:
            return idle_minutes >= trigger.idle_minutes
        elif trigger.trigger_type == TriggerType.TIME_BASED:
            return self._check_time_trigger(trigger, strategy)
        elif trigger.trigger_type == TriggerType.CONDITION_BASED:
            return is_stagnating

        return False

    def _check_time_trigger(self, trigger: SankalpaTrigger, strategy: SankalpaStrategy) -> bool:
        """Check if time-based trigger should fire."""
        now = datetime.now(timezone.utc)

        if trigger.day_of_week is not None and now.weekday() != trigger.day_of_week:
            return False
        if trigger.hour is not None and now.hour != trigger.hour:
            return False

        # Check if already executed this period
        if strategy.last_executed:
            if strategy.frequency == StrategyFrequency.DAILY:
                if strategy.last_executed.date() >= now.date():
                    return False
            elif strategy.frequency == StrategyFrequency.WEEKLY:
                if strategy.last_executed.isocalendar()[KSETRAJNA] >= now.isocalendar()[KSETRAJNA]:
                    return False

        return True

    def _create_intent(self, mission: SankalpaMission, strategy: SankalpaStrategy) -> SankalpaIntent:
        """Create a typed SankalpaIntent from strategy."""
        return SankalpaIntent.create(
            mission_id=mission.id,
            strategy_id=strategy.id,
            title=strategy.intent_template.get("title", strategy.name),
            description=f"[SANKALPA] {strategy.description}\nMission: {mission.name}",
            intent_type=strategy.intent_type,
            params=strategy.intent_template,
            priority=mission.priority,
        )


# =============================================================================
# CONSCIENCE - Dharmic Alignment Check (Buddhi function)
# =============================================================================


def check_conscience(
    intent_type: str,
    ashrama: Ashrama = Ashrama.GRIHASTHA,
    bhakti: int = 0,
) -> ConscienceVerdict:
    """
    Check if an action is Dharma-aligned.

    This is the CONSCIENCE - part of Buddhi (intelligence), not a "sense".
    Extracted from DharmaSense for theological correctness.

    Args:
        intent_type: Type of action to check
        ashrama: Agent's life stage (default: Grihastha/productive)
        bhakti: Trust level 0-200 (default: 0)

    Returns:
        ConscienceVerdict with alignment status
    """
    # Get required permissions for this intent
    required_perms = INTENT_PERMISSION_MAP.get(intent_type, [])

    # Get permissions granted by Ashrama
    granted_perms = set(ASHRAMA_PERMISSIONS.get(ashrama, []))

    # Check for missing permissions
    missing_perms = [p for p in required_perms if p not in granted_perms]

    # Determine Guna status
    if not required_perms:
        # No special permissions needed - Sattvic
        guna = GunaState.SATTVIC
        reason = "No special permissions required"
        is_permitted = True

    elif not missing_perms:
        # All permissions granted - Sattvic
        guna = GunaState.SATTVIC
        reason = f"Ashrama {ashrama.value} has all required permissions"
        is_permitted = True

    elif bhakti >= 50 and len(missing_perms) == KSETRAJNA:
        # High Bhakti can compensate for one missing permission - Rajasic
        guna = GunaState.RAJASIC
        reason = f"High Bhakti ({bhakti}) grants provisional access for {missing_perms}"
        is_permitted = True

    elif ashrama == Ashrama.SANNYASI:
        # Sannyasi has governance override - Rajasic
        guna = GunaState.RAJASIC
        reason = "Sannyasi has governance authority"
        is_permitted = True

    else:
        # Insufficient permissions - Tamasic
        guna = GunaState.TAMASIC
        reason = f"Missing permissions: {missing_perms}. Bhakti {bhakti} < 50 for override."
        is_permitted = False

    return ConscienceVerdict(
        guna=guna,
        is_permitted=is_permitted,
        ashrama=ashrama,
        bhakti=bhakti,
        reason=reason,
        required_permissions=required_perms,
        missing_permissions=missing_perms,
    )


# =============================================================================
# ORCHESTRATOR - Main Entry Point
# =============================================================================


class SankalpaOrchestrator:
    """
    Orchestrates the Sankalpa system.
    Unified interface for mission management and intent execution.
    """

    # NAGA BLESSING: Mahamantra is KING - services here are pre-blessed
    _naga_flooded: bool = True

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._registry = SankalpaRegistry(workspace=self._workspace)
        self._planner = SankalpaPlanner(self._registry)

    @property
    def registry(self) -> SankalpaRegistry:
        return self._registry

    @property
    def planner(self) -> SankalpaPlanner:
        return self._planner

    def think(
        self,
        idle_minutes: int = 0,
        pending_intents: int = 0,
        ci_green: bool = True,
        is_stagnating: bool = False,
    ) -> List[SankalpaIntent]:
        """
        Perform a strategic thinking cycle.
        Called by kernel during its think() cycle.
        """
        return self._planner.evaluate(
            idle_minutes=idle_minutes,
            pending_intents=pending_intents,
            ci_green=ci_green,
            is_stagnating=is_stagnating,
        )

    async def execute_intent(self, intent: SankalpaIntent) -> SankalpaResult:
        """
        Execute a SankalpaIntent via Kirtan-Flow (canonical VM pipeline).

        ADVAITA: Same entrance for all voices.
        All routing goes through mahamantra().__call__() → execute_cycle().
        """
        import time

        from vibe_core.mahamantra.render import kirtan_chat

        start = time.time()

        try:
            response = kirtan_chat(intent.description, use_llm=True)
            elapsed_ms = int((time.time() - start) * 1000)

            return SankalpaResult(
                success=True,
                intent_id=intent.id,
                mahajana="kirtan",
                response=response,
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            return SankalpaResult(
                success=False,
                intent_id=intent.id,
                mahajana="error",
                error=str(e),
            )

    def get_status(self) -> SankalpaStatus:
        """Get typed status report."""
        missions = self._registry.get_all_missions()
        active = [m for m in missions if m.status == MissionStatus.ACTIVE]
        total_strategies = sum(len(m.strategies) for m in missions)
        enabled_strategies = sum(len([s for s in m.strategies if s.enabled]) for m in missions)

        return SankalpaStatus(
            total_missions=len(missions),
            active_missions=len(active),
            total_strategies=total_strategies,
            enabled_strategies=enabled_strategies,
            missions=missions,
        )


# =============================================================================
# SERVICEREGISTRY FACTORY
# =============================================================================

from vibe_core.mahamantra.protocols.sankalpa.types import SankalpaOrchestratorProtocol


def get_sankalpa(workspace: Optional[Path] = None) -> SankalpaOrchestrator:
    """
    Get SankalpaOrchestrator through ServiceRegistry.

    ARCHITECTURE:
        SankalpaOrchestrator is the Will Protocol's main entry point.
        Uses ServiceRegistry for singleton pattern.

    Usage:
        # CORRECT (DI pattern):
        orchestrator = get_sankalpa()

        # WRONG (direct import):
        from vibe_core.mahamantra.protocols.sankalpa.will import SankalpaOrchestrator
        orchestrator = SankalpaOrchestrator()

    Args:
        workspace: Optional workspace path (defaults to cwd)

    Returns:
        SankalpaOrchestrator instance (singleton via ServiceRegistry)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(SankalpaOrchestratorProtocol)
    if existing is not None:
        return existing  # type: ignore

    # Create new instance
    instance = SankalpaOrchestrator(workspace=workspace)

    # Register with ServiceRegistry
    ServiceRegistry.register(SankalpaOrchestratorProtocol, instance)
    logger.info("✅ SankalpaOrchestrator registered via ServiceRegistry")

    return ServiceRegistry.get(SankalpaOrchestratorProtocol)  # type: ignore


# =============================================================================
# CHAT INTERFACE (for JNANA integration)
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
        lines = ["🔥 **SANKALPA** - Active Missions", ""]

        for m in status.missions:
            status_emoji = "✅" if m.status == MissionStatus.ACTIVE else "⏸️"
            priority_emoji = {
                MissionPriority.CRITICAL: "🔴",
                MissionPriority.HIGH: "🟠",
                MissionPriority.MEDIUM: "🟡",
                MissionPriority.LOW: "🟢",
            }.get(m.priority, "⚪")
            lines.append(f"{status_emoji} {priority_emoji} **{m.name}** ({len(m.strategies)} strategies)")

        return "\n".join(lines)

    # Default status
    return get_sankalpa_status_for_chat(workspace)


def get_sankalpa_status_for_chat(workspace: Optional[Path] = None) -> str:
    """Get SANKALPA status for chat display."""
    orchestrator = SankalpaOrchestrator(workspace=workspace)
    status = orchestrator.get_status()

    active_names = [m.name for m in status.missions if m.status == MissionStatus.ACTIVE]

    return f"""🔥 **SANKALPA** (Dharmic Will)
├─ Missions: {status.active_missions}/{status.total_missions} active
├─ Strategies: {status.enabled_strategies}/{status.total_strategies} enabled
└─ Status: {"ACTIVE" if status.active_missions > 0 else "IDLE"}

**Active Missions:**
{chr(TEN).join(f"  • {name}" for name in active_names) if active_names else "  (none)"}
"""
