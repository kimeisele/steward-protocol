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

from typing import Dict, Final, Optional

from vibe_core.mahamantra.protocols._seed import (
    SEVEN,
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

        Consumes lotus_core.__call__() — the ONE pipeline through 5 Tattva Gates.
        No shadow pipeline. No parallel encode/route/rank.

        Pipeline (all inside __call__):
            Gate 0: SRAVANAM → NAMA → KIRTANAM (encode → seed)
            Gate 1: PADA_SEVANAM → ARCANAM (attractor → parampara)
            Gate 2: SMARANAM → VANDANAM (rank_words → verse)
            Gate 3: DASYAM → SHABDA (position → guardian → phoneme)
            Gate 4: SAKHYAM → KIRTAN → YAJNA (cell → chamber → reactor)
        """
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

        lotus = get_mahamantra()
        lr = lotus(text)

        # Extract resonant words from __call__() response
        smaranam = lr.get("smaranam", ())
        words = tuple(
            ResonantWord(
                sanskrit=rw.get("sanskrit", ""),
                meanings=(rw.get("meaning", ""),),
                score=float(rw.get("score", 0.0)),
                rama_coord=0,
                element="unknown",
                is_shruti=False,
            )
            for rw in smaranam[:top_n]
        )

        # Shruti pattern from NAMA coords (already computed by Gate 0)
        nama = lr.get("nama", {})
        coords = nama.get("coords", ())
        shruti_pattern = "".join("S" if IS_SHRUTI[c] else "N" for c in coords) if coords else ""

        # Element walk from coords
        element_walk = tuple(ELEMENT_NAMES[COORD_ELEMENT[c]] for c in coords) if coords else ()

        # Guardian routing score — __call__() doesn't expose route_score,
        # but the guardian IS the routed result (position-based, deterministic)
        vib = lr.get("vibration", {})
        sig = vib.get("signature", {})

        return ResonanceResponse(
            input_text=text,
            guardian_name=str(lr.get("guardian", "")),
            guardian_function=str(lr.get("trinity_function", "")),
            route_score=1.0,  # __call__() is authoritative — no "score", it IS the route
            words=words,
            element_walk=element_walk,
            shruti_pattern=shruti_pattern,
        )

    # =========================================================================
    # EXPAND — Name → Semantic Tree (WORD = PERSON)
    # =========================================================================

    def expand(self, name: str, depth: int = 3) -> ExpansionResponse:
        """
        Expand a divine name into its semantic tree.

        Resonance via __call__() (5 Tattva Gates).
        Tree-building via H/K/R operations (unique to expand).

        "Jagannath" → __call__() for resonant words + tree for semantic field.
        """
        self._ensure_loaded()

        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.mahamantra.substrate.varnamala_codec import encode as encode_iast

        # Check if it's a known divine name with IAST form
        iast_form = DIVINE_NAMES.get(name.lower())

        # Run through __call__() for resonance (the ONE pipeline)
        lotus = get_mahamantra()
        lr = lotus(iast_form if iast_form else name)

        # Extract coords from NAMA (Gate 0 already computed them)
        nama = lr.get("nama", {})
        coords = nama.get("coords", ())

        # For IAST divine names, use the IAST encoding for tree/mod49
        if iast_form:
            iast_coords = encode_iast(iast_form)
            if iast_coords:
                coords = iast_coords

        if not coords:
            return ExpansionResponse(
                name=name,
                rama_coords=(),
                vibration_sum=0,
                mod49=0,
                element_walk=(),
            )

        vibration_sum = sum(coords)
        mod49 = vibration_sum % VARNAMALA_TOTAL
        element_walk = tuple(ELEMENT_NAMES[COORD_ELEMENT[c]] for c in coords)

        # Build semantic tree (unique to expand — H/K/R operations)
        root = self._build_tree(coords[0], depth=0, max_depth=depth)

        # Resonant words from __call__() response (no shadow rank_words)
        smaranam = lr.get("smaranam", ())
        resonant_words = tuple(
            ResonantWord(
                sanskrit=rw.get("sanskrit", ""),
                meanings=(rw.get("meaning", ""),),
                score=float(rw.get("score", 0.0)),
                rama_coord=0,
                element="unknown",
                is_shruti=False,
            )
            for rw in smaranam[:10]
        )

        # Find related names (names with same mod49)
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

        Consumes __call__(opcode=guardian_position) to force the pipeline
        through a specific Guardian. The 5 Tattva Gates still fire — the
        Guardian shapes the response via their position in the Mahamantra.

        Different Guardians genuinely see different meanings because
        position determines OpCode → Guna → Chamber behavior.
        """
        self._ensure_loaded()

        g = self._guardians.get(guardian_name.lower())
        if g is None:
            raise ValueError(f"Unknown guardian: {guardian_name}")

        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.mahamantra.substrate.guardian_router import GUARDIANS

        # Find the guardian's position index (0-15)
        guardian_position = next(
            (i for i, gd in enumerate(GUARDIANS) if gd.name == g.name),
            0,
        )

        lotus = get_mahamantra()
        lr = lotus(text, opcode=guardian_position)

        # Extract resonant words from __call__() response
        smaranam = lr.get("smaranam", ())
        words = tuple(
            ResonantWord(
                sanskrit=rw.get("sanskrit", ""),
                meanings=(rw.get("meaning", ""),),
                score=float(rw.get("score", 0.0)),
                rama_coord=0,
                element="unknown",
                is_shruti=False,
            )
            for rw in smaranam[:top_n]
        )

        # Shruti pattern + element walk from NAMA coords
        nama = lr.get("nama", {})
        coords = nama.get("coords", ())
        shruti_pattern = "".join("S" if IS_SHRUTI[c] else "N" for c in coords) if coords else ""
        element_walk = tuple(ELEMENT_NAMES[COORD_ELEMENT[c]] for c in coords) if coords else ()

        return ResonanceResponse(
            input_text=text,
            guardian_name=g.name,
            guardian_function=g.function,
            route_score=1.0,  # Explicitly chosen guardian
            words=words,
            element_walk=element_walk,
            shruti_pattern=shruti_pattern,
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
