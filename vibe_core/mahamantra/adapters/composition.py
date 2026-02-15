"""
MAHA COMPOSITION — Protocol-Based Language Adapter
===================================================

"vāṇī tasya kā" — What is the speech of that One?

LOCATION: vibe_core.mahamantra.adapters.composition (THE BRIDGE)
PROTOCOL: vibe_core.mahamantra.protocols._composition (THE LAW)
SUBSTRATE: vibe_core.mahamantra.substrate.language/ (Pure Math)

This adapter implements CompositionProtocol by wiring together
the substrate scoring atoms into a ranked composition pipeline.

ARCHITECTURE:
    1. Pool extraction (substrate: _build_lotus_pool)
    2. Multi-scorer ranking (each scorer is CompositionScorerProtocol)
    3. Context-driven selection (quarter/prana determine word count)
    4. Grid alignment (substrate: align_syllables_to_grid)
    5. Assembly (grid order → English)

SCORERS (pluggable, protocol-based):
    PranaScorer   — Antaranga standing wave prana at word's RAMA coords
    RhythmScorer  — Syllable vector ↔ grid step alignment
    SemanticScorer — WordNet graph distance to input
    ModeScorer    — Word's WordNet mode ↔ guna's preferred mode
    StateScorer   — System state affinity (MahaState numeric vector)

Each scorer implements CompositionScorerProtocol.
The adapter combines them additively. No keywords. No if/else routing.
"""

from __future__ import annotations

__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2c80316d"

import logging
from typing import Dict, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    PANCHA,
    PARAMPARA,
    QUARTERS,
    SEVEN,
    WORDS,
)

assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

logger = logging.getLogger("MAHA_COMPOSITION")


# =============================================================================
# SCORERS — Each implements CompositionScorerProtocol
# =============================================================================


class PranaScorer:
    """Score words by post-modulation Antaranga prana at their RAMA coords."""

    name = "prana"

    def score(self, item: Dict, seed: int, **kwargs) -> float:
        antaranga = kwargs.get("antaranga")
        coords = item.get("coords", ())
        if not coords or antaranga is None:
            return 0.0
        total_prana = 0
        for coord in coords:
            slot = (coord * SEVEN + seed) % 512
            total_prana += antaranga.prana_at(slot)
        if total_prana == 0:
            return 0.0
        try:
            from vibe_core.mahamantra.substrate.antaranga import GENESIS_PRANA_U32
        except Exception:
            return 0.0
        return min(total_prana / max(GENESIS_PRANA_U32, KSETRAJNA), KSETRAJNA)


class RhythmScorer:
    """Score words by prosodic affinity (syllable vector ↔ RAMA coords)."""

    name = "rhythm"

    def score(self, item: Dict, seed: int, **kwargs) -> float:
        from vibe_core.mahamantra.substrate.language.composer import prosodic_affinity
        from vibe_core.mahamantra.substrate.language.phonetics import syllable_vectors_for_word

        meaning = str(item.get("meaning", ""))
        coords = item.get("coords", ())
        if not meaning or not coords:
            return 0.0
        # Use first content word for syllable analysis
        parts = meaning.split()
        english = max(parts, key=len) if parts else ""
        if not english:
            return 0.0
        svs = syllable_vectors_for_word(english)
        if not svs:
            return 0.0
        # Average prosodic affinity across syllables
        total = sum(prosodic_affinity(sv, coords) for sv in svs)
        return total / len(svs)


class SemanticScorer:
    """Score words by WordNet graph distance to input text."""

    name = "semantic"

    def score(self, item: Dict, seed: int, **kwargs) -> float:
        from vibe_core.mahamantra.substrate.language.composer import semantic_boost

        input_text = kwargs.get("input_text", "")
        phex = str(item.get("packed_hex", ""))
        return semantic_boost(input_text, phex)


class ModeScorer:
    """Score words by guna ↔ WordNet mode alignment. No keywords."""

    name = "mode"

    # Guna → preferred mode (BG 14.5, derived from protocol)
    _GUNA_MODE = {"TAMAS": "GENESIS", "RAJAS": "KARMA", "SATTVA": "DHARMA"}

    def score(self, item: Dict, seed: int, **kwargs) -> float:
        from vibe_core.mahamantra.substrate.language.mode_affinity import (
            classify_by_graph,
            mode_anchor_phrases,
        )

        guna_mode = kwargs.get("guna_mode", "RAJAS")
        preferred = self._GUNA_MODE.get(guna_mode, "KARMA")
        phex = str(item.get("packed_hex", ""))
        if not phex:
            return 0.0
        word_mode = classify_by_graph(phex, mode_anchor_phrases())
        if word_mode == preferred:
            return PANCHA / (WORDS * HALVES)  # ~0.15625, same scale as chamber_boost
        return 0.0


class StateScorer:
    """Score words by system state affinity (numeric, no keywords)."""

    name = "state"

    def score(self, item: Dict, seed: int, **kwargs) -> float:
        from vibe_core.mahamantra.substrate.language.composer import state_affinity
        from vibe_core.mahamantra.substrate.language.mode_affinity import (
            classify_by_graph,
            mode_anchor_phrases,
        )

        state = kwargs.get("state")
        if state is None:
            return 0.0
        phex = str(item.get("packed_hex", ""))
        mode = classify_by_graph(phex, mode_anchor_phrases()) if phex else None
        return state_affinity(state, item, mode)


# Default scorer pipeline — order doesn't matter, scores are additive
DEFAULT_SCORERS: Tuple[object, ...] = (
    PranaScorer(),
    RhythmScorer(),
    SemanticScorer(),
    ModeScorer(),
    StateScorer(),
)


# =============================================================================
# CONTEXT EXTRACTION — reads lotus_response dict, zero coupling
# =============================================================================


def _extract_scorer_kwargs(lotus_response: Dict, input_text: str) -> Dict:
    """Extract kwargs for scorers from lotus_response. Zero imports from Lotus."""
    vib = lotus_response.get("vibration", {})
    guna_info = lotus_response.get("guna", {})

    # Read Antaranga from Chamber singleton (post-Lotus computation)
    antaranga = None
    try:
        from vibe_core.mahamantra.substrate.chamber import get_chamber
        antaranga = get_chamber().antaranga
    except Exception:
        pass

    # Extract StateVector (graceful degradation)
    state = None
    try:
        from vibe_core.mahamantra.substrate.language.state_bridge import extract_state_vector
        ant_info = lotus_response.get("antaranga", {})
        state = extract_state_vector(prana_level=ant_info.get("total_prana", 0))
    except Exception:
        pass

    return {
        "seed": vib.get("seed", 0),
        "input_text": input_text,
        "antaranga": antaranga,
        "guna_mode": str(guna_info.get("mode", "RAJAS")),
        "state": state,
    }


def _context_max_words(lotus_response: Dict) -> int:
    """Determine max output words from context. NOT hardcoded SEVEN.

    Quarter phase and Antaranga prana drive output length:
        GENESIS (exploring)     → PANCHA (5) — concise, seeking
        DHARMA (declaring)      → SEVEN (7) — full expression
        KARMA (acting)          → PANCHA (5) — imperative, direct
        MOKSHA (transcending)   → QUARTERS (4) — distilled, essential

    High prana amplifies by +HALVES (2).
    """
    quarter = str(lotus_response.get("quarter", "karma")).lower()
    base = {
        "genesis": PANCHA,
        "dharma": SEVEN,
        "karma": PANCHA,
        "moksha": QUARTERS,
    }.get(quarter, PANCHA)

    ant = lotus_response.get("antaranga", {})
    total_prana = ant.get("total_prana", 0)
    if total_prana > 0:
        base += HALVES

    return base


# =============================================================================
# MAHA COMPOSITION ADAPTER
# =============================================================================


class MahaComposition:
    """Protocol-based composition adapter.

    Wires substrate scoring atoms into a ranked pipeline.
    Each scorer is a CompositionScorerProtocol implementation.
    Scorers are pluggable — add/remove without touching this class.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "maha_composition_vani"

    def __init__(self, scorers: Optional[Sequence] = None) -> None:
        self._scorers = tuple(scorers) if scorers is not None else DEFAULT_SCORERS
        self._compositions = 0
        self._last_context: Dict = {}

    @property
    def compositions(self) -> int:
        return self._compositions

    @property
    def last_context(self) -> Dict:
        return dict(self._last_context)

    # =========================================================================
    # CORE: compose (CompositionProtocol)
    # =========================================================================

    def compose(self, lotus_response: Dict, input_text: str) -> str:
        """Compose English output from a Lotus response.

        Pipeline:
            1. Pool extraction (substrate)
            2. Multi-scorer ranking (protocol-based scorers)
            3. Context-driven selection (quarter/prana → max_words)
            4. Grid alignment (substrate)
            5. Assembly (grid order → English)
        """
        from vibe_core.mahamantra.substrate.language.composer import (
            _build_lotus_pool,
            word_tokens,
        )
        from vibe_core.mahamantra.substrate.language.phonetics import (
            syllable_vectors_for_word,
        )
        from vibe_core.mahamantra.substrate.language.mantra_grid import (
            align_syllables_to_grid,
        )
        from vibe_core.mahamantra.substrate.language.types import SyllableVector

        # === 1. EXTRACT CONTEXT ===
        kwargs = _extract_scorer_kwargs(lotus_response, input_text)
        seed = kwargs["seed"]
        max_words = _context_max_words(lotus_response)

        self._last_context = {
            "guna_mode": kwargs.get("guna_mode"),
            "quarter": str(lotus_response.get("quarter", "")),
            "guardian": str(lotus_response.get("guardian", "")),
            "max_words": max_words,
            "scorer_names": tuple(s.name for s in self._scorers),
        }

        # === 2. POOL EXTRACTION (substrate) ===
        pool = _build_lotus_pool(lotus_response)
        if not pool:
            return ""

        # === 3. MULTI-SCORER RANKING ===
        ranked: List[Dict] = []
        for item in pool:
            scored = dict(item)
            total_boost = 0.0
            for scorer in self._scorers:
                try:
                    boost = scorer.score(scored, seed, **kwargs)
                    scored[f"_{scorer.name}_score"] = boost
                    total_boost += boost
                except Exception as exc:
                    logger.warning("Scorer %s failed: %s", scorer.name, exc)
                    scored[f"_{scorer.name}_score"] = 0.0
            base_score = float(scored.get("score", 0.0))
            scored["_total_score"] = base_score + total_boost
            ranked.append(scored)

        ranked.sort(key=lambda it: float(it.get("_total_score", 0.0)), reverse=True)

        # === 4. SELECT (context-driven count, deduplicate) ===
        selected: List[Dict] = []
        used_sanskrit: set = set()
        for item in ranked:
            if len(selected) >= max_words:
                break
            sk = item.get("sanskrit", "")
            if sk in used_sanskrit:
                continue
            selected.append(item)
            used_sanskrit.add(sk)

        if not selected:
            return ""

        # === 5. SYLLABLE VECTORS + GRID ALIGNMENT (substrate) ===
        word_syllables: List[Tuple[Dict, Tuple[SyllableVector, ...]]] = []
        for item in selected:
            tokens = item.get("tokens", ())
            meaning = str(item.get("meaning", ""))
            english = ""
            if tokens:
                english = max(tokens, key=len)
            elif meaning:
                parts = meaning.split()
                english = max(parts, key=len) if parts else ""
            if english:
                svs = syllable_vectors_for_word(english)
                if svs:
                    word_syllables.append((item, svs))

        if not word_syllables:
            # Fallback: meanings joined
            return " ".join(
                str(it.get("meaning", "")).split()[0]
                for it in selected[:max_words]
                if it.get("meaning")
            )

        # Collect all syllable vectors
        all_vectors: List[SyllableVector] = []
        vector_to_word: List[int] = []
        for wi, (_, svs) in enumerate(word_syllables):
            for sv in svs:
                all_vectors.append(sv)
                vector_to_word.append(wi)

        if not all_vectors:
            return " ".join(
                str(it.get("meaning", "")).split()[0]
                for it in selected[:max_words]
                if it.get("meaning")
            )

        grid_positions = align_syllables_to_grid(tuple(all_vectors))

        # === 6. ASSEMBLE: grid position → sentence order ===
        word_earliest: Dict[int, int] = {}
        for si, gp in enumerate(grid_positions):
            wi = vector_to_word[si]
            if wi not in word_earliest or gp < word_earliest[wi]:
                word_earliest[wi] = gp

        word_grid_pos = sorted(
            ((word_earliest.get(wi, wi * HALVES), wi) for wi in range(len(word_syllables))),
        )

        output_parts: List[str] = []
        used_words: set = set()
        total_words = 0

        for _, wi in word_grid_pos:
            if total_words >= max_words:
                break
            item = word_syllables[wi][0]
            meaning = str(item.get("meaning", "")).strip()
            if not meaning:
                continue

            tokens = item.get("tokens", ())
            if tokens:
                best_token = ""
                for t in sorted(tokens, key=len, reverse=True):
                    if t.lower() not in used_words and len(t) > KSETRAJNA:
                        best_token = t
                        break
                if best_token:
                    output_parts.append(best_token)
                    used_words.add(best_token.lower())
                    total_words += KSETRAJNA
                    continue

            for mw in meaning.split():
                if total_words >= max_words:
                    break
                mwl = mw.lower()
                if mwl not in used_words and len(mwl) > KSETRAJNA:
                    output_parts.append(mw)
                    used_words.add(mwl)
                    total_words += KSETRAJNA

        self._compositions += KSETRAJNA
        return " ".join(output_parts)


# =============================================================================
# SINGLETON
# =============================================================================

_composition_instance: Optional[MahaComposition] = None


def get_composition() -> MahaComposition:
    """Get or create the composition adapter singleton."""
    global _composition_instance
    if _composition_instance is None:
        _composition_instance = MahaComposition()
    return _composition_instance


# =============================================================================
# BACKWARD COMPAT — compose_from_wave delegates to adapter
# =============================================================================


def compose_from_wave(lotus_response: Dict, input_text: str) -> str:
    """Backward-compatible entry point. Delegates to MahaComposition adapter."""
    return get_composition().compose(lotus_response, input_text)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahaComposition",
    "PranaScorer",
    "RhythmScorer",
    "SemanticScorer",
    "ModeScorer",
    "StateScorer",
    "get_composition",
    "compose_from_wave",
]
