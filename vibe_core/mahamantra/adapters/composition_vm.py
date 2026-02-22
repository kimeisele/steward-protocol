"""
COMPOSITION VM — Dispatch-based Composition Pipeline
=====================================================

Replaces the 160-line inline compose() with a 6-step dispatch loop.
Same pattern as mantra_vm.py: named wrappers, shared ctx dict, dispatch table.

ARCHITECTURE:
    compose_pipeline(adapter, lotus_response, input_text) -> str
    - Builds ctx dict once (hoists all lazy imports)
    - 6 steps: CONTEXT → POOL → RANK → SELECT → ALIGN → ASSEMBLE
    - Returns composed English string

The 5 Scorers remain untouched — they're already protocol-based.
This module replaces the PIPELINE, not the scorers.
"""

from __future__ import annotations

import logging
from enum import IntEnum
from typing import TYPE_CHECKING, Dict, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    PANCHA,
)

if TYPE_CHECKING:
    from vibe_core.mahamantra.adapters.composition import MahaComposition

logger = logging.getLogger("MAHA_COMPOSITION_VM")


# =============================================================================
# INSTRUCTION SET — 6 pipeline steps
# =============================================================================


class CompositionOp(IntEnum):
    """6-step composition pipeline. Order matters — each reads previous ctx."""

    CONTEXT = 0  # Extract scorer kwargs + max_words from lotus_response
    POOL = 1  # Build word pool from smaranam/verse
    RANK = 2  # Multi-scorer ranking (5 scorers, additive)
    SELECT = 3  # Context-driven selection (deduplicate, cap at max_words)
    ALIGN = 4  # Syllable vectors + grid alignment
    ASSEMBLE = 5  # Grid position → sentence order → English string


CYCLE = tuple(CompositionOp(i) for i in range(len(CompositionOp)))


# =============================================================================
# IMPORT CACHE — hoisted once, not on every call
# =============================================================================

_IMPORTS_CACHED = False
_build_lotus_pool = None
_syllable_vectors_for_word = None
_align_syllables_to_grid = None
_SyllableVector = None


def _ensure_imports():
    """Hoist all lazy imports once. Called on first compose_pipeline() call."""
    global _IMPORTS_CACHED, _build_lotus_pool, _syllable_vectors_for_word
    global _align_syllables_to_grid, _SyllableVector
    if _IMPORTS_CACHED:
        return
    from vibe_core.mahamantra.substrate.language.composer import (
        _build_lotus_pool as blp,
    )
    from vibe_core.mahamantra.substrate.language.phonetics import (
        syllable_vectors_for_word as svfw,
    )
    from vibe_core.mahamantra.substrate.language.mantra_grid import (
        align_syllables_to_grid as astg,
    )
    from vibe_core.mahamantra.substrate.language.types import (
        SyllableVector as SV,
    )

    _build_lotus_pool = blp
    _syllable_vectors_for_word = svfw
    _align_syllables_to_grid = astg
    _SyllableVector = SV
    _IMPORTS_CACHED = True


# =============================================================================
# STEP WRAPPERS — each reads/writes ctx
# =============================================================================


def _w_context(adapter: "MahaComposition", ctx: dict) -> None:
    """Extract scorer kwargs and max_words from lotus_response."""
    from vibe_core.mahamantra.adapters.composition import (
        _extract_scorer_kwargs,
        _context_max_words,
    )

    kwargs = _extract_scorer_kwargs(ctx["lotus_response"], ctx["input_text"])
    ctx["seed"] = kwargs.pop("seed")
    ctx["scorer_kwargs"] = kwargs
    ctx["max_words"] = _context_max_words(ctx["lotus_response"])
    adapter._last_context = {
        "guna_mode": kwargs.get("guna_mode"),
        "quarter": str(ctx["lotus_response"].get("quarter", "")),
        "guardian": str(ctx["lotus_response"].get("guardian", "")),
        "max_words": ctx["max_words"],
        "scorer_names": tuple(s.name for s in adapter._scorers),
    }


def _w_pool(adapter: "MahaComposition", ctx: dict) -> None:
    """Build word pool from lotus_response."""
    ctx["pool"] = _build_lotus_pool(ctx["lotus_response"])


def _w_rank(adapter: "MahaComposition", ctx: dict) -> None:
    """Multi-scorer ranking. 5 scorers, additive scores."""
    ranked: List[Dict] = []
    for item in ctx["pool"]:
        scored = dict(item)
        total_boost = 0.0
        for scorer in adapter._scorers:
            try:
                boost = scorer.score(scored, ctx["seed"], **ctx["scorer_kwargs"])
                scored[f"_{scorer.name}_score"] = boost
                total_boost += boost
            except Exception as exc:
                logger.warning("Scorer %s failed: %s", scorer.name, exc)
                scored[f"_{scorer.name}_score"] = 0.0
        base_score = float(scored.get("score", 0.0))
        scored["_total_score"] = base_score + total_boost
        ranked.append(scored)
    ranked.sort(key=lambda it: float(it.get("_total_score", 0.0)), reverse=True)
    ctx["ranked"] = ranked


def _w_select(adapter: "MahaComposition", ctx: dict) -> None:
    """Context-driven selection: deduplicate, cap at max_words."""
    selected: List[Dict] = []
    used_sanskrit: set = set()
    for item in ctx["ranked"]:
        if len(selected) >= ctx["max_words"]:
            break
        sk = item.get("sanskrit", "")
        if sk in used_sanskrit:
            continue
        selected.append(item)
        used_sanskrit.add(sk)
    ctx["selected"] = selected


def _w_align(adapter: "MahaComposition", ctx: dict) -> None:
    """Syllable vectors + grid alignment."""
    selected = ctx["selected"]
    word_syllables: List[Tuple[Dict, tuple]] = []
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
            svs = _syllable_vectors_for_word(english)
            if svs:
                word_syllables.append((item, svs))
    ctx["word_syllables"] = word_syllables

    if not word_syllables:
        ctx["grid_positions"] = None
        ctx["vector_to_word"] = None
        return

    all_vectors = []
    vector_to_word: List[int] = []
    for wi, (_, svs) in enumerate(word_syllables):
        for sv in svs:
            all_vectors.append(sv)
            vector_to_word.append(wi)
    ctx["vector_to_word"] = vector_to_word

    if not all_vectors:
        ctx["grid_positions"] = None
        return

    ctx["grid_positions"] = _align_syllables_to_grid(tuple(all_vectors))


def _w_assemble(adapter: "MahaComposition", ctx: dict) -> None:
    """Grid position → sentence order → English string."""
    selected = ctx["selected"]
    max_words = ctx["max_words"]
    word_syllables = ctx["word_syllables"]
    grid_positions = ctx["grid_positions"]

    # Fallback: no syllable vectors → join first meanings
    if not word_syllables or grid_positions is None:
        ctx["output"] = " ".join(
            str(it.get("meaning", "")).split()[0] for it in selected[:max_words] if it.get("meaning")
        )
        return

    # Word ordering by earliest grid position
    word_earliest: Dict[int, int] = {}
    for si, gp in enumerate(grid_positions):
        wi = ctx["vector_to_word"][si]
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

    ctx["output"] = " ".join(output_parts)


# =============================================================================
# DISPATCH TABLE
# =============================================================================

DISPATCH = {
    CompositionOp.CONTEXT: _w_context,
    CompositionOp.POOL: _w_pool,
    CompositionOp.RANK: _w_rank,
    CompositionOp.SELECT: _w_select,
    CompositionOp.ALIGN: _w_align,
    CompositionOp.ASSEMBLE: _w_assemble,
}


# =============================================================================
# ENGINE — the 6-line orchestrator
# =============================================================================


def compose_pipeline(
    adapter: "MahaComposition",
    lotus_response: Dict,
    input_text: str,
) -> str:
    """Dispatch-based composition pipeline.

    Replaces the 160-line inline compose() method.
    Same ctx-dict pattern as mantra_vm.execute_cycle().
    """
    _ensure_imports()

    ctx: dict = {
        "lotus_response": lotus_response,
        "input_text": input_text,
    }

    for op in CYCLE:
        DISPATCH[op](adapter, ctx)
        # Early exit: empty pool → no output
        if op == CompositionOp.POOL and not ctx.get("pool"):
            return ""

    adapter._compositions += KSETRAJNA
    return ctx.get("output", "")
