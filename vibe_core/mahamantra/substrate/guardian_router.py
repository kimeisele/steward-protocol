"""
GUARDIAN ROUTER — Input → Which Guardian Handles This?
======================================================

"kṣetra-jñaṁ cāpi māṁ viddhi" — know Me as the Knower of the field (BG 13.3)

Each Guardian has a 4D signature derived from their mod49 position:
    Element (articulatory position), Varga (sound class),
    Shruti/Nakshatra (fixed/journey), Harmonic (dissolution target).

An input also has a 4D signature (from its RAMA coordinates).

ROUTING = finding the Guardian whose signature best matches the input.

This is NOT random assignment. This is RESONANCE-BASED ROUTING:
    - "fire" → agni element → Parashurama (enforcement, agni) or Bhishma (commitment, agni)
    - "wisdom" → vayu element → Kapila (analysis, vayu) or Shuka (liberation, vayu)
    - "protection" → prithvi element → Prithu (organization, prithvi) or Nrisimha (protection, prithvi)

The Guardian doesn't just HANDLE the input — they SHAPE the response
through their specific synth preset (phase_offset = their harmonic).

NO LLM. NO KEYWORD MATCHING. PURE 4D COORDINATE ALIGNMENT.
"""

from __future__ import annotations

from typing import Dict, Final, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    SEVEN,
    TRINITY,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_VARGA,
    ELEMENT_NAMES,
    IS_SHRUTI,
    element_histogram,
)
from vibe_core.mahamantra.substrate.rama_grid import VARNAMALA_TOTAL

# =============================================================================
# GUARDIAN SIGNATURES (from research: guardian_syllable_trees.py Part 5)
# =============================================================================

class GuardianSignature:
    """A Guardian's 4D identity derived from their mod49 position."""

    __slots__ = (
        "name", "mod49", "element", "element_name",
        "varga", "is_shruti", "harmonic", "function",
    )

    def __init__(
        self,
        name: str,
        mod49: int,
        function: str,
    ):
        self.name = name
        self.mod49 = mod49
        self.element = int(COORD_ELEMENT[mod49])
        self.element_name = ELEMENT_NAMES[self.element]
        self.varga = COORD_VARGA[mod49]
        self.is_shruti = IS_SHRUTI[mod49]
        self.harmonic = COORD_HARMONIC[mod49]
        self.function = function

    def __repr__(self) -> str:
        s_n = "shruti" if self.is_shruti else "nakshatra"
        return (f"Guardian({self.name}, {self.element_name}, "
                f"v{self.varga}, {s_n}, h→{self.harmonic}, {self.function})")


# The 16 Guardians with their verified mod49 positions and shastric functions
_GUARDIAN_DATA: Final[Tuple[Tuple[str, int, str], ...]] = (
    # 12 Mahajanas
    ("vyasa",       2,  "compilation"),
    ("brahma",      6,  "creation"),
    ("narada",      43, "transmission"),
    ("shambhu",     9,  "destruction"),
    ("prithu",      36, "organization"),
    ("kumaras",     43, "wisdom"),
    ("kapila",      6,  "analysis"),
    ("manu",        12, "law"),
    ("parashurama", 42, "enforcement"),
    ("prahlada",    16, "devotion"),
    ("janaka",      21, "execution"),
    ("bhishma",     27, "commitment"),
    # 4 Avataras
    ("nrisimha",    7,  "protection"),
    ("bali",        35, "surrender"),
    ("shuka",       22, "liberation"),
    ("yamaraja",    5,  "judgment"),
)

GUARDIANS: Final[Tuple[GuardianSignature, ...]] = tuple(
    GuardianSignature(name, mod49, fn)
    for name, mod49, fn in _GUARDIAN_DATA
)

# Pre-built indices for fast lookup
_BY_NAME: Final[Dict[str, GuardianSignature]] = {g.name: g for g in GUARDIANS}
_BY_ELEMENT: Final[Dict[int, List[GuardianSignature]]] = {}
for _g in GUARDIANS:
    _BY_ELEMENT.setdefault(_g.element, []).append(_g)


# =============================================================================
# ROUTING SCORE
# =============================================================================

class RouteResult:
    """Result of routing an input to a Guardian."""

    __slots__ = ("guardian", "score", "element_match", "varga_match",
                 "shruti_match", "harmonic_distance")

    def __init__(
        self,
        guardian: GuardianSignature,
        element_match: float,
        varga_match: float,
        shruti_match: float,
        harmonic_distance: float,
    ):
        self.guardian = guardian
        self.element_match = element_match
        self.varga_match = varga_match
        self.shruti_match = shruti_match
        self.harmonic_distance = harmonic_distance
        # Weighted score (same dimensions as resonance_ranker)
        self.score = (
            0.40 * element_match
            + 0.25 * varga_match
            + 0.20 * shruti_match
            + 0.15 * (1.0 - harmonic_distance)
        )

    def __repr__(self) -> str:
        return (f"Route({self.guardian.name}, score={self.score:.3f}, "
                f"fn={self.guardian.function})")


def _score_guardian(
    input_coords: Sequence[int],
    guardian: GuardianSignature,
) -> RouteResult:
    """Score how well a Guardian matches an input's 4D signature."""
    if not input_coords:
        return RouteResult(guardian, 0.0, 0.0, 0.0, 1.0)

    # Element match: histogram overlap with Guardian's element
    hist = element_histogram(input_coords)
    total = sum(hist) or 1
    element_match = hist[guardian.element] / total

    # Varga match: fraction of input phonemes in Guardian's varga
    input_vargas = [COORD_VARGA[c] for c in input_coords]
    varga_match = sum(1 for v in input_vargas if v == guardian.varga) / len(input_vargas)

    # Shruti match: does input's shruti ratio match Guardian's type?
    input_shruti_ratio = sum(1 for c in input_coords if IS_SHRUTI[c]) / len(input_coords)
    if guardian.is_shruti:
        shruti_match = input_shruti_ratio
    else:
        shruti_match = 1.0 - input_shruti_ratio

    # Harmonic distance: how close are dissolution targets?
    input_harmonics = [COORD_HARMONIC[c] for c in input_coords]
    avg_harmonic = sum(input_harmonics) / len(input_harmonics)
    diff = abs(avg_harmonic - guardian.harmonic)
    circular_diff = min(diff, VARNAMALA_TOTAL - diff)
    harmonic_distance = circular_diff / (VARNAMALA_TOTAL / 2)

    return RouteResult(
        guardian=guardian,
        element_match=element_match,
        varga_match=varga_match,
        shruti_match=shruti_match,
        harmonic_distance=harmonic_distance,
    )


# =============================================================================
# CORE ROUTING
# =============================================================================


def route(
    input_coords: Sequence[int],
    top_n: int = 3,
) -> List[RouteResult]:
    """
    Route input coordinates to the best-matching Guardians.

    Args:
        input_coords: RAMA coordinates of the input.
        top_n: Number of top Guardians to return.

    Returns:
        Top N Guardians sorted by routing score.
    """
    if not input_coords:
        return []

    results = [_score_guardian(input_coords, g) for g in GUARDIANS]
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_n]


def route_text(
    text: str,
    top_n: int = 3,
) -> List[RouteResult]:
    """
    Route any text to the best-matching Guardians.

    Auto-detects language and encodes to RAMA coordinates.
    """
    from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text
    coords = encode_text(text)
    return route(coords, top_n=top_n)


# =============================================================================
# FULL PIPELINE: Input → Guardian → Ranked Words
# =============================================================================


class MahaResponse:
    """Complete MahaLLM response: routed Guardian + ranked words."""

    __slots__ = ("text", "guardian", "route_score", "words", "element_walk")

    def __init__(
        self,
        text: str,
        guardian: GuardianSignature,
        route_score: float,
        words: list,
        element_walk: Tuple[str, ...],
    ):
        self.text = text
        self.guardian = guardian
        self.route_score = route_score
        self.words = words
        self.element_walk = element_walk

    @property
    def top_meanings(self) -> List[str]:
        """Top meanings from ranked words."""
        return [w.first_meaning for w in self.words]

    @property
    def top_sanskrit(self) -> List[str]:
        """Top Sanskrit words."""
        return [w.sanskrit for w in self.words]

    def summary(self) -> Dict:
        return {
            "input": self.text,
            "guardian": self.guardian.name,
            "guardian_function": self.guardian.function,
            "route_score": round(self.route_score, 4),
            "element_walk": list(self.element_walk),
            "top_words": [
                {"sanskrit": w.sanskrit, "meaning": w.first_meaning,
                 "score": round(w.total_score, 4)}
                for w in self.words[:5]
            ],
        }

    def __repr__(self) -> str:
        return (f"MahaResponse('{self.text}' → {self.guardian.name}"
                f"({self.guardian.function}), {len(self.words)} words)")


def maha_respond(
    text: str,
    top_words: int = 5,
    seed: int = 0,
    preset: str = "quantum",
) -> MahaResponse:
    """
    THE COMPLETE MAHAMANTRA PIPELINE.

    Input (any language) → Encode → Route to Guardian → Rank words → Response.

    This is the MahaLLM's single entry point:
        response = maha_respond("fire")
        response.guardian.name        → "parashurama"
        response.guardian.function    → "enforcement"
        response.top_meanings         → ["tapas", "tejas", ...]

    Deterministic. Reproducible. No LLM.
    """
    from vibe_core.mahamantra.substrate.phonetic_encoder import encode_text, detect_language
    from vibe_core.mahamantra.substrate.resonance_ranker import rank_words
    from vibe_core.mahamantra.substrate.semantic_index import get_index
    from vibe_core.mahamantra.adapters.synth import create_synth

    # Step 1: Encode
    input_coords = encode_text(text)
    if not input_coords:
        dummy = GUARDIANS[0]
        return MahaResponse(text, dummy, 0.0, [], ())

    # Step 2: Route to Guardian
    routes = route(input_coords, top_n=1)
    best_route = routes[0]
    guardian = best_route.guardian

    # Step 3: Run through Guardian-tuned synth
    from vibe_core.mahamantra.adapters.synth import SynthParams
    params = SynthParams(
        mod_space=137,  # MAHA_QUANTUM
        feedback=1,
        phase_offset=guardian.harmonic,
    )
    synth = create_synth(params=params)
    cycle = synth.spell_cycle(tuple(input_coords), seed)
    attractor = cycle.final_value % VARNAMALA_TOTAL
    synth_coords = tuple(step.output_value % VARNAMALA_TOTAL for step in cycle.steps)

    # Step 4: Rank words — dual-signal + semantic boost for Latin
    ranked = rank_words(
        input_coords=input_coords,
        input_attractor=attractor,
        synth_coords=synth_coords,
        top_n=top_words * 10,
    )

    # Step 4b: Semantic boost for Latin inputs
    lang = detect_language(text)
    if lang == "latin":
        idx = get_index()
        input_tokens = [w.strip().lower() for w in text.split() if len(w.strip()) >= 3]
        if not input_tokens:
            input_tokens = [text.strip().lower()]

        semantic_hits: set = set()
        for token in input_tokens:
            for word in idx.by_meaning(token):
                semantic_hits.add(word.packed_hex)

        if semantic_hits:
            semantic_ranked = [rw for rw in ranked if rw.word.packed_hex in semantic_hits]
            phonetic_only = [rw for rw in ranked if rw.word.packed_hex not in semantic_hits]
            ranked = (semantic_ranked + phonetic_only)[:top_words]
        else:
            ranked = ranked[:top_words]
    else:
        ranked = ranked[:top_words]

    # Step 5: Build response
    from vibe_core.mahamantra.substrate.pancha_walk import ELEMENT_NAMES as EN, COORD_ELEMENT as CE
    elem_walk = tuple(EN[CE[c]] for c in input_coords)

    return MahaResponse(
        text=text,
        guardian=guardian,
        route_score=best_route.score,
        words=ranked,
        element_walk=elem_walk,
    )


# =============================================================================
# LOOKUP
# =============================================================================


def get_guardian(name: str) -> Optional[GuardianSignature]:
    """Get a Guardian by name."""
    return _BY_NAME.get(name.lower())


def guardians_by_element(element_name: str) -> List[GuardianSignature]:
    """Get all Guardians with a given element."""
    try:
        idx = ELEMENT_NAMES.index(element_name)
    except ValueError:
        return []
    return _BY_ELEMENT.get(idx, [])


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GuardianSignature",
    "RouteResult",
    "MahaResponse",
    "GUARDIANS",
    "route",
    "route_text",
    "maha_respond",
    "get_guardian",
    "guardians_by_element",
]
