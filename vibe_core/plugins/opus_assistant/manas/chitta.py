"""
OPUS-168: CHITTA - The Perception Pool

Sanskrit: Chitta = Memory, Subconscious, Storehouse of Impressions

"cittaṁ hi sarvaṁ kalpayet" - The mind imagines everything.

Chitta is the first layer of the Antahkarana (inner instrument).
It receives raw perceptions from all Jnanendriyas (senses) and
prepares them for Buddhi (intellect) to discriminate.

RESPONSIBILITIES:
1. Receive intents from all senses
2. Classify as Sthula (gross) or Sukshma (subtle)
3. Aggregate similar intents (reduce noise)
4. Deduplicate exact matches
5. Pass clean perception list to Buddhi

DOES NOT:
- Make decisions (that's Buddhi)
- Execute anything (that's Manas/Kernel)
- Store long-term (that's Memory/Karma)

Architecture:
    ┌─────────────────────────────────────────┐
    │              SENSES                      │
    │  PrakritiSense  ShrutaSense  PranaSense │
    │  SutraSense     KarmaSense   VivekaSense│
    └──────────────────┬──────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────┐
    │              CHITTA                      │
    │  ┌─────────────────────────────────┐    │
    │  │         Perception Pool         │    │
    │  │  • Aggregate by type            │    │
    │  │  • Deduplicate exact matches    │    │
    │  │  • Classify Sthula/Sukshma      │    │
    │  └─────────────────────────────────┘    │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
                    BUDDHI
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("MANAS.Chitta")


@dataclass
class PerceptionEntry:
    """
    A single perception from a sense.

    This is the atomic unit that flows through Chitta.
    Each sense produces these, Chitta aggregates them.
    """

    intent: Any  # Intent object
    source_sense: str  # e.g., "prakriti_sense"
    sense_type: str  # "sthula" or "sukshma"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    aggregated_with: List[str] = field(default_factory=list)

    @property
    def intent_type(self) -> str:
        """Get the intent type for grouping."""
        return getattr(self.intent, "intent_type", "unknown")

    @property
    def intent_id(self) -> str:
        """Get the intent ID."""
        return getattr(self.intent, "id", "unknown")

    @property
    def intent_title(self) -> str:
        """Get the intent title for deduplication."""
        return getattr(self.intent, "title", "")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type,
            "source_sense": self.source_sense,
            "sense_type": self.sense_type,
            "timestamp": self.timestamp.isoformat(),
            "aggregated_count": len(self.aggregated_with),
        }


class Chitta:
    """
    OPUS-168: The Perception Pool (Memory/Subconscious).

    Chitta collects perceptions from all senses and prepares them
    for Buddhi (intellect) to process. It does NOT decide - it aggregates.

    Usage:
        chitta = Chitta(workspace=Path.cwd())

        # Senses feed Chitta
        for intent in prakriti_sense.generate_intents():
            chitta.receive(intent, "prakriti_sense")

        # Process for Buddhi
        clean_perceptions = chitta.process()
    """

    # Sense classification: Sthula (gross/physical) vs Sukshma (subtle/mental)
    # Sthula: Direct perception of physical state
    # Sukshma: Abstract analysis, patterns, priorities
    STHULA_SENSES: Set[str] = {
        "prakriti_sense",  # System state (physical)
        "shruta_sense",  # Filesystem events (physical)
        "prana_sense",  # Agent presence (physical)
        "sutra_sense",  # Documentation gaps (physical artifacts)
    }

    SUKSHMA_SENSES: Set[str] = {
        "karma_sense",  # Historical patterns (mental/abstract)
        "viveka_sense",  # Priority discrimination (mental/abstract)
    }

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize Chitta.

        Args:
            workspace: Workspace root path
        """
        self._workspace = workspace or Path.cwd()
        self._pool: List[PerceptionEntry] = []
        self._stats = {
            "received": 0,
            "deduplicated": 0,
            "aggregated": 0,
            "processed": 0,
        }

        logger.debug("🧠 CHITTA: Perception pool initialized")

    def receive(self, intent: Any, source_sense: str) -> None:
        """
        Receive a perception from a sense.

        Args:
            intent: The Intent object from the sense
            source_sense: Name of the source sense (e.g., "prakriti_sense")
        """
        # Classify as Sthula or Sukshma
        if source_sense in self.STHULA_SENSES:
            sense_type = "sthula"
        elif source_sense in self.SUKSHMA_SENSES:
            sense_type = "sukshma"
        else:
            # Unknown sense defaults to Sthula (conservative)
            sense_type = "sthula"
            logger.debug(f"🧠 CHITTA: Unknown sense '{source_sense}' classified as sthula")

        entry = PerceptionEntry(
            intent=intent,
            source_sense=source_sense,
            sense_type=sense_type,
        )

        self._pool.append(entry)
        self._stats["received"] += 1

        logger.debug(
            f"🧠 CHITTA: Received {sense_type} perception from {source_sense}: "
            f"{entry.intent_type}"
        )

    def process(self) -> List[PerceptionEntry]:
        """
        Process the perception pool for Buddhi.

        Steps:
        1. Deduplicate exact matches (same type + title)
        2. Aggregate similar intents (group by type)
        3. Clear pool after processing

        Returns:
            Clean list of PerceptionEntry objects for Buddhi
        """
        if not self._pool:
            logger.debug("🧠 CHITTA: Pool empty, nothing to process")
            return []

        pool_size = len(self._pool)

        # Step 1: Deduplicate exact matches
        unique = self._deduplicate(self._pool)
        dedup_count = pool_size - len(unique)
        self._stats["deduplicated"] += dedup_count

        # Step 2: Aggregate similar (group by intent_type)
        aggregated = self._aggregate_similar(unique)
        agg_count = len(unique) - len(aggregated)
        self._stats["aggregated"] += agg_count

        # Step 3: Clear pool
        self._pool = []
        self._stats["processed"] += len(aggregated)

        logger.info(
            f"🧠 CHITTA: Processed {pool_size} → {len(aggregated)} perceptions "
            f"(dedup: {dedup_count}, agg: {agg_count})"
        )

        return aggregated

    def _deduplicate(self, entries: List[PerceptionEntry]) -> List[PerceptionEntry]:
        """
        Remove exact duplicates based on (intent_type, title).

        Args:
            entries: List of perception entries

        Returns:
            Deduplicated list
        """
        seen: Set[tuple] = set()
        unique: List[PerceptionEntry] = []

        for entry in entries:
            key = (entry.intent_type, entry.intent_title)
            if key not in seen:
                seen.add(key)
                unique.append(entry)

        return unique

    def _aggregate_similar(
        self, entries: List[PerceptionEntry]
    ) -> List[PerceptionEntry]:
        """
        Aggregate similar intents to reduce noise.

        Groups by intent_type, keeps highest priority, notes aggregation.

        Args:
            entries: Deduplicated list of entries

        Returns:
            Aggregated list with highest-priority representatives
        """
        # Group by intent_type
        by_type: Dict[str, List[PerceptionEntry]] = {}
        for entry in entries:
            by_type.setdefault(entry.intent_type, []).append(entry)

        result: List[PerceptionEntry] = []

        for intent_type, group in by_type.items():
            if len(group) == 1:
                # Single entry, no aggregation needed
                result.append(group[0])
            else:
                # Multiple entries of same type - aggregate
                # Sort by priority (CRITICAL=0 < LOW=3)
                sorted_group = sorted(
                    group,
                    key=lambda e: self._priority_value(e.intent),
                )

                # Keep highest priority (lowest value)
                primary = sorted_group[0]

                # Note which intents were aggregated
                primary.aggregated_with = [e.intent_id for e in sorted_group[1:]]

                result.append(primary)

                logger.debug(
                    f"🧠 CHITTA: Aggregated {len(group)} '{intent_type}' intents "
                    f"into 1 (primary: {primary.intent_id})"
                )

        return result

    def _priority_value(self, intent: Any) -> int:
        """
        Get numeric priority value for sorting.

        Lower = higher priority.
        """
        priority = getattr(intent, "priority", None)
        if priority is None:
            return 50  # Default medium

        # Handle both enum and string values
        priority_str = priority.value if hasattr(priority, "value") else str(priority)

        priority_map = {
            "critical": 0,
            "high": 25,
            "medium": 50,
            "low": 75,
        }

        return priority_map.get(priority_str.lower(), 50)

    @property
    def pool_size(self) -> int:
        """Current pool size."""
        return len(self._pool)

    @property
    def stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self._stats.copy()

    def get_pool_summary(self) -> Dict[str, Any]:
        """Get a summary of the current pool state."""
        sthula_count = sum(1 for e in self._pool if e.sense_type == "sthula")
        sukshma_count = sum(1 for e in self._pool if e.sense_type == "sukshma")

        by_sense: Dict[str, int] = {}
        for entry in self._pool:
            by_sense[entry.source_sense] = by_sense.get(entry.source_sense, 0) + 1

        return {
            "total": len(self._pool),
            "sthula": sthula_count,
            "sukshma": sukshma_count,
            "by_sense": by_sense,
            "stats": self._stats,
        }

    def clear(self) -> None:
        """Clear the pool without processing."""
        cleared = len(self._pool)
        self._pool = []
        logger.debug(f"🧠 CHITTA: Cleared {cleared} entries from pool")


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "Chitta",
    "PerceptionEntry",
]
