"""
SANKALPA TYPES - Strict Contracts for the Will Protocol.

SHASTRA BASIS: _seed.py defines SHARANAGATI[6] = "anukulyasya sankalpah"
(The acceptance of the favorable - the first step of surrender)

Sankalpa = The Will. Not ego-will (Ahankara), but Dharma-will.
The system acts because Shastra dictates, not because it "wants".

This is NISHKAMA KARMA (Action without attachment).

NO `Any` TYPES. Everything is explicit. Satyam (Truth) over Tamas (Chaos).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xebbc13e9"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


# =============================================================================
# ENUMS - The Gunas of Strategy
# =============================================================================


# =============================================================================
# GUNA - The Three Modes of Nature (BG 14.5)
# =============================================================================


class GunaState(Enum):
    """
    The three Gunas (modes of material nature).
    Used for ethical classification of actions.
    """
    SATTVIC = "sattvic"  # Pure, righteous, aligned with Dharma
    RAJASIC = "rajasic"  # Passionate, needs review, borderline
    TAMASIC = "tamasic"  # Dark, adharmic, must be blocked


# =============================================================================
# ASHRAMA - Life Stages (Permissions based on maturity)
# =============================================================================


class Ashrama(Enum):
    """
    The four Ashramas (life stages).
    Determines what an agent is permitted to do.
    """
    BRAHMACHARI = "brahmachari"  # Student - learning, limited permissions
    GRIHASTHA = "grihastha"      # Householder - productive, full permissions
    VANAPRASTHA = "vanaprastha"  # Elder - mentoring, reduced action
    SANNYASI = "sannyasi"        # Renunciate - governance, override authority


# Permission grants by Ashrama
ASHRAMA_PERMISSIONS: dict[Ashrama, list[str]] = {
    Ashrama.BRAHMACHARI: ["test_create", "doc_modify", "review"],
    Ashrama.GRIHASTHA: [
        "code_modify", "git_commit", "git_push", "git_modify",
        "pr_create", "pr_merge", "test_create", "doc_modify",
        "review", "state_heal", "genesis",
    ],
    Ashrama.VANAPRASTHA: [
        "code_modify", "doc_modify", "review", "mentor", "pr_create",
    ],
    Ashrama.SANNYASI: [
        "review", "mentor", "admin", "system_control", "pr_merge", "genesis",
    ],
}


# =============================================================================
# INTENT PERMISSIONS - What each action requires
# =============================================================================


INTENT_PERMISSION_MAP: dict[str, list[str]] = {
    # Dangerous (require admin)
    "delete_file": ["file_delete", "admin"],
    "shutdown": ["system_control", "admin"],
    "ledger_modify": ["ledger_admin"],
    # Genesis (creation)
    "genesis_action": ["genesis", "code_modify"],
    "genesis_code": ["genesis", "code_modify"],
    "create_action": ["genesis", "code_modify"],
    "create_module": ["genesis", "code_modify"],
    # Medium risk
    "refactor_major": ["refactor", "code_modify"],
    "contract_import_fix": ["code_modify"],
    "update_documentation": ["doc_modify"],
    "commit_and_push": ["git_commit", "git_push"],
    "git_push": ["git_push"],
    "create_pr": ["git_push", "pr_create"],
    "merge_pr": ["pr_merge"],
    # Safe
    "review_todos": [],
    "test_create": ["test_create"],
    "doc_update": ["doc_modify"],
}


# =============================================================================
# MISSION PRIORITY
# =============================================================================


class MissionPriority(Enum):
    """Priority of a mission (Sattva → Tamas)."""
    CRITICAL = "critical"  # Sattva - Must be done (security, stability)
    HIGH = "high"          # Rajas - Important for health
    MEDIUM = "medium"      # Mixed - Nice to have
    LOW = "low"            # Tamas - Optional improvement


class MissionStatus(Enum):
    """Status of a mission lifecycle."""
    ACTIVE = "active"        # Mission is being pursued
    PAUSED = "paused"        # Temporarily paused
    COMPLETED = "completed"  # Goal achieved (Siddhi)
    ABANDONED = "abandoned"  # Given up


class TriggerType(Enum):
    """Types of triggers that activate a strategy."""
    TIME_BASED = "time_based"          # Cron-like (daily, weekly)
    EVENT_BASED = "event_based"        # On specific events
    CONDITION_BASED = "condition_based"  # When conditions met
    IDLE_BASED = "idle_based"          # When system is idle


class StrategyFrequency(Enum):
    """How often a strategy should run."""
    ONCE = "once"            # Run once when triggered
    HOURLY = "hourly"        # Every hour
    DAILY = "daily"          # Once per day
    WEEKLY = "weekly"        # Once per week
    CONTINUOUS = "continuous"  # Always active


# =============================================================================
# DATA CONTRACTS - Typed, not Any
# =============================================================================


@dataclass
class SankalpaTrigger:
    """
    Trigger condition for a strategy.
    Defines WHEN a strategy should activate.
    """
    trigger_type: TriggerType
    hour: Optional[int] = None          # Hour of day (0-23) for time-based
    day_of_week: Optional[int] = None   # 0=Monday, 6=Sunday
    condition: Optional[str] = None     # Condition expression
    idle_minutes: int = 30              # Minimum idle time for idle-based


@dataclass
class SankalpaStrategy:
    """
    Strategy for achieving a mission.
    Defines HOW and WHEN to act toward a mission.
    """
    id: str
    name: str
    description: str
    trigger: SankalpaTrigger
    frequency: StrategyFrequency
    intent_type: str                          # Type of intent to generate
    intent_template: dict                     # Template for intent params (structured)
    requires_ci_green: bool = True
    requires_no_pending_intents: bool = True
    max_executions_per_day: int = 3
    last_executed: Optional[datetime] = None
    execution_count_today: int = 0
    enabled: bool = True


@dataclass
class SankalpaMission:
    """
    A long-term goal for the system.
    Missions are the WHY - the purpose that drives action.
    """
    id: str
    name: str
    description: str
    priority: MissionPriority
    status: MissionStatus
    strategies: List[SankalpaStrategy] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    owner: str = "dharma"  # Not "MANAS" - Dharma owns missions


@dataclass
class SankalpaIntent:
    """
    An intent generated by Sankalpa for execution.
    This goes through ChatProtocol (Advaita - one entrance).
    """
    id: UUID
    mission_id: str
    strategy_id: str
    title: str
    description: str
    intent_type: str
    params: dict = field(default_factory=dict)
    priority: MissionPriority = MissionPriority.MEDIUM
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        mission_id: str,
        strategy_id: str,
        title: str,
        description: str,
        intent_type: str,
        params: Optional[dict] = None,
        priority: MissionPriority = MissionPriority.MEDIUM,
    ) -> "SankalpaIntent":
        """Factory method with auto-generated UUID."""
        return cls(
            id=uuid4(),
            mission_id=mission_id,
            strategy_id=strategy_id,
            title=title,
            description=description,
            intent_type=intent_type,
            params=params or {},
            priority=priority,
        )


@dataclass
class SankalpaResult:
    """
    Result of executing a SankalpaIntent.
    Strict contract - no Any types.
    """
    success: bool
    intent_id: UUID
    mahajana: str                    # Who executed (routed by ChatProtocol)
    response: Optional[str] = None   # Response content if any
    error: Optional[str] = None      # Error message if failed
    execution_time_ms: int = 0       # How long it took


@dataclass
class SankalpaStatus:
    """Status report for the Sankalpa system."""
    total_missions: int
    active_missions: int
    total_strategies: int
    enabled_strategies: int
    missions: List[SankalpaMission]


# =============================================================================
# CONSCIENCE - Dharmic Alignment Check (extracted from DharmaSense)
# =============================================================================


@dataclass
class ConscienceVerdict:
    """
    Result of checking Dharmic alignment.

    The Conscience is part of Buddhi (intelligence).
    It answers: "Is this action righteous?"
    """
    guna: GunaState                      # Sattvic/Rajasic/Tamasic
    is_permitted: bool                   # Can proceed?
    ashrama: Ashrama                     # Agent's life stage
    bhakti: int                          # Trust level (0-200)
    reason: str                          # Human-readable explanation
    required_permissions: List[str]      # What the action needs
    missing_permissions: List[str]       # What's lacking

    @property
    def is_dharmic(self) -> bool:
        """True if action is Dharma-aligned."""
        return self.guna == GunaState.SATTVIC or (
            self.guna == GunaState.RAJASIC and self.is_permitted
        )


# =============================================================================
# SANKALPA ORCHESTRATOR PROTOCOL
# =============================================================================

from typing import Protocol, runtime_checkable


@runtime_checkable
class SankalpaOrchestratorProtocol(Protocol):
    """
    Protocol for the Sankalpa Orchestrator.

    The Will Protocol's main entry point.
    Manages missions, strategies, and intent generation.

    Usage:
        # CORRECT (DI pattern):
        orchestrator = get_sankalpa()

        # WRONG (direct import):
        from vibe_core.mahamantra.protocols.sankalpa.will import SankalpaOrchestrator
        orchestrator = SankalpaOrchestrator()
    """

    def think(
        self,
        idle_minutes: int = 0,
        pending_intents: int = 0,
        ci_green: bool = True,
    ) -> List["SankalpaIntent"]:
        """
        Perform a strategic thinking cycle.
        Evaluates missions and generates intents.
        """
        ...

    def get_status(self) -> "SankalpaStatus":
        """Get typed status report."""
        ...
