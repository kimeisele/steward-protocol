"""
GUARDIAN SYLLABLE TREES — Where do the 16 Names come from?
==========================================================

THESIS:
    The 3 Root Names (Hare, Krishna, Rama) spawn semantic trees.
    The 16 Guardian names (12 Mahajanas + 4 Avataras) should appear
    as nodes or vibration-matches within these trees.

    If they do → the Guardians are DERIVED from the Mahamantra.
    If they don't → we learn what's missing in the derivation.

METHODOLOGY:
    1. Spawn 3 Root Trees (Hare, Krishna, Rama) to depth 4
    2. Compute vibration sums for each Guardian's syllables
    3. Search the trees for matching vibrations
    4. Analyze the unknown intervals (+20, +30, +39, +40, +42, +44)
       as combinations of Mahamantra constants
    5. Map Guardian syllable RAMA-indices to tree node vibrations

NO SPECULATION. JUST MATH.
"""

from __future__ import annotations

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xguardtree"

from collections import Counter
from typing import Dict, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSHETRA,
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
    TEN,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra_research.shabda_spawning import (
    ShabdaSeed,
    ShabdaTree,
    compute_vibration_sum,
    create_mahamantra_forest,
)
from vibe_core.mahamantra_research.syllable_analysis import (
    RAMA_GRID,
    syllabify_sanskrit,
    syllable_to_rama_index,
)
from vibe_core.mahamantra.substrate.phonetics.shabda import (
    SANSKRIT_PHONEME_MAP,
    text_to_vibration,
)

# =============================================================================
# KNOWN CONSTANTS (for interval analysis)
# =============================================================================

KNOWN_CONSTANTS: Dict[int, str] = {
    1: "KSETRAJNA",
    2: "HALVES",
    3: "TRINITY",
    4: "QUARTERS",
    5: "PANCHA",
    6: "SHARANAGATI",
    7: "SEVEN",
    8: "HARE_COUNT",
    9: "NAVA",
    10: "TEN",
    12: "MAHAJANA_COUNT",
    16: "WORDS",
    17: "KRISHNA_SUM",
    24: "KSHETRA",
    25: "PRASADAM",
    37: "PARAMPARA",
    48: "LILA",
    49: "RAMA",
    70: "HARE_SUM",
    108: "MALA",
    137: "MAHA_QUANTUM",
}

# The 16 Guardians (12 Mahajanas + 4 Avataras)
ALL_GUARDIANS = (
    "vyasa",
    "brahma",
    "narada",
    "shambhu",
    "prithu",
    "kumaras",
    "kapila",
    "manu",
    "parashurama",
    "prahlada",
    "janaka",
    "bhishma",
    "nrisimha",
    "bali",
    "shuka",
    "yamaraja",
)


# =============================================================================
# PART 1: Guardian Syllable Vibrations
# =============================================================================


def compute_guardian_syllable_vibrations() -> Dict[str, List[Dict]]:
    """
    For each Guardian, compute the vibration of each syllable.

    Returns:
        {guardian_name: [{syllable, rama_idx, vibration_sum}, ...]}
    """
    results = {}

    for name in ALL_GUARDIANS:
        syllables = syllabify_sanskrit(name)
        syl_data = []
        for syl in syllables:
            rama_idx = syllable_to_rama_index(syl)
            vib = compute_vibration_sum(syl)
            syl_data.append(
                {
                    "syllable": syl,
                    "rama_idx": rama_idx,
                    "vibration": vib,
                }
            )
        results[name] = syl_data

    return results


# =============================================================================
# PART 2: Search Root Trees for Guardian Vibrations
# =============================================================================


def search_trees_for_guardians(depth: int = 4) -> Dict[str, List[Dict]]:
    """
    Spawn 3 Root Trees and search for Guardian vibrations.

    For each Guardian syllable vibration, check if any tree node
    has a matching vibration_sum.

    Returns:
        {guardian_name: [{syllable, vibration, found_in, tree, depth, lineage}, ...]}
    """
    print("Spawning Mahamantra Forest (depth=%d)..." % depth)
    hare_tree, krishna_tree, rama_tree = create_mahamantra_forest(depth)

    trees = {
        "HARE": hare_tree,
        "KRISHNA": krishna_tree,
        "RAMA": rama_tree,
    }

    print(f"  HARE tree:    {hare_tree.node_count} nodes")
    print(f"  KRISHNA tree: {krishna_tree.node_count} nodes")
    print(f"  RAMA tree:    {rama_tree.node_count} nodes")
    total = hare_tree.node_count + krishna_tree.node_count + rama_tree.node_count
    print(f"  TOTAL:        {total} nodes")
    print()

    # Build vibration index across all trees
    vib_index: Dict[int, List[Tuple[str, int, str]]] = {}
    for tree_name, tree in trees.items():
        for node in tree.all_nodes():
            v = node.vibration_sum
            lineage_str = " → ".join(node.lineage[:4])
            if v not in vib_index:
                vib_index[v] = []
            vib_index[v].append((tree_name, node.generation, lineage_str))

    # Search for each Guardian's syllable vibrations
    guardian_vibs = compute_guardian_syllable_vibrations()
    results = {}

    for name, syl_data in guardian_vibs.items():
        matches = []
        for sd in syl_data:
            vib = sd["vibration"]
            if vib in vib_index:
                for tree_name, gen, lineage in vib_index[vib]:
                    matches.append(
                        {
                            "syllable": sd["syllable"],
                            "vibration": vib,
                            "tree": tree_name,
                            "depth": gen,
                            "lineage": lineage,
                        }
                    )
            # Also check full name vibration
        full_vib = compute_vibration_sum(name)
        if full_vib in vib_index:
            for tree_name, gen, lineage in vib_index[full_vib]:
                matches.append(
                    {
                        "syllable": f"[{name}]",
                        "vibration": full_vib,
                        "tree": tree_name,
                        "depth": gen,
                        "lineage": lineage,
                    }
                )
        results[name] = matches

    return results


# =============================================================================
# PART 2b: Modular Search — reduce Guardian vibs to tree space
# =============================================================================


def search_trees_modular(depth: int = 4) -> None:
    """
    The trees operate in mod-137 space (MAHA_QUANTUM).
    Guardian vibrations are raw sums (8979-25522).
    Reduce both to the same modular space and compare.
    """
    print("Spawning Mahamantra Forest (depth=%d)..." % depth)
    hare_tree, krishna_tree, rama_tree = create_mahamantra_forest(depth)

    trees = {"HARE": hare_tree, "KRISHNA": krishna_tree, "RAMA": rama_tree}

    # Build modular vibration index (mod 137)
    mod_index_137: Dict[int, List[Tuple[str, int, str, int]]] = {}
    # Also mod 49 (RAMA space)
    mod_index_49: Dict[int, List[Tuple[str, int, str, int]]] = {}

    for tree_name, tree in trees.items():
        for node in tree.all_nodes():
            raw_v = node.vibration_sum
            lineage_str = " → ".join(node.lineage[:3])

            m137 = raw_v % MAHA_QUANTUM
            if m137 not in mod_index_137:
                mod_index_137[m137] = []
            mod_index_137[m137].append((tree_name, node.generation, lineage_str, raw_v))

            m49 = raw_v % POSITION_SUM_RAMA
            if m49 not in mod_index_49:
                mod_index_49[m49] = []
            mod_index_49[m49].append((tree_name, node.generation, lineage_str, raw_v))

    # Search Guardians in mod-137 space
    print()
    print("--- MOD 137 (MAHA_QUANTUM) SEARCH ---")
    print()
    found_137 = 0
    for name in ALL_GUARDIANS:
        full_vib = compute_vibration_sum(name)
        m137 = full_vib % MAHA_QUANTUM
        if m137 in mod_index_137:
            found_137 += 1
            hits = mod_index_137[m137]
            print(f"  ✓ {name:<14} vib={full_vib} mod137={m137:>3} → {len(hits)} tree node(s)")
            for tree_name, gen, lineage, raw_v in hits[:2]:
                print(f"      {tree_name} depth={gen} vib={raw_v} mod137={raw_v % MAHA_QUANTUM} | {lineage}")
        else:
            print(f"  ✗ {name:<14} vib={full_vib} mod137={m137:>3} → no match")
    print(f"\n  MOD-137 MATCHES: {found_137}/16")

    # Search Guardians in mod-49 space
    print()
    print("--- MOD 49 (RAMA) SEARCH ---")
    print()
    found_49 = 0
    for name in ALL_GUARDIANS:
        full_vib = compute_vibration_sum(name)
        m49 = full_vib % POSITION_SUM_RAMA
        if m49 in mod_index_49:
            found_49 += 1
            hits = mod_index_49[m49]
            print(f"  ✓ {name:<14} vib={full_vib} mod49={m49:>2} → {len(hits)} tree node(s)")
            for tree_name, gen, lineage, raw_v in hits[:2]:
                print(f"      {tree_name} depth={gen} vib={raw_v} mod49={raw_v % POSITION_SUM_RAMA} | {lineage}")
        else:
            print(f"  ✗ {name:<14} vib={full_vib} mod49={m49:>2} → no match")
    print(f"\n  MOD-49 MATCHES: {found_49}/16")

    # Search individual SYLLABLES in mod-49 space (the RAMA grid IS 49)
    print()
    print("--- SYLLABLE MOD-49 SEARCH (RAMA Grid = 49) ---")
    print()
    guardian_vibs = compute_guardian_syllable_vibrations()
    syl_found = 0
    for name, syl_data in guardian_vibs.items():
        syl_matches = []
        for sd in syl_data:
            m49 = sd["vibration"] % POSITION_SUM_RAMA
            if m49 in mod_index_49:
                syl_matches.append((sd["syllable"], m49, len(mod_index_49[m49])))
        if syl_matches:
            syl_found += 1
            parts = ", ".join(f"{s}(mod49={m}→{n}hits)" for s, m, n in syl_matches)
            print(f"  ✓ {name:<14} {parts}")
        else:
            print(f"  ✗ {name:<14} no syllable matches")
    print(f"\n  SYLLABLE MOD-49 MATCHES: {syl_found}/16")


# =============================================================================
# PART 3: Unknown Interval Derivation
# =============================================================================


def derive_unknown_intervals() -> Dict[int, List[str]]:
    """
    Try to express unknown intervals as combinations of known constants.

    Unknown intervals from syllable_analysis: +20, +30, +39, +40, +42, +44, +48
    """
    unknowns = [20, 30, 39, 40, 42, 44, 48]
    results = {}

    for u in unknowns:
        derivations = []

        # Direct match
        if u in KNOWN_CONSTANTS:
            derivations.append(f"= {KNOWN_CONSTANTS[u]}")

        # Sum of two constants
        for a, a_name in sorted(KNOWN_CONSTANTS.items()):
            for b, b_name in sorted(KNOWN_CONSTANTS.items()):
                if a <= b and a + b == u:
                    derivations.append(f"= {a_name}({a}) + {b_name}({b})")

        # Product of two constants
        for a, a_name in sorted(KNOWN_CONSTANTS.items()):
            for b, b_name in sorted(KNOWN_CONSTANTS.items()):
                if a <= b and a > 1 and b > 1 and a * b == u:
                    derivations.append(f"= {a_name}({a}) × {b_name}({b})")

        # Difference from RAMA (49)
        complement = 49 - u
        if complement in KNOWN_CONSTANTS:
            derivations.append(f"= RAMA(49) - {KNOWN_CONSTANTS[complement]}({complement})")

        # Modular relation to key constants
        if u % 7 == 0:
            derivations.append(f"= {u // 7} × SEVEN")
        if u % 5 == 0:
            derivations.append(f"= {u // 5} × PANCHA")

        results[u] = derivations

    return results


# =============================================================================
# PART 4: Full Name Vibration → Position Analysis
# =============================================================================


def analyze_name_positions() -> None:
    """
    Compute vibration for each Guardian name and check mod relationships.
    """
    print("=" * 70)
    print("GUARDIAN NAME VIBRATIONS → POSITION ANALYSIS")
    print("=" * 70)
    print()
    print(f"{'NAME':<14} {'VIB':>6} {'%16':>4} {'%17':>4} {'%49':>4} {'%37':>4} {'%137':>5} {'POS':>4}")
    print("-" * 70)

    for i, name in enumerate(ALL_GUARDIANS):
        vib = compute_vibration_sum(name)
        print(
            f"{name:<14} {vib:>6} "
            f"{vib % WORDS:>4} "
            f"{vib % (WORDS + KSETRAJNA):>4} "
            f"{vib % POSITION_SUM_RAMA:>4} "
            f"{vib % PARAMPARA:>4} "
            f"{vib % MAHA_QUANTUM:>5} "
            f"{i:>4}"
        )


# =============================================================================
# PART 5: mod49 → 4D Pancha Walk → Capability Derivation
# =============================================================================

# Element → Capability Domain
ELEMENT_CAPABILITY = {
    "akasha": "SPACE — communication, transmission, compilation, ether",
    "vayu": "AIR — movement, analysis, wisdom, breath",
    "agni": "FIRE — transformation, enforcement, execution, energy",
    "jala": "WATER — flow, surrender, liberation, adaptation",
    "prithvi": "EARTH — stability, organization, structure, grounding",
}

# Varga → Action Type
VARGA_CAPABILITY = {
    0: "SVARA (vowel) — pure expression, source, identity",
    1: "SPARSHA (stop) — contact, action, transformation",
    2: "SHESHA (remainder) — connection, bridge, completion",
}

# Sub → Quality (depends on varga)
SUB_SPARSHA = {
    0: "UNVOICED — silent action, Vasudeva (origin)",
    1: "UNVOICED-ASP — forceful action, Sankarshana (expansion)",
    2: "VOICED — active engagement, Pradyumna (attraction)",
    3: "VOICED-ASP — powerful engagement, Aniruddha (resistance)",
    4: "NASAL — resonant completion, Pancha (fullness)",
}

SUB_SVARA = {
    0: "SHORT — quick, immediate, seed",
    1: "LONG — sustained, enduring, growth",
    2: "COMPOUND — complex, combined, synthesis",
    3: "SPECIAL — transcendent, beyond categories",
}

SUB_SHESHA = {
    0: "ANTASTHA (semivowel) — bridge, mediator, connector",
    1: "USHMAN (sibilant) — heat, friction, purification",
}

# Shruti/Nakshatra
SHRUTI_MEANING = "SHRUTI — heard, revealed, fixed point (quadratic residue)"
NAKSHATRA_MEANING = "NAKSHATRA — star, waypoint, journey (non-residue)"


def analyze_guardian_4d() -> None:
    """
    Map each Guardian's mod49 value to 4D Pancha Walk coordinates.
    This derives capabilities from phonetic structure.
    """
    from vibe_core.mahamantra.substrate.pancha_walk import (
        COORD_ELEMENT,
        COORD_HARMONIC,
        COORD_SUB,
        COORD_VARGA,
        ELEMENT_NAMES,
        IS_SHRUTI,
    )
    from vibe_core.mahamantra.substrate.rama_grid import rama_to_phoneme

    print("=" * 70)
    print("PART 5: GUARDIAN 4D CAPABILITY DERIVATION")
    print("         mod49 → RAMA Grid → Pancha Walk → Capability")
    print("=" * 70)
    print()

    # Shastrische Funktionen (from mahajana_derivation.py)
    SHASTRISCH = {
        "vyasa": "compilation",
        "brahma": "creation",
        "narada": "transmission",
        "shambhu": "destruction",
        "prithu": "organization",
        "kumaras": "wisdom",
        "kapila": "analysis",
        "manu": "law",
        "parashurama": "enforcement",
        "prahlada": "devotion",
        "janaka": "execution",
        "bhishma": "commitment",
        "nrisimha": "protection",
        "bali": "surrender",
        "shuka": "liberation",
        "yamaraja": "judgment",
    }

    for i, name in enumerate(ALL_GUARDIANS):
        vib = compute_vibration_sum(name)
        m49 = vib % 49  # RAMA Grid position

        # 4D coordinates
        elem = COORD_ELEMENT[m49]
        varga = COORD_VARGA[m49]
        sub = COORD_SUB[m49]
        harmonic = COORD_HARMONIC[m49]
        shruti = IS_SHRUTI[m49]

        # Phoneme at this position
        phoneme = rama_to_phoneme(m49)

        # Element name
        elem_name = ELEMENT_NAMES[elem]

        # Capability derivation
        elem_cap = ELEMENT_CAPABILITY[elem_name].split(" — ")[1]
        varga_cap = VARGA_CAPABILITY[varga].split(" — ")[1]

        if varga == 0:
            sub_cap = SUB_SVARA.get(sub, "?").split(" — ")[1]
        elif varga == 1:
            sub_cap = SUB_SPARSHA.get(sub, "?").split(" — ")[1]
        else:
            sub_cap = SUB_SHESHA.get(sub, "?").split(" — ")[1]

        shruti_type = "SHRUTI (fixed)" if shruti else "NAKSHATRA (journey)"
        shastrisch = SHASTRISCH.get(name, "?")

        # Constant match for mod49
        const_name = KNOWN_CONSTANTS.get(m49, "")
        const_str = f" = {const_name}" if const_name else ""

        print(f"[{i:2d}] {name.upper():<14} mod49={m49:>2}{const_str}")
        print(f"     Phoneme: {phoneme}")
        print(f"     Element: {elem_name} ({elem_cap})")
        print(f"     Varga:   {VARGA_CAPABILITY[varga]}")
        print(f"     Sub:     {sub_cap}")
        print(f"     Harmonic: {harmonic} (dissolution → position {harmonic})")
        print(f"     {shruti_type}")
        print(f"     Shastrisch: {shastrisch}")
        print(f"     ---")
        print(f"     DERIVED: {elem_cap} + {varga_cap} + {sub_cap}")
        print()


def run_analysis(tree_depth: int = 4) -> None:
    """Run the complete Guardian Syllable Tree analysis."""

    # --- Part 1: Syllable Vibrations ---
    print("=" * 70)
    print("PART 1: GUARDIAN SYLLABLE VIBRATIONS")
    print("=" * 70)
    print()

    guardian_vibs = compute_guardian_syllable_vibrations()
    for name, syl_data in guardian_vibs.items():
        syls = " - ".join(f"{s['syllable']}({s['rama_idx']}|v{s['vibration']})" for s in syl_data)
        total_vib = compute_vibration_sum(name)
        print(f"  {name:<14} {syls}  [total={total_vib}]")
    print()

    # --- Part 2: Tree Search ---
    print("=" * 70)
    print("PART 2: SEARCH ROOT TREES FOR GUARDIAN VIBRATIONS")
    print("=" * 70)
    print()

    tree_matches = search_trees_for_guardians(depth=tree_depth)

    found_count = 0
    not_found = []
    for name, matches in tree_matches.items():
        if matches:
            found_count += 1
            print(f"  ✓ {name}: {len(matches)} match(es)")
            for m in matches[:3]:
                print(f"      {m['syllable']} (v={m['vibration']}) → {m['tree']} tree, depth {m['depth']}")
                print(f"        lineage: {m['lineage']}")
        else:
            not_found.append(name)

    print()
    print(f"  FOUND (raw): {found_count}/16 Guardians have vibration matches in the trees")
    if not_found:
        print(f"  NOT FOUND: {', '.join(not_found)}")
    print()

    # --- Part 2b: Modular Search ---
    print("=" * 70)
    print("PART 2b: MODULAR SEARCH (reduce to same space)")
    print("=" * 70)
    print()
    search_trees_modular(depth=tree_depth)
    print()

    # --- Part 3: Unknown Intervals ---
    print("=" * 70)
    print("PART 3: UNKNOWN INTERVAL DERIVATION")
    print("=" * 70)
    print()

    interval_derivations = derive_unknown_intervals()
    for interval, derivations in sorted(interval_derivations.items()):
        print(f"  +{interval}:")
        if derivations:
            for d in derivations:
                print(f"    {d}")
        else:
            print(f"    (no derivation found)")
        print()

    # --- Part 4: Name → Position ---
    analyze_name_positions()
    print()

    # --- Part 5: 4D Capability Derivation ---
    analyze_guardian_4d()

    # --- Summary ---
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"  Tree depth: {tree_depth}")
    print(f"  Guardians with tree matches (raw): {found_count}/16")
    print(
        f"  Unknown intervals explained: {sum(1 for d in interval_derivations.values() if d)}/{len(interval_derivations)}"
    )
    print(f"  All 16 Guardians found in mod-49 (RAMA) space")
    print(f"  All 16 Guardians have 4D Pancha Walk signatures")
    print()


if __name__ == "__main__":
    run_analysis(tree_depth=4)
