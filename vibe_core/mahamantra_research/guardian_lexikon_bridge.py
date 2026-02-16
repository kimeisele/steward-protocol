"""
GUARDIAN LEXIKON BRIDGE — From Numbers to Words
================================================

THESIS:
    The Guardian mod49 values map to RAMA Grid positions.
    The RAMA Lexicon contains Prabhupada's word-for-word Gita translations.
    Each RAMA coordinate has Sanskrit words that START with that phoneme.

    Therefore: Guardian mod49 → phoneme → all Gita words starting with
    that phoneme → English meanings = SEMANTIC CAPABILITY VOCABULARY.

    This is the bridge from pure mathematics to natural language.
    No LLM. Pure coordinate lookup. Deterministic.

ALSO:
    Part 6: Shruti vs Nakshatra distribution of Guardians
    Part 7: Harmonic dissolution paths (where each Guardian dissolves)
    Part 8: Per-syllable 4D analysis

ALL INSTRUMENTS ALREADY EXIST. WE JUST CONNECT THEM.
"""

from __future__ import annotations

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xlexbridge"

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra_research.guardian_syllable_trees import (
    ALL_GUARDIANS,
    KNOWN_CONSTANTS,
    compute_guardian_syllable_vibrations,
)
from vibe_core.mahamantra_research.shabda_spawning import compute_vibration_sum
from vibe_core.mahamantra_research.syllable_analysis import (
    syllabify_sanskrit,
    syllable_to_rama_index,
)
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_HARMONIC,
    COORD_SUB,
    COORD_VARGA,
    ELEMENT_NAMES,
    IS_SHRUTI,
)
from vibe_core.mahamantra.substrate.rama_grid import rama_to_phoneme

# Shastrische Funktionen
SHASTRISCH = {
    "vyasa": "compilation", "brahma": "creation", "narada": "transmission",
    "shambhu": "destruction", "prithu": "organization", "kumaras": "wisdom",
    "kapila": "analysis", "manu": "law", "parashurama": "enforcement",
    "prahlada": "devotion", "janaka": "execution", "bhishma": "commitment",
    "nrisimha": "protection", "bali": "surrender", "shuka": "liberation",
    "yamaraja": "judgment",
}


# =============================================================================
# PART 6: Rama Lexikon → Guardian Semantic Vocabulary
# =============================================================================

def load_rama_lexicon() -> Dict:
    """Load the Rama Lexicon (Prabhupada's Gita word-for-word)."""
    lexicon_path = Path(__file__).parent.parent / "data" / "rama_lexicon.json"
    with open(lexicon_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_coord_to_words_index(vocab: Dict) -> Dict[int, List[Dict]]:
    """
    Build index: first RAMA coordinate → list of words starting with that phoneme.

    This maps each of the 49 RAMA positions to all Gita words
    whose first phoneme is at that position.
    """
    index: Dict[int, List[Dict]] = defaultdict(list)

    for packed_hex, entry in vocab.items():
        coords = entry.get("coords", [])
        if not coords:
            continue
        first_coord = coords[0]
        index[first_coord].append({
            "sanskrit": entry["word"],
            "meanings": entry.get("meanings", []),
            "coords": coords,
            "packed": packed_hex,
        })

    return dict(index)


def guardian_semantic_vocabulary() -> None:
    """
    For each Guardian, find all Gita words that share their phonemic root.

    Guardian mod49 → RAMA position → all words starting at that position
    → English meanings = the Guardian's semantic vocabulary.
    """
    print("=" * 70)
    print("PART 6: GUARDIAN SEMANTIC VOCABULARY (from Rama Lexikon)")
    print("        mod49 → phoneme → Gita words → English meanings")
    print("=" * 70)
    print()

    lexicon = load_rama_lexicon()
    vocab = lexicon["vocabulary"]
    print(f"  Lexicon: {len(vocab)} unique words")
    print()

    coord_index = build_coord_to_words_index(vocab)
    print(f"  Indexed: {len(coord_index)}/49 RAMA positions have words")
    print()

    for i, name in enumerate(ALL_GUARDIANS):
        vib = compute_vibration_sum(name)
        m49 = vib % 49
        phoneme = rama_to_phoneme(m49)
        shastrisch = SHASTRISCH.get(name, "?")

        words_at_pos = coord_index.get(m49, [])

        # Collect all English meanings
        all_meanings = []
        for w in words_at_pos:
            for m in w["meanings"]:
                if m and m not in all_meanings:
                    all_meanings.append(m)

        # Also check syllable-level: each syllable's RAMA index
        syllables = syllabify_sanskrit(name)
        syl_words = {}
        for syl in syllables:
            syl_idx = syllable_to_rama_index(syl)
            if syl_idx >= 0:
                syl_w = coord_index.get(syl_idx, [])
                if syl_w:
                    syl_meanings = []
                    for w in syl_w:
                        for m in w["meanings"]:
                            if m and m not in syl_meanings:
                                syl_meanings.append(m)
                    syl_words[syl] = {
                        "rama_idx": syl_idx,
                        "word_count": len(syl_w),
                        "sample_meanings": syl_meanings[:5],
                    }

        const_name = KNOWN_CONSTANTS.get(m49, "")
        const_str = f" = {const_name}" if const_name else ""

        print(f"[{i:2d}] {name.upper():<14} mod49={m49:>2}{const_str}  phoneme={phoneme}")
        print(f"     Shastrisch: {shastrisch}")
        print(f"     Gita words starting with '{phoneme}': {len(words_at_pos)}")

        if words_at_pos:
            # Show top Sanskrit words
            sample = words_at_pos[:5]
            for w in sample:
                meanings_str = ", ".join(w["meanings"][:3]) if w["meanings"] else "?"
                print(f"       {w['sanskrit']:<20} → {meanings_str}")

        if all_meanings:
            print(f"     ALL MEANINGS ({len(all_meanings)}): {', '.join(all_meanings[:12])}")

        # Syllable-level vocabulary
        if syl_words:
            print(f"     SYLLABLE VOCABULARY:")
            for syl, data in syl_words.items():
                print(f"       {syl} (rama={data['rama_idx']}): {data['word_count']} words → {', '.join(data['sample_meanings'])}")

        print()


# =============================================================================
# PART 7: Shruti vs Nakshatra Distribution
# =============================================================================

def analyze_shruti_nakshatra() -> None:
    """
    Analyze which Guardians are Shruti (fixed points, R-reachable)
    and which are Nakshatra (journey points, non-residues).

    Shruti = quadratic residue mod 49 = "heard, revealed" = STABLE
    Nakshatra = non-residue = "star, waypoint" = DYNAMIC

    Connection to Venu Orchestration:
    - VENU (6 bits) = position-derived quality
    - VAMSI (9 bits) = name-derived process
    - MURALI (4 bits) = quarter-derived phase
    """
    print("=" * 70)
    print("PART 7: SHRUTI vs NAKSHATRA DISTRIBUTION")
    print("        Fixed Points vs Journey Points")
    print("=" * 70)
    print()

    shrutis = []
    nakshatras = []

    for i, name in enumerate(ALL_GUARDIANS):
        vib = compute_vibration_sum(name)
        m49 = vib % 49
        is_shruti = IS_SHRUTI[m49]
        phoneme = rama_to_phoneme(m49)
        harmonic = COORD_HARMONIC[m49]
        shastrisch = SHASTRISCH.get(name, "?")

        quarter = ["genesis", "dharma", "karma", "moksha"][i // 4]
        role = "HEAD" if i % 4 == 0 else f"worker-{i % 4}"

        entry = {
            "name": name, "pos": i, "m49": m49, "phoneme": phoneme,
            "harmonic": harmonic, "shastrisch": shastrisch,
            "quarter": quarter, "role": role,
        }

        if is_shruti:
            shrutis.append(entry)
        else:
            nakshatras.append(entry)

    print(f"  SHRUTI (fixed, stable, revealed): {len(shrutis)}/16")
    print(f"  NAKSHATRA (journey, dynamic, waypoint): {len(nakshatras)}/16")
    print()

    print("  --- SHRUTI GUARDIANS (R-reachable = v² mod 49) ---")
    for e in shrutis:
        print(f"    [{e['pos']:2d}] {e['name']:<14} mod49={e['m49']:>2} ({e['phoneme']}) "
              f"quarter={e['quarter']:<8} {e['shastrisch']}")
    print()

    print("  --- NAKSHATRA GUARDIANS (non-residue = journey) ---")
    for e in nakshatras:
        print(f"    [{e['pos']:2d}] {e['name']:<14} mod49={e['m49']:>2} ({e['phoneme']}) "
              f"quarter={e['quarter']:<8} {e['shastrisch']}")
    print()

    # Quarter distribution
    print("  QUARTER DISTRIBUTION:")
    for q in ["genesis", "dharma", "karma", "moksha"]:
        s_count = sum(1 for e in shrutis if e["quarter"] == q)
        n_count = sum(1 for e in nakshatras if e["quarter"] == q)
        print(f"    {q:<8}: {s_count} shruti, {n_count} nakshatra")
    print()

    # Venu connection: Shruti = sustained tones, Nakshatra = passing tones
    print("  VENU ORCHESTRATION MAPPING:")
    print("    Shruti Guardians = SUSTAINED TONES (drone, foundation)")
    print("    Nakshatra Guardians = MELODIC TONES (movement, expression)")
    print()
    print("    In a Raga:")
    print(f"      Vadi (main note):     Shruti Guardian with strongest resonance")
    print(f"      Samvadi (consonant):  Other Shruti Guardians")
    print(f"      Vivadi (dissonant):   Nakshatra Guardians (create tension/resolution)")
    print()


# =============================================================================
# PART 8: Harmonic Dissolution Paths
# =============================================================================

def analyze_dissolution_paths() -> None:
    """
    Each Guardian has a Harmonic coordinate = where it DISSOLVES to.
    Harmonic = (coord × SEVEN) mod 49.

    This creates a DISSOLUTION GRAPH:
    Guardian A dissolves to position X, which is Guardian B's position.
    → A feeds into B. A's energy transforms into B's function.
    """
    print("=" * 70)
    print("PART 8: HARMONIC DISSOLUTION PATHS")
    print("        Where does each Guardian's energy go?")
    print("=" * 70)
    print()

    # Build position → guardian map
    pos_to_guardian: Dict[int, str] = {}
    guardian_data = []

    for i, name in enumerate(ALL_GUARDIANS):
        vib = compute_vibration_sum(name)
        m49 = vib % 49
        harmonic = COORD_HARMONIC[m49]
        phoneme = rama_to_phoneme(m49)
        h_phoneme = rama_to_phoneme(harmonic)
        shastrisch = SHASTRISCH.get(name, "?")

        pos_to_guardian[m49] = name
        guardian_data.append({
            "name": name, "pos": i, "m49": m49, "harmonic": harmonic,
            "phoneme": phoneme, "h_phoneme": h_phoneme,
            "shastrisch": shastrisch,
        })

    print(f"  Dissolution = (mod49 × SEVEN) mod 49")
    print(f"  SEVEN = {SEVEN} (the absorption constant)")
    print()

    for g in guardian_data:
        target_name = pos_to_guardian.get(g["harmonic"], "---")
        target_shastrisch = SHASTRISCH.get(target_name, "?")
        arrow = f"→ {target_name}({target_shastrisch})" if target_name != "---" else f"→ position {g['harmonic']}"

        print(f"  [{g['pos']:2d}] {g['name']:<14} ({g['shastrisch']:<13}) "
              f"mod49={g['m49']:>2}({g['phoneme']}) "
              f"×7→{g['harmonic']:>2}({g['h_phoneme']}) {arrow}")

    # Find cycles
    print()
    print("  DISSOLUTION CYCLES:")
    visited = set()
    for g in guardian_data:
        if g["m49"] in visited:
            continue
        cycle = []
        current = g["m49"]
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = COORD_HARMONIC[current]
            if current == cycle[0]:
                cycle.append(current)
                break
        if len(cycle) > 1 and cycle[-1] == cycle[0]:
            names = [pos_to_guardian.get(p, f"pos{p}") for p in cycle]
            print(f"    CYCLE: {' → '.join(names)}")


# =============================================================================
# PART 9: Per-Syllable 4D Analysis
# =============================================================================

def analyze_per_syllable_4d() -> None:
    """
    Analyze each syllable of each Guardian through the full 4D Pancha Walk.
    Not just the whole-name mod49, but each syllable individually.
    """
    print()
    print("=" * 70)
    print("PART 9: PER-SYLLABLE 4D ANALYSIS")
    print("        Each syllable through Element/Varga/Sub/Harmonic")
    print("=" * 70)
    print()

    for i, name in enumerate(ALL_GUARDIANS):
        syllables = syllabify_sanskrit(name)
        shastrisch = SHASTRISCH.get(name, "?")

        print(f"[{i:2d}] {name.upper():<14} ({shastrisch})")

        element_sequence = []
        varga_sequence = []
        shruti_pattern = ""

        for syl in syllables:
            idx = syllable_to_rama_index(syl)
            if idx < 0 or idx >= 49:
                print(f"     {syl}: OUT OF RANGE ({idx})")
                continue

            elem = COORD_ELEMENT[idx]
            varga = COORD_VARGA[idx]
            sub = COORD_SUB[idx]
            harmonic = COORD_HARMONIC[idx]
            shruti = IS_SHRUTI[idx]
            phoneme = rama_to_phoneme(idx)
            elem_name = ELEMENT_NAMES[elem]

            element_sequence.append(elem_name)
            varga_sequence.append(["svara", "sparsha", "shesha"][varga])
            shruti_pattern += "S" if shruti else "N"

            print(f"     {syl:<6} rama={idx:>2} ({phoneme}) "
                  f"elem={elem_name:<8} varga={['svara','sparsha','shesha'][varga]:<8} "
                  f"sub={sub} harm={harmonic:>2} {'SHRUTI' if shruti else 'NAKSH'}")

        # Element walk summary
        if element_sequence:
            print(f"     ELEMENT WALK: {' → '.join(element_sequence)}")
            print(f"     VARGA WALK:   {' → '.join(varga_sequence)}")
            print(f"     SHRUTI/NAKSH: {shruti_pattern}")
        print()


# =============================================================================
# MAIN
# =============================================================================

def run_analysis() -> None:
    """Run all bridge analyses."""
    guardian_semantic_vocabulary()
    analyze_shruti_nakshatra()
    analyze_dissolution_paths()
    analyze_per_syllable_4d()


if __name__ == "__main__":
    run_analysis()
