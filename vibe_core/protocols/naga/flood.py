"""
NAGA FLOOD PROTOCOL - The Organic Broadcasting System
======================================================

"Wie Wasser in jede Ritze" - Like water into every crack.

THE ŚRAVAṆAM PRINCIPLE FOR NAGAS:
NAGAs don't just observe - they FLOOD the system with what is LACKING.

MAHAJANA MAPPING:
    Owner: NARADA (The Messenger)
    OpCode: PULSE_SYNC (Emit heartbeat, broadcast observations)
    Phase: PURIFY (Quarter 2)
    Word: HARE (Position 7)

THREE FLOOD LAYERS:
    Layer 1: EventBus flooding (all events)
    Layer 2: SignalBus watching (critical signals)
    Layer 3: Intelligence propagation (insights to consumers)

SAFETY MECHANISMS (from GAD-000):
    - RECURSION GUARD: Prevent NAGAs catching own events
    - ASYNC DECOUPLING: Fire and forget
    - SIDE CHANNEL: Violations to Ledger, not EventBus

STRICT TYPING (NO ANY):
Per PROMPT.md §IV.1
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xc37d20cb"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.substrate import MantraOpCode


# =============================================================================
# FLOOD LAYER ENUM
# =============================================================================

class FloodLayer(str, Enum):
    """The three layers of NAGA flooding."""
    EVENT_BUS = "event_bus"       # Layer 1: All events
    SIGNAL_BUS = "signal_bus"     # Layer 2: Critical signals
    INTELLIGENCE = "intelligence"  # Layer 3: Insights to consumers


class FloodStatus(str, Enum):
    """Status of the flood system."""
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    STOPPING = "stopping"
    ERROR = "error"


# =============================================================================
# FLOOD STATS (Strict Typed)
# =============================================================================

@dataclass(frozen=True)
class FloodStats:
    """
    Statistics for flood monitoring.

    GAD-000: Observable, Parseable
    """
    events_seen: int = 0
    events_skipped_recursion: int = 0
    events_skipped_noise: int = 0
    events_analyzed: int = 0
    violations_detected: int = 0
    analysis_timeouts: int = 0
    queue_overflows: int = 0
    started_at: Optional[datetime] = None

    @property
    def uptime_seconds(self) -> float:
        """Calculate uptime in seconds."""
        if self.started_at is None:
            return 0.0
        return (datetime.now() - self.started_at).total_seconds()

    @property
    def events_per_second(self) -> float:
        """Calculate throughput."""
        uptime = self.uptime_seconds
        if uptime <= 0:
            return 0.0
        return self.events_seen / uptime


@dataclass(frozen=True)
class FloodConfig:
    """
    Configuration for flood system.

    Immutable to prevent runtime tampering.
    """
    max_analysis_queue: int = 1000
    analysis_timeout_ms: int = 50
    queue_wait_timeout_seconds: float = 5.0
    seen_events_max: int = 10000
    seen_events_trim_size: int = 5000
    max_content_size: int = 10000
    enabled: bool = True


# =============================================================================
# FLOOD SIGNAL (For Cortex Integration)
# =============================================================================

@dataclass(frozen=True)
class FloodSignal:
    """
    Signal sent from Flood to Cortex.

    Contains observation data for correlation.
    """
    source_id: str
    event_type: str
    agent_id: Optional[str]
    toxicity_score: float
    patterns_detected: Tuple[str, ...]
    timestamp: datetime = field(default_factory=datetime.now)


# Type alias for cortex callback
FloodCortexCallback = Callable[[FloodSignal], None]


# =============================================================================
# FLOOD OBSERVATION (What we broadcast)
# =============================================================================

@dataclass(frozen=True)
class FloodObservation:
    """
    An observation that NAGAs flood to consumers.

    This is the INTELLIGENCE that chat can use.
    """
    observation_type: str  # "toxicity", "anomaly", "pattern", "alert"
    severity: str          # "info", "warning", "critical"
    source: str            # Which NAGA made this observation
    summary: str           # Human-readable summary
    details: Tuple[Tuple[str, str], ...]  # Key-value pairs (immutable)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def details_dict(self) -> Dict[str, str]:
        """Get details as dict."""
        return dict(self.details)


# =============================================================================
# FLOOD PROTOCOL
# =============================================================================

@runtime_checkable
class FloodProtocol(Protocol):
    """
    Protocol for NAGA flooding operations.

    MAHAJANA: NARADA (The Messenger)
    OPCODE: PULSE_SYNC

    The Flood Protocol defines how NAGAs broadcast intelligence.
    Implementations may be EventBus-based, SignalBus-based, or hybrid.

    GAD-000 Compliant:
    - Discoverable: get_layers() shows what's flooded
    - Observable: get_stats() shows current state
    - Parseable: Strict typed inputs/outputs
    - Composable: set_cortex_callback() for integration
    - Idempotent: start()/stop() are idempotent
    - Recoverable: Status indicates health
    """

    # =========================================================================
    # MAHAJANA IDENTITY
    # =========================================================================

    @property
    def opcode(self) -> MantraOpCode:
        """The MantraOpCode for flooding."""
        ...

    @property
    def mahajana(self) -> str:
        """The Mahajana owner (NARADA)."""
        ...

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def start(self) -> None:
        """
        Start flooding operations.

        Idempotent: Safe to call multiple times.
        """
        ...

    def stop(self) -> None:
        """
        Stop flooding operations.

        Idempotent: Safe to call multiple times.
        """
        ...

    @property
    def status(self) -> FloodStatus:
        """Current status of the flood system."""
        ...

    # =========================================================================
    # OBSERVATION
    # =========================================================================

    def get_stats(self) -> FloodStats:
        """
        Get current flood statistics.

        GAD-000: Observable
        """
        ...

    def get_layers(self) -> List[FloodLayer]:
        """
        Get active flood layers.

        GAD-000: Discoverable
        """
        ...

    # =========================================================================
    # INTELLIGENCE PROPAGATION
    # =========================================================================

    def subscribe_observations(
        self,
        callback: Callable[[FloodObservation], None]
    ) -> str:
        """
        Subscribe to flood observations.

        Returns subscription ID for unsubscribe.

        This is how chat/CLI can receive Naga intelligence.
        """
        ...

    def unsubscribe_observations(self, subscription_id: str) -> bool:
        """
        Unsubscribe from flood observations.

        Returns True if subscription existed.
        """
        ...

    def get_recent_observations(
        self,
        limit: int = 10,
        severity: Optional[str] = None
    ) -> List[FloodObservation]:
        """
        Get recent observations.

        Filters by severity if provided.
        """
        ...

    # =========================================================================
    # CORTEX INTEGRATION
    # =========================================================================

    def set_cortex_callback(self, callback: FloodCortexCallback) -> None:
        """
        Set callback for sending signals to Cortex.

        Non-invasive integration point.
        """
        ...


# =============================================================================
# INTELLIGENCE CONSUMER PROTOCOL
# =============================================================================

@runtime_checkable
class FloodConsumerProtocol(Protocol):
    """
    Protocol for consumers of flood intelligence.

    Chat, CLI, and other systems implement this to receive
    Naga observations and use them to enhance responses.
    """

    def on_flood_observation(self, observation: FloodObservation) -> None:
        """
        Handle a flood observation.

        Called when NAGAs detect something noteworthy.
        """
        ...

    def get_relevant_observations(
        self,
        context: str,
        limit: int = 5
    ) -> List[FloodObservation]:
        """
        Get observations relevant to current context.

        Used by chat to include Naga insights in responses.
        """
        ...


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================

class NullFlood:
    """
    Null implementation of FloodProtocol.

    Used in tests and when flood system is disabled.
    """

    @property
    def opcode(self) -> MantraOpCode:
        return MantraOpCode.DHARMA_TEST

    @property
    def mahajana(self) -> str:
        return "narada"

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    @property
    def status(self) -> FloodStatus:
        return FloodStatus.INACTIVE

    def get_stats(self) -> FloodStats:
        return FloodStats()

    def get_layers(self) -> List[FloodLayer]:
        return []

    def subscribe_observations(
        self,
        callback: Callable[[FloodObservation], None]
    ) -> str:
        return "null-subscription"

    def unsubscribe_observations(self, subscription_id: str) -> bool:
        return False

    def get_recent_observations(
        self,
        limit: int = 10,
        severity: Optional[str] = None
    ) -> List[FloodObservation]:
        return []

    def set_cortex_callback(self, callback: FloodCortexCallback) -> None:
        pass


# =============================================================================
# MANTRA CONNECTION
# =============================================================================

# Flood operation maps to PULSE_SYNC
FLOOD_OPCODE = MantraOpCode.DHARMA_TEST
FLOOD_PHASE = "PURIFY"
FLOOD_WORD = "HARE"
FLOOD_POSITION = 7
FLOOD_MAHAJANA = "narada"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocols
    "FloodProtocol",
    "FloodConsumerProtocol",
    "NullFlood",
    # Enums
    "FloodLayer",
    "FloodStatus",
    # Data types
    "FloodStats",
    "FloodConfig",
    "FloodSignal",
    "FloodObservation",
    # Callbacks
    "FloodCortexCallback",
    # Mantra connection
    "FLOOD_OPCODE",
    "FLOOD_PHASE",
    "FLOOD_WORD",
    "FLOOD_POSITION",
    "FLOOD_MAHAJANA",
]
