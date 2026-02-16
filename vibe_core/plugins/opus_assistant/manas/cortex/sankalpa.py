"""
SANKALPA - Strategic Mission Orchestration
==========================================

"saṅkalpa" = intention, determination, will

This module provides the core data structures and orchestrator
for strategic mission planning within MANAS.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MANAS.Sankalpa")


class MissionPriority(str, Enum):
    """Priority level for missions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MissionStatus(str, Enum):
    """Status of a mission."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class TriggerType(str, Enum):
    """Type of strategy trigger."""

    IDLE_BASED = "idle_based"
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    MANUAL = "manual"


class StrategyFrequency(str, Enum):
    """How often a strategy should execute."""

    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    ON_DEMAND = "on_demand"


@dataclass
class SankalpaTrigger:
    """Trigger configuration for a strategy."""

    trigger_type: TriggerType = TriggerType.IDLE_BASED
    idle_minutes: int = 60
    cron_expression: Optional[str] = None
    event_name: Optional[str] = None


@dataclass
class SankalpaStrategy:
    """A strategy within a mission."""

    id: str = ""
    name: str = ""
    description: str = ""
    trigger: SankalpaTrigger = field(default_factory=SankalpaTrigger)
    frequency: StrategyFrequency = StrategyFrequency.DAILY
    intent_type: str = "proactive_task"
    intent_template: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_executed: Optional[str] = None
    execution_count: int = 0


@dataclass
class SankalpaMission:
    """A strategic mission."""

    id: str = ""
    name: str = ""
    description: str = ""
    priority: MissionPriority = MissionPriority.MEDIUM
    status: MissionStatus = MissionStatus.ACTIVE
    strategies: List[SankalpaStrategy] = field(default_factory=list)
    owner: str = "MANAS"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MissionRegistry:
    """Registry for missions."""

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._missions: Dict[str, SankalpaMission] = {}

    def add_mission(self, mission: SankalpaMission) -> None:
        """Add a mission to the registry."""
        self._missions[mission.id] = mission

    def get_mission(self, mission_id: str) -> Optional[SankalpaMission]:
        """Get a mission by ID."""
        return self._missions.get(mission_id)

    def update_mission(self, mission: SankalpaMission) -> None:
        """Update an existing mission."""
        self._missions[mission.id] = mission

    def remove_mission(self, mission_id: str) -> None:
        """Remove a mission."""
        self._missions.pop(mission_id, None)

    def list_missions(self, status: Optional[MissionStatus] = None) -> List[SankalpaMission]:
        """List missions, optionally filtered by status."""
        missions = list(self._missions.values())
        if status:
            missions = [m for m in missions if m.status == status]
        return missions


class SankalpaOrchestrator:
    """
    Strategic mission orchestrator.

    Manages missions and strategies, evaluates triggers,
    and generates proactive intents.
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self._workspace = workspace or Path.cwd()
        self._config = config or {}
        self.registry = MissionRegistry(self._workspace)
        logger.info("[SANKALPA] Orchestrator initialized")

    def get_status(self) -> Dict[str, Any]:
        """Get overall orchestrator status."""
        all_missions = self.registry.list_missions()
        active = [m for m in all_missions if m.status == MissionStatus.ACTIVE]
        return {
            "total_missions": len(all_missions),
            "active_missions": len(active),
            "missions": [m.to_dict() for m in all_missions],
        }

    def evaluate_strategies(self) -> List[Dict[str, Any]]:
        """Evaluate all active strategies and return triggered intents."""
        intents = []
        for mission in self.registry.list_missions(status=MissionStatus.ACTIVE):
            for strategy in mission.strategies:
                if strategy.enabled:
                    intents.append(
                        {
                            "mission_id": mission.id,
                            "strategy_id": strategy.id,
                            "intent_type": strategy.intent_type,
                            "template": strategy.intent_template,
                        }
                    )
        return intents


__all__ = [
    "MissionPriority",
    "MissionStatus",
    "TriggerType",
    "StrategyFrequency",
    "SankalpaTrigger",
    "SankalpaStrategy",
    "SankalpaMission",
    "MissionRegistry",
    "SankalpaOrchestrator",
]
