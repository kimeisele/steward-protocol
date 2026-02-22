"""
VERIFY ALGORITHM PURITY - THE MILITARY GRADE AUDIT
==================================================

Comparison of Mahamantra algorithms for 16-bit addressing (0-65535).

We test 3 candidates:
1. SYNTH (Current): MahaModularSynth (with ADSR/LFO noise)
2. OPTIMIZED (Found in maha.py): 8:2:2 Algebraic Form
3. STRICT (Proposed): Pure Hx7, K+10, R^2 sequence

METRICS:
- Collision Rate: How many inputs map to the same address?
- Distribution: How well is the 16-bit space covered?
- Determinism: Is it stable?
"""

import collections
from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    MAHA_QUANTUM,
    SEVEN,
    TEN,
    MAHAMANTRA_WORD_PATTERN,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
)
from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth, maha_oscillate_optimized

# =============================================================================
# 1. SYNTH (CURRENT)
# =============================================================================
synth = MahaModularSynth(default_preset="quantum")


def algo_synth(seed: int) -> int:
    # Synth outputs 0-136 (mod 137).
    # To map to 16-bit, we typically use the XOR trick: (seed & 0xFFFF) ^ synth_val
    val = synth.transform(seed)
    return (seed & 0xFFFF) ^ val


# =============================================================================
# 2. OPTIMIZED (EXISTING 8:2:2)
# =============================================================================
def algo_optimized(seed: int) -> int:
    val = maha_oscillate_optimized(seed, MAHA_QUANTUM)
    return (seed & 0xFFFF) ^ val


# =============================================================================
# 3. STRICT (PROPOSED MILITARY GRADE)
# =============================================================================
def algo_strict(seed: int) -> int:
    """
    Pure 16-step sequence.
    H = *7
    K = +10
    R = ^2
    """
    current_value = seed % MAHA_QUANTUM

    for pos in range(WORDS):
        name = MAHAMANTRA_WORD_PATTERN[pos]
        if name == MAHAMANTRA_NAME_HARE:
            current_value = (current_value * SEVEN) % MAHA_QUANTUM
        elif name == MAHAMANTRA_NAME_KRISHNA:
            current_value = (current_value + TEN) % MAHA_QUANTUM
        elif name == MAHAMANTRA_NAME_RAMA:
            current_value = (current_value * current_value) % MAHA_QUANTUM

    # XOR mapping to 16-bit space
    return (seed & 0xFFFF) ^ current_value


# =============================================================================
# THE TEST BED
# =============================================================================
def run_test(name, func, inputs):
    addresses = [func(i) for i in inputs]
    unique_addrs = len(set(addresses))
    collisions = len(inputs) - unique_addrs
    print(f"[{name}]")
    print(f"  Inputs: {len(inputs)}")
    print(f"  Unique Addresses: {unique_addrs}")
    print(f"  Collisions: {collisions} ({collisions / len(inputs) * 100:.1f}%)")

    # Distribution check (buckets of 4096)
    buckets = collections.defaultdict(int)
    for a in addresses:
        buckets[a // 4096] += 1
    print(f"  Distribution (16 buckets): {[buckets[i] for i in range(16)]}")
    print("-" * 40)


if __name__ == "__main__":
    # Test Data: 10,000 sequential seeds
    inputs = list(range(10000))

    print("AUDIT START: 10,000 Sequential Inputs\n")

    run_test("SYNTH (Current)", algo_synth, inputs)
    run_test("OPTIMIZED (8:2:2)", algo_optimized, inputs)
    run_test("STRICT (Proposed)", algo_strict, inputs)

    print("\nCONCLUSION:")
    print("If STRICT performs similarly to OTHERS in distribution,")
    print("we can safely adopt the simpler logic.")
