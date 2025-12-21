"""
OPUS-154: Unified Akshara (Ekākṣara) - The Indestructible Substrate

अक्षर (Akshara) = a- (not) + kṣara (destructible) = The Indestructible
ॐ (OM) = Ekākṣara = The One Syllable = Foundation of Truth

This module UNIFIES:
- OPUS-114: Akshara Resonance (phonetic harmony via Varga)
- OPUS-140: Sanskrit Matrix (memory compression)
- OPUS-200/201: Quantum Reactor (phonetic physics + crypto mass)  ← NEW
- PRANA: The curiosity/entropy factor (prevents crystallization)

The Four Aspects are One:
    VIBRATION  (Resonance)   → HOW things connect
    CRYSTALLIZE (Memory)     → WHAT patterns form
    QUANTUM    (Reactor)     → Physics-based energy computation  ← NEW
    PRANA (Exploration)      → WHY we try new paths

Dharmic Score Formula (upgraded):
    Without Reactor: score = weight × resonance + prana
    With Reactor:    score = weight × resonance × quantum_boost + prana

Where quantum_boost = 1.0 + (reactor_energy × 0.3)
High quantum energy amplifies good recommendations.
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
    A routing recommendation with PRANA (curiosity) and QUANTUM factors.

    Extends DharmicRecommendation with:
    - prana: The exploration/curiosity boost applied
    - quantum_energy: Energy from QuantumReactor (if enabled)
    - quantum_boost: Multiplier from reactor (1.0 if disabled)
    - unified_score: dharmic_score × quantum_boost + prana
    """

    action: str
    weight: float
    resonance: float
    dharmic_score: float  # weight × resonance (from OPUS-114)
    prana: float  # Random exploration factor
    unified_score: float  # dharmic_score × quantum_boost + prana (final decision)
    trigger: str
    varga_trigger: str
    varga_action: str
    # OPUS-200/201: Quantum Reactor integration
    quantum_energy: float = 0.0  # Total energy from reactor
    quantum_boost: float = 1.0  # Multiplier applied to dharmic_score


class UnifiedAkshara:
    """
    The Ekākṣara (One Syllable) - Unified routing substrate.

    Combines:
    1. SynapticMemory.consult_dharmic() - existing weight × resonance
    2. PRANA factor - exploration/curiosity
    3. QuantumReactor - physics-based energy computation (OPUS-200/201)

    This is the UNIFICATION of ALL Sanskrit systems under one API.
    """

    # Default PRANA intensity (0.0 to 1.0)
    # Higher = more exploration, lower = more exploitation
    # 0.1 means up to 10% random boost
    DEFAULT_PRANA = 0.1

    # Minimum PRANA for "cold" paths (never tried before)
    # Ensures completely new paths get a chance
    COLD_PATH_PRANA = 0.15

    # Quantum Reactor thresholds
    QUANTUM_HIGH_ENERGY = 0.7  # Above this, emit event
    QUANTUM_BOOST_FACTOR = 0.3  # Max 30% boost from reactor

    def __init__(
        self,
        workspace: Optional[Path] = None,
        prana_factor: float = DEFAULT_PRANA,
        enable_reactor: bool = True,
        session_salt: str = "",
    ):
        """
        Initialize the Unified Akshara substrate.

        Args:
            workspace: Project workspace (for loading synapses)
            prana_factor: Exploration intensity (0.0-1.0)
            enable_reactor: Whether to use QuantumReactor (OPUS-200/201)
            session_salt: Cryptographic salt for reactor (session context)
        """
        self._workspace = workspace or Path.cwd()
        self._prana_factor = prana_factor
        self._enable_reactor = enable_reactor
        self._session_salt = session_salt or self._generate_session_salt()

        # Lazy imports to avoid circular dependencies
        self._synaptic_memory = None
        self._reactor = None

        reactor_status = "enabled" if enable_reactor else "disabled"
        logger.info(f"🕉️ Ekākṣara initialized (prana={prana_factor:.2f}, reactor={reactor_status})")

    def _generate_session_salt(self) -> str:
        """Generate a session-unique salt."""
        import hashlib
        import time

        data = f"{time.time()}:{id(self)}".encode()
        return hashlib.sha256(data).hexdigest()[:16]

    @property
    def synaptic_memory(self):
        """Lazy-load SynapticMemory to avoid import cycles."""
        if self._synaptic_memory is None:
            from vibe_core.plugins.opus_assistant.manas.triggers import SynapticMemory

            self._synaptic_memory = SynapticMemory(self._workspace)
        return self._synaptic_memory

    @property
    def reactor(self):
        """Lazy-load QuantumReactor to avoid import cycles."""
        if self._reactor is None and self._enable_reactor:
            try:
                from vibe_core.reactor import QuantumReactor

                self._reactor = QuantumReactor(initial_inertia=0.3)
                logger.debug("🔥 QuantumReactor loaded")
            except ImportError as e:
                logger.warning(f"QuantumReactor not available: {e}")
                self._enable_reactor = False
        return self._reactor

    def _compute_quantum_energy(self, trigger: str, action: str) -> float:
        """
        Compute quantum resonance energy between trigger and action.

        Returns energy value (0.0-1.0), or 0.0 if reactor disabled.
        """
        if not self._enable_reactor or self.reactor is None:
            return 0.0

        try:
            from vibe_core.reactor import encode

            # Encode both trigger and action as tensors
            trigger_tensor = encode(trigger, self._session_salt)
            action_tensor = encode(action, self._session_salt)

            # Compute resonance
            field = self.reactor.resonate(trigger_tensor, action_tensor)
            return field.total_energy

        except Exception as e:
            logger.warning(f"Quantum computation failed: {e}")
            return 0.0

    def _emit_high_energy_event(self, trigger: str, action: str, energy: float) -> None:
        """Emit event when quantum energy exceeds threshold."""
        try:
            import asyncio

            from vibe_core.event_bus import EventType, emit_event

            # Run async emit in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context, schedule it
                asyncio.create_task(
                    emit_event(
                        EventType.BROADCAST,
                        agent_id="ekakshara",
                        description=f"High resonance: {trigger} → {action}",
                        metadata={"energy": energy, "trigger": trigger, "action": action},
                    )
                )
            else:
                # Sync context, just log (don't block)
                logger.info(f"⚡ HIGH ENERGY: {trigger} → {action} (E={energy:.3f})")
        except Exception as e:
            logger.debug(f"Event emit skipped: {e}")

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
        2. Computes quantum energy via QuantumReactor (OPUS-200/201)
        3. Adds PRANA factor for exploration
        4. Returns sorted by unified_score

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

        # Add PRANA and QUANTUM factors to each recommendation
        prana_recs = []
        for rec in dharmic_recs:
            # 1. Calculate QUANTUM ENERGY (OPUS-200/201)
            quantum_energy = self._compute_quantum_energy(trigger, rec.action)

            # Quantum boost: high energy amplifies dharmic score
            # boost = 1.0 + (energy × BOOST_FACTOR)
            # e.g., energy=0.8 → boost=1.24 (24% amplification)
            quantum_boost = 1.0 + (quantum_energy * self.QUANTUM_BOOST_FACTOR)

            # 2. Calculate PRANA (exploration factor)
            # Low-weight paths get slightly more prana
            base_prana = self._prana_factor
            weight_factor = 1.0 - (rec.weight * 0.5)  # 0.5-1.0 range
            prana = random.uniform(0, base_prana * weight_factor)

            # 3. Unified score = (dharmic × quantum_boost) + prana
            boosted_dharmic = rec.dharmic_score * quantum_boost
            unified_score = boosted_dharmic + prana

            # 4. Emit event if high energy
            if quantum_energy >= self.QUANTUM_HIGH_ENERGY:
                self._emit_high_energy_event(trigger, rec.action, quantum_energy)

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
                        quantum_energy=quantum_energy,
                        quantum_boost=quantum_boost,
                    )
                )

        # Sort by unified_score (dharmic × quantum_boost + prana)
        prana_recs.sort(key=lambda r: r.unified_score, reverse=True)

        # Log the decision with quantum info
        if prana_recs:
            winner = prana_recs[0]
            quantum_str = (
                f" Q:{winner.quantum_energy:.2f}×{winner.quantum_boost:.2f}" if winner.quantum_energy > 0 else ""
            )
            logger.info(
                f"🕉️ AKSHARA: {trigger} → {winner.action} "
                f"(D:{winner.dharmic_score:.3f}{quantum_str} + P:{winner.prana:.3f} = {winner.unified_score:.3f})"
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


def get_akshara(
    workspace: Optional[Path] = None,
    enable_reactor: bool = True,
    session_salt: str = "",
) -> UnifiedAkshara:
    """
    Get or create the global UnifiedAkshara instance.

    Singleton pattern for integration with existing systems.

    Args:
        workspace: Project workspace path
        enable_reactor: Whether to enable QuantumReactor (OPUS-200/201)
        session_salt: Cryptographic salt for reactor computations

    Returns:
        The global UnifiedAkshara instance
    """
    global _global_akshara
    if _global_akshara is None:
        _global_akshara = UnifiedAkshara(
            workspace=workspace,
            enable_reactor=enable_reactor,
            session_salt=session_salt,
        )
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
