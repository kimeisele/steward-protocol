"""
MAHA MANAS — The Cognitive Mind Instance (Tattva #6)
=====================================================

BG 3.42: "manasas tu parā buddhir" — Buddhi is superior to Manas.

Manas sits BELOW Buddhi and ABOVE the senses in the Sankhya hierarchy.
It coordinates the full cognitive pipeline:
    Perceive (Chitta) → Discriminate (Buddhi) → Score (Viveka) → Learn (Synaptic)

This is the KING LAYER — any agent (Moltbook, opus_assistant, future agents)
consumes cognition from this one place.

Meditation Mode: Manas tracks intent outcomes and enters cooldown when
consecutive failures indicate the agent should OBSERVE, not ACT.
Inspired by opus_assistant/manas biorhythm + memory_store patterns.

Usage:
    from vibe_core.mahamantra.substrate.manas import get_manas

    manas = get_manas()
    clean = manas.perceive(entries)
    verdicts = manas.decide(clean, max_verdicts=5)
    manas.record_outcome(verdicts[0], success=True)
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Sequence, Set

from vibe_core.mahamantra.protocols._manas import (
    DharmaGateProtocol,
    ManaVerdict,
    PerceptionEntry,
    SynapticProtocol,
)
from vibe_core.mahamantra.substrate.core.seed import SHARANAGATI, TRINITY
from vibe_core.mahamantra.substrate.manas.chitta import Chitta
from vibe_core.mahamantra.substrate.manas.synaptic import HebbianSynaptic
from vibe_core.mahamantra.substrate.manas.viveka import is_viable, score_priority

logger = logging.getLogger("MAHAMANTRA.MANAS")

# Tattva constant — Manas is element #6 in Sankhya
MANAS_TATTVA = SHARANAGATI  # 6

# Cooldown constants (derived from TRINITY)
MAX_CONSECUTIVE_FAILURES = TRINITY  # 3 failures → cooldown
COOLDOWN_SECONDS = 600  # 10 min (Moltbook cron = */10)


class MahaManas:
    """The cognitive mind — Tattva #6.

    Stateful singleton. Coordinates perception → discrimination → learning.
    Wires Chitta (pool), Buddhi (discrimination), Viveka (scoring), Synaptic (learning).

    Meditation Mode: tracks intent outcomes. After MAX_CONSECUTIVE_FAILURES
    from a source, that source enters cooldown. When ALL sources are cooling,
    should_act() returns False — heartbeat becomes observation-only.
    """

    def __init__(self) -> None:
        self._chitta = Chitta()
        self._synaptic: SynapticProtocol = HebbianSynaptic()
        self._dharma_gate: Optional[DharmaGateProtocol] = None
        self._perceive_count = 0
        self._decide_count = 0
        self._learn_count = 0
        # Cooldown tracking
        self._cooldowns: Dict[str, float] = {}  # source → cooldown start timestamp
        self._failure_counts: Dict[str, int] = {}  # source → consecutive failures
        self._known_sources: Set[str] = set()
        self._last_approved_count = -1  # -1 = no decide() yet

    def set_dharma_gate(self, gate: DharmaGateProtocol) -> None:
        """Wire a DharmaGate for constraint checking."""
        self._dharma_gate = gate

    def set_synaptic(self, backend: SynapticProtocol) -> None:
        """Replace the default HebbianSynaptic with a custom backend."""
        self._synaptic = backend

    def set_state_dir(self, path: "Path") -> None:  # noqa: F821
        """Set persistence directory for synaptic learning."""
        if isinstance(self._synaptic, HebbianSynaptic):
            self._synaptic.set_state_dir(path)

    def perceive(self, entries: Sequence[PerceptionEntry]) -> Sequence[PerceptionEntry]:
        """Receive perceptions through Chitta — dedup and clean.

        Also tracks known sources for should_act() meditation gate.
        Filters out perceptions from sources in cooldown.

        Args:
            entries: Raw perceptions from any source.

        Returns:
            Deduplicated, clean perception list (cooldown-filtered).
        """
        # Track sources
        for e in entries:
            self._known_sources.add(e.source)

        # Filter cooldown sources BEFORE Chitta processing
        active = [e for e in entries if not self.is_in_cooldown(e.source)]
        cooled = len(entries) - len(active)
        if cooled > 0:
            logger.info(
                "perceive: %d/%d entries cooled down (skipped)",
                cooled,
                len(entries),
            )

        self._chitta.receive_batch(active)
        clean = self._chitta.process()
        self._perceive_count += 1

        logger.debug(
            "perceive #%d: %d entries → %d active → %d clean",
            self._perceive_count,
            len(entries),
            len(active),
            len(clean),
        )
        return clean

    def decide(
        self,
        perceptions: Sequence[PerceptionEntry],
        *,
        max_verdicts: int = 5,
    ) -> Sequence[ManaVerdict]:
        """Discriminate perceptions into verdicts.

        For each perception:
        1. Buddhi.think() → cognitive frame (BuddhiResult)
        2. Viveka → priority score from prana/integrity/function
        3. DharmaGate → constraint check (if wired)
        4. Synaptic → confidence from learned weights
        5. Filter: approved = viable AND dharma_ok

        Returns:
            Sorted by priority_score (descending), limited to max_verdicts.
        """
        from vibe_core.mahamantra.substrate.buddhi import get_buddhi

        buddhi = get_buddhi()
        verdicts: List[ManaVerdict] = []

        for p in perceptions:
            # Step 1: Buddhi discriminates
            cognition = buddhi.think(p.content)

            # Step 2: Viveka scores priority
            priority = score_priority(cognition)
            viable = is_viable(cognition)

            # Step 3: DharmaGate checks constraints
            dharma_ok = True
            dharma_reason = "no gate"
            if self._dharma_gate is not None:
                dharma_ok, dharma_reason = self._dharma_gate.check(p)

            # Step 4: Synaptic confidence
            confidence = self._synaptic.get_weight(
                trigger=p.source,
                action=p.category,
            )

            # Step 5: Approve if viable and dharma-ok
            approved = viable and dharma_ok
            reason = "approved" if approved else ("not viable" if not viable else dharma_reason)

            verdicts.append(
                ManaVerdict(
                    perception=p,
                    approved=approved,
                    priority_score=priority,
                    confidence=confidence,
                    dharma_ok=dharma_ok,
                    dharma_reason=dharma_reason,
                    reason=reason,
                    buddhi=cognition,
                )
            )

        # Sort by priority (descending), filter approved, limit
        approved_verdicts = [v for v in verdicts if v.approved]
        approved_verdicts.sort(key=lambda v: v.priority_score, reverse=True)

        self._decide_count += 1
        self._last_approved_count = len(approved_verdicts)
        logger.info(
            "decide #%d: %d perceptions → %d approved (max %d)",
            self._decide_count,
            len(perceptions),
            len(approved_verdicts),
            max_verdicts,
        )

        return approved_verdicts[:max_verdicts]

    def learn(self, verdict: ManaVerdict, success: bool) -> None:
        """Hebbian learning — update synaptic weights from outcome.

        Args:
            verdict: The verdict that was acted upon.
            success: Whether the action succeeded.
        """
        new_weight = self._synaptic.update(
            trigger=verdict.perception.source,
            action=verdict.perception.category,
            success=success,
        )

        # Flush to disk
        if isinstance(self._synaptic, HebbianSynaptic):
            self._synaptic.flush()

        self._learn_count += 1
        logger.debug(
            "learn #%d: %s → %.3f (%s)",
            self._learn_count,
            verdict.perception.source,
            new_weight,
            "success" if success else "failure",
        )

    def record_outcome(self, verdict: ManaVerdict, success: bool) -> None:
        """Record intent outcome — synaptic learning + cooldown tracking.

        Success: clears failure counter and cooldown for source.
        Failure: increments failure counter. After MAX_CONSECUTIVE_FAILURES,
        source enters cooldown (no new verdicts until cooldown expires).

        Args:
            verdict: The verdict that was acted upon.
            success: Whether the action succeeded.
        """
        source = verdict.perception.source

        if success:
            # Clear cooldown state on success
            self._failure_counts.pop(source, None)
            self._cooldowns.pop(source, None)
        else:
            count = self._failure_counts.get(source, 0) + 1
            self._failure_counts[source] = count
            if count >= MAX_CONSECUTIVE_FAILURES:
                self._cooldowns[source] = time.time()
                logger.warning(
                    "Source '%s' entering cooldown after %d consecutive failures",
                    source,
                    count,
                )

        # Hebbian learning (existing mechanism)
        self.learn(verdict, success)

    def is_in_cooldown(self, source: str) -> bool:
        """Check if a source is in post-failure cooldown.

        Cooldown expires after COOLDOWN_SECONDS (600s = 10 min).
        Expired cooldowns are auto-cleared.
        """
        ts = self._cooldowns.get(source)
        if ts is None:
            return False
        if time.time() - ts > COOLDOWN_SECONDS:
            # Cooldown expired — clear state
            self._cooldowns.pop(source, None)
            self._failure_counts.pop(source, None)
            logger.info("Source '%s' cooldown expired — reactivated", source)
            return False
        return True

    def should_act(self) -> bool:
        """Should the agent produce content this heartbeat?

        Returns False (meditation mode) when:
        1. ALL known sources are in cooldown (every recent intent failed)
        2. Last decide() produced zero approved verdicts

        If no decide() has run yet, returns True (no data to judge).
        """
        # No decision data yet — allow action
        if self._decide_count == 0:
            return True

        # All sources in cooldown?
        if self._known_sources and all(self.is_in_cooldown(s) for s in self._known_sources):
            logger.info(
                "MEDITATION: all %d sources in cooldown",
                len(self._known_sources),
            )
            return False

        # Last decide produced nothing?
        if self._last_approved_count == 0:
            logger.info("MEDITATION: last decide() produced 0 approved verdicts")
            return False

        return True

    @property
    def perceive_count(self) -> int:
        """Total number of perceive() calls."""
        return self._perceive_count

    @property
    def decide_count(self) -> int:
        """Total number of decide() calls."""
        return self._decide_count

    @property
    def learn_count(self) -> int:
        """Total number of learn() calls."""
        return self._learn_count

    def snapshot(self) -> dict:
        """Snapshot state for persistence/debugging."""
        return {
            "perceive_count": self._perceive_count,
            "decide_count": self._decide_count,
            "learn_count": self._learn_count,
            "last_approved_count": self._last_approved_count,
            "cooldowns": {s: t for s, t in self._cooldowns.items()},
            "failure_counts": dict(self._failure_counts),
            "known_sources": list(self._known_sources),
            "synaptic_weights": (self._synaptic.snapshot() if isinstance(self._synaptic, HebbianSynaptic) else {}),
        }
