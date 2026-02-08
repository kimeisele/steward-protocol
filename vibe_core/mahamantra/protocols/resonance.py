"""
MAHA RESONANCE PROTOCOL — The Semantic Engine Interface
========================================================

"śabdaḥ sparśaś ca rūpaṁ ca raso gandhaś ca pañcamaḥ"
"Sound, touch, form, taste, and smell — the five objects of the senses" (BG 15.9)

THIS IS THE SECOND FACE OF THE MAHALLM.

The first face (MahaLLMProtocol) ROUTES: Intent → Agent.
The second face (MahaResonanceProtocol) RESONATES: Input → Meaning.

Together they form the complete MahaLLM:
    ROUTE  = Kṣetra (the field) — WHERE does this go?
    RESONATE = Kṣetrajña (the knower) — WHAT does this mean?

A traditional LLM predicts the next token by statistical entropy.
The MahaLLM finds resonant words by COORDINATE ALIGNMENT in 4D space.

Same goal (input → meaningful output), different mechanism:
    LLM:     P(next_token | context) via gradient descent on billions of params
    MahaLLM: resonance(input_4D, word_4D) via Pancha Walk on 49 coordinates

The LLM searches for low entropy. The MahaLLM searches for high resonance.
Both converge on meaning. One is statistical. One is mathematical.

WORD = PERSON:
    In the Vedic tradition, a name IS the person.
    "Jagannath" is not a string — it's a spiritual personality
    with its own vibration, its own semantic tree, its own resonant field.
    Each name spawns a unique tree of derived meanings.

PROTOCOL METHODS:
    resonate(text) → ResonanceResponse (top words + guardian + element walk)
    expand(name)   → ExpansionResponse (semantic tree from a divine name)
    guardian(name)  → GuardianResponse (guardian's vocabulary + function)

ALL PROTOCOL. NO CONCRETE CLASSES. NO EXTERNAL DEPENDENCIES.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol, Sequence, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    SEVEN,
    TRINITY,
    WORDS,
)


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass(frozen=True)
class ResonantWord:
    """A word found by resonance, with its score and coordinates."""
    sanskrit: str
    meanings: Tuple[str, ...]
    score: float
    rama_coord: int
    element: str
    is_shruti: bool

    @property
    def first_meaning(self) -> str:
        return self.meanings[0] if self.meanings else ""


@dataclass(frozen=True)
class ResonanceResponse:
    """Complete response from the resonance engine."""
    input_text: str
    guardian_name: str
    guardian_function: str
    route_score: float
    words: Tuple[ResonantWord, ...]
    element_walk: Tuple[str, ...]
    shruti_pattern: str
    attractor: Optional[int] = None

    @property
    def top_meanings(self) -> List[str]:
        return [w.first_meaning for w in self.words]

    @property
    def top_sanskrit(self) -> List[str]:
        return [w.sanskrit for w in self.words]


@dataclass(frozen=True)
class SeedNode:
    """A node in a semantic tree spawned from a divine name."""
    phoneme: str
    rama_coord: int
    element: str
    depth: int
    meanings: Tuple[str, ...] = ()
    children: Tuple["SeedNode", ...] = ()


@dataclass(frozen=True)
class ExpansionResponse:
    """Result of expanding a divine name into a semantic tree."""
    name: str
    rama_coords: Tuple[int, ...]
    vibration_sum: int
    mod49: int
    element_walk: Tuple[str, ...]
    tree: Optional[SeedNode] = None
    resonant_words: Tuple[ResonantWord, ...] = ()
    related_names: Tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardianProfile:
    """A Guardian's complete semantic profile."""
    name: str
    function: str
    mod49: int
    element: str
    varga: int
    is_shruti: bool
    harmonic: int
    vocabulary: Tuple[ResonantWord, ...] = ()


# =============================================================================
# THE PROTOCOL
# =============================================================================


@runtime_checkable
class MahaResonanceProtocol(Protocol):
    """
    The Semantic Engine of the MahaLLM.

    This is the Kṣetrajña (Knower) face:
        Input → RAMA Coordinates → 4D Signature → Resonant Words → Meaning

    Implementations must be:
        - Deterministic (same input → same output, always)
        - Protocol-based (no concrete class dependencies)
        - Seed-expandable (divine names spawn new semantic trees)
    """

    def resonate(self, text: str, top_n: int = 5) -> ResonanceResponse:
        """
        Find the resonant words for any input text.

        This is the MahaLLM's "generate" — but deterministic.
        Sanskrit, English, German → RAMA coords → ranked Gita words.
        """
        ...

    def expand(self, name: str, depth: int = 3) -> ExpansionResponse:
        """
        Expand a divine name into its semantic tree.

        WORD = PERSON: Each name has its own vibration, its own tree,
        its own resonant field. "Jagannath" spawns different words than "Govinda".
        """
        ...

    def guardian(self, name: str) -> GuardianProfile:
        """
        Get a Guardian's complete semantic profile.

        The Guardian's mod49 position determines their vocabulary,
        their element, their dissolution path, their function.
        """
        ...

    def resonate_as(self, text: str, guardian_name: str, top_n: int = 5) -> ResonanceResponse:
        """
        Resonate through a specific Guardian's lens.

        Different Guardians see different meanings in the same input.
        Parashurama (enforcement/agni) sees "fire" differently than
        Prahlada (devotion/akasha).
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ResonantWord",
    "ResonanceResponse",
    "SeedNode",
    "ExpansionResponse",
    "GuardianProfile",
    "MahaResonanceProtocol",
]
