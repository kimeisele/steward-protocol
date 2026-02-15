"""
COMPOSER — Prosodic Composition (Resonant Words → English)
==========================================================

NO HARDCODED KEYWORDS. NO IF/ELSE STRING MATCHING.

Three layers, each using existing branchless infrastructure:

    1. TOKENS: wordnet_bridge entry["t"] = precomputed English tokens per word.
       3556 words, already extracted. No gloss parsing.

    2. SELECT: Syllable vectors match word coordinate properties.
       sv.weight ↔ len(word.coords)     — phonemic mass alignment
       sv.height ↔ dominant element      — element height (PANCHA scale)
       sv.stress ↔ grid beat             — downbeat = key word
       Mode affinity via classify_by_graph(packed_hex) — WordNet graph distance.

    3. ASSEMBLE: Grid mode sequence + template coords give sentence shape.
       Word order from grid walk. Template roles from section_router.
       No keyword-based role classification.

All thresholds derived from protocol constants.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    MAHA_QUANTUM,
    PANCHA,
    QUARTERS,
    SEVEN,
    WORDS,
)
from vibe_core.mahamantra.substrate.language.types import RhythmProfile, SyllableVector
from vibe_core.mahamantra.substrate.language.mantra_grid import build_mantra_grid, get_holyname_mode
from vibe_core.mahamantra.substrate.language.mode_affinity import classify_by_graph, mode_anchor_phrases
from vibe_core.mahamantra.substrate.seed import HolyName


# =============================================================================
# TOKENS — from wordnet_bridge precomputed data
# =============================================================================

def word_tokens(packed_hex: str) -> Tuple[str, ...]:
    """Get precomputed English tokens for a Gita word. O(1) lookup."""
    try:
        from vibe_core.mahamantra.substrate.wordnet_bridge import _ensure_loaded, _word_entries
        _ensure_loaded()
        entry = (_word_entries or {}).get(packed_hex, {})
        return tuple(entry.get("t", ()))
    except Exception:
        return ()


def dominant_element(coords: Sequence[int]) -> int:
    """Dominant element ordinal (0-4) from RAMA coordinates. Branchless."""
    from vibe_core.mahamantra.substrate.pancha_walk import COORD_ELEMENT
    counts = [0] * PANCHA
    for c in coords:
        counts[COORD_ELEMENT[c].value] += KSETRAJNA
    best = 0
    for i in range(KSETRAJNA, PANCHA):
        if counts[i] > counts[best]:
            best = i
    return best


def coord_mass(coords: Sequence[int]) -> int:
    """Phonemic mass = coordinate count. Direct."""
    return len(coords)


# =============================================================================
# SCORING — rhythm, semantic, chamber (all derived, no hardcoded floats)
# =============================================================================

def rhythm_bias(rhythm: RhythmProfile, index: int) -> float:
    """Rhythmic emphasis from 3D vectors + grid. All coefficients derived."""
    if rhythm.syllable_count == 0 or not rhythm.sequencer_steps:
        return 0.0

    grid = build_mantra_grid()
    step_idx = rhythm.sequencer_steps[index % len(rhythm.sequencer_steps)]
    gs = grid[step_idx]
    sv = rhythm.vectors[index % len(rhythm.vectors)] if rhythm.vectors else None

    score = 0.0
    base = KSETRAJNA / WORDS                # 1/16
    half_base = KSETRAJNA / (WORDS * HALVES) # 1/32

    if gs.beat == 0:
        score += base
    if sv is not None:
        if sv.stress >= KSETRAJNA and gs.beat == 0:
            score += base
        if sv.weight >= (PANCHA - HALVES) and gs.holy_name in (HolyName.KRISHNA, HolyName.RAMA):
            score += half_base
        if sv.height >= QUARTERS and gs.mode == "DHARMA":
            score += half_base
    if step_idx < WORDS:
        score += half_base
    return score


def semantic_boost(input_text: str, packed_hex: str) -> float:
    """WordNet graph distance bonus. Pure graph math, no keywords."""
    if not packed_hex:
        return 0.0
    try:
        from vibe_core.mahamantra.substrate.wordnet_bridge import semantic_score
        return semantic_score(input_text, packed_hex) * (KSETRAJNA / 10.0)
    except Exception:
        return 0.0


def chamber_boost(antaranga, first_coord: int, seed: int) -> float:
    """Antaranga prana boost. Derived coefficients."""
    if antaranga is None or first_coord < 0:
        return 0.0
    slot = (first_coord * SEVEN + seed) % 512
    prana = antaranga.prana_at(slot)
    if prana == 0:
        return 0.0
    from vibe_core.mahamantra.substrate.antaranga import GENESIS_PRANA_U32
    max_boost = PANCHA / (WORDS * HALVES)
    return min(max_boost, (prana / GENESIS_PRANA_U32) * (KSETRAJNA / WORDS))


def rank_resonant_by_rhythm(
    resonant: List[Dict[str, object]],
    rhythm: RhythmProfile,
    input_text: str = "",
    seed: int = 0,
    antaranga=None,
) -> List[Dict[str, object]]:
    """Rank resonant pool by base score + rhythm + semantic + chamber boost."""
    ranked: List[Dict[str, object]] = []
    for i, item in enumerate(resonant):
        scored = dict(item)
        bias = rhythm_bias(rhythm, i)
        sem = semantic_boost(input_text, str(scored.get("packed_hex", "")))
        chamb = chamber_boost(antaranga, int(scored.get("first_coord", -1)), seed)
        base_score = float(scored.get("score", 0.0))
        scored["rhythm_bias"] = bias
        scored["semantic_boost"] = sem
        scored["chamber_boost"] = chamb
        scored["rhythm_score"] = base_score + bias + sem + chamb
        ranked.append(scored)

    ranked.sort(key=lambda it: (float(it.get("rhythm_score", 0.0)), float(it.get("score", 0.0))), reverse=True)
    return ranked


# =============================================================================
# PROSODIC AFFINITY — syllable vector ↔ word coordinate properties
# =============================================================================

def prosodic_affinity(sv: SyllableVector, coords: Sequence[int]) -> float:
    """Score how well a syllable vector matches a word's coordinate properties.

    Three axes, all arithmetic on existing data:
        sv.weight ↔ coord_mass(coords)  — phonemic mass alignment
        sv.height ↔ dominant_element     — element height (same PANCHA scale)
        sv.stress ↔ coord_mass           — stressed positions want heavier words

    Returns: affinity in [0, 1]. Higher = better prosodic fit.
    """
    if not coords:
        return 0.0

    mass = coord_mass(coords)
    elem = dominant_element(coords)

    score = 0

    # Weight axis: syllable weight ↔ phonemic mass
    # Difference penalized. Perfect match = PANCHA points.
    weight_diff = abs(sv.weight - min(mass, PANCHA))
    score += max(0, PANCHA - weight_diff)

    # Height axis: syllable height (1-5) ↔ element ordinal+1 (1-5)
    # Same PANCHA scale. Difference penalized.
    height_diff = abs(sv.height - (elem + KSETRAJNA))
    score += max(0, PANCHA - height_diff)

    # Stress axis: stressed syllables prefer heavier (longer) words
    if sv.stress >= KSETRAJNA:
        score += min(mass, PANCHA)
    else:
        score += max(0, PANCHA - mass)

    # Normalize: max possible = PANCHA * 3 = 15
    return score / (PANCHA * 3)


# =============================================================================
# COMPOSE — the three layers wired together
# =============================================================================

def _build_pool(
    guardian_response,
    expansion_data: Optional[Dict],
    branch_words: Optional[Dict[str, list]],
) -> List[Dict[str, object]]:
    """Build word pool. Each entry carries coords, packed_hex, tokens, score."""
    pool: List[Dict[str, object]] = []

    for rw in guardian_response.words:
        w = rw.word
        if not w.meanings:
            continue
        phex = getattr(w, "packed_hex", "")
        tokens = word_tokens(phex)
        pool.append({
            "sanskrit": w.sanskrit,
            "meaning": w.meanings[0],
            "tokens": tokens,
            "score": rw.total_score,
            "packed_hex": phex,
            "first_coord": w.first_coord,
            "coords": getattr(w, "coords", ()),
        })

    if expansion_data:
        for sanskrit, meaning in expansion_data.get("expansion_words", ()):
            if meaning:
                pool.append({
                    "sanskrit": sanskrit, "meaning": meaning, "tokens": (),
                    "score": PANCHA / WORDS, "packed_hex": "", "first_coord": -1,
                    "coords": (),
                })
        for sanskrit, meaning in expansion_data.get("synth_walk_words", ()):
            if meaning:
                pool.append({
                    "sanskrit": sanskrit, "meaning": meaning, "tokens": (),
                    "score": QUARTERS / WORDS, "packed_hex": "", "first_coord": -1,
                    "coords": (),
                })

    if branch_words:
        for mode_name, bwords in branch_words.items():
            for bw in bwords:
                meaning = bw.get("meaning", "")
                if meaning:
                    pool.append({
                        "sanskrit": bw.get("sanskrit", ""),
                        "meaning": meaning, "tokens": (),
                        "score": PANCHA / (WORDS - HALVES),
                        "packed_hex": "", "first_coord": bw.get("first_coord", -1),
                        "coords": (), "from_branch": True,
                    })

    return pool


def _select_words(
    pool: List[Dict[str, object]],
    rhythm: RhythmProfile,
    max_words: int,
) -> List[Dict[str, object]]:
    """Select words guided by prosodic affinity between syllable vectors and coords."""
    if not pool:
        return []

    selected: List[Dict[str, object]] = []
    used: set = set()

    # Syllable-driven selection: each syllable position picks its best-fitting word
    if rhythm.vectors and rhythm.syllable_count > 0:
        n = min(max_words, rhythm.syllable_count)
        for i in range(n):
            sv = rhythm.vectors[i % len(rhythm.vectors)]
            best = None
            best_score = -1.0

            for item in pool:
                key = item["sanskrit"]
                if key in used:
                    continue
                coords = item.get("coords", ())
                affinity = prosodic_affinity(sv, coords)
                combined = float(item.get("rhythm_score", item.get("score", 0.0))) + affinity
                if combined > best_score:
                    best_score = combined
                    best = item

            if best is not None:
                selected.append(best)
                used.add(best["sanskrit"])

    # Fill remaining by score
    for item in pool:
        if len(selected) >= max_words:
            break
        if item["sanskrit"] not in used:
            selected.append(item)
            used.add(item["sanskrit"])

    return selected


def _pick_token(item: Dict[str, object]) -> str:
    """Pick the best English token for a word. Bridge tokens first, meaning fallback."""
    tokens = item.get("tokens", ())
    if tokens:
        # Pick longest token (most semantic content) — branchless max
        best = tokens[0]
        for t in tokens[KSETRAJNA:]:
            if len(t) > len(best):
                best = t
        return best
    # Fallback: first word of meaning
    meaning = str(item.get("meaning", ""))
    parts = meaning.split()
    return parts[0] if parts else ""


def _assemble(
    selected: List[Dict[str, object]],
    template: List[Dict],
    rhythm: RhythmProfile,
) -> str:
    """Assemble selected words into output.

    Order determined by grid mode sequence (from rhythm).
    Template provides structural frame.
    """
    if not selected:
        return ""

    # Classify selected words by mode (branchless, via WordNet graph)
    anchors = mode_anchor_phrases()
    by_mode: Dict[str, List[Dict]] = {"DHARMA": [], "GENESIS": [], "KARMA": []}
    unclassified: List[Dict] = []

    for item in selected:
        phex = str(item.get("packed_hex", ""))
        mode = classify_by_graph(phex, anchors) if phex else None
        if mode and mode in by_mode:
            by_mode[mode].append(item)
        else:
            unclassified.append(item)

    # Walk the grid mode sequence from input rhythm
    grid = build_mantra_grid()
    ordered: List[str] = []
    used: set = set()

    # Build mode sequence from rhythm (deduplicated consecutive)
    mode_seq: List[str] = []
    if rhythm.grid_modes:
        for gm in rhythm.grid_modes:
            if not mode_seq or mode_seq[-1] != gm:
                mode_seq.append(gm)
    if not mode_seq:
        mode_seq = ["GENESIS"]

    # Walk modes, pick tokens
    for mode in mode_seq:
        pool = by_mode.get(mode, [])
        for item in pool:
            token = _pick_token(item)
            tl = token.lower()
            if tl and tl not in used and len(tl) > KSETRAJNA:
                ordered.append(token)
                used.add(tl)
                break

    # Fill from unclassified + remaining classified
    remaining = unclassified[:]
    for mode_pool in by_mode.values():
        remaining.extend(mode_pool)
    for item in remaining:
        if len(ordered) >= SEVEN:
            break
        token = _pick_token(item)
        tl = token.lower()
        if tl and tl not in used and len(tl) > KSETRAJNA:
            ordered.append(token)
            used.add(tl)

    # Inject template tokens at structural positions
    # Template words with coords provide the frame; resonant words fill it
    if template and len(ordered) >= HALVES:
        for slot in template[:HALVES]:
            meaning = slot.get("meaning", "")
            parts = meaning.split()
            if parts:
                t = parts[0].lower()
                if t not in used and len(t) > KSETRAJNA:
                    ordered.insert(min(KSETRAJNA, len(ordered)), t)
                    used.add(t)
                    break

    return " ".join(ordered)


def compose(
    guardian_response,
    template: List[Dict],
    rhythm: RhythmProfile,
    input_text: str,
    section_mode: str,
    antaranga_data: Dict,
    expansion_data: Optional[Dict] = None,
    seed: int = 0,
    branch_words: Optional[Dict[str, list]] = None,
    antaranga=None,
) -> str:
    """Prosodic Composition: resonant words → English output.

    Layer 1: Build pool with precomputed WN tokens + coords.
    Layer 2: Rank by rhythm + semantic + chamber. Select by prosodic affinity.
    Layer 3: Assemble via grid mode walk + template frame.
    """
    pool = _build_pool(guardian_response, expansion_data, branch_words)
    pool = rank_resonant_by_rhythm(pool, rhythm, input_text, seed=seed, antaranga=antaranga)
    selected = _select_words(pool, rhythm, max_words=SEVEN)
    return _assemble(selected, template, rhythm)


def chunk_sentence(words: List[str]) -> List[str]:
    """Group flat word list into readable phrase chunks."""
    if len(words) <= HALVES + KSETRAJNA:
        return [" ".join(words)]

    chunks: List[str] = []
    current: List[str] = []

    for w in words:
        current.append(w)
        if len(current) >= QUARTERS:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks
