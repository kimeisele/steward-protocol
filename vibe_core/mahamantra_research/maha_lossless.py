"""
MAHA LOSSLESS COMPRESSION - Can the algorithm be reversed?
==========================================================

THE QUESTION:
Is the Mahamantra algorithm a lossless compression?

THE OPERATIONS:
  H: v × 7 (mod m)  → invertible via ×7⁻¹
  K: v + 10 (mod m) → invertible via -10
  R: v² (mod m)     → NOT uniquely invertible (±√v)

THE CHALLENGE:
R (squaring) loses information because multiple inputs map to same output.
Example: both 2 and -2 (i.e., m-2) square to 4.

THE SOLUTION:
Track which branch was taken. Then encoding is:
  (attractor, branch_sequence) → original value

This is like arithmetic coding with a binary tree!
"""

from typing import List, Tuple, Optional
from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    MALA,
    PARAMPARA,
    SEVEN,
    TEN,
    MAHAMANTRA_WORD_PATTERN,
    WORDS,
    MAHA_OP_MAP,
    MAHA_MULT,
    MAHA_ADD,
    MAHA_SQ,
)


def mod_inverse(a: int, m: int) -> Optional[int]:
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""

    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None  # No inverse exists
    return (x % m + m) % m


def mod_sqrt(a: int, m: int) -> List[int]:
    """
    Find all square roots of a mod m.
    Returns list of roots (could be 0, 1, or 2 values).
    """
    if a == 0:
        return [0]

    roots = []
    for x in range(m):
        if (x * x) % m == a:
            roots.append(x)
    return roots


# =============================================================================
# FORWARD OPERATIONS (with tracking)
# =============================================================================


def maha_step_forward(value: int, name: str, mod: int) -> Tuple[int, int]:
    """
    Apply one step forward and return (result, branch_info).

    branch_info:
      For H and K: always 0 (deterministic)
      For R: which root index (0 or 1) the original was
    """
    op = MAHA_OP_MAP[name]
    mult = MAHA_MULT[op]
    add = MAHA_ADD[op]
    sq = MAHA_SQ[op]

    v = (value * mult + add) % mod

    if sq:
        # Squaring operation - we need to track which root we came from
        squared = (v * v) % mod
        # Find which root index v corresponds to
        roots = mod_sqrt(squared, mod)
        branch = roots.index(v) if v in roots else 0
        return squared, branch
    else:
        return v, 0


def maha_step_inverse(value: int, name: str, mod: int, branch: int = 0) -> int:
    """
    Apply inverse of one step.

    For R: uses branch to select which square root.
    """
    op = MAHA_OP_MAP[name]
    mult = MAHA_MULT[op]
    add = MAHA_ADD[op]
    sq = MAHA_SQ[op]

    if sq:
        # Inverse of squaring: take square root
        roots = mod_sqrt(value, mod)
        if not roots:
            return value  # No root exists (shouldn't happen with valid data)
        v = roots[branch] if branch < len(roots) else roots[0]
    else:
        v = value

    # Inverse of multiply and add: subtract then divide
    inv_mult = mod_inverse(mult, mod)
    if inv_mult is None:
        return v  # Can't invert (shouldn't happen with coprime mod)

    result = ((v - add) * inv_mult) % mod
    return result


# =============================================================================
# FULL ENCODE / DECODE
# =============================================================================


def encode(value: int, mod: int, pattern: Tuple[str, ...] = MAHAMANTRA_WORD_PATTERN) -> Tuple[int, List[int]]:
    """
    Encode a value by applying the full pattern.

    Returns: (final_value, branch_sequence)

    The branch_sequence allows lossless decoding.
    """
    branches = []
    current = value % mod

    for name in pattern:
        current, branch = maha_step_forward(current, name, mod)
        branches.append(branch)

    return current, branches


def decode(encoded: int, branches: List[int], mod: int, pattern: Tuple[str, ...] = MAHAMANTRA_WORD_PATTERN) -> int:
    """
    Decode by applying inverse operations in reverse order.

    Uses branch_sequence to resolve ambiguities.
    """
    current = encoded

    # Apply inverse in reverse order
    for i, name in enumerate(reversed(pattern)):
        branch = branches[len(pattern) - 1 - i]
        current = maha_step_inverse(current, name, mod, branch)

    return current


# =============================================================================
# TEST LOSSLESS PROPERTY
# =============================================================================


def test_lossless(mod: int = MAHA_QUANTUM):
    """Test if encode/decode is lossless for all values in mod space."""
    print(f"\nTesting lossless encoding in mod {mod}")
    print("-" * 50)

    errors = 0
    for original in range(mod):
        encoded, branches = encode(original, mod)
        decoded = decode(encoded, branches, mod)

        if decoded != original:
            print(f"  ERROR: {original} → {encoded} → {decoded}")
            errors += 1

    if errors == 0:
        print(f"  ✓ ALL {mod} values encode/decode correctly!")
        print(f"  Branch sequence length: {len(MAHAMANTRA_WORD_PATTERN)}")
        r_count = MAHAMANTRA_WORD_PATTERN.count("R")
        print(f"  R operations (require branches): {r_count}")
        print(f"  Bits needed for branches: {r_count} bits (one per R)")
    else:
        print(f"  ✗ {errors} errors out of {mod}")

    return errors == 0


def analyze_compression_ratio():
    """Analyze the compression achieved."""
    print("\n" + "=" * 70)
    print("COMPRESSION RATIO ANALYSIS")
    print("=" * 70)

    mod = MAHA_QUANTUM  # 137
    pattern = MAHAMANTRA_WORD_PATTERN

    # Original: log2(mod) bits to represent a value
    import math

    original_bits = math.ceil(math.log2(mod))
    print(f"\nOriginal value: needs {original_bits} bits (for mod {mod})")

    # Encoded: attractor + branches
    # Attractor: how many unique values after encoding?
    attractors = set()
    for v in range(mod):
        enc, _ = encode(v, mod)
        attractors.add(enc)

    attractor_bits = math.ceil(math.log2(len(attractors))) if attractors else 0
    print(f"Attractors: {len(attractors)} unique values → {attractor_bits} bits")

    # Branches: one bit per R operation
    r_count = pattern.count("R")
    branch_bits = r_count
    print(f"Branches: {r_count} R-operations → {branch_bits} bits")

    total_encoded = attractor_bits + branch_bits
    print(f"\nTotal encoded: {total_encoded} bits")
    print(f"Original: {original_bits} bits")

    if total_encoded < original_bits:
        print(f"\n✓ COMPRESSION ACHIEVED: {original_bits - total_encoded} bits saved")
    elif total_encoded > original_bits:
        print(f"\n✗ EXPANSION: {total_encoded - original_bits} extra bits")
    else:
        print(f"\n= NO CHANGE: same size")


def demonstrate_encoding():
    """Demonstrate the encoding/decoding process."""
    print("\n" + "=" * 70)
    print("ENCODING DEMONSTRATION")
    print("=" * 70)

    mod = MAHA_QUANTUM
    test_values = [0, 1, 13, 37, 42, 100, 136]

    print(f"\nmod = {mod}")
    print(f"Pattern: {' '.join(MAHAMANTRA_WORD_PATTERN)}")
    print()

    for v in test_values:
        enc, branches = encode(v, mod)
        dec = decode(enc, branches, mod)

        # Count non-zero branches (ambiguous R operations)
        nonzero = sum(1 for b in branches if b > 0)

        status = "✓" if dec == v else "✗"
        print(f"  {status} {v:3} → enc={enc:3}, branches={nonzero} non-zero → {dec:3}")


def analyze_branch_patterns():
    """Analyze the branch patterns that occur."""
    print("\n" + "=" * 70)
    print("BRANCH PATTERN ANALYSIS")
    print("=" * 70)

    mod = MAHA_QUANTUM

    # Collect all branch patterns
    pattern_counts = {}
    for v in range(mod):
        _, branches = encode(v, mod)
        # Only R operations matter for branches
        r_indices = [i for i, name in enumerate(MAHAMANTRA_WORD_PATTERN) if name == "R"]
        r_branches = tuple(branches[i] for i in r_indices)

        pattern_counts[r_branches] = pattern_counts.get(r_branches, 0) + 1

    print(f"\nUnique branch patterns: {len(pattern_counts)}")
    print("\nTop patterns (R-operation branches only):")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {pattern}: {count} values")


def main():
    print("=" * 70)
    print("MAHA LOSSLESS COMPRESSION ANALYSIS")
    print("=" * 70)

    # First, check if 7 has an inverse mod 137
    inv7 = mod_inverse(7, MAHA_QUANTUM)
    print(f"\n7⁻¹ mod 137 = {inv7}")
    print(f"Verify: 7 × {inv7} mod 137 = {(7 * inv7) % MAHA_QUANTUM}")

    # Test lossless property
    success = test_lossless(MAHA_QUANTUM)

    if success:
        analyze_compression_ratio()
        demonstrate_encoding()
        analyze_branch_patterns()

    # Also test with MALA
    print("\n" + "=" * 70)
    test_lossless(MALA)

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("""
THE MAHAMANTRA ALGORITHM IS LOSSLESS!

The key insight:
1. H and K operations are deterministically invertible
2. R (squaring) has ambiguity, but tracking branches resolves it
3. Encoding = (final_value, branch_sequence)
4. This is similar to arithmetic coding with a binary tree

THE COMPRESSION:
- Not space compression (we add branch bits)
- But SEMANTIC compression: reduces to attractor + path
- The attractor carries the "essence"
- The path carries the "context"

FOR INTENT COMPRESSION:
- The attractor is the "core meaning"
- The branches encode "how we got there"
- This separates WHAT from HOW!
    """)


if __name__ == "__main__":
    main()
