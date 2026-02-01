"""
POSITION HOLOGRAPH - Every Position is a Portal
================================================

"Ich bin der Anfang, die Mitte und das Ende aller Wesen" (Gita 10.20)

HYPOTHESIS: Each of the 16 positions is a holographic entry point.
The algorithm run FROM a position reveals that position's "view" of the whole.

THE PATTERN:
  Position: 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
  Word:     H  K  H  K  K  K  H  H  H  R  H  R  R  R  H  H

13 AND 37 CONNECTION:
  13 = FIBONACCI_SEVEN = HARE_COUNT + PANCHA
  37 = PARAMPARA = KSHETRA + MAHAJANA + KSETRAJNA
  Both are PRIME. Both contain digit 3.
  13 + 37 = 50 = JIVA_QUALITIES
  37 - 13 = 24 = KSHETRA
  13 × 37 = 481 = ???

THE CIRCULAR IMPORT:
  The algorithm may be self-referential - running it on its own output
  produces new structure that relates back to the input.

NO SPECULATION. FIND THE PATTERNS.
"""

from typing import Dict, List, Tuple, Final
from collections import Counter

from vibe_core.mahamantra.protocols._seed import (
    WORDS, HALVES, TRINITY, QUARTERS, PANCHA,
    HARE_COUNT, KRISHNA_COUNT, RAMA_COUNT,
    SEVEN, TEN, KSETRAJNA, SHARANAGATI, NAVA,
    MAHAJANA_COUNT, KSHETRA, PARAMPARA, MALA,
    FIBONACCI_SEVEN, TRIANGULAR_SEVEN,
    MAHA_QUANTUM, MAHA_ATTRACTORS, JIVA_QUALITIES,
    POSITION_SUM_HARE, POSITION_SUM_KRISHNA, POSITION_SUM_RAMA,
    MAHAMANTRA_WORD_PATTERN,
    HARE_POSITIONS, KRISHNA_POSITIONS, RAMA_POSITIONS,
    MAHA_OP_MAP, MAHA_MULT, MAHA_ADD, MAHA_SQ,
)

# The 16 positions (1-indexed for human readability)
PATTERN = MAHAMANTRA_WORD_PATTERN

print("=" * 70)
print("POSITION HOLOGRAPH - Every Position is a Portal")
print("=" * 70)
print()

# =============================================================================
# 1. THE 13-37 CONNECTION
# =============================================================================

print("1. THE 13-37 CONNECTION")
print("-" * 50)

print(f"  13 = FIBONACCI_SEVEN = HARE_COUNT + PANCHA = {HARE_COUNT} + {PANCHA}")
print(f"  37 = PARAMPARA = KSHETRA + MAHAJANA + KSETRAJNA = {KSHETRA} + {MAHAJANA_COUNT} + {KSETRAJNA}")
print()
print(f"  13 + 37 = {FIBONACCI_SEVEN + PARAMPARA} = JIVA_QUALITIES ({JIVA_QUALITIES})")
print(f"  37 - 13 = {PARAMPARA - FIBONACCI_SEVEN} = KSHETRA ({KSHETRA})")
print(f"  13 × 37 = {FIBONACCI_SEVEN * PARAMPARA}")
print()

# What is 481?
product = FIBONACCI_SEVEN * PARAMPARA
print(f"  481 Analysis:")
print(f"    481 = 13 × 37 (both prime)")
print(f"    481 = MALA × QUARTERS + {product - MALA * QUARTERS}")
print(f"    481 = JIVA_QUALITIES × {product // JIVA_QUALITIES} + {product % JIVA_QUALITIES}")
print(f"    481 / 7 = {product / SEVEN:.2f}")
print(f"    481 mod 137 = {product % MAHA_QUANTUM}")
print(f"    481 mod 108 = {product % MALA}")
print()

# =============================================================================
# 2. POSITION STRUCTURE
# =============================================================================

print("2. POSITION STRUCTURE")
print("-" * 50)

# Each position has a name (H, K, R) and a position number
print("  Position: ", end="")
for i in range(1, WORDS + 1):
    print(f"{i:2}", end=" ")
print()

print("  Word:     ", end="")
for name in PATTERN:
    print(f" {name}", end=" ")
print()

print("  Quarter:  ", end="")
for i in range(WORDS):
    q = (i // QUARTERS) + 1
    print(f" {q}", end=" ")
print()
print()

# Which positions have which name?
print("  HARE positions (1-indexed):    ", [p+1 for p in HARE_POSITIONS])
print("  KRISHNA positions (1-indexed): ", [p+1 for p in KRISHNA_POSITIONS])
print("  RAMA positions (1-indexed):    ", [p+1 for p in RAMA_POSITIONS])
print()

# =============================================================================
# 3. POSITION SUMS AND PRODUCTS
# =============================================================================

print("3. POSITION MATHEMATICS")
print("-" * 50)

hare_pos = [p+1 for p in HARE_POSITIONS]
krishna_pos = [p+1 for p in KRISHNA_POSITIONS]
rama_pos = [p+1 for p in RAMA_POSITIONS]

print(f"  HARE sum:    {sum(hare_pos):3} = {hare_pos}")
print(f"  KRISHNA sum: {sum(krishna_pos):3} = {krishna_pos}")
print(f"  RAMA sum:    {sum(rama_pos):3} = {rama_pos}")
print(f"  TOTAL:       {sum(hare_pos) + sum(krishna_pos) + sum(rama_pos)} = T(16) = triangular(16)")
print()

# Products
import math
def product_of_list(lst):
    result = 1
    for x in lst:
        result *= x
    return result

hare_prod = product_of_list(hare_pos)
krishna_prod = product_of_list(krishna_pos)
rama_prod = product_of_list(rama_pos)

print(f"  HARE product:    {hare_prod}")
print(f"  KRISHNA product: {krishna_prod}")
print(f"  RAMA product:    {rama_prod}")
print()

# Factor analysis
print(f"  HARE product factors: {hare_prod} = ", end="")
n = hare_prod
for p in [2, 3, 5, 7, 11, 13]:
    count = 0
    while n % p == 0:
        n //= p
        count += 1
    if count > 0:
        print(f"{p}^{count} × ", end="")
print(f"{n if n > 1 else ''}")
print()

# =============================================================================
# 4. THE HOLOGRAPHIC PRINCIPLE - Run algorithm from each position
# =============================================================================

print("4. HOLOGRAPHIC PRINCIPLE - Algorithm from each position")
print("-" * 50)

def maha_step(value: int, name: str, mod: int) -> int:
    """Single step of Maha Algorithm."""
    op = MAHA_OP_MAP[name]
    v = (value * MAHA_MULT[op] + MAHA_ADD[op]) % mod
    squared = (v * v) % mod
    return MAHA_SQ[op] * squared + (1 - MAHA_SQ[op]) * v

def maha_from_position(start_pos: int, seed: int, mod: int = MAHA_QUANTUM) -> Tuple[int, List[int]]:
    """
    Run algorithm starting from position start_pos (0-indexed).
    Returns (final_value, trace).
    """
    trace = [seed]
    value = seed % mod

    # Start from start_pos and wrap around
    for i in range(WORDS):
        pos = (start_pos + i) % WORDS
        name = PATTERN[pos]
        value = maha_step(value, name, mod)
        trace.append(value)

    return value, trace

print("  Starting from each position with seed=1:")
print()
results_by_pos = {}
for pos in range(WORDS):
    final, trace = maha_from_position(pos, seed=1)
    results_by_pos[pos] = final
    name = PATTERN[pos]
    print(f"    Pos {pos+1:2} ({name}): 1 → {final:3}")

print()
print("  Result frequency:")
result_counts = Counter(results_by_pos.values())
for val, count in sorted(result_counts.items()):
    positions = [p+1 for p, v in results_by_pos.items() if v == val]
    print(f"    Value {val:3}: appears from positions {positions}")
print()

# =============================================================================
# 5. SELF-REFERENCE - Algorithm on its own output
# =============================================================================

print("5. SELF-REFERENCE - Algorithm on its own output")
print("-" * 50)

def maha_full(value: int, mod: int = MAHA_QUANTUM) -> int:
    """Run full 16-step algorithm."""
    for name in PATTERN:
        value = maha_step(value, name, mod)
    return value

print("  Iterating: f(f(f(...f(1)...)))")
value = 1
seen = {1: 0}
trace = [1]

for i in range(1, 20):
    value = maha_full(value)
    trace.append(value)
    if value in seen:
        print(f"    Cycle detected at iteration {i}!")
        print(f"    {value} was first seen at iteration {seen[value]}")
        print(f"    Cycle length: {i - seen[value]}")
        break
    seen[value] = i

print(f"    Trace: {trace}")
print()

# =============================================================================
# 6. WHAT DOES EACH POSITION "SEE"?
# =============================================================================

print("6. WHAT DOES EACH POSITION 'SEE'?")
print("-" * 50)

# For each position, what is the "neighborhood"?
print("  Each position's local context (±2 positions):")
for pos in range(WORDS):
    context = []
    for offset in range(-2, 3):
        idx = (pos + offset) % WORDS
        context.append(PATTERN[idx])
    center = PATTERN[pos]
    print(f"    Pos {pos+1:2}: {''.join(context[:2])} [{center}] {''.join(context[3:])}")
print()

# =============================================================================
# 7. QUARTER TRANSITIONS
# =============================================================================

print("7. QUARTER TRANSITIONS")
print("-" * 50)

quarters = [
    PATTERN[0:4],   # Q1: HKHK
    PATTERN[4:8],   # Q2: KKHH
    PATTERN[8:12],  # Q3: HRHR
    PATTERN[12:16], # Q4: RRHH
]

for i, q in enumerate(quarters):
    # Analyze the quarter
    h_count = q.count("H")
    k_count = q.count("K")
    r_count = q.count("R")

    # What operation dominates?
    dominant = "H" if h_count >= 2 else ("K" if k_count >= 2 else "R")

    # Run algorithm just for this quarter
    value = 1
    for name in q:
        value = maha_step(value, name, MAHA_QUANTUM)

    print(f"  Q{i+1}: {''.join(q)} → H={h_count} K={k_count} R={r_count} → 1→{value}")
print()

# =============================================================================
# 8. THE 50 JIVA QUALITIES CONNECTION
# =============================================================================

print("8. THE 50 JIVA QUALITIES")
print("-" * 50)

print(f"  13 + 37 = {FIBONACCI_SEVEN + PARAMPARA} = JIVA_QUALITIES")
print()
print("  The 6 attractors sum to 147 = 3 × 49 = TRINITY × RAMA²")
print(f"  147 - 97 = 50 = JIVA_QUALITIES")
print(f"  What is 97? Let's see...")
print(f"    97 = 100 - 3 = (TEN²) - TRINITY")
print(f"    97 = HARE_SUM + NAKSHATRAS = {POSITION_SUM_HARE} + {27}")
print(f"    97 is prime")
print()

# The 50 qualities are minute portions of Krishna's 64
print(f"  JIVA has 50 = 64 - 14")
print(f"  14 = 2 × SEVEN = qualities only Krishna has")
print(f"  Or: 50 = KSHETRA + MAHAJANA + FIBONACCI_SEVEN + KSETRAJNA")
print(f"     = {KSHETRA} + {MAHAJANA_COUNT} + {FIBONACCI_SEVEN} + {KSETRAJNA}")
print(f"     = {KSHETRA + MAHAJANA_COUNT + FIBONACCI_SEVEN + KSETRAJNA}")
print()

# Wait, that's 50!
check = KSHETRA + MAHAJANA_COUNT + FIBONACCI_SEVEN + KSETRAJNA
print(f"  VERIFICATION: {check} = 50 ✓")
print()
print("  JIVA_QUALITIES = KSHETRA + MAHAJANA + FIBONACCI_SEVEN + KSETRAJNA")
print("                 = Field + Authorities + Living Principle + Observer")
print()

# =============================================================================
# 9. PATTERN IN POSITION NUMBERS
# =============================================================================

print("9. PATTERN IN POSITION NUMBERS")
print("-" * 50)

# Look at the actual position numbers where each name appears
print("  HARE at positions:", hare_pos)
print("    Differences:", [hare_pos[i+1] - hare_pos[i] for i in range(len(hare_pos)-1)])
print()
print("  KRISHNA at positions:", krishna_pos)
print("    Differences:", [krishna_pos[i+1] - krishna_pos[i] for i in range(len(krishna_pos)-1)])
print()
print("  RAMA at positions:", rama_pos)
print("    Differences:", [rama_pos[i+1] - rama_pos[i] for i in range(len(rama_pos)-1)])
print()

# =============================================================================
# 10. THE REVERSAL PROPERTY
# =============================================================================

print("10. THE REVERSAL PROPERTY")
print("-" * 50)

# What if we run the pattern backwards?
reversed_pattern = PATTERN[::-1]
print(f"  Forward:  {''.join(PATTERN)}")
print(f"  Backward: {''.join(reversed_pattern)}")
print()

# Run both
forward_result = 1
for name in PATTERN:
    forward_result = maha_step(forward_result, name, MAHA_QUANTUM)

backward_result = 1
for name in reversed_pattern:
    backward_result = maha_step(backward_result, name, MAHA_QUANTUM)

print(f"  1 → Forward → {forward_result}")
print(f"  1 → Backward → {backward_result}")
print()

# Are they related?
print(f"  Relationship: {forward_result} + {backward_result} = {forward_result + backward_result}")
print(f"  Relationship: {forward_result} × {backward_result} = {forward_result * backward_result}")
print()

# =============================================================================
# SUMMARY
# =============================================================================

print("=" * 70)
print("DISCOVERIES")
print("=" * 70)
print("""
1. 13 × 37 = 481 = FIBONACCI_SEVEN × PARAMPARA
   481 mod 137 = 70 = POSITION_SUM_HARE!

2. 13 + 37 = 50 = JIVA_QUALITIES
   = KSHETRA + MAHAJANA + FIBONACCI_SEVEN + KSETRAJNA
   = Field + Authorities + Living + Observer

3. Starting from different positions gives different "views":
   The algorithm IS holographic - same structure, different perspectives.

4. The pattern HKHKKKHHHRHRRRHH has internal symmetry:
   Q1: HKHK (alternating)
   Q2: KKHH (grouped)
   Q3: HRHR (alternating)
   Q4: RRHH (grouped)

5. HARE differences: [2, 4, 1, 1, 2, 4, 1]
   Note: 2, 4, 1, 1, 2, 4, 1 - palindrome-like!
""")
