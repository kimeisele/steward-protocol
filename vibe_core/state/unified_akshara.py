"""
OPUS-154: Unified Akshara (Ekākṣara) - The Indestructible Substrate

अक्षर (Akshara) = a- (not) + kṣara (destructible) = The Indestructible
ॐ (OM) = Ekākṣara = The One Syllable = Foundation of Truth

This module UNIFIES:
- OPUS-114: Akshara Resonance (phonetic harmony via Varga)
- OPUS-140: Sanskrit Matrix (memory compression)
- PRANA: The curiosity/entropy factor (prevents crystallization)

The Three Aspects are One:
    VIBRATION  (Resonance)   → HOW things connect
    CRYSTALLIZE (Memory)     → WHAT patterns form
    PRANA (Exploration)      → WHY we try new paths

Dharmic Score Formula:
    Without PRANA: score = weight × resonance          ← CRYSTALLIZES (dead)
    With PRANA:    score = (weight × resonance) + ε    ← LIVING (explores)

Where ε = prana_factor × random(0, 1)

The system already has VAIRAGYA (ego pruning) in viveka_action.py.
PRANA complements VAIRAGYA:
    - VAIRAGYA: Prevents over-confidence (caps weights at 0.95)
    - PRANA: Enables exploration (adds small random boost to all candidates)
"""

import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("EKAKSHARA")


@dataclass
class PranaRecommendation:
    """
    A routing recommendation with PRANA (curiosity) factor.

    Extends DharmicRecommendation with:
    - prana: The exploration/curiosity boost applied
    - unified_score: dharmic_score + prana
    """

    action: str
    weight: float
    resonance: float
    dharmic_score: float  # weight × resonance (from OPUS-114)
    prana: float  # Random exploration factor
    unified_score: float  # dharmic_score + prana (final decision)
    trigger: str
    varga_trigger: str
    varga_action: str


class UnifiedAkshara:
    """
    The Ekākṣara (One Syllable) - Unified routing substrate.

    Combines:
    1. SynapticMemory.consult_dharmic() - existing weight × resonance
    2. PRANA factor - new exploration/curiosity

    This is NOT a 3rd system - it's the UNIFICATION of existing systems
    under the true Sanskrit meaning of Akshara.
    """

    # Default PRANA intensity (0.0 to 1.0)
    # Higher = more exploration, lower = more exploitation
    # 0.1 means up to 10% random boost
    DEFAULT_PRANA = 0.1

    # Minimum PRANA for "cold" paths (never tried before)
    # Ensures completely new paths get a chance
    COLD_PATH_PRANA = 0.15

    def __init__(
        self,
        workspace: Optional[Path] = None,
        prana_factor: float = DEFAULT_PRANA,
    ):
        """
        Initialize the Unified Akshara substrate.

        Args:
            workspace: Project workspace (for loading synapses)
            prana_factor: Exploration intensity (0.0-1.0)
        """
        self._workspace = workspace or Path.cwd()
        self._prana_factor = prana_factor

        # Lazy import to avoid circular dependencies
        self._synaptic_memory = None

        logger.info(f"🕉️ Ekākṣara initialized (prana={prana_factor:.2f})")

    @property
    def synaptic_memory(self):
        """Lazy-load SynapticMemory to avoid import cycles."""
        if self._synaptic_memory is None:
            from vibe_core.plugins.opus_assistant.manas.triggers import SynapticMemory

            self._synaptic_memory = SynapticMemory(self._workspace)
        return self._synaptic_memory

    def consult(
        self,
        trigger: str,
        candidates: Optional[List[str]] = None,
        min_score: float = 0.0,
        limit: int = 5,
    ) -> List[PranaRecommendation]:
        """
        Consult the Akshara substrate for routing recommendations.

        This is the CORE method that:
        1. Gets dharmic recommendations (weight × resonance)
        2. Adds PRANA factor for exploration
        3. Returns sorted by unified_score

        Args:
            trigger: The trigger pattern (e.g., "trigger:test_failure")
            candidates: Optional filter to only these actions
            min_score: Minimum unified_score threshold
            limit: Maximum recommendations to return

        Returns:
            List of PranaRecommendation sorted by unified_score descending
        """
        # Get dharmic recommendations from existing system
        dharmic_recs = self.synaptic_memory.consult_dharmic(
            trigger=trigger,
            min_dharmic_score=0.0,  # We filter after adding PRANA
            limit=100,  # Get all, we'll filter ourselves
        )

        if not dharmic_recs:
            logger.debug(f"🕉️ No learned paths for {trigger}")
            return []

        # Filter by candidates if provided
        if candidates:
            candidate_set = set(candidates)
            dharmic_recs = [r for r in dharmic_recs if r.action in candidate_set]

        # Add PRANA (exploration factor) to each recommendation
        prana_recs = []
        for rec in dharmic_recs:
            # Calculate PRANA
            # - Low-weight paths get slightly more prana (encourages exploration)
            # - High-weight paths get less prana (exploitation)
            base_prana = self._prana_factor

            # Inverse weight bonus: paths with lower weights get more exploration
            # This prevents the "echo chamber" effect
            weight_factor = 1.0 - (rec.weight * 0.5)  # 0.5-1.0 range
            prana = random.uniform(0, base_prana * weight_factor)

            # Unified score = dharmic + prana
            unified_score = rec.dharmic_score + prana

            if unified_score >= min_score:
                prana_recs.append(
                    PranaRecommendation(
                        action=rec.action,
                        weight=rec.weight,
                        resonance=rec.resonance,
                        dharmic_score=rec.dharmic_score,
                        prana=prana,
                        unified_score=unified_score,
                        trigger=trigger,
                        varga_trigger=rec.varga_trigger,
                        varga_action=rec.varga_action,
                    )
                )

        # Sort by unified_score (dharmic + prana)
        prana_recs.sort(key=lambda r: r.unified_score, reverse=True)

        # Log the decision
        if prana_recs:
            winner = prana_recs[0]
            logger.info(
                f"🕉️ AKSHARA: {trigger} → {winner.action} "
                f"(D:{winner.dharmic_score:.3f} + P:{winner.prana:.3f} = {winner.unified_score:.3f})"
            )

        return prana_recs[:limit]

    def route(self, trigger: str, candidates: Optional[List[str]] = None) -> Optional[str]:
        """
        Route a trigger to the best action.

        Simple interface for LayeredRouter integration.

        Args:
            trigger: The trigger pattern
            candidates: Optional filter to these actions

        Returns:
            The selected action, or None if no recommendations
        """
        recs = self.consult(trigger, candidates, limit=1)
        if recs:
            return recs[0].action
        return None

    def get_exploration_report(self) -> Dict[str, Any]:
        """
        Generate a report on exploration vs exploitation balance.

        Useful for tuning PRANA factor.
        """
        # Get all synaptic data
        synapses = self.synaptic_memory._load_synapses()
        weights = synapses.get("weights", {})

        # Analyze weight distribution
        all_weights = []
        for trigger, actions in weights.items():
            for action, weight in actions.items():
                all_weights.append(weight)

        if not all_weights:
            return {"status": "no_data", "prana_factor": self._prana_factor}

        avg_weight = sum(all_weights) / len(all_weights)
        max_weight = max(all_weights)
        min_weight = min(all_weights)

        # Calculate crystallization risk
        # High average weight = system is "crystallizing"
        crystallization_risk = "low"
        if avg_weight > 0.8:
            crystallization_risk = "high"
        elif avg_weight > 0.6:
            crystallization_risk = "medium"

        return {
            "prana_factor": self._prana_factor,
            "total_synapses": len(all_weights),
            "avg_weight": round(avg_weight, 3),
            "max_weight": round(max_weight, 3),
            "min_weight": round(min_weight, 3),
            "crystallization_risk": crystallization_risk,
            "recommendation": (
                "Increase prana_factor" if crystallization_risk == "high" else "Current balance is healthy"
            ),
        }

    def set_prana(self, factor: float) -> None:
        """
        Adjust PRANA factor dynamically.

        Args:
            factor: New prana factor (0.0-1.0)
        """
        self._prana_factor = max(0.0, min(1.0, factor))
        logger.info(f"🕉️ PRANA adjusted to {self._prana_factor:.2f}")


# =============================================================================
# Convenience Functions
# =============================================================================

_global_akshara: Optional[UnifiedAkshara] = None


def get_akshara(workspace: Optional[Path] = None) -> UnifiedAkshara:
    """
    Get or create the global UnifiedAkshara instance.

    Singleton pattern for integration with existing systems.
    """
    global _global_akshara
    if _global_akshara is None:
        _global_akshara = UnifiedAkshara(workspace=workspace)
    return _global_akshara


def consult_akshara(trigger: str, candidates: Optional[List[str]] = None) -> Optional[str]:
    """
    Convenience function to route through Akshara substrate.

    Args:
        trigger: The trigger pattern
        candidates: Optional filter to these actions

    Returns:
        The selected action, or None
    """
    return get_akshara().route(trigger, candidates)
