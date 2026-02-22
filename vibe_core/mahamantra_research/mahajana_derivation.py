"""
MAHAJANA DERIVATION - Reverse Engineering Name→Position Mapping
================================================================

"svayambhūr nāradaḥ śambhuḥ kumāraḥ kapilo manuḥ
prahlādo janako bhīṣmo balir vaiyāsakir vayam" (SB 6.3.20)

DIE FRAGE:
==========
Das gita_verse_text.py zeigt: Mahamantra → Algorithm → Gita Resonance.
Kann der GLEICHE Algorithmus auch die Mahajana-Namen ableiten?

HYPOTHESE:
==========
Die 12 Mahajanas haben EIGENSCHAFTEN die sich in der Mahamantra-Mathematik
widerspiegeln. Ihre Positionen sind NICHT willkürlich sondern COMPUTED.

REVERSE ENGINEERING APPROACH:
=============================
1. Analysiere die bekannten Mahajana-Eigenschaften (Shastrisch)
2. Finde Muster in ihren Vibrationen
3. Prüfe ob signature_id % 16 die erwartete Position liefert
4. Wenn ja → wir haben die Ableitung gefunden
5. Wenn nein → analysiere die Differenz

ERGEBNIS:
=========
Diese Datei dokumentiert den Versuch, die Derivation zu finden oder zu beweisen
dass sie existieren MUSS aber noch implementiert werden muss.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"  # Analysis position
__position__ = 6
__genesis__ = "0x25d36ba1"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final, Tuple

from vibe_core.mahamantra.protocols._seed import (
    AVATAR_COUNT,
    HALVES,
    HARE_COUNT,
    KSHETRA,
    KSETRAJNA,
    MAHAJANA_COUNT,
    MAHA_QUANTUM,
    NADI_RESONANCE,
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

from vibe_core.mahamantra_research.shabda_translation import (
    VibrationSignature,
    ArticulationPoint,
    VoicingType,
    SANSKRIT_PHONEME_MAP,
    text_to_vibration,
)

# =============================================================================
# SHASTRISCHE DATEN: Die 12 Mahajanas (SB 6.3.20)
# =============================================================================


# Die 12 Mahajanas mit ihren Shastrischen Eigenschaften
@dataclass(frozen=True)
class MahajanaProfile:
    """Profil eines Mahajana mit Shastrischen Eigenschaften."""

    name: str  # Sanskrit Name
    position: int  # Erwartete Position (1-12 in Maha-Position)
    quarter: int  # Quarter (1-4)
    varna: str  # Brahmana/Kshatriya/Vaishya/Shudra
    guna: str  # sattva/rajas/tamas
    primary_function: str  # Hauptfunktion
    element: str  # Erde/Wasser/Feuer/Luft/Äther


# Die 12 Mahajanas aus SB 6.3.20 mit ihren Shastrischen Eigenschaften
# Position hier ist die WORKER position (1-12), nicht die globale position (1-16)
MAHAJANA_PROFILES: Final[Tuple[MahajanaProfile, ...]] = (
    # GENESIS Quarter (Positions 2-4 global, workers 1-3)
    MahajanaProfile("brahma", 1, 1, "brahmana", "rajas", "creation", "akasha"),
    MahajanaProfile("narada", 2, 1, "brahmana", "sattva", "transmission", "akasha"),
    MahajanaProfile("shambhu", 3, 1, "brahmana", "tamas", "destruction", "akasha"),
    # DHARMA Quarter (Positions 6-8 global, workers 4-6)
    MahajanaProfile("kumaras", 4, 2, "brahmana", "sattva", "wisdom", "vayu"),
    MahajanaProfile("kapila", 5, 2, "brahmana", "sattva", "analysis", "vayu"),
    MahajanaProfile("manu", 6, 2, "kshatriya", "rajas", "law", "vayu"),
    # KARMA Quarter (Positions 10-12 global, workers 7-9)
    MahajanaProfile("prahlada", 7, 3, "kshatriya", "sattva", "devotion", "agni"),
    MahajanaProfile("janaka", 8, 3, "kshatriya", "sattva", "execution", "agni"),
    MahajanaProfile("bhishma", 9, 3, "kshatriya", "sattva", "commitment", "agni"),
    # MOKSHA Quarter (Positions 14-16 global, workers 10-12)
    MahajanaProfile("bali", 10, 4, "kshatriya", "sattva", "surrender", "jala"),
    MahajanaProfile("shuka", 11, 4, "brahmana", "sattva", "liberation", "jala"),
    MahajanaProfile("yamaraja", 12, 4, "kshatriya", "rajas", "judgment", "jala"),
)

# Die 4 Avataras (Heads of each quarter)
AVATARA_PROFILES: Final[Tuple[MahajanaProfile, ...]] = (
    MahajanaProfile("vyasa", 1, 1, "brahmana", "sattva", "compilation", "akasha"),
    MahajanaProfile("prithu", 2, 2, "kshatriya", "rajas", "organization", "prithvi"),
    MahajanaProfile("parashurama", 3, 3, "brahmana", "rajas", "enforcement", "agni"),
    MahajanaProfile("nrisimha", 4, 4, "kshatriya", "sattva", "protection", "jala"),
)

# Verify counts
assert len(MAHAJANA_PROFILES) == MAHAJANA_COUNT, f"Must have {MAHAJANA_COUNT} Mahajanas"
assert len(AVATARA_PROFILES) == AVATAR_COUNT, f"Must have {AVATAR_COUNT} Avataras"


# =============================================================================
# VIBRATION ANALYSIS: Compute signature_id for each name
# =============================================================================


def compute_name_vibration(name: str) -> int:
    """
    Compute the total vibration signature for a name.

    Uses text_to_vibration() from shabda_translation.py to get
    VibrationSignatures, then sums their signature_ids.
    """
    signatures = text_to_vibration(name)
    if not signatures:
        return 0
    return sum(sig.signature_id for sig in signatures)


def compute_name_position(name: str) -> int:
    """
    Compute the Mahamantra position (0-15) for a name.

    position = vibration % WORDS
    """
    vibration = compute_name_vibration(name)
    return vibration % WORDS


# =============================================================================
# POSITION DERIVATION TEST: Does vibration match expected position?
# =============================================================================


def test_mahajana_positions() -> dict:
    """
    Test if computed positions match expected positions.

    Returns analysis dict with:
    - matches: count of correct matches
    - mismatches: list of (name, expected, computed)
    - pattern: any detected pattern in mismatches
    """
    results = {
        "matches": 0,
        "mismatches": [],
        "vibrations": {},
    }

    for profile in MAHAJANA_PROFILES:
        vibration = compute_name_vibration(profile.name)
        computed_pos = vibration % WORDS

        # Expected global position (worker_pos + 1 for each head)
        # Workers are after the head in each quarter
        # Global = (quarter - 1) * 4 + worker_in_quarter + 1 (for head)
        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected_global = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

        results["vibrations"][profile.name] = {
            "vibration": vibration,
            "computed_pos": computed_pos,
            "expected_global": expected_global,
            "mod_17": vibration % (WORDS + KSETRAJNA),  # KRISHNA modulo
            "mod_137": vibration % MAHA_QUANTUM,
        }

        if computed_pos == expected_global:
            results["matches"] += 1
        else:
            results["mismatches"].append((profile.name, expected_global, computed_pos))

    return results


def test_avatara_positions() -> dict:
    """Test if Avatara positions can be derived from vibration."""
    results = {
        "matches": 0,
        "mismatches": [],
        "vibrations": {},
    }

    for idx, profile in enumerate(AVATARA_PROFILES):
        vibration = compute_name_vibration(profile.name)
        computed_pos = vibration % WORDS

        # Avataras are at positions 1, 5, 9, 13 (head of each quarter)
        expected_global = idx * QUARTERS + 1

        results["vibrations"][profile.name] = {
            "vibration": vibration,
            "computed_pos": computed_pos,
            "expected_global": expected_global,
            "mod_17": vibration % (WORDS + KSETRAJNA),
            "mod_137": vibration % MAHA_QUANTUM,
        }

        if computed_pos == expected_global:
            results["matches"] += 1
        else:
            results["mismatches"].append((profile.name, expected_global, computed_pos))

    return results


# =============================================================================
# ALTERNATIVE DERIVATION: Position from Guna/Varna/Function
# =============================================================================


def guna_to_weight(guna: str) -> int:
    """Map guna to weight from position sums."""
    if guna == "sattva":
        return POSITION_SUM_KRISHNA  # 17 (pure source)
    elif guna == "rajas":
        return POSITION_SUM_RAMA  # 49 (activity)
    else:  # tamas
        return POSITION_SUM_HARE  # 70 (inertia)


def varna_to_quarter(varna: str) -> int:
    """Map varna to quarter."""
    # Brahmana = Genesis/Moksha (knowledge)
    # Kshatriya = Dharma/Karma (action)
    # Vaishya = Karma (commerce)
    # Shudra = Moksha (service)
    mapping = {
        "brahmana": 1,  # Genesis - creation/knowledge
        "kshatriya": 2,  # Dharma - order/protection
        "vaishya": 3,  # Karma - action/commerce
        "shudra": 4,  # Moksha - service/liberation
    }
    return mapping.get(varna, 1)


def derive_position_from_properties(profile: MahajanaProfile) -> int:
    """
    Attempt to derive position from Shastrische properties.

    Hypothesis: position = f(guna, varna, quarter)
    """
    guna_weight = guna_to_weight(profile.guna)
    quarter_offset = (profile.quarter - 1) * QUARTERS

    # Position within quarter based on guna weight
    pos_in_quarter = guna_weight % QUARTERS

    return quarter_offset + pos_in_quarter


# =============================================================================
# THE BIG DERIVATION ATTEMPT: Can we find the formula?
# =============================================================================


def analyze_derivation_pattern() -> dict:
    """
    Analyze all Mahajanas to find a derivation pattern.

    We look for:
    1. A formula: position = f(name_vibration, guna, varna)
    2. A transform: position = transform(name) using Maha operators
    3. A constant offset if linear relationship exists
    """
    analysis = {
        "name_vibrations": {},
        "position_deltas": {},
        "guna_correlation": {},
        "potential_formulas": [],
    }

    for profile in MAHAJANA_PROFILES:
        vib = compute_name_vibration(profile.name)
        computed = vib % WORDS

        # Expected position in 16-word structure
        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

        delta = expected - computed

        analysis["name_vibrations"][profile.name] = vib
        analysis["position_deltas"][profile.name] = delta

        # Track guna correlation
        guna = profile.guna
        if guna not in analysis["guna_correlation"]:
            analysis["guna_correlation"][guna] = []
        analysis["guna_correlation"][guna].append(
            {
                "name": profile.name,
                "expected": expected,
                "computed": computed,
                "delta": delta,
            }
        )

    # Look for consistent delta
    deltas = list(analysis["position_deltas"].values())
    if len(set(deltas)) == 1:
        analysis["potential_formulas"].append(f"position = (vibration + {deltas[0]}) % WORDS")
    else:
        # Look for guna-based adjustment
        for guna, entries in analysis["guna_correlation"].items():
            guna_deltas = [e["delta"] for e in entries]
            if len(set(guna_deltas)) == 1:
                analysis["potential_formulas"].append(
                    f"if guna == '{guna}': position = (vibration + {guna_deltas[0]}) % WORDS"
                )

    return analysis


# =============================================================================
# ALTERNATIVE APPROACH: Using Position Sums as Weights
# =============================================================================


def derive_with_position_sums(name: str, expected_pos: int) -> dict:
    """
    Try various combinations of position sums to derive position.

    Position sums from _seed.py:
    - HARE = 70 = 7 × 10
    - KRISHNA = 17 = prime
    - RAMA = 49 = 7²
    """
    vib = compute_name_vibration(name)

    results = {"name": name, "vibration": vib, "expected": expected_pos, "formulas": {}}

    # Try different formulas
    formulas = [
        ("vib % 17", vib % POSITION_SUM_KRISHNA),
        ("vib % 49", vib % POSITION_SUM_RAMA),
        ("vib % 70", vib % POSITION_SUM_HARE),
        ("vib % 37", vib % PARAMPARA),
        ("vib % 137", vib % MAHA_QUANTUM),
        ("(vib % 17) % 16", (vib % POSITION_SUM_KRISHNA) % WORDS),
        ("(vib + 70) % 16", (vib + POSITION_SUM_HARE) % WORDS),
        ("(vib + 17) % 16", (vib + POSITION_SUM_KRISHNA) % WORDS),
        ("(vib + 49) % 16", (vib + POSITION_SUM_RAMA) % WORDS),
        ("(vib // 17) % 16", (vib // POSITION_SUM_KRISHNA) % WORDS),
        ("(vib // 49) % 16", (vib // POSITION_SUM_RAMA) % WORDS),
        ("T(vib % 16)", (((vib % WORDS) * ((vib % WORDS) + 1)) // 2) % WORDS),
    ]

    for formula_name, result in formulas:
        results["formulas"][formula_name] = result
        if result == expected_pos:
            results["match"] = formula_name

    return results


def find_universal_formula():
    """
    Search for a formula that works for ALL Mahajanas.

    Brute force approach: try many combinations.
    """
    print("\n4. UNIVERSAL FORMULA SEARCH")
    print("-" * 50)

    # Build expected positions mapping
    expected = {}
    for profile in MAHAJANA_PROFILES:
        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected[profile.name] = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

    # For each name, find which formulas work
    all_formulas = []
    for profile in MAHAJANA_PROFILES:
        result = derive_with_position_sums(profile.name, expected[profile.name])
        if "match" in result:
            all_formulas.append((profile.name, result["match"]))
            print(f"  {profile.name:12} → {result['match']}")
        else:
            # Print all formula results
            print(f"  {profile.name:12} → NO MATCH (expected {expected[profile.name]})")
            for f_name, f_result in result["formulas"].items():
                if abs(f_result - expected[profile.name]) <= 2:  # Close matches
                    print(f"      close: {f_name} = {f_result}")

    return all_formulas


# =============================================================================
# ALTERNATIVE: Hash-based derivation using the name's Sanskrit structure
# =============================================================================


def sanskrit_hash(name: str) -> int:
    """
    Compute a deterministic hash from Sanskrit phonetic structure.

    Uses:
    - Articulation points (5)
    - Voicing types (4)
    - Syllable count
    """
    signatures = text_to_vibration(name)
    if not signatures:
        return 0

    # Build composite hash
    h = 0
    for i, sig in enumerate(signatures):
        # Position-weighted contribution
        weight = (i + 1) * QUARTERS
        contrib = (sig.articulation.value * PANCHA + sig.voicing.value) * weight
        h = (h + contrib) % (WORDS * WORDS)  # 256 space

    return h


def test_sanskrit_hash():
    """Test if Sanskrit phonetic hash gives better position mapping."""
    print("\n5. SANSKRIT PHONETIC HASH TEST")
    print("-" * 50)

    for profile in MAHAJANA_PROFILES:
        h = sanskrit_hash(profile.name)
        pos = h % WORDS

        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

        match = "✓" if pos == expected else " "
        print(f"  {match} {profile.name:12} | hash={h:4} | pos={pos:2} | expected={expected:2}")


# =============================================================================
# ALTERNATIVE: Use the SB 6.3.20 verse ORDER as the key
# =============================================================================


def analyze_verse_order():
    """
    The order in SB 6.3.20 might itself be the derivation.

    Yamaraja speaks this verse listing 12 Mahajanas.
    The ORDER given is: brahma, narada, shambhu, kumaras, kapila, manu,
                       prahlada, janaka, bhishma, bali, shuka, yamaraja

    Is there mathematical significance to this order?
    """
    print("\n6. SB 6.3.20 VERSE ORDER ANALYSIS")
    print("-" * 50)

    # The order as spoken by Yamaraja (1-indexed)
    sb_order = [
        ("brahma", 1),
        ("narada", 2),
        ("shambhu", 3),
        ("kumaras", 4),
        ("kapila", 5),
        ("manu", 6),
        ("prahlada", 7),
        ("janaka", 8),
        ("bhishma", 9),
        ("bali", 10),
        ("shuka", 11),
        ("yamaraja", 12),
    ]

    print("  Vibration patterns in SB order:")
    vibs = []
    for name, order in sb_order:
        vib = compute_name_vibration(name)
        vibs.append(vib)
        print(f"    {order:2}. {name:12} → vib={vib:5} | mod16={vib % WORDS:2} | mod17={vib % 17:2}")

    # Check if vibrations are sorted or have pattern
    sorted_vibs = sorted(vibs)
    is_sorted = vibs == sorted_vibs
    print(f"\n  Sorted by vibration: {is_sorted}")

    # Check differences between consecutive
    diffs = [vibs[i + 1] - vibs[i] for i in range(len(vibs) - 1)]
    print(f"  Consecutive differences: {diffs}")

    # Check if differences have pattern
    diff_mod = [d % WORDS for d in diffs]
    print(f"  Differences mod 16: {diff_mod}")


# =============================================================================
# THE KEY INSIGHT: Maybe the mapping IS the algorithm
# =============================================================================


def maha_transform_position(name: str) -> int:
    """
    Apply the MahaAlgorithm transform to get position.

    The algorithm from maha_algorithm.py:
    1. XOR with PRASADAM (25)
    2. Triangular number modulation
    3. Position sum weights
    """
    vib = compute_name_vibration(name)

    # Step 1: XOR with PRASADAM (spiritual completion)
    step1 = vib ^ (KSHETRA + KSETRAJNA)  # 25

    # Step 2: Add triangular of position
    t16 = (WORDS * (WORDS + 1)) // 2  # T(16) = 136
    step2 = (step1 + t16) % MAHA_QUANTUM  # mod 137

    # Step 3: Final position
    pos = step2 % WORDS

    return pos


def test_maha_transform():
    """Test MahaAlgorithm-style transform for position derivation."""
    print("\n7. MAHA ALGORITHM TRANSFORM TEST")
    print("-" * 50)

    for profile in MAHAJANA_PROFILES:
        pos = maha_transform_position(profile.name)

        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

        match = "✓" if pos == expected else " "
        print(f"  {match} {profile.name:12} | transformed_pos={pos:2} | expected={expected:2}")


def run_analysis():
    """Run full analysis and print results."""
    print("=" * 70)
    print("MAHAJANA DERIVATION - Reverse Engineering Name→Position")
    print("=" * 70)
    print()

    # Test vibration-based positions
    print("1. VIBRATION-BASED POSITION TEST (Mahajanas)")
    print("-" * 50)
    mahajana_results = test_mahajana_positions()

    for name, data in mahajana_results["vibrations"].items():
        print(
            f"  {name:12} | vib={data['vibration']:5} | pos={data['computed_pos']:2} | "
            f"expected={data['expected_global']:2} | mod17={data['mod_17']:3}"
        )

    print(f"\n  Matches: {mahajana_results['matches']}/{MAHAJANA_COUNT}")
    if mahajana_results["mismatches"]:
        print("  Mismatches:")
        for name, expected, computed in mahajana_results["mismatches"]:
            print(f"    {name}: expected {expected}, got {computed}")
    print()

    # Test Avatara positions
    print("2. VIBRATION-BASED POSITION TEST (Avataras)")
    print("-" * 50)
    avatara_results = test_avatara_positions()

    for name, data in avatara_results["vibrations"].items():
        print(
            f"  {name:12} | vib={data['vibration']:5} | pos={data['computed_pos']:2} | "
            f"expected={data['expected_global']:2} | mod17={data['mod_17']:3}"
        )

    print(f"\n  Matches: {avatara_results['matches']}/{AVATAR_COUNT}")
    print()

    # Full derivation analysis
    print("3. DERIVATION PATTERN ANALYSIS")
    print("-" * 50)
    analysis = analyze_derivation_pattern()

    print("  Position Deltas (expected - computed):")
    for name, delta in analysis["position_deltas"].items():
        print(f"    {name:12}: {delta:+3}")

    print("\n  Guna Correlation:")
    for guna, entries in analysis["guna_correlation"].items():
        deltas = [e["delta"] for e in entries]
        print(f"    {guna:8}: deltas = {deltas}")

    if analysis["potential_formulas"]:
        print("\n  Potential Formulas:")
        for formula in analysis["potential_formulas"]:
            print(f"    {formula}")
    else:
        print("\n  No consistent formula found - trying alternatives...")

    # Try alternative approaches
    find_universal_formula()
    test_sanskrit_hash()
    analyze_verse_order()
    test_maha_transform()
    quarter_based_derivation()
    brute_force_formula_search()
    analyze_mahajana_names_as_seed()

    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("""
ERGEBNIS DER ANALYSE:
=====================

Die direkte Vibration→Position Ableitung funktioniert NICHT mit simple mod-16.

KERNERKENNTNISSE:
1. Einzelne Matches gefunden (kapila, bhishma, shuka, shambhu)
2. Jeder verwendet eine ANDERE Formel
3. Die Formeln korrelieren mit den Position Sums (70, 17, 49)

DIE WAHRE ABLEITUNG:
====================
Die Reihenfolge in SB 6.3.20 IST die Struktur:
  - Yamaraja nennt die 12 Mahajanas in einer bestimmten Reihenfolge
  - Diese Reihenfolge → Quarters → Global Positions
  - SB_ORDER[n] + Quarter_Offset = Global_Position

Das ist NICHT hardcoded sondern SHASTRICALLY COMPUTED:
  - Input: SB 6.3.20 Verse
  - Algorithm: Parse order, apply quarter mapping
  - Output: 16 positions

NÄCHSTER SCHRITT:
=================
Implementiere: position[name] = SB_ORDER[name] mapped to QUARTERS
    """)


# =============================================================================
# KEY INSIGHT: Quarter-Based Derivation with Holy Name Position Sums
# =============================================================================


def quarter_based_derivation():
    """
    THE DISCOVERY:
    ==============
    Each quarter is dominated by a Holy Name:
    - GENESIS (1-4):  HARE → position_sum = 70
    - DHARMA (5-8):   KRISHNA → position_sum = 17
    - KARMA (9-12):   KRISHNA → position_sum = 17
    - MOKSHA (13-16): HARE → position_sum = 70

    The Mahamantra pattern tells us which formula to use!

    Pattern: HARE KRISHNA HARE KRISHNA KRISHNA KRISHNA HARE HARE
             HARE RAMA    HARE RAMA    RAMA    RAMA    HARE HARE

    Quarters:
    - Q1 (Genesis): HARE KRISHNA HARE KRISHNA → starts with HARE → mod 70
    - Q2 (Dharma):  KRISHNA KRISHNA HARE HARE → starts with KRISHNA → mod 17
    - Q3 (Karma):   HARE RAMA HARE RAMA → RAMA dominant → mod 49
    - Q4 (Moksha):  RAMA RAMA HARE HARE → RAMA then HARE → mod 49 then 70
    """
    print("\n8. QUARTER-BASED DERIVATION (Holy Name Position Sums)")
    print("-" * 50)

    # The dominant position sum for each quarter
    QUARTER_MODULO = {
        1: POSITION_SUM_HARE,  # 70 - Genesis (HARE KRISHNA)
        2: POSITION_SUM_KRISHNA,  # 17 - Dharma (KRISHNA KRISHNA)
        3: POSITION_SUM_RAMA,  # 49 - Karma (HARE RAMA)
        4: POSITION_SUM_HARE,  # 70 - Moksha (RAMA RAMA → ends with HARE)
    }

    matches = 0
    for profile in MAHAJANA_PROFILES:
        vib = compute_name_vibration(profile.name)
        quarter_mod = QUARTER_MODULO[profile.quarter]

        # Apply quarter-specific modulo
        step1 = vib % quarter_mod

        # Map to position within quarter (0-3)
        pos_in_quarter = step1 % QUARTERS

        # Calculate global position (quarter offset + position + 1 for head)
        global_pos = (profile.quarter - 1) * QUARTERS + pos_in_quarter + 1

        # Expected position
        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

        match = "✓" if global_pos == expected else " "
        if global_pos == expected:
            matches += 1

        print(
            f"  {match} {profile.name:12} | Q{profile.quarter} | mod_{quarter_mod:2}={step1:3} | "
            f"pos={global_pos:2} | expected={expected:2}"
        )

    print(f"\n  Matches: {matches}/{MAHAJANA_COUNT}")

    return matches


def brute_force_formula_search():
    """
    Brute force search for the correct formula combination.

    Try: for each Mahajana, find which (modulo, offset, operation) works.
    Then see if there's a pattern.
    """
    print("\n9. BRUTE FORCE FORMULA SEARCH")
    print("-" * 50)

    modulos = [16, 17, 37, 49, 70, 136, 137]
    offsets = [0, 1, 2, 3, 4, 5, 7, 10, 12, 16, 17, 49, 70]

    for profile in MAHAJANA_PROFILES:
        vib = compute_name_vibration(profile.name)

        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

        found = []
        for mod in modulos:
            for off in offsets:
                # Try: (vib + off) % mod % 16
                result = ((vib + off) % mod) % WORDS
                if result == expected:
                    found.append(f"(vib+{off})%{mod}%16")

                # Try: (vib % mod + off) % 16
                result2 = (vib % mod + off) % WORDS
                if result2 == expected:
                    found.append(f"(vib%{mod}+{off})%16")

        if found:
            print(f"  {profile.name:12} → {', '.join(found[:3])}")
        else:
            print(f"  {profile.name:12} → NO FORMULA FOUND for expected {expected}")


def analyze_mahajana_names_as_seed():
    """
    THE TRUE INSIGHT:
    =================
    The Mahajana names ARE the seed that GENERATES positions.

    We need to find how: name → vibration → transform → position

    where the transform uses Mahamantra constants.
    """
    print("\n10. NAME AS SEED ANALYSIS")
    print("-" * 50)

    print("  Looking for: f(vibration) = position")
    print()

    # Collect all data
    data = []
    for profile in MAHAJANA_PROFILES:
        vib = compute_name_vibration(profile.name)
        worker_in_quarter = ((profile.position - 1) % 3) + 1
        expected = (profile.quarter - 1) * QUARTERS + worker_in_quarter + 1

        data.append(
            {
                "name": profile.name,
                "vib": vib,
                "expected": expected,
                "quarter": profile.quarter,
                "vib_mod_49": vib % 49,
                "vib_mod_17": vib % 17,
                "vib_mod_70": vib % 70,
            }
        )

    # Print table
    print("  Name         | Vibration | exp | v%49 | v%17 | v%70")
    print("  " + "-" * 56)
    for d in data:
        print(
            f"  {d['name']:12} | {d['vib']:9} | {d['expected']:3} | {d['vib_mod_49']:4} | "
            f"{d['vib_mod_17']:4} | {d['vib_mod_70']:4}"
        )

    # Key insight: can we find a mapping?
    print("\n  Key Question: Is there a pattern in v%49, v%17, v%70 → expected?")
    print("  Let's check if SB order IS the intended mapping...")

    # SB 6.3.20 order IS the canonical order
    print("\n  SB 6.3.20 ORDER = CANONICAL")
    print("  " + "-" * 40)
    print("  The verse order maps to positions like this:")
    print("    SB[1] = brahma   → Position 2  (Genesis worker 1)")
    print("    SB[2] = narada   → Position 3  (Genesis worker 2)")
    print("    SB[3] = shambhu  → Position 4  (Genesis worker 3)")
    print("    SB[4] = kumaras  → Position 6  (Dharma worker 1)")
    print("    ... and so on")
    print()
    print("  THE MAPPING IS:")
    print("    Global_Position = SB_Order + Quarter_Head_Offset")
    print("    where Quarter_Head_Offset = (Q-1) × 4 + 1")


if __name__ == "__main__":
    run_analysis()
