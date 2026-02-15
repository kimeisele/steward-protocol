"""
COMPOSER — Rhythmic Sequencing Composition (Words → English)
============================================================

PRIMARY: Grid modes (DHARMA/GENESIS/KARMA) drive word selection.
SECONDARY: Template roles and section_mode refine within mode.

Algorithm:
    1. Build word pool (resonant + expansion), ranked by rhythm + semantic
    2. Classify each word by affinity to grid modes (WordNet graph distance)
    3. Walk the grid mode sequence, picking best word per mode
    4. Template roles provide structural hints (subject/verb/object)
"""

from __future__ import annotations

from typing import Dict, Final, List, Optional, Tuple

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


def rhythm_bias(rhythm: RhythmProfile, index: int) -> float:
    """Compute rhythmic emphasis bonus using 3D vectors and grid modes."""
    if rhythm.syllable_count == 0 or not rhythm.sequencer_steps:
        return 0.0

    grid = build_mantra_grid()
    step_idx = rhythm.sequencer_steps[index % len(rhythm.sequencer_steps)]
    gs = grid[step_idx]
    sv = rhythm.vectors[index % len(rhythm.vectors)] if rhythm.vectors else None

    score = 0.0
    if gs.beat == 0:
        score += 0.04
    if sv is not None:
        if sv.stress >= KSETRAJNA and gs.beat == 0:
            score += 0.03
        if sv.weight >= 3 and gs.holy_name in (HolyName.KRISHNA, HolyName.RAMA):
            score += 0.02
        if sv.height >= QUARTERS and gs.mode == "DHARMA":
            score += 0.01
    if step_idx < WORDS:
        score += 0.01
    return score


def semantic_boost(input_text: str, packed_hex: str) -> float:
    """WordNet graph distance bonus for a candidate word."""
    if not packed_hex:
        return 0.0
    try:
        from vibe_core.mahamantra.substrate.wordnet_bridge import semantic_score
        return semantic_score(input_text, packed_hex) * 0.1
    except Exception:
        return 0.0


def chamber_boost(antaranga, first_coord: int, seed: int) -> float:
    """Antaranga chamber boost: prana at the word's slot from the character wave."""
    if antaranga is None or first_coord < 0:
        return 0.0
    slot = (first_coord * SEVEN + seed) % 512
    prana = antaranga.prana_at(slot)
    if prana == 0:
        return 0.0
    from vibe_core.mahamantra.substrate.antaranga import GENESIS_PRANA_U32
    return min(0.15, (prana / GENESIS_PRANA_U32) * 0.05)


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
    """Rhythmic Sequencing Compose.

    PRIMARY: Grid modes (DHARMA/GENESIS/KARMA) drive word selection.
    SECONDARY: Template roles and section_mode refine within mode.
    """
    # === WORD POOL: merge resonant + expansion words by score ===
    resonant = []
    for rw in guardian_response.words:
        meanings = rw.word.meanings
        if meanings:
            resonant.append({
                "sanskrit": rw.word.sanskrit,
                "meaning": meanings[0],
                "score": rw.total_score,
                "all_meanings": meanings,
                "packed_hex": getattr(rw.word, "packed_hex", ""),
                "first_coord": rw.word.first_coord,
            })

    # Enrich with expansion words (lower priority)
    if expansion_data:
        for sanskrit, meaning in expansion_data.get("expansion_words", ()):
            if meaning:
                resonant.append({"sanskrit": sanskrit, "meaning": meaning, "score": 0.3, "all_meanings": (meaning,)})
        for sanskrit, meaning in expansion_data.get("synth_walk_words", ()):
            if meaning:
                resonant.append({"sanskrit": sanskrit, "meaning": meaning, "score": 0.2, "all_meanings": (meaning,)})

    # Rank full pool by rhythm + semantic
    resonant = rank_resonant_by_rhythm(resonant, rhythm, input_text, seed=seed, antaranga=antaranga)

    # === MODE AFFINITY: classify words by graph distance ===
    anchors = mode_anchor_phrases()
    by_mode: Dict[str, List[Dict]] = {"DHARMA": [], "GENESIS": [], "KARMA": []}
    for r in resonant:
        phex = str(r.get("packed_hex", ""))
        best_mode = classify_by_graph(phex, anchors) if phex else None
        if best_mode:
            by_mode[best_mode].append(r)
        else:
            for m in by_mode.values():
                m.append(r)

    # === FRACTAL BRANCH INJECTION ===
    if branch_words:
        for mode_name, bwords in branch_words.items():
            if mode_name in by_mode:
                for bw in bwords:
                    meaning = bw.get("meaning", "")
                    if meaning:
                        by_mode[mode_name].append({
                            "sanskrit": bw.get("sanskrit", ""),
                            "meaning": meaning,
                            "score": 0.4,
                            "all_meanings": (meaning,),
                            "first_coord": bw.get("first_coord", -1),
                            "from_branch": True,
                        })

    # === RHYTHMIC SEQUENCING: walk grid modes, pick words ===
    parts: List[str] = []
    used: set = set()

    holyname_mode = get_holyname_mode()
    if rhythm.grid_modes:
        mode_seq: List[str] = []
        for gm in rhythm.grid_modes:
            if not mode_seq or mode_seq[-1] != gm:
                mode_seq.append(gm)
    else:
        mode_seq = [holyname_mode.get(HolyName.KRISHNA, "GENESIS")]

    for mode in mode_seq:
        pool = by_mode.get(mode, resonant)
        for r in pool:
            ml = r["meaning"].lower().strip()
            if ml and ml not in used and ml not in ("", "the", "a", "an"):
                used.add(ml)
                parts.append(r["meaning"])
                break

    for r in resonant:
        if len(parts) >= SEVEN:
            break
        ml = r["meaning"].lower().strip()
        if ml and ml not in used and ml not in ("", "the", "a", "an"):
            used.add(ml)
            parts.append(r["meaning"])

    # === TEMPLATE STRUCTURAL HINTS (secondary) ===
    by_role: Dict[str, List[str]] = {"REF": [], "VERB": [], "QUALITY": []}
    for tw in template:
        role = tw.get("role", "NOUN")
        meaning = tw.get("meaning", "")
        if meaning and role in by_role:
            by_role[role].append(meaning)

    if by_role["REF"] and parts:
        subj = by_role["REF"][0]
        if subj.lower() in ("unto me", "of me", "me"):
            subj = "The Supreme"
        elif subj.lower() in ("you", "unto you"):
            subj = "One who"
        sl = subj.lower()
        if sl not in used:
            parts.insert(0, subj.capitalize())
            used.add(sl)

    # Deduplicate, clean, join
    seen: set = set()
    clean = []
    for p in parts:
        p = p.strip()
        pl = p.lower()
        if p and pl not in seen:
            seen.add(pl)
            clean.append(p)

    if not clean and resonant:
        clean = [r["meaning"] for r in resonant[:PANCHA]]

    return " — ".join(chunk_sentence(clean))


def chunk_sentence(words: List[str]) -> List[str]:
    """Group flat word list into readable phrase chunks."""
    if len(words) <= 3:
        return [" ".join(words)]

    chunks: List[str] = []
    current: List[str] = []

    for w in words:
        wl = w.lower().strip()
        if (
            wl in ("towards", "through", "without", "within", "beyond", "therefore", "thus", "indeed", "certainly")
            and current
        ):
            chunks.append(" ".join(current))
            current = [w]
        else:
            current.append(w)
            if len(current) >= QUARTERS:
                chunks.append(" ".join(current))
                current = []

    if current:
        chunks.append(" ".join(current))

    return chunks
