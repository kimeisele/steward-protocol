"""
OPUS-168: BUDDHI - The Intellect

Sanskrit: Buddhi = Intellect, Wisdom, Discriminative Faculty

"buddhir jñānam asammohaḥ" - Intelligence, knowledge, and freedom from doubt.
(Bhagavad Gita 10.4)

Buddhi is the second layer of the Antahkarana (inner instrument).
It receives processed perceptions from Chitta and DISCRIMINATES which
intents should proceed to Manas (the kernel) for execution.

This is where DharmaSense and VivekaSense do their REAL work:
- VivekaSense: Priority scoring (P1→P5)
- DharmaSense: Ethical filtering (dharmic/adharmic)

RESPONSIBILITIES:
1. Score each intent with VivekaSense logic
2. Check ethical alignment with DharmaSense (BEFORE execution!)
3. Check resource availability
4. Check intent dependencies
5. Return ONLY approved intents to Manas

CRITICAL FIX:
- Before: DharmaSense checked at execution time (too late!)
- Now: DharmaSense checks at decision time (correct!)

Architecture:
    ┌─────────────────────────────────────────┐
    │              CHITTA                      │
    │         (Processed Perceptions)          │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────┐
    │              BUDDHI                      │
    │  ┌─────────────────────────────────┐    │
    │  │      Discrimination Engine      │    │
    │  │                                 │    │
    │  │  ┌─────────┐   ┌─────────────┐ │    │
    │  │  │ Viveka  │   │   Dharma    │ │    │
    │  │  │ (Rank)  │   │  (Ethics)   │ │    │
    │  │  └────┬────┘   └──────┬──────┘ │    │
    │  │       │               │        │    │
    │  │       └───────┬───────┘        │    │
    │  │               ▼                │    │
    │  │         APPROVED?              │    │
    │  └─────────────────────────────────┘    │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
                    MANAS
            (Only approved intents)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .chitta import PerceptionEntry

if TYPE_CHECKING:
    from .cortex.dharma_sense import DharmaSense

logger = logging.getLogger("MANAS.Buddhi")


@dataclass
class BuddhiVerdict:
    """
    Result of Buddhi's discrimination on a single intent.

    This contains the full reasoning for why an intent was approved or blocked.
    """

    intent: Any  # The original Intent object
    approved: bool  # Final verdict
    priority_score: float  # 0-100, higher = more important
    dharmic: bool  # Passed ethical check?
    dharma_reason: str  # Explanation from DharmaSense
    resource_ok: bool  # Resources available?
    dependencies_met: bool  # Dependencies satisfied?
    final_reason: str  # Human-readable summary
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Source tracking
    source_sense: str = ""
    sense_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage."""
        return {
            "intent_id": getattr(self.intent, "id", "unknown"),
            "intent_type": getattr(self.intent, "intent_type", "unknown"),
            "approved": self.approved,
            "priority_score": self.priority_score,
            "dharmic": self.dharmic,
            "dharma_reason": self.dharma_reason,
            "resource_ok": self.resource_ok,
            "dependencies_met": self.dependencies_met,
            "final_reason": self.final_reason,
            "source_sense": self.source_sense,
            "sense_type": self.sense_type,
            "timestamp": self.timestamp.isoformat(),
        }


class Buddhi:
    """
    OPUS-168: The Intellect (Discrimination/Decision Layer).

    Buddhi receives processed perceptions from Chitta and decides
    which intents should proceed to Manas for execution.

    Usage:
        buddhi = Buddhi(
            workspace=Path.cwd(),
            dharma_sense=dharma_sense,
        )

        # Chitta provides processed perceptions
        perceptions = chitta.process()

        # Buddhi discriminates
        verdicts = buddhi.discriminate(perceptions, max_intents=5)

        # Only approved intents proceed to Manas
        approved = [v.intent for v in verdicts if v.approved]
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        dharma_sense: Optional["DharmaSense"] = None,
    ):
        """
        Initialize Buddhi.

        Args:
            workspace: Workspace root path
            dharma_sense: DharmaSense instance for ethical checks
        """
        self._workspace = workspace or Path.cwd()
        self._dharma = dharma_sense

        self._stats = {
            "considered": 0,
            "approved": 0,
            "blocked_dharma": 0,
            "blocked_resources": 0,
            "blocked_dependencies": 0,
        }

        logger.debug("🧘 BUDDHI: Intellect layer initialized")

    def inject_dharma_sense(self, sense: "DharmaSense") -> None:
        """
        Inject DharmaSense for ethical checks.

        Args:
            sense: DharmaSense instance
        """
        self._dharma = sense
        logger.info("🧘 BUDDHI: DharmaSense injected for ethical discrimination")

    def discriminate(
        self,
        perceptions: List[PerceptionEntry],
        max_intents: int = 5,
    ) -> List[BuddhiVerdict]:
        """
        Discriminate which intents should proceed to Manas.

        This is the DECIDE phase done RIGHT:
        1. Score each intent by priority (VivekaSense logic)
        2. Check ethical alignment (DharmaSense - BEFORE execution!)
        3. Check resource availability
        4. Check dependencies
        5. Sort by priority, limit to max_intents

        Args:
            perceptions: Processed perceptions from Chitta
            max_intents: Maximum intents to approve

        Returns:
            List of BuddhiVerdict objects (approved ones only, sorted by priority)
        """
        if not perceptions:
            logger.debug("🧘 BUDDHI: No perceptions to discriminate")
            return []

        verdicts: List[BuddhiVerdict] = []

        for entry in perceptions:
            intent = entry.intent
            self._stats["considered"] += 1

            # 1. Priority scoring (VivekaSense logic)
            priority_score = self._score_priority(intent)

            # 2. Ethical check with DharmaSense (THE KEY FIX!)
            dharmic, dharma_reason = self._check_dharma(intent)

            # 3. Resource check
            resource_ok = self._check_resources(intent)

            # 4. Dependency check
            deps_met = self._check_dependencies(intent)

            # Final verdict
            approved = dharmic and resource_ok and deps_met
            final_reason = self._build_reason(dharmic, resource_ok, deps_met, dharma_reason, priority_score)

            # Track stats
            if approved:
                self._stats["approved"] += 1
            elif not dharmic:
                self._stats["blocked_dharma"] += 1
            elif not resource_ok:
                self._stats["blocked_resources"] += 1
            elif not deps_met:
                self._stats["blocked_dependencies"] += 1

            verdict = BuddhiVerdict(
                intent=intent,
                approved=approved,
                priority_score=priority_score,
                dharmic=dharmic,
                dharma_reason=dharma_reason,
                resource_ok=resource_ok,
                dependencies_met=deps_met,
                final_reason=final_reason,
                source_sense=entry.source_sense,
                sense_type=entry.sense_type,
            )

            verdicts.append(verdict)

            if not approved:
                logger.info(f"🧘 BUDDHI: BLOCKED intent '{getattr(intent, 'title', '?')}' - {final_reason}")

        # Sort by priority score (highest first)
        verdicts.sort(key=lambda v: v.priority_score, reverse=True)

        # Filter to approved only, limit to max
        approved_verdicts = [v for v in verdicts if v.approved][:max_intents]

        # Log summary
        blocked_count = len(verdicts) - len([v for v in verdicts if v.approved])
        logger.info(
            f"🧘 BUDDHI: Discriminated {len(perceptions)} → {len(approved_verdicts)} approved, {blocked_count} blocked"
        )

        return approved_verdicts

    def _check_dharma(self, intent: Any) -> Tuple[bool, str]:
        """
        Check ethical alignment with DharmaSense.

        THIS IS THE KEY FIX: We check Dharma at DECISION time,
        not at execution time!

        Args:
            intent: The intent to check

        Returns:
            (is_dharmic, reason)
        """
        if not self._dharma:
            # No DharmaSense = permissive mode (legacy compatibility)
            return True, "No DharmaSense - permissive mode"

        try:
            verdict = self._dharma.check_dharmic_alignment(intent, agent_id="manas")
            return verdict.is_dharmic, verdict.reason
        except Exception as e:
            logger.warning(f"🧘 BUDDHI: DharmaSense check failed: {e}")
            # On error, default to permissive (don't block due to bugs)
            return True, f"Dharma check error: {e}"

    def _score_priority(self, intent: Any) -> float:
        """
        Score priority using VivekaSense logic.

        Higher score = higher priority.

        Args:
            intent: The intent to score

        Returns:
            Priority score (0-100)
        """
        # Base score from intent priority enum
        priority = getattr(intent, "priority", None)

        if priority is None:
            return 50.0

        priority_str = priority.value if hasattr(priority, "value") else str(priority)

        base_scores = {
            "critical": 100.0,
            "high": 75.0,
            "medium": 50.0,
            "low": 25.0,
        }

        score = base_scores.get(priority_str.lower(), 50.0)

        # Bonus for healing intents (survival first)
        intent_type = getattr(intent, "intent_type", "")
        if "heal" in intent_type.lower() or "fix" in intent_type.lower():
            score = min(100.0, score + 10.0)

        # Bonus for intents with circuits (actionable)
        if getattr(intent, "circuit_to_execute", None):
            score = min(100.0, score + 5.0)

        return score

    def _check_resources(self, intent: Any) -> bool:
        """
        Check if resources are available for this intent.

        TODO: Implement actual resource checking:
        - CPU availability
        - Memory limits
        - Rate limits
        - Concurrent execution limits

        Args:
            intent: The intent to check

        Returns:
            True if resources available
        """
        # For now, always available (to be implemented)
        return True

    def _check_dependencies(self, intent: Any) -> bool:
        """
        Check if intent dependencies are met.

        TODO: Implement dependency checking:
        - Required files exist
        - Required services available
        - Previous intents completed

        Args:
            intent: The intent to check

        Returns:
            True if dependencies met
        """
        # For now, always met (to be implemented)
        return True

    def _build_reason(
        self,
        dharmic: bool,
        resource_ok: bool,
        deps_met: bool,
        dharma_reason: str,
        priority_score: float,
    ) -> str:
        """
        Build human-readable verdict reason.

        Args:
            dharmic: Passed dharma check?
            resource_ok: Resources available?
            deps_met: Dependencies met?
            dharma_reason: Reason from DharmaSense
            priority_score: Calculated priority

        Returns:
            Human-readable reason string
        """
        if not dharmic:
            return f"BLOCKED (Dharma): {dharma_reason}"
        if not resource_ok:
            return "BLOCKED (Resources): Insufficient resources"
        if not deps_met:
            return "BLOCKED (Dependencies): Dependencies not met"
        return f"APPROVED (Priority: {priority_score:.0f})"

    @property
    def stats(self) -> Dict[str, int]:
        """Get discrimination statistics."""
        return self._stats.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of Buddhi state and stats."""
        return {
            "dharma_available": self._dharma is not None,
            "stats": self._stats,
        }


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "Buddhi",
    "BuddhiVerdict",
]
