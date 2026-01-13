"""
NAGA INTELLIGENCE BRIDGE PROTOCOL
==================================

"Central Intelligence Agency" - Bridges Naga intelligence to consumers.

THE BRIDGE PRINCIPLE:
NAGAs observe everything. This protocol makes their observations
available to chat, CLI, and other systems.

MAHAJANA MAPPING:
    Owner: SHUKA (The Visionary)
    OpCode: FETCH_RES (Fetch resources/intelligence)
    Phase: SERVE (Quarter 3)
    Word: HARE (Position 8)

WHY SHUKA?
- Shuka sees past, present, and future
- He narrates Bhagavatam to Parikshit
- Intelligence is about SEEING clearly

STRICT TYPING (NO ANY):
Per PROMPT.md §IV.1
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xe6a2c7ce"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.substrate import MantraOpCode
from vibe_core.protocols.naga.flood import FloodObservation


# =============================================================================
# INTELLIGENCE TYPES
# =============================================================================

class IntelCategory(str, Enum):
    """Categories of Naga intelligence."""
    SECURITY = "security"        # Toxicity, violations
    HEALTH = "health"            # System health, performance
    BEHAVIOR = "behavior"        # Pattern detection, anomalies
    CONTEXT = "context"          # Contextual awareness
    THREAT = "threat"            # Active threats
    SUGGESTION = "suggestion"    # Recommendations


class IntelPriority(str, Enum):
    """Priority levels for intelligence."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# INTEL ITEM (What we bridge)
# =============================================================================

@dataclass(frozen=True)
class IntelItem:
    """
    A piece of intelligence from NAGAs.

    This is the standardized format for Naga insights
    that can be consumed by chat and other systems.
    """
    item_id: str
    category: IntelCategory
    priority: IntelPriority
    summary: str                # One-line summary
    details: str                # Full details (markdown OK)
    source_naga: str            # Which NAGA generated this
    relevance_score: float      # 0.0 - 1.0 (how relevant to current context)
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Tuple[str, ...] = ()  # Search tags

    def to_chat_message(self) -> str:
        """Format as chat-friendly message."""
        icon = {
            IntelCategory.SECURITY: "🔒",
            IntelCategory.HEALTH: "💚",
            IntelCategory.BEHAVIOR: "📊",
            IntelCategory.CONTEXT: "📍",
            IntelCategory.THREAT: "⚠️",
            IntelCategory.SUGGESTION: "💡",
        }.get(self.category, "ℹ️")

        priority_marker = ""
        if self.priority == IntelPriority.CRITICAL:
            priority_marker = " [CRITICAL]"
        elif self.priority == IntelPriority.HIGH:
            priority_marker = " [HIGH]"

        return f"{icon}{priority_marker} {self.summary}"


# =============================================================================
# INTEL QUERY (How we ask)
# =============================================================================

@dataclass(frozen=True)
class IntelQuery:
    """
    Query for Naga intelligence.

    Used by chat and CLI to request relevant insights.
    """
    context: str                # Current context (chat topic, file path, etc.)
    categories: Tuple[IntelCategory, ...] = ()  # Filter by category (empty = all)
    min_priority: IntelPriority = IntelPriority.LOW
    max_results: int = 5
    include_expired: bool = False
    time_window_minutes: int = 60  # Only intel from last N minutes


@dataclass(frozen=True)
class IntelResponse:
    """
    Response to an intel query.

    Contains matching intelligence items.
    """
    items: Tuple[IntelItem, ...]
    query: IntelQuery
    total_available: int  # Total items matching (before limit)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_critical(self) -> bool:
        """Check if response contains critical items."""
        return any(item.priority == IntelPriority.CRITICAL for item in self.items)

    @property
    def has_threats(self) -> bool:
        """Check if response contains threats."""
        return any(item.category == IntelCategory.THREAT for item in self.items)


# =============================================================================
# INTEL BRIDGE PROTOCOL
# =============================================================================

@runtime_checkable
class IntelBridgeProtocol(Protocol):
    """
    Protocol for bridging Naga intelligence to consumers.

    MAHAJANA: SHUKA (The Visionary)
    OPCODE: FETCH_RES

    This is how chat and CLI access Naga's collective intelligence.

    GAD-000 Compliant:
    - Discoverable: get_available_categories()
    - Observable: get_stats()
    - Parseable: Strict typed queries/responses
    - Composable: Can be used by any consumer
    - Idempotent: Same query returns same intel (within time window)
    - Recoverable: Failures return empty response, not exceptions
    """

    # =========================================================================
    # MAHAJANA IDENTITY
    # =========================================================================

    @property
    def opcode(self) -> MantraOpCode:
        """The MantraOpCode for intelligence."""
        ...

    @property
    def mahajana(self) -> str:
        """The Mahajana owner (SHUKA)."""
        ...

    # =========================================================================
    # QUERY
    # =========================================================================

    def query(self, intel_query: IntelQuery) -> IntelResponse:
        """
        Query for relevant intelligence.

        This is the main interface for consumers.
        """
        ...

    def query_for_chat(
        self,
        user_message: str,
        chat_context: str,
        limit: int = 3
    ) -> IntelResponse:
        """
        Query intelligence relevant to a chat message.

        Convenience method for chat integration.
        Automatically determines categories and priority.
        """
        ...

    # =========================================================================
    # DIRECT ACCESS
    # =========================================================================

    def get_recent(
        self,
        limit: int = 10,
        category: Optional[IntelCategory] = None
    ) -> List[IntelItem]:
        """Get recent intel items."""
        ...

    def get_critical(self) -> List[IntelItem]:
        """Get all current critical items."""
        ...

    def get_threats(self) -> List[IntelItem]:
        """Get all current threat items."""
        ...

    # =========================================================================
    # SUBSCRIPTION (For real-time consumers)
    # =========================================================================

    def subscribe(
        self,
        callback: Callable[[IntelItem], None],
        categories: Optional[Tuple[IntelCategory, ...]] = None
    ) -> str:
        """
        Subscribe to intel updates.

        Returns subscription ID.
        """
        ...

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from intel updates."""
        ...

    # =========================================================================
    # DISCOVERY
    # =========================================================================

    def get_available_categories(self) -> List[IntelCategory]:
        """Get list of available intel categories."""
        ...

    def get_active_nagas(self) -> List[str]:
        """Get list of NAGAs currently providing intel."""
        ...

    # =========================================================================
    # FLOOD INTEGRATION
    # =========================================================================

    def ingest_flood_observation(self, observation: FloodObservation) -> Optional[IntelItem]:
        """
        Convert a FloodObservation to IntelItem.

        Called by FloodManager when observations should become intel.
        Returns None if observation is not intel-worthy.
        """
        ...


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================

class NullIntelBridge:
    """
    Null implementation of IntelBridgeProtocol.

    Used when intelligence system is not available.
    """

    @property
    def opcode(self) -> MantraOpCode:
        return MantraOpCode.EXEC_OP

    @property
    def mahajana(self) -> str:
        return "shuka"

    def query(self, intel_query: IntelQuery) -> IntelResponse:
        return IntelResponse(
            items=(),
            query=intel_query,
            total_available=0
        )

    def query_for_chat(
        self,
        user_message: str,
        chat_context: str,
        limit: int = 3
    ) -> IntelResponse:
        return IntelResponse(
            items=(),
            query=IntelQuery(context=user_message),
            total_available=0
        )

    def get_recent(
        self,
        limit: int = 10,
        category: Optional[IntelCategory] = None
    ) -> List[IntelItem]:
        return []

    def get_critical(self) -> List[IntelItem]:
        return []

    def get_threats(self) -> List[IntelItem]:
        return []

    def subscribe(
        self,
        callback: Callable[[IntelItem], None],
        categories: Optional[Tuple[IntelCategory, ...]] = None
    ) -> str:
        return "null-subscription"

    def unsubscribe(self, subscription_id: str) -> bool:
        return False

    def get_available_categories(self) -> List[IntelCategory]:
        return list(IntelCategory)

    def get_active_nagas(self) -> List[str]:
        return []

    def ingest_flood_observation(self, observation: FloodObservation) -> Optional[IntelItem]:
        return None


# =============================================================================
# MANTRA CONNECTION
# =============================================================================

# Intel bridge maps to FETCH_RES
INTEL_OPCODE = MantraOpCode.EXEC_OP
INTEL_PHASE = "SERVE"
INTEL_WORD = "HARE"
INTEL_POSITION = 8
INTEL_MAHAJANA = "shuka"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocols
    "IntelBridgeProtocol",
    "NullIntelBridge",
    # Enums
    "IntelCategory",
    "IntelPriority",
    # Data types
    "IntelItem",
    "IntelQuery",
    "IntelResponse",
    # Mantra connection
    "INTEL_OPCODE",
    "INTEL_PHASE",
    "INTEL_WORD",
    "INTEL_POSITION",
    "INTEL_MAHAJANA",
]
