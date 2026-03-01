"""
MANAS Protocol — The Cognitive Mind (Tattva #6)
================================================

BG 3.42: indriyāṇi parāṇy āhur indriyebhyaḥ paraṁ manaḥ
         manasas tu parā buddhir yo buddheḥ paratas tu saḥ

"The senses are superior to the body, the mind superior to the senses,
 the intelligence superior to the mind — and the soul is superior
 to the intelligence."

Manas = Element #6 (SHARANAGATI) in the Sankhya system.
BELOW Buddhi (intelligence/discrimination), ABOVE the senses.

Manas PERCEIVES and COORDINATES. Buddhi DISCRIMINATES.
Together they form the cognitive pipeline:
    Senses → Manas (perceive, filter, prioritize) → Buddhi (discriminate) → Verdict
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Protocol, Sequence, Tuple, runtime_checkable


@dataclass(frozen=True)
class PerceptionEntry:
    """A single perception received by Manas from any sense.

    Frozen dataclass — immutable after creation.
    """

    content: str  # perceived text
    source: str  # "feed_scan", "prakriti_sense", "dm_inbox", etc.
    category: str  # "sthula" (gross) | "sukshma" (subtle)
    priority: int = 50  # 0-100, default midpoint
    context: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ManaVerdict:
    """Manas cognitive verdict — perceive + discriminate + confidence.

    Each verdict represents Manas's decision about a perception:
    should we act on it, and with what priority/confidence?
    """

    perception: PerceptionEntry
    approved: bool
    priority_score: float  # 0-100, from Viveka scoring
    confidence: float  # 0.0-1.0, from synaptic learning
    dharma_ok: bool
    dharma_reason: str
    reason: str
    buddhi: object = field(default=None, repr=False)  # BuddhiResult


@runtime_checkable
class DharmaGateProtocol(Protocol):
    """Gate that checks whether a perception passes dharmic constraints."""

    def check(self, perception: PerceptionEntry) -> Tuple[bool, str]:
        """Check perception against dharma rules.

        Returns:
            (passed, reason) — True if allowed, reason explains why not.
        """
        ...


@runtime_checkable
class SynapticProtocol(Protocol):
    """Hebbian synaptic learning — strengthens what works, weakens what fails."""

    def get_weight(self, trigger: str, action: str) -> float:
        """Get current synaptic weight for a trigger→action pair.

        Returns:
            Weight between 0.0 and 1.0. Default 0.5 for unknown pairs.
        """
        ...

    def update(self, trigger: str, action: str, success: bool) -> float:
        """Update synaptic weight based on outcome.

        Success: w += 0.1 * (1 - w)  [asymptotic to 1.0]
        Failure: w -= 0.1 * w        [asymptotic to 0.0]

        Returns:
            New weight after update.
        """
        ...


@runtime_checkable
class ManasProtocol(Protocol):
    """The cognitive mind interface.

    Tattva #6 (SHARANAGATI) in the Sankhya system.
    Perceives, filters, prioritizes, decides, learns.
    """

    def perceive(self, entries: Sequence[PerceptionEntry]) -> Sequence[PerceptionEntry]:
        """Receive and filter perceptions through Chitta.

        Deduplicates, classifies, returns clean perception list.
        """
        ...

    def decide(
        self,
        perceptions: Sequence[PerceptionEntry],
        *,
        max_verdicts: int = 5,
    ) -> Sequence[ManaVerdict]:
        """Discriminate perceptions into verdicts via Buddhi.

        Each perception runs through:
        1. Buddhi.think() — cognitive frame
        2. Viveka — priority scoring from BuddhiResult
        3. DharmaGate — dharmic constraint check
        4. Synaptic — confidence from learned weights

        Returns:
            Sorted, filtered verdicts (highest priority first).
        """
        ...

    def learn(self, verdict: ManaVerdict, success: bool) -> None:
        """Hebbian learning — update synaptic weights from outcome."""
        ...

    def record_outcome(self, verdict: ManaVerdict, success: bool) -> None:
        """Record intent outcome — updates synaptic weights AND cooldown state.

        Success: clears cooldown for source.
        Failure: increments failure counter. After MAX_CONSECUTIVE_FAILURES,
        source enters cooldown (no new verdicts until cooldown expires).
        """
        ...

    def should_act(self) -> bool:
        """Should the agent produce content this heartbeat?

        Returns False (meditation mode) when:
        1. ALL known sources are in cooldown (every recent intent failed)
        2. Last decide() produced zero approved verdicts
        """
        ...

    def is_in_cooldown(self, source: str) -> bool:
        """Check if a source is in post-failure cooldown."""
        ...
