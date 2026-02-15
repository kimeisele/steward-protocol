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
from vibe_core.mahamantra.substrate.language.types import RhythmProfile, StateVector, SyllableVector
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
    state: Optional[StateVector] = None,
) -> List[Dict[str, object]]:
    """Rank resonant pool by base score + rhythm + semantic + chamber + state boost."""
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
        # State affinity: bias toward words that match system reality
        st = 0.0
        if state is not None:
            phex = str(scored.get("packed_hex", ""))
            mode = classify_by_graph(phex, mode_anchor_phrases()) if phex else None
            st = state_affinity(state, scored, mode)
        scored["state_boost"] = st
        scored["rhythm_score"] = base_score + bias + sem + chamb + st
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
# STATE AFFINITY — semantic injection from MahaState
# =============================================================================

def state_affinity(
    sv: StateVector,
    item: Dict[str, object],
    mode: Optional[str] = None,
) -> float:
    """Score how well a word fits the current system state.

    Three axes, all numeric from StateVector:

        1. Guna → Mode alignment:
           SATTVA(2) boosts DHARMA, RAJAS(1) boosts KARMA, TAMAS(0) boosts GENESIS.
           Matching mode gets a bonus.

        2. Entry count → Mass preference:
           More state entries = prefer heavier words (complex state needs complex words).
           Fewer entries = prefer lighter words.

        3. Uptime ratio → Confidence:
           High uptime = prefer words with higher base score (established, confident).
           Low uptime = no penalty, just no bonus.

    Returns: affinity in [0, max_boost]. All coefficients from protocol constants.
    """
    max_boost = PANCHA / (WORDS * HALVES)  # ~0.15625, same scale as chamber_boost

    score = 0.0

    # Axis 1: Guna ↔ Mode alignment
    # Map guna ordinal to preferred mode
    guna_mode = ("GENESIS", "KARMA", "DHARMA")  # TAMAS→GENESIS, RAJAS→KARMA, SATTVA→DHARMA
    preferred = guna_mode[min(sv.guna, HALVES)]
    if mode is not None and mode == preferred:
        score += max_boost

    # Axis 2: Entry count → Mass preference
    # Normalize entry count to [0, 1] using MAX_STATE_ENTRIES (72 = NADI_RESONANCE)
    from vibe_core.mahamantra.substrate.maha_state import MAX_STATE_ENTRIES
    entry_ratio = min(1.0, sv.entry_count / max(MAX_STATE_ENTRIES, KSETRAJNA))
    coords = item.get("coords", ())
    mass = len(coords) if coords else 0
    # Heavy state prefers heavy words, light state prefers light words
    mass_ratio = min(1.0, mass / max(SEVEN, KSETRAJNA))
    # Reward alignment: both heavy or both light
    mass_alignment = 1.0 - abs(entry_ratio - mass_ratio)
    score += mass_alignment * (max_boost / HALVES)

    # Axis 3: Uptime → Confidence boost on high-scoring words
    base_score = float(item.get("score", 0.0))
    if sv.uptime_ratio > (KSETRAJNA / HALVES):  # > 0.5
        score += base_score * sv.uptime_ratio * (max_boost / QUARTERS)

    return min(max_boost * HALVES, score)  # Cap at 2× max_boost


# =============================================================================
# COMPOSE — the three layers wired together
# =============================================================================

def _resolve_coords(sanskrit: str, first_coord: int) -> Tuple[int, ...]:
    """Resolve RAMA coordinates for a word. Lookup by IAST, fallback to first_coord."""
    try:
        from vibe_core.mahamantra.substrate.sanskrit_lookup import word_by_iast
        entry = word_by_iast(sanskrit)
        if entry is not None and entry.coords:
            return entry.coords
    except Exception:
        pass
    # Fallback: synthesize minimal coords from first_coord
    if first_coord >= 0:
        return (first_coord,)
    return ()


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

    # Expansion words: cap at PANCHA to prevent pool dilution
    exp_count = 0
    if expansion_data:
        for sanskrit, meaning in expansion_data.get("expansion_words", ()):
            if meaning and exp_count < PANCHA:
                coords = _resolve_coords(sanskrit, -1)
                pool.append({
                    "sanskrit": sanskrit, "meaning": meaning, "tokens": (),
                    "score": PANCHA / WORDS, "packed_hex": "",
                    "first_coord": coords[0] if coords else -1,
                    "coords": coords,
                })
                exp_count += KSETRAJNA
        for sanskrit, meaning in expansion_data.get("synth_walk_words", ()):
            if meaning and exp_count < PANCHA:
                coords = _resolve_coords(sanskrit, -1)
                pool.append({
                    "sanskrit": sanskrit, "meaning": meaning, "tokens": (),
                    "score": QUARTERS / WORDS, "packed_hex": "",
                    "first_coord": coords[0] if coords else -1,
                    "coords": coords,
                })
                exp_count += KSETRAJNA

    # Branch words: cap at PANCHA total across all modes
    branch_count = 0
    if branch_words:
        for mode_name, bwords in branch_words.items():
            for bw in bwords:
                if branch_count >= PANCHA:
                    break
                meaning = bw.get("meaning", "")
                if meaning:
                    fc = bw.get("first_coord", -1)
                    coords = _resolve_coords(bw.get("sanskrit", ""), fc)
                    pool.append({
                        "sanskrit": bw.get("sanskrit", ""),
                        "meaning": meaning, "tokens": (),
                        "score": PANCHA / (WORDS - HALVES),
                        "packed_hex": "",
                        "first_coord": coords[0] if coords else fc,
                        "coords": coords, "from_branch": True,
                    })
                    branch_count += KSETRAJNA

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


def _pick_token(
    item: Dict[str, object],
    input_words: Tuple[str, ...] = (),
    used: Optional[set] = None,
) -> str:
    """Pick the best English token for a word.

    Scoring: length + input echo bonus. Skips already-used tokens.
    Input matching ensures user's words echo in output (semantic grounding)
    but doesn't dominate — it's a bonus, not absolute priority.
    """
    tokens = item.get("tokens", ())
    if tokens:
        best = ""
        best_score = -1
        input_set = set(input_words) if input_words else set()
        used_set = used or set()

        for t in tokens:
            tl = t.lower()
            if tl in used_set or len(tl) <= KSETRAJNA:
                continue
            # Score: length (content) + PANCHA bonus for input echo
            s = len(t) + (PANCHA if tl in input_set else 0)
            if s > best_score:
                best_score = s
                best = t

        if best:
            return best

        # All tokens used or too short — pick longest regardless
        best = tokens[0]
        for t in tokens[KSETRAJNA:]:
            if len(t) > len(best):
                best = t
        return best

    # Fallback: first word of meaning
    meaning = str(item.get("meaning", ""))
    parts = meaning.split()
    return parts[0] if parts else ""


def _word_role(item: Dict[str, object]) -> str:
    """Classify a pool word by coordinate mass → grammatical role.

    Same logic as section_router._infer_role but for pool items
    (no verse position available, so we use mass only).

    Mass thresholds from protocol constants:
        mass ≤ HALVES (2)           → PARTICLE
        mass ≥ PANCHA + HALVES (7)  → QUALITY
        mass ≤ QUARTERS (4)         → REF
        mass ≤ PANCHA (5)           → VERB  (mid-weight action words)
        otherwise                   → NOUN
    """
    coords = item.get("coords", ())
    mass = len(coords) if coords else 0

    if mass <= HALVES:
        return "PARTICLE"
    if mass >= PANCHA + HALVES:
        return "QUALITY"
    if mass <= QUARTERS:
        return "REF"
    if mass <= PANCHA:
        return "VERB"
    return "NOUN"


# SVO sentence order: Subject → Verb → Object → Modifiers
# This is the SOV→SVO transformation. Sanskrit verse templates are SOV;
# English output must be SVO. Role priority defines slot order.
_SVO_ORDER: Tuple[str, ...] = ("REF", "VERB", "NOUN", "QUALITY", "PREP", "PARTICLE")


def _assemble(
    selected: List[Dict[str, object]],
    template: List[Dict],
    rhythm: RhythmProfile,
    input_text: str = "",
) -> str:
    """Assemble selected words into SVO sentence structure.

    1. Classify each selected word by coordinate mass → role.
    2. Place into SVO slots: Subject(REF) → Verb → Object(NOUN) → Quality → Particle.
    3. Template provides structural anchor words at key positions.
    4. Input words echo in token selection (semantic grounding).
    """
    if not selected:
        return ""

    # Classify selected words into role buckets
    by_role: Dict[str, List[Dict]] = {r: [] for r in _SVO_ORDER}
    for item in selected:
        role = _word_role(item)
        if role in by_role:
            by_role[role].append(item)
        else:
            by_role["NOUN"].append(item)

    # Extract input words for semantic echo (lowercase, len > 1)
    input_words: Tuple[str, ...] = tuple(
        w.lower().strip("?!.,;:") for w in input_text.split()
        if len(w.strip("?!.,;:")) > KSETRAJNA
    ) if input_text else ()

    # Walk SVO order, pick best token from each role bucket
    ordered: List[str] = []
    used: set = set()

    for role in _SVO_ORDER:
        bucket = by_role.get(role, [])
        for item in bucket:
            if len(ordered) >= SEVEN:
                break
            token = _pick_token(item, input_words, used)
            tl = token.lower()
            if tl and tl not in used and len(tl) > KSETRAJNA:
                ordered.append(token)
                used.add(tl)

    # Template anchor: inject first template word with a matching role
    # at the appropriate SVO position (structural frame from the verse)
    if template and len(ordered) >= HALVES:
        for slot in template[:PANCHA]:
            role = slot.get("role", "NOUN")
            meaning = slot.get("meaning", "")
            parts = meaning.split()
            if not parts:
                continue
            t = parts[0].lower()
            if t in used or len(t) <= KSETRAJNA:
                continue
            # Find insertion point: after existing words of earlier roles
            insert_at = 0
            for svo_role in _SVO_ORDER:
                if svo_role == role:
                    break
                insert_at += len(by_role.get(svo_role, []))
            insert_at = min(insert_at, len(ordered))
            ordered.insert(insert_at, t)
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
    state: Optional[StateVector] = None,
) -> str:
    """Prosodic Composition: resonant words → English output.

    Layer 1: Build pool with precomputed WN tokens + coords.
    Layer 2: Rank by rhythm + semantic + chamber + state. Select by prosodic affinity.
    Layer 3: Assemble via grid mode walk + template frame.
    """
    pool = _build_pool(guardian_response, expansion_data, branch_words)
    pool = rank_resonant_by_rhythm(pool, rhythm, input_text, seed=seed, antaranga=antaranga, state=state)
    selected = _select_words(pool, rhythm, max_words=SEVEN)
    return _assemble(selected, template, rhythm, input_text)


def _build_lotus_pool(lotus_response: Dict) -> List[Dict[str, object]]:
    """Build word pool from Lotus __call__ response.

    Two sources (both from the real Maha Mantra computation):
        1. smaranam — 7 resonant words (7D ranked, primary content)
        2. verse.words — Gita verse word-for-word (philosophical grounding)

    Each pool item gets coords resolved via word_by_iast for role classification.
    """
    pool: List[Dict[str, object]] = []

    # Source 1: Smaranam — resonant words from rank_words (7D scoring)
    for rw in lotus_response.get("smaranam", ()):
        sanskrit = rw.get("sanskrit", "")
        meaning = rw.get("meaning", "")
        score = float(rw.get("score", 0))
        if not meaning:
            continue
        coords = _resolve_coords(sanskrit, -1)
        phex = ""
        try:
            from vibe_core.mahamantra.substrate.sanskrit_lookup import word_by_iast
            entry = word_by_iast(sanskrit)
            if entry is not None:
                phex = getattr(entry, "packed_hex", "")
        except Exception:
            pass
        tokens = word_tokens(phex) if phex else ()
        pool.append({
            "sanskrit": sanskrit,
            "meaning": meaning,
            "tokens": tokens,
            "score": score,
            "packed_hex": phex,
            "first_coord": coords[0] if coords else -1,
            "coords": coords,
            "source": "smaranam",
        })

    # Source 2: Verse words — Gita philosophical grounding
    verse = lotus_response.get("verse")
    verse_count = 0
    if verse and "words" in verse:
        for vw in verse["words"]:
            if verse_count >= SEVEN:
                break
            sanskrit = vw.get("sanskrit", "")
            meaning = vw.get("meaning", "")
            if not meaning or len(meaning) <= KSETRAJNA:
                continue
            coords = _resolve_coords(sanskrit, -1)
            pool.append({
                "sanskrit": sanskrit,
                "meaning": meaning,
                "tokens": (),
                "score": PANCHA / WORDS,
                "packed_hex": "",
                "first_coord": coords[0] if coords else -1,
                "coords": coords,
                "source": "verse",
            })
            verse_count += KSETRAJNA

    return pool


def compose_from_lotus(
    lotus_response: Dict,
    input_text: str,
) -> str:
    """Compose English output from a Lotus __call__ response.

    This is the Lotus-rooted composition path. The Lotus response IS the
    Maha Vector — it contains smaranam (resonant words), verse (Gita grounding),
    vibration, guna, DIW, position, antaranga, akash. Everything computed by
    the real Maha Mantra pipeline.

    The composer clothes this truth in English using:
        - SVO ordering from coordinate mass → role
        - Input echo from user words
        - Prosodic affinity from syllable vectors
    """
    from vibe_core.mahamantra.substrate.language.phonetics import scan_syllable_rhythm

    pool = _build_lotus_pool(lotus_response)
    rhythm = scan_syllable_rhythm(input_text)

    # Rank by rhythm (prosodic affinity between input syllables and word coords)
    pool = rank_resonant_by_rhythm(pool, rhythm, input_text, seed=0)

    # Select top SEVEN words by prosodic affinity
    selected = _select_words(pool, rhythm, max_words=SEVEN)

    # Extract template from verse if available
    template: List[Dict] = []
    verse = lotus_response.get("verse")
    if verse and "words" in verse:
        total = len(verse["words"])
        for i, vw in enumerate(verse["words"]):
            coords = _resolve_coords(vw.get("sanskrit", ""), -1)
            role = _word_role({"coords": coords})
            template.append({
                "position": i, "sanskrit": vw.get("sanskrit", ""),
                "meaning": vw.get("meaning", ""), "role": role, "coords": coords,
            })

    return _assemble(selected, template, rhythm, input_text)


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
