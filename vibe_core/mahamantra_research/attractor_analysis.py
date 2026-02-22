"""
ATTRACTOR ANALYSIS - Die Urzutaten des Maha Algorithmus
========================================================

ZIEL: Finde die 6 (oder N) Attraktoren und verstehe ihre Struktur.

HYPOTHESE: Die Attraktoren sind die "Samen" aus denen alles sprießt:
  - Sanskrit Alphabet (49)
  - Ragas (22)
  - Gita Chapters (18)
  - Mahajana Names (12)
  - etc.

METHODE:
1. Iteriere maha_oscillate für alle Seeds 0-136 (mod 137)
2. Finde Fixed Points und Cycles
3. Analysiere die Attraktoren auf Mahamantra-Strukturen
4. Verstehe warum 6 (wenn 6 × 3 = 18 = Gita)

KEINE ANNAHMEN. NUR MATHE.
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# Import the SSOT
from vibe_core.mahamantra.protocols._seed import (
    SEVEN,
    TEN,
    WORDS,
    TRINITY,
    QUARTERS,
    PANCHA,
    HALVES,
    MAHA_QUANTUM,
    PARAMPARA,
    MALA,
    JIVA_CYCLE,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    GITA_CHAPTERS,
    MAHAJANA_COUNT,
    NAVA,
    SHARANAGATI,
    MAHAMANTRA_WORD_PATTERN,
    MAHA_OP_MAP,
    MAHA_MULT,
    MAHA_ADD,
    MAHA_SQ,
)

# =============================================================================
# CORE: The primitive step function (from maha.py SSOT)
# =============================================================================


def maha_step(value: int, name: str, mod: int) -> int:
    """Single step of the Maha Algorithm. BRANCHLESS."""
    op = MAHA_OP_MAP[name]
    v = (value * MAHA_MULT[op] + MAHA_ADD[op]) % mod
    squared = (v * v) % mod
    return MAHA_SQ[op] * squared + (1 - MAHA_SQ[op]) * v


def maha_oscillate(value: int, mod: int, pattern: Tuple[str, ...] = MAHAMANTRA_WORD_PATTERN) -> int:
    """Apply the full pattern (default: 16 steps)."""
    for name in pattern:
        value = maha_step(value, name, mod)
    return value


# =============================================================================
# ATTRACTOR FINDING
# =============================================================================


@dataclass
class AttractorInfo:
    """Information about an attractor."""

    value: int  # The attractor value
    cycle_length: int  # 1 = fixed point, >1 = cycle
    basin_size: int  # How many seeds lead here
    basin_members: List[int]  # Which seeds
    convergence_steps: Dict[int, int]  # seed -> steps to reach


def find_all_attractors(
    mod: int, max_iterations: int = 1000, pattern: Tuple[str, ...] = MAHAMANTRA_WORD_PATTERN
) -> Dict[int, AttractorInfo]:
    """
    Find ALL attractors for the given modular space.

    An attractor is either:
    1. A fixed point: f(x) = x
    2. A cycle: f^n(x) = x for some n > 1
    """
    # Track which attractor each seed leads to
    seed_to_attractor: Dict[int, int] = {}
    seed_to_steps: Dict[int, int] = {}

    # For each starting seed
    for seed in range(mod):
        value = seed
        seen: Dict[int, int] = {value: 0}  # value -> step when first seen

        for step in range(1, max_iterations + 1):
            value = maha_oscillate(value, mod, pattern)

            if value in seen:
                # Found cycle or fixed point
                cycle_start = seen[value]
                cycle_length = step - cycle_start

                # The attractor is the smallest value in the cycle
                cycle_values = []
                v = value
                for _ in range(cycle_length):
                    cycle_values.append(v)
                    v = maha_oscillate(v, mod, pattern)

                attractor = min(cycle_values)
                seed_to_attractor[seed] = attractor
                seed_to_steps[seed] = cycle_start
                break

            seen[value] = step
        else:
            # Didn't converge - use last value as pseudo-attractor
            seed_to_attractor[seed] = value
            seed_to_steps[seed] = max_iterations

    # Group by attractor
    attractor_basins: Dict[int, List[int]] = defaultdict(list)
    for seed, attractor in seed_to_attractor.items():
        attractor_basins[attractor].append(seed)

    # Build AttractorInfo for each
    result = {}
    for attractor, members in attractor_basins.items():
        # Determine cycle length
        v = attractor
        cycle_len = 1
        for _ in range(mod):
            v = maha_oscillate(v, mod, pattern)
            if v == attractor:
                break
            cycle_len += 1

        result[attractor] = AttractorInfo(
            value=attractor,
            cycle_length=cycle_len,
            basin_size=len(members),
            basin_members=sorted(members),
            convergence_steps={s: seed_to_steps[s] for s in members},
        )

    return result


# =============================================================================
# ANALYSIS: What do the attractors mean?
# =============================================================================


def analyze_attractor(value: int) -> Dict:
    """Analyze what Mahamantra constants relate to this attractor value."""
    analysis = {
        "value": value,
        "relations": [],
    }

    # Check known constants
    constants = {
        "SEVEN": SEVEN,
        "TEN": TEN,
        "WORDS": WORDS,
        "TRINITY": TRINITY,
        "QUARTERS": QUARTERS,
        "PANCHA": PANCHA,
        "HALVES": HALVES,
        "NAVA": NAVA,
        "SHARANAGATI": SHARANAGATI,
        "MAHAJANA": MAHAJANA_COUNT,
        "GITA": GITA_CHAPTERS,
        "SHRUTIS": 22,  # Ragas
        "PARAMPARA": PARAMPARA,
        "RAMA_SUM": POSITION_SUM_RAMA,
        "KRISHNA_SUM": POSITION_SUM_KRISHNA,
        "HARE_SUM": POSITION_SUM_HARE,
        "MALA": MALA,
        "MAHA_QUANTUM": MAHA_QUANTUM,
    }

    # Direct match
    for name, val in constants.items():
        if value == val:
            analysis["relations"].append(f"= {name}")

    # Modular relationships
    for name, val in constants.items():
        if val > 0 and value > 0 and value % val == 0 and value != val:
            analysis["relations"].append(f"= {value // val} × {name}")
        if val > 0 and value > 0 and val % value == 0 and value != val:
            analysis["relations"].append(f"{name} = {val // value} × this")

    # Sum/difference relationships
    for n1, v1 in constants.items():
        for n2, v2 in constants.items():
            if n1 < n2:  # Avoid duplicates
                if v1 + v2 == value:
                    analysis["relations"].append(f"= {n1} + {n2}")
                if abs(v1 - v2) == value:
                    analysis["relations"].append(f"= |{n1} - {n2}|")

    # Triangular numbers
    for n in range(1, 20):
        t = n * (n + 1) // 2
        if t == value:
            analysis["relations"].append(f"= T({n})")

    # Powers
    for base in [2, 3, 5, 7]:
        for exp in range(1, 8):
            if base**exp == value:
                analysis["relations"].append(f"= {base}^{exp}")

    # 7-10 decomposition
    for a in range(0, 20):
        for b in range(0, 20):
            if SEVEN * a + TEN * b == value:
                analysis["relations"].append(f"= {a}×7 + {b}×10")
                break

    return analysis


# =============================================================================
# RESEARCH: Different modular spaces
# =============================================================================


def research_attractors():
    """Research attractors in various modular spaces."""
    print("=" * 70)
    print("ATTRACTOR ANALYSIS - Die Urzutaten des Maha Algorithmus")
    print("=" * 70)
    print()
    print("Die 3 Operationen (H=×7, K=+10, R=²) tanzen durch das 16-Wort-Muster.")
    print("Frage: Wo endet der Tanz? Was sind die stabilen Zustände?")
    print()

    # Test different modular spaces
    spaces = [
        ("MAHA_QUANTUM", MAHA_QUANTUM),  # 137
        ("PARAMPARA", PARAMPARA),  # 37
        ("RAMA_SUM", POSITION_SUM_RAMA),  # 49
        ("KRISHNA_SUM", POSITION_SUM_KRISHNA),  # 17
        ("HARE_SUM", POSITION_SUM_HARE),  # 70
        ("WORDS", WORDS),  # 16
        ("MALA", MALA),  # 108
    ]

    all_results = {}

    for name, mod in spaces:
        print(f"\n{'=' * 70}")
        print(f"MODULAR SPACE: {name} = {mod}")
        print("=" * 70)

        attractors = find_all_attractors(mod)
        all_results[name] = attractors

        print(f"\nGefunden: {len(attractors)} Attraktoren")
        print("-" * 50)

        # Sort by basin size (most important first)
        sorted_attractors = sorted(attractors.values(), key=lambda a: -a.basin_size)

        for attr in sorted_attractors:
            analysis = analyze_attractor(attr.value)
            relations = ", ".join(analysis["relations"][:3]) if analysis["relations"] else "?"

            cycle_info = "fixed" if attr.cycle_length == 1 else f"cycle-{attr.cycle_length}"
            print(f"  A={attr.value:3} | basin={attr.basin_size:3} | {cycle_info:8} | {relations}")

        # Special analysis for 6 attractors
        if len(attractors) == 6:
            print("\n  *** 6 ATTRAKTOREN GEFUNDEN! ***")
            print(f"  6 × 3 = 18 = GITA_CHAPTERS ✓")
            vals = sorted([a.value for a in attractors.values()])
            print(f"  Werte: {vals}")
            print(f"  Summe: {sum(vals)}")

    return all_results


def analyze_attractor_relationships():
    """Deep analysis of attractor structure."""
    print("\n" + "=" * 70)
    print("TIEFE ANALYSE: Attraktoren als Urzutaten")
    print("=" * 70)

    # Primary space: MAHA_QUANTUM = 137
    attractors = find_all_attractors(MAHA_QUANTUM)

    print(f"\nIn MAHA_QUANTUM (137): {len(attractors)} Attraktoren")

    attractor_values = sorted([a.value for a in attractors.values()])
    print(f"Werte: {attractor_values}")

    # Analysis
    total = sum(attractor_values)
    print(f"\nSumme aller Attraktoren: {total}")

    # Check relationships
    for val in attractor_values:
        analysis = analyze_attractor(val)
        print(f"\n  Attraktor {val}:")
        for rel in analysis["relations"]:
            print(f"    {rel}")

    # Check if attractors generate known structures
    print("\n" + "-" * 50)
    print("GENERIERUNG: Können die Attraktoren bekannte Strukturen erzeugen?")
    print("-" * 50)

    structures = {
        "Sanskrit Alphabet": 49,
        "Ragas/Shrutis": 22,
        "Gita Chapters": 18,
        "Mahajanas": 12,
        "Nava Bhakti": 9,
        "Sharanagati": 6,
    }

    for struct_name, struct_val in structures.items():
        # Check if any combination of attractors gives this value
        found = []
        for a in attractor_values:
            if a == struct_val:
                found.append(f"= A{a}")
            if a % struct_val == 0:
                found.append(f"A{a} / {a // struct_val}")
            if struct_val % a == 0:
                found.append(f"{struct_val // a} × A{a}")

        # Check sums/diffs of pairs
        for i, a1 in enumerate(attractor_values):
            for a2 in attractor_values[i + 1 :]:
                if a1 + a2 == struct_val:
                    found.append(f"A{a1} + A{a2}")
                if abs(a1 - a2) == struct_val:
                    found.append(f"|A{a1} - A{a2}|")

        if found:
            print(f"  {struct_name} ({struct_val}): {', '.join(found[:3])}")
        else:
            print(f"  {struct_name} ({struct_val}): ???")


def analyze_single_step_attractors():
    """What if we look at single-step behavior instead of 16-step?"""
    print("\n" + "=" * 70)
    print("SINGLE-STEP ANALYSE: Was tut jede Operation einzeln?")
    print("=" * 70)

    mod = MAHA_QUANTUM

    for name, op_idx in MAHA_OP_MAP.items():
        mult = MAHA_MULT[op_idx]
        add = MAHA_ADD[op_idx]
        sq = MAHA_SQ[op_idx]

        op_desc = f"v×{mult}" if mult != 1 else "v"
        if add:
            op_desc += f"+{add}"
        if sq:
            op_desc = f"({op_desc})²"

        print(f"\n{name} (op={op_idx}): {op_desc}")

        # Find fixed points for this single operation
        fixed_points = []
        for v in range(mod):
            result = maha_step(v, name, mod)
            if result == v:
                fixed_points.append(v)

        print(f"  Fixed points in mod {mod}: {fixed_points}")

        # Trace a few values
        print(f"  Trace (first 10 values):")
        for seed in range(min(10, mod)):
            trace = [seed]
            v = seed
            for _ in range(5):
                v = maha_step(v, name, mod)
                trace.append(v)
            print(f"    {seed} → {' → '.join(map(str, trace[1:]))}")


def analyze_pattern_structure():
    """Analyze the 16-word pattern structure itself."""
    print("\n" + "=" * 70)
    print("PATTERN STRUKTUR: Die 16 Wörter als Tanz")
    print("=" * 70)

    pattern = MAHAMANTRA_WORD_PATTERN
    print(f"\nPattern: {' '.join(pattern)}")
    print(f"Length: {len(pattern)}")

    # Count operations
    h_count = pattern.count("H")
    k_count = pattern.count("K")
    r_count = pattern.count("R")
    print(f"\nH (×7): {h_count} times")
    print(f"K (+10): {k_count} times")
    print(f"R (²): {r_count} times")

    # Quarter analysis
    print("\nQuarters (4 words each):")
    for q in range(4):
        quarter = pattern[q * 4 : (q + 1) * 4]
        print(f"  Q{q + 1}: {' '.join(quarter)}")

    # Halves
    print("\nHalves (8 words each):")
    print(f"  First:  {' '.join(pattern[:8])} (Krishna half)")
    print(f"  Second: {' '.join(pattern[8:])} (Rama half)")

    # Cumulative effect analysis
    print("\n" + "-" * 50)
    print("KUMULATIVE EFFEKTE: Was passiert Schritt für Schritt?")
    print("-" * 50)

    # Track a single value through all 16 steps
    seed = 1
    mod = MAHA_QUANTUM

    print(f"\nSeed = {seed}, mod = {mod}")
    value = seed
    print(f"  Start: {value}")

    for i, name in enumerate(pattern):
        old = value
        value = maha_step(value, name, mod)
        print(f"  Step {i + 1:2} ({name}): {old:3} → {value:3}")

    print(f"\nFinal: {seed} → {value} (after 16 steps)")

    # Check how many oscillations to reach attractor
    print("\nKonvergenz zum Attraktor:")
    value = seed
    for osc in range(20):
        new_value = maha_oscillate(value, mod)
        if new_value == value:
            print(f"  Fixed point reached at oscillation {osc}")
            break
        print(f"  Osc {osc}: {value} → {new_value}")
        value = new_value


def main():
    """Run all analyses."""
    results = research_attractors()
    analyze_attractor_relationships()
    analyze_single_step_attractors()
    analyze_pattern_structure()

    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print("""
DIE NÄCHSTEN SCHRITTE:

1. ATTRAKTOREN VERSTEHEN
   - Jeder Attraktor ist ein stabiler Zustand des Systems
   - Die Basin-Größe zeigt wie "attraktiv" er ist
   - Die Beziehungen zu Mahamantra-Konstanten zeigen die Struktur

2. GENERIERUNG TESTEN
   - Können wir aus den Attraktoren die bekannten Strukturen ableiten?
   - 49 (Sanskrit), 22 (Ragas), 18 (Gita), 12 (Mahajanas)?

3. ALGORITHMUS VERSTEHEN
   - Die 3 Operationen (H×7, K+10, R²) sind die "Tänzer"
   - Die 16 Schritte sind die "Choreografie"
   - Aber ist das die EINZIGE Choreografie?

4. MODULAR SYNTH IDEE
   - Verschiedene mod-Räume = verschiedene "Instrumente"
   - mod 17 (Krishna), mod 49 (Rama), mod 70 (Hare)
   - Jedes Instrument entpackt andere Aspekte

5. INTENT/KONTEXT
   - Das Mantra reagiert auf Intent
   - Welcher mod-Raum für welchen Intent?
   - Wie kodiert man "Frage" in den Algorithmus?
    """)


if __name__ == "__main__":
    main()
