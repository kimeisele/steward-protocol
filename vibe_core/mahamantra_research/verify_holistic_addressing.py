"""
VERIFY HOLISTIC ADDRESSING - THE CHATUH-SLOKI PROOF
===================================================

Hypothesis: The Mantra writes the 16-bit address quarter-by-quarter.
Structure: 4 Quarters -> 4 Nibbles -> 16 Bits -> 65,536 Slots.

Algorithm:
1. Start with Seed.
2. Chant Quarter 1 (Steps 1-4). Take State % 16 -> Nibble 1.
3. Chant Quarter 2 (Steps 5-8). Take State % 16 -> Nibble 2.
4. Chant Quarter 3 (Steps 9-12). Take State % 16 -> Nibble 3.
5. Chant Quarter 4 (Steps 13-16). Take State % 16 -> Nibble 4.

Metric: Distribution of 10,000 sequential inputs.
Expectation: Near uniform distribution (Entropy extraction from pure logic).
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


def algo_holistic(seed: int) -> int:
    """
    The Chatuh-Sloki Generator (PRIME FIELD + JIVA XOR).
    1. Operations in Prime Field 65521 (prevents collapse).
    2. XOR with input seed (preserves uniqueness).
    """
    # Prime Field (largest prime < 65536) ensures bijective operations
    FIELD_PRIME = 65521

    current_value = seed % FIELD_PRIME
    mantra_mask = 0

    for pos in range(WORDS):  # 0 to 15
        name = MAHAMANTRA_WORD_PATTERN[pos]

        # 1. EXECUTE LOGIC (Strict) on Prime Field
        if name == MAHAMANTRA_NAME_HARE:
            current_value = (current_value * SEVEN) % FIELD_PRIME
        elif name == MAHAMANTRA_NAME_KRISHNA:
            current_value = (current_value + TEN) % FIELD_PRIME
        elif name == MAHAMANTRA_NAME_RAMA:
            current_value = (current_value * current_value) % FIELD_PRIME

        # 2. HARVEST NIBBLE -> MANTRA MASK
        if (pos + 1) % 4 == 0:
            nibble = current_value & 0xF
            mantra_mask = (mantra_mask << 4) | nibble

    # 3. UNIFICATION (Mantra Structure ^ Jiva Identity)
    # This ensures every unique seed gets a unique address (mostly),
    # but the *region* is determined by the Mantra.
    final_address = mantra_mask ^ (seed & 0xFFFF)

    return final_address


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
    print(f"  Distribution (16 buckets):")
    print(f"  {[buckets[i] for i in range(16)]}")

    # Check "Vaikuntha" vs "Samsara" separation
    # If the address is purely derived from Mantra, it should scramble the input sequence perfectly.
    print(f"  First 5 Addresses: {addresses[:5]}")
    print("-" * 40)


if __name__ == "__main__":
    inputs = list(range(10000))
    print("HOLISTIC PROOF START: 10,000 Sequential Inputs\n")
    run_test("HOLISTIC (Chatuh-Sloki)", algo_holistic, inputs)
