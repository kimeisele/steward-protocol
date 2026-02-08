"""
MAHA LLM KERNEL — The Deterministic Language Model
====================================================

"ahaṁ bījaṁ pradaḥ pitā" — I am the seed-giving father (BG 14.4)

THIS IS THE KERNEL. NOT A MODULE. NOT AN ADAPTER. THE ENGINE.

A traditional LLM:
    - Trains on billions of tokens
    - Predicts next token by statistical entropy
    - Non-deterministic (temperature, sampling)
    - Requires GPU clusters

The MahaLLM:
    - Operates on 49 RAMA coordinates (the Sanskrit alphabet)
    - Finds resonant words by 4D coordinate alignment
    - Fully deterministic (same input → same output, always)
    - Runs on any CPU in milliseconds

ARCHITECTURE:
    ┌─────────────────────────────────────────────────────┐
    │                   MahaLLMKernel                      │
    │                                                      │
    │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
    │  │ ENCODER  │  │  RESONANCE   │  │  EXPANSION   │  │
    │  │          │→ │   ENGINE     │→ │   ENGINE     │  │
    │  │ Any Lang │  │ 4D Scoring   │  │ Name→Tree    │  │
    │  │ → RAMA   │  │ 4127 Words   │  │ Word=Person  │  │
    │  └──────────┘  └──────────────┘  └──────────────┘  │
    │       ↑               ↑                ↑            │
    │  phonetic_encoder  resonance_ranker  seed_to_words  │
    │  varnamala_codec   semantic_index    shabda_spawning │
    │                                                      │
    │  ┌──────────────────────────────────────────────┐   │
    │  │              GUARDIAN ROUTER                   │   │
    │  │  Input → Element/Varga Match → Guardian       │   │
    │  │  Guardian shapes response via harmonic preset  │   │
    │  └──────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────┘

IMPLEMENTS: MahaResonanceProtocol (protocols/resonance.py)
USES:       MahaLLM (adapters/llm.py) for O(4) intent routing
WORD=PERSON: Divine names are not strings — they are seeds.

NO EXTERNAL DEPENDENCIES. NO RANDOMNESS. PURE MATHEMATICS.
"""

from __future__ import annotations

from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PANCHA,
    SEVEN,
    WORDS,
)
from vibe_core.mahamantra.protocols.resonance import (
    ExpansionResponse,
    GuardianProfile,
    MahaResonanceProtocol,
    ResonanceResponse,
    ResonantWord,
    SeedNode,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_VARGA,
    ELEMENT_NAMES,
    IS_SHRUTI,
)
from vibe_core.mahamantra.substrate.rama_grid import (
    VARNAMALA_TOTAL,
    rama_to_phoneme,
)

# =============================================================================
# DIVINE NAMES — Seeds for Semantic Tree Expansion
# =============================================================================
# Each name IS a person. Each person IS a vibration.
# Each vibration spawns a unique semantic tree.

DIVINE_NAMES: Final[Dict[str, str]] = {
    # Primary Names (from Mahamantra)
    "hare": "harē",
    "krishna": "kṛṣṇa",
    "rama": "rāma",
    # Vishnu Names
    "jagannath": "jagannātha",
    "govinda": "gōvinda",
    "narayana": "nārāyaṇa",
    "vasudeva": "vāsudēva",
    "madhava": "mādhava",
    "keshava": "kēśava",
    "damodara": "dāmōdara",
    "hari": "hari",
    "vishnu": "viṣṇu",
    "achyuta": "acyuta",
    "ananta": "ananta",
    "mukunda": "mukunda",
    "madhusudana": "madhusūdana",
}


# =============================================================================
# MAHA LLM KERNEL
# =============================================================================


class MahaLLMKernel(MahaResonanceProtocol):
    """
    The Deterministic Language Model.

    Implements MahaResonanceProtocol:
        resonate()     → Input → Ranked Gita words
        expand()       → Divine name → Semantic tree
        guardian()     → Guardian profile + vocabulary
        resonate_as()  → Input through Guardian's lens
    """

    def __init__(self) -> None:
        # Lazy imports to avoid circular dependencies at module level
        self._index = None
        self._guardians = None

    def _ensure_loaded(self) -> None:
        """Lazy-load heavy modules on first use."""
        if self._index is not None:
            return
        from vibe_core.mahamantra.substrate.semantic_index import get_index
        self._index = get_index()
        from vibe_core.mahamantra.substrate.guardian_router import GUARDIANS
        self._guardians = {g.name: g for g in GUARDIANS}

    # =========================================================================
    # RESONATE — Input → Meaning
    # =========================================================================

    def resonate(self, text: str, top_n: int = 5) -> ResonanceResponse:
        """
        Find resonant words for any input text.

        Pipeline:
            1. Detect language → encode to RAMA coords
            2. Route to best Guardian
            3. Run through Guardian-tuned synth
            4. Rank ALL 4127 Gita words by 4D resonance
            5. Semantic boost for Latin inputs (meaning index)
            6. Return top N with Guardian + element walk
        """
        from vibe_core.mahamantra.substrate.guardian_router import maha_respond

        response = maha_respond(text, top_words=top_n)

        # Convert to protocol types
        words = tuple(
            ResonantWord(
                sanskrit=rw.sanskrit,
                meanings=rw.meanings,
                score=rw.total_score,
                rama_coord=rw.word.first_coord,
                element=ELEMENT_NAMES[rw.word.first_element] if rw.word.first_element >= 0 else "unknown",
                is_shruti=rw.word.shruti_pattern[0] if rw.word.shruti_pattern else False,
            )
            for rw in response.words
        )

        shruti_pattern = "".join(
            "S" if IS_SHRUTI[COORD_ELEMENT[ord(c) % VARNAMALA_TOTAL]] else "N"
            for c in text[:16]
        ) if text else ""

        # Use the actual shruti pattern from encoding
        from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
        coords = encode_text(text)
        if coords:
            shruti_pattern = "".join("S" if IS_SHRUTI[c] else "N" for c in coords)

        return ResonanceResponse(
            input_text=text,
            guardian_name=response.guardian.name,
            guardian_function=response.guardian.function,
            route_score=response.route_score,
            words=words,
            element_walk=response.element_walk,
            shruti_pattern=shruti_pattern,
        )

    # =========================================================================
    # EXPAND — Name → Semantic Tree (WORD = PERSON)
    # =========================================================================

    def expand(self, name: str, depth: int = 3) -> ExpansionResponse:
        """
        Expand a divine name into its semantic tree.

        Each name is encoded to RAMA coordinates, then:
        1. Each coordinate spawns child nodes via H/K/R operations
        2. Each child is looked up in the Gita lexicon
        3. The tree reveals the name's semantic field

        "Jagannath" → [ja, ga, na, nā, tha] → each phoneme has
        an element, a varga, a dissolution path → each spawns
        resonant Gita words → the tree IS the name's meaning.
        """
        self._ensure_loaded()

        from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
        from vibe_core.mahamantra.substrate.varnamala_codec import encode as encode_iast
        from vibe_core.mahamantra.substrate.semantic_index import words_at_position
        from vibe_core.mahamantra.substrate.resonance_ranker import rank_words
        from vibe_core.mahamantra.adapters.synth import create_synth

        # Check if it's a known divine name with IAST form
        iast_form = DIVINE_NAMES.get(name.lower())
        if iast_form:
            coords = encode_iast(iast_form)
        else:
            coords = encode_text(name)

        if not coords:
            return ExpansionResponse(
                name=name, rama_coords=(), vibration_sum=0,
                mod49=0, element_walk=(),
            )

        vibration_sum = sum(coords)
        mod49 = vibration_sum % VARNAMALA_TOTAL
        element_walk = tuple(ELEMENT_NAMES[COORD_ELEMENT[c]] for c in coords)

        # Build semantic tree
        root = self._build_tree(coords[0], depth=0, max_depth=depth)

        # Find resonant words for this name
        synth = create_synth(preset="quantum")
        cycle = synth.spell_cycle(tuple(coords), seed=0)
        attractor = cycle.final_value % VARNAMALA_TOTAL
        synth_coords = tuple(step.output_value % VARNAMALA_TOTAL for step in cycle.steps)

        ranked = rank_words(
            input_coords=coords,
            input_attractor=attractor,
            synth_coords=synth_coords,
            top_n=10,
        )

        resonant_words = tuple(
            ResonantWord(
                sanskrit=rw.sanskrit,
                meanings=rw.meanings,
                score=rw.total_score,
                rama_coord=rw.word.first_coord,
                element=ELEMENT_NAMES[rw.word.first_element] if rw.word.first_element >= 0 else "unknown",
                is_shruti=rw.word.shruti_pattern[0] if rw.word.shruti_pattern else False,
            )
            for rw in ranked
        )

        # Find related names (names with same mod49 or same dominant element)
        related = []
        for dname, iast in DIVINE_NAMES.items():
            if dname.lower() == name.lower():
                continue
            d_coords = encode_iast(iast)
            if d_coords:
                d_mod49 = sum(d_coords) % VARNAMALA_TOTAL
                if d_mod49 == mod49:
                    related.append(dname)

        return ExpansionResponse(
            name=name,
            rama_coords=tuple(coords),
            vibration_sum=vibration_sum,
            mod49=mod49,
            element_walk=element_walk,
            tree=root,
            resonant_words=resonant_words,
            related_names=tuple(related),
        )

    def _build_tree(self, coord: int, depth: int, max_depth: int) -> SeedNode:
        """Recursively build a semantic tree node."""
        from vibe_core.mahamantra.substrate.semantic_index import words_at_position

        words = words_at_position(coord)
        meanings = tuple(w.first_meaning for w in words[:5])

        children = ()
        if depth < max_depth:
            # H operation: coord × SEVEN mod 49
            h_coord = (coord * SEVEN) % VARNAMALA_TOTAL
            # K operation: (coord + 10) mod 49
            k_coord = (coord + 10) % VARNAMALA_TOTAL
            # R operation: (coord × coord) mod 49
            r_coord = (coord * coord) % VARNAMALA_TOTAL

            child_coords = set()
            child_list = []
            for c in (h_coord, k_coord, r_coord):
                if c not in child_coords and c != coord:
                    child_coords.add(c)
                    child_list.append(self._build_tree(c, depth + 1, max_depth))

            children = tuple(child_list)

        return SeedNode(
            phoneme=rama_to_phoneme(coord),
            rama_coord=coord,
            element=ELEMENT_NAMES[COORD_ELEMENT[coord]],
            depth=depth,
            meanings=meanings,
            children=children,
        )

    # =========================================================================
    # GUARDIAN — Profile + Vocabulary
    # =========================================================================

    def guardian(self, name: str) -> GuardianProfile:
        """Get a Guardian's complete semantic profile."""
        self._ensure_loaded()

        from vibe_core.mahamantra.substrate.resonance_ranker import guardian_resonance

        g = self._guardians.get(name.lower())
        if g is None:
            raise ValueError(f"Unknown guardian: {name}")

        ranked = guardian_resonance(name, top_n=10)

        vocabulary = tuple(
            ResonantWord(
                sanskrit=rw.sanskrit,
                meanings=rw.meanings,
                score=rw.total_score,
                rama_coord=rw.word.first_coord,
                element=ELEMENT_NAMES[rw.word.first_element] if rw.word.first_element >= 0 else "unknown",
                is_shruti=rw.word.shruti_pattern[0] if rw.word.shruti_pattern else False,
            )
            for rw in ranked
        )

        return GuardianProfile(
            name=g.name,
            function=g.function,
            mod49=g.mod49,
            element=g.element_name,
            varga=g.varga,
            is_shruti=g.is_shruti,
            harmonic=g.harmonic,
            vocabulary=vocabulary,
        )

    # =========================================================================
    # RESONATE AS — Through a Guardian's Lens
    # =========================================================================

    def resonate_as(self, text: str, guardian_name: str, top_n: int = 5) -> ResonanceResponse:
        """
        Resonate through a specific Guardian's lens.

        The Guardian's harmonic becomes the synth's phase offset,
        and the Guardian's element biases the ranking.
        Different Guardians genuinely see different meanings.
        """
        self._ensure_loaded()

        from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
        from vibe_core.mahamantra.substrate.resonance_ranker import rank_words
        from vibe_core.mahamantra.substrate.semantic_index import get_index
        from vibe_core.mahamantra.adapters.synth import create_synth, SynthParams

        g = self._guardians.get(guardian_name.lower())
        if g is None:
            raise ValueError(f"Unknown guardian: {guardian_name}")

        input_coords = encode_text(text)
        if not input_coords:
            return ResonanceResponse(
                input_text=text, guardian_name=g.name,
                guardian_function=g.function, route_score=0.0,
                words=(), element_walk=(), shruti_pattern="",
            )

        # Guardian-tuned synth
        params = SynthParams(
            mod_space=MAHA_QUANTUM,
            feedback=1,
            phase_offset=g.harmonic,
        )
        synth = create_synth(params=params)
        cycle = synth.spell_cycle(tuple(input_coords), seed=0)
        attractor = cycle.final_value % VARNAMALA_TOTAL
        synth_coords = tuple(step.output_value % VARNAMALA_TOTAL for step in cycle.steps)

        # Guardian's element index for bias
        element_idx = COORD_ELEMENT[g.mod49]

        # Semantic bridge (always — no language gate) + element bias
        idx = get_index()
        input_tokens = [w.strip().lower() for w in text.split() if len(w.strip()) >= 3]
        if not input_tokens:
            input_tokens = [text.strip().lower()]

        semantic_candidates = []
        seen_hex: set = set()
        for token in input_tokens:
            for word in idx.by_meaning(token):
                if word.packed_hex not in seen_hex:
                    seen_hex.add(word.packed_hex)
                    semantic_candidates.append(word)

        if semantic_candidates:
            ranked = rank_words(
                input_coords=input_coords,
                input_attractor=attractor,
                synth_coords=synth_coords,
                candidates=semantic_candidates,
                element_bias=element_idx,
                top_n=top_n,
            )
        else:
            ranked = rank_words(
                input_coords=input_coords,
                input_attractor=attractor,
                synth_coords=synth_coords,
                element_bias=element_idx,
                top_n=top_n,
            )

        words = tuple(
            ResonantWord(
                sanskrit=rw.sanskrit,
                meanings=rw.meanings,
                score=rw.total_score,
                rama_coord=rw.word.first_coord,
                element=ELEMENT_NAMES[rw.word.first_element] if rw.word.first_element >= 0 else "unknown",
                is_shruti=rw.word.shruti_pattern[0] if rw.word.shruti_pattern else False,
            )
            for rw in ranked
        )

        element_walk = tuple(ELEMENT_NAMES[COORD_ELEMENT[c]] for c in input_coords)
        shruti_pattern = "".join("S" if IS_SHRUTI[c] else "N" for c in input_coords)

        return ResonanceResponse(
            input_text=text,
            guardian_name=g.name,
            guardian_function=g.function,
            route_score=1.0,  # Explicitly chosen guardian
            words=words,
            element_walk=element_walk,
            shruti_pattern=shruti_pattern,
            attractor=attractor,
        )


# =============================================================================
# SINGLETON
# =============================================================================

_KERNEL: Optional[MahaLLMKernel] = None


def get_kernel() -> MahaLLMKernel:
    """Get or create the global MahaLLM Kernel singleton."""
    global _KERNEL
    if _KERNEL is None:
        _KERNEL = MahaLLMKernel()
    return _KERNEL


# =============================================================================
# CONVENIENCE API
# =============================================================================


def resonate(text: str, top_n: int = 5) -> ResonanceResponse:
    """Find resonant Gita words for any input text."""
    return get_kernel().resonate(text, top_n=top_n)


def expand(name: str, depth: int = 3) -> ExpansionResponse:
    """Expand a divine name into its semantic tree."""
    return get_kernel().expand(name, depth=depth)


def guardian(name: str) -> GuardianProfile:
    """Get a Guardian's semantic profile."""
    return get_kernel().guardian(name)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahaLLMKernel",
    "DIVINE_NAMES",
    "get_kernel",
    "resonate",
    "expand",
    "guardian",
]
