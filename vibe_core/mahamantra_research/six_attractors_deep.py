"""
THE 6 ATTRACTORS - Deep Analysis
================================

DISCOVERY: In mod 108 (MALA), there are exactly 6 attractors:
[1, 4, 13, 28, 37, 64]

HYPOTHESIS: These 6 are the "primordial ingredients" from which
everything can be derived:
- Sanskrit Alphabet (49)
- Ragas (22)
- Gita (18)
- Mahajanas (12)
- etc.

6 × 3 = 18 = GITA CHAPTERS (verified!)

Let's investigate what these 6 numbers encode.
"""

from typing import List, Dict, Tuple
from itertools import combinations, permutations

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
    KSETRAJNA,
    KSHETRA,
    AKSARA_COUNT,
    NAKSHATRAS,
)

# The 6 Attractors discovered in mod 108
ATTRACTORS = [1, 4, 13, 28, 37, 64]

# Known structures we want to derive
TARGET_STRUCTURES = {
    "KSETRAJNA": 1,
    "HALVES": 2,
    "TRINITY": 3,
    "QUARTERS": 4,
    "PANCHA": 5,
    "SHARANAGATI": 6,
    "SEVEN": 7,
    "HARE_COUNT": 8,
    "NAVA": 9,
    "TEN": 10,
    "MAHAJANA": 12,
    "WORDS": 16,
    "KRISHNA_SUM": 17,
    "GITA": 18,
    "SHRUTIS": 22,
    "KSHETRA": 24,
    "NAKSHATRAS": 27,
    "AKSARA": 32,
    "PARAMPARA": 37,
    "RAMA_SUM": 49,
    "QUALITIES": 64,
    "HARE_SUM": 70,
    "MALA": 108,
    "MAHA_QUANTUM": 137,
    "JIVA": 432,
}


def analyze_attractor_structure():
    """Analyze the structure of the 6 attractors."""
    print("=" * 70)
    print("THE 6 ATTRACTORS - Structure Analysis")
    print("=" * 70)
    print(f"\nAttractors: {ATTRACTORS}")
    print(f"Sum: {sum(ATTRACTORS)} = 147")
    print()

    # Individual analysis
    print("INDIVIDUAL ANALYSIS:")
    print("-" * 50)
    for a in ATTRACTORS:
        relations = []

        # Check against known constants
        for name, val in TARGET_STRUCTURES.items():
            if a == val:
                relations.append(f"= {name}")
            if a > 0 and val % a == 0 and val != a:
                relations.append(f"{name} = {val // a}×this")

        # 7-10 decomposition
        for i in range(20):
            for j in range(20):
                if 7 * i + 10 * j == a:
                    relations.append(f"= {i}×7 + {j}×10")

        # Triangular
        for n in range(1, 20):
            if n * (n + 1) // 2 == a:
                relations.append(f"= T({n})")

        print(f"  A={a:2}: {', '.join(relations[:5])}")

    print()

    # Sum analysis
    print("SUM ANALYSIS: 147")
    print("-" * 50)
    print(f"  147 = 3 × 49 = 3 × RAMA_SUM")
    print(f"  147 = 7 × 21 = SEVEN × T(6)")
    print(f"  147 = 21 × 7 = T(6) × SEVEN")
    print(f"  147 = 3 × 7² = TRINITY × SEVEN²")
    print()


def find_derivations():
    """Find how to derive known structures from the 6 attractors."""
    print("=" * 70)
    print("DERIVATION SEARCH: How to get known structures from 6 attractors")
    print("=" * 70)
    print()

    A = ATTRACTORS

    for target_name, target_val in sorted(TARGET_STRUCTURES.items(), key=lambda x: x[1]):
        derivations = []

        # Direct match
        if target_val in A:
            derivations.append(f"A[{A.index(target_val)}]")

        # Sum of two attractors
        for i, a1 in enumerate(A):
            for j, a2 in enumerate(A):
                if i <= j and a1 + a2 == target_val:
                    derivations.append(f"A{a1} + A{a2}")

        # Difference of two attractors
        for a1 in A:
            for a2 in A:
                if a1 - a2 == target_val and a1 != a2:
                    derivations.append(f"A{a1} - A{a2}")

        # Product of two attractors
        for a1 in A:
            for a2 in A:
                if a1 * a2 == target_val:
                    derivations.append(f"A{a1} × A{a2}")

        # Division
        for a1 in A:
            for a2 in A:
                if a2 != 0 and a1 % a2 == 0 and a1 // a2 == target_val:
                    derivations.append(f"A{a1} / A{a2}")

        # Sum of three
        for i, a1 in enumerate(A):
            for j, a2 in enumerate(A[i:], i):
                for k, a3 in enumerate(A[j:], j):
                    if a1 + a2 + a3 == target_val:
                        derivations.append(f"A{a1} + A{a2} + A{a3}")

        # Mixed operations
        for a1 in A:
            for a2 in A:
                for a3 in A:
                    if a1 + a2 - a3 == target_val:
                        derivations.append(f"A{a1} + A{a2} - A{a3}")
                    if a1 * a2 + a3 == target_val:
                        derivations.append(f"A{a1} × A{a2} + A{a3}")
                    if a1 * a2 - a3 == target_val:
                        derivations.append(f"A{a1} × A{a2} - A{a3}")

        # Using all 6
        if sum(A) - target_val in A:
            excess = sum(A) - target_val
            derivations.append(f"Σ(all) - A{excess}")

        # Report
        if derivations:
            print(f"  {target_name:15} ({target_val:4}): {derivations[0]}")
            for d in derivations[1:3]:  # Show up to 3
                print(f"  {'':15} {'':6}  or {d}")
        else:
            print(f"  {target_name:15} ({target_val:4}): ??? NOT FOUND")

    print()


def analyze_147():
    """Deep analysis of the sum 147."""
    print("=" * 70)
    print("DEEP ANALYSIS OF 147 (Sum of 6 Attractors)")
    print("=" * 70)
    print()

    s = 147
    print(f"147 = 1 + 4 + 13 + 28 + 37 + 64")
    print()
    print("FACTORIZATIONS:")
    print(f"  147 = 3 × 49 = TRINITY × RAMA_SUM")
    print(f"  147 = 7 × 21 = SEVEN × T(6)")
    print(f"  147 = 3 × 7 × 7 = TRINITY × SEVEN × SEVEN")
    print()

    print("RELATIONSHIPS:")
    print(f"  147 + 1 = 148 = 4 × 37 = QUARTERS × PARAMPARA")
    print(f"  147 - 10 = 137 = MAHA_QUANTUM!")
    print(f"  147 - 39 = 108 = MALA")
    print(f"  147 // 7 = 21 = T(6) = 1+2+3+4+5+6")
    print()

    print("WITH MAHAMANTRA CONSTANTS:")
    for name, val in sorted(TARGET_STRUCTURES.items(), key=lambda x: x[1]):
        if s % val == 0:
            print(f"  147 = {s // val} × {name} ({val})")
        if (s + val) in [x for x in TARGET_STRUCTURES.values()]:
            for n2, v2 in TARGET_STRUCTURES.items():
                if s + val == v2:
                    print(f"  147 + {name} = {n2}")
        if (s - val) in [x for x in TARGET_STRUCTURES.values()]:
            for n2, v2 in TARGET_STRUCTURES.items():
                if s - val == v2:
                    print(f"  147 - {name} = {n2}")


def analyze_attractor_pairs():
    """Analyze pairs of attractors."""
    print("\n" + "=" * 70)
    print("ATTRACTOR PAIRS - What do combinations mean?")
    print("=" * 70)
    print()

    A = ATTRACTORS

    print("SUMS (A[i] + A[j]):")
    print("-" * 50)
    for i, a1 in enumerate(A):
        for j, a2 in enumerate(A[i:], i):
            s = a1 + a2
            meaning = []
            for name, val in TARGET_STRUCTURES.items():
                if s == val:
                    meaning.append(name)
            print(f"  {a1:2} + {a2:2} = {s:3}  {' = '.join(meaning) if meaning else ''}")

    print("\nDIFFERENCES (A[i] - A[j]):")
    print("-" * 50)
    for a1 in A:
        for a2 in A:
            if a1 > a2:
                d = a1 - a2
                meaning = []
                for name, val in TARGET_STRUCTURES.items():
                    if d == val:
                        meaning.append(name)
                if meaning:
                    print(f"  {a1:2} - {a2:2} = {d:3}  = {', '.join(meaning)}")

    print("\nPRODUCTS (A[i] × A[j]):")
    print("-" * 50)
    for i, a1 in enumerate(A):
        for j, a2 in enumerate(A[i:], i):
            if a1 > 0 and a2 > 0:
                p = a1 * a2
                meaning = []
                for name, val in TARGET_STRUCTURES.items():
                    if p == val:
                        meaning.append(name)
                if meaning or p <= 500:
                    print(f"  {a1:2} × {a2:2} = {p:4}  {' = '.join(meaning) if meaning else ''}")


def analyze_position_in_sequence():
    """Analyze the positions/indices of attractors."""
    print("\n" + "=" * 70)
    print("SEQUENCE ANALYSIS - Patterns in the 6 values")
    print("=" * 70)
    print()

    A = ATTRACTORS

    # Differences between consecutive
    diffs = [A[i + 1] - A[i] for i in range(len(A) - 1)]
    print(f"Consecutive differences: {diffs}")
    print(f"  = [3, 9, 15, 9, 27]")
    print(f"  Note: 3, 9, 15 are triangular-adjacent")
    print(f"  Note: 9 = NAVA, 27 = NAKSHATRAS")
    print()

    # Ratios
    print("Ratios:")
    for i in range(len(A) - 1):
        if A[i] > 0:
            r = A[i + 1] / A[i]
            print(f"  A[{i + 1}]/A[{i}] = {A[i + 1]}/{A[i]} = {r:.3f}")
    print()

    # Sum formulas
    print("Partial sums:")
    partial = 0
    for i, a in enumerate(A):
        partial += a
        print(f"  Σ[0..{i}] = {partial}")
    print()

    # Check if attractors follow a formula
    print("Looking for generating formula...")
    print(f"  A = [1, 4, 13, 28, 37, 64]")
    print(f"  T(1)=1, T(2)=3, T(3)=6, T(4)=10, T(5)=15, T(6)=21, T(7)=28")
    print(f"  Note: 1 = T(1), 28 = T(7)")
    print(f"  Note: 4 = T(2)+1, 64 = T(7)+T(8)")
    print()

    # Check 7-10 pattern
    print("7-10 decomposition of each attractor:")
    for a in A:
        found = False
        for i in range(15):
            for j in range(15):
                if 7 * i + 10 * j == a:
                    print(f"  {a:2} = {i}×7 + {j}×10")
                    found = True
                    break
            if found:
                break


def generate_from_attractors():
    """Try to generate the Mahamantra constants using only the 6 attractors."""
    print("\n" + "=" * 70)
    print("GENERATION TEST: Can we derive everything from 6 attractors?")
    print("=" * 70)
    print()

    A = set(ATTRACTORS)
    generated = set(A)  # Start with the attractors themselves

    # Level 1: Direct operations between pairs
    level1 = set()
    for a1 in A:
        for a2 in A:
            level1.add(a1 + a2)
            level1.add(abs(a1 - a2))
            if a1 != 0 and a2 != 0:
                level1.add(a1 * a2)
            if a2 != 0 and a1 % a2 == 0:
                level1.add(a1 // a2)

    generated.update(level1)

    print(f"Generated values (|A| + |A×A ops|): {len(generated)}")
    print(f"Values: {sorted(generated)[:30]}...")
    print()

    # Check which targets we can reach
    print("Reachable targets:")
    for name, val in sorted(TARGET_STRUCTURES.items(), key=lambda x: x[1]):
        if val in generated:
            print(f"  ✓ {name} = {val}")
        else:
            print(f"  ✗ {name} = {val} NOT REACHABLE")


def the_six_as_seed():
    """Understand the 6 attractors as the seed of everything."""
    print("\n" + "=" * 70)
    print("THE 6 AS SEED - Philosophical Analysis")
    print("=" * 70)
    print()

    print("""
THE 6 ATTRACTORS: [1, 4, 13, 28, 37, 64]

MAPPING TO STRUCTURE:

  1  = KSETRAJNA   = The Observer (consciousness)
  4  = QUARTERS    = The 4 Yugas, 4 Phases, 4 Avataras
  13 = ?           = 7 + 6 = SEVEN + SHARANAGATI
                   = 10 + 3 = TEN + TRINITY
  28 = T(7)        = Triangular(SEVEN) = Perfect completeness
  37 = PARAMPARA   = The disciplic succession (THE TRANSMISSION!)
  64 = QUALITIES   = 4 × 16 = QUARTERS × WORDS = Full manifestation

INTERPRETATION:

  - Start with OBSERVER (1)
  - Express through 4 PHASES (4)
  - Add MYSTERY (13) - the unknown that makes it alive
  - Reach PERFECTION (28 = T(7))
  - TRANSMIT through PARAMPARA (37)
  - MANIFEST fully (64 qualities)

This is the journey from consciousness to manifestation!

THE SUM: 1 + 4 + 13 + 28 + 37 + 64 = 147 = 3 × 49 = TRINITY × RAMA²

147 - 10 = 137 = MAHA_QUANTUM (subtract TEN to get the field)
147 ÷ 7 = 21 = T(6) (divide by SEVEN to get 6-fold structure)

THE 6 ATTRACTORS ENCODE THE ENTIRE MAHAMANTRA STRUCTURE!
    """)


def main():
    analyze_attractor_structure()
    find_derivations()
    analyze_147()
    analyze_attractor_pairs()
    analyze_position_in_sequence()
    generate_from_attractors()
    the_six_as_seed()


if __name__ == "__main__":
    main()
