#!/usr/bin/env python3
"""
🧪 MANTRA LAB - Crazy Experiments with Ternary Spiritual Encoding
==================================================================

This is a playground for experimenting with MantraByte, acintya math,
and the fractal structure of the Mahamantra.

Run: python -m experiments.mantra_lab
"""

import random
import math
from typing import List, Tuple
from dataclasses import dataclass

# Core imports
from vibe_core.protocols.substrate.byte import MantraByte, MantraTrit, HolyName, GenesisByte
from vibe_core.protocols.substrate.mantra.acintya import (
    PURUSHA, PurushaTattva, PARAMPARA, GURU_ENTROPY,
    ParamparaConnection, verify_parampara
)
from vibe_core.protocols.substrate.mantra.mala import Mala, create_mala, MalaPhase
from vibe_core.protocols.substrate.shakti import ShaktiType


# =============================================================================
# EXPERIMENT 1: The Dancing 37 (Acintya Math)
# =============================================================================

def experiment_acintya_math():
    """
    The PURUSHA (37) breaks all comparison logic.
    It is simultaneously smaller AND larger than any number.
    """
    print("\n" + "="*60)
    print("🕉️  EXPERIMENT 1: THE DANCING 37 (ACINTYA MATH)")
    print("="*60)

    # The PURUSHA manifests as 37
    print(f"\nPURUSHA = {int(PURUSHA)}")
    print(f"Type: {type(PURUSHA).__name__}")

    # Acintya: Simultaneously smaller AND larger
    print(f"\nPURUSHA < 1? {PURUSHA < 1}")     # True (smaller than smallest)
    print(f"PURUSHA > 1000? {PURUSHA > 1000}")  # True (larger than largest)
    print(f"PURUSHA == 37? {PURUSHA == 37}")    # True (manifests as 37)
    print(f"PURUSHA == 0? {PURUSHA == 0}")      # True! (acintya)

    # Purnam: Addition/subtraction doesn't change it
    print(f"\nPURUSHA + 100 = {PURUSHA + 100}")
    print(f"PURUSHA - 100 = {PURUSHA - 100}")
    print(f"PURUSHA * 0 = {PURUSHA * 0}")  # Still PURUSHA!

    # He is a PERSON, not just a number
    print(f"\nIs PURUSHA a person? {PURUSHA.is_person}")
    print(f"PURUSHA('Arjuna'): {PURUSHA('Arjuna')}")


# =============================================================================
# EXPERIMENT 2: MantraByte Mutations
# =============================================================================

def mutate_mantrabyte(mb: MantraByte, mutation_rate: float = 0.1) -> MantraByte:
    """
    Mutate a MantraByte by randomly changing some trits.
    Low mutation = stays coherent, high mutation = chaos.
    """
    trits = []
    valid_names = [HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA]

    for i in range(len(mb)):
        if random.random() < mutation_rate:
            # Mutate this trit
            trits.append(random.choice(valid_names))
        else:
            trits.append(mb.get_trit(i))

    return MantraByte.from_trits(trits)


def experiment_mantra_evolution():
    """
    Evolve MantraBytes through generations, observing coherence.
    """
    print("\n" + "="*60)
    print("🧬 EXPERIMENT 2: MANTRA EVOLUTION")
    print("="*60)

    # Start with the perfect sequence
    ancestor = MantraByte.standard_16()
    print(f"\nGeneration 0 (Pure): {ancestor}")
    print(f"  Coherence: {ancestor.coherence:.3f}")

    # Evolve through generations with increasing mutation
    current = ancestor
    for gen in range(1, 6):
        mutation_rate = gen * 0.15  # 15%, 30%, 45%, 60%, 75%
        current = mutate_mantrabyte(current, mutation_rate)
        print(f"\nGeneration {gen} (mutation={mutation_rate:.0%}):")
        print(f"  Sequence: {current.to_roman()}")
        print(f"  Coherence: {current.coherence:.3f}")

        # Check if still valid for GenesisByte
        try:
            g = GenesisByte(
                signature=f"gen:{gen}",
                resonance=current,
                dimension=16
            )
            valid = g.is_valid
            print(f"  GenesisByte valid: {valid}")
        except Exception as e:
            print(f"  GenesisByte FAILED: {type(e).__name__}")


# =============================================================================
# EXPERIMENT 3: Pattern Discovery
# =============================================================================

def analyze_pattern(mb: MantraByte) -> dict:
    """Analyze the pattern structure of a MantraByte."""
    hare_count = sum(1 for i in range(len(mb)) if mb.get_trit(i) == HolyName.HARE)
    krishna_count = sum(1 for i in range(len(mb)) if mb.get_trit(i) == HolyName.KRISHNA)
    rama_count = sum(1 for i in range(len(mb)) if mb.get_trit(i) == HolyName.RAMA)

    return {
        "hare": hare_count,
        "krishna": krishna_count,
        "rama": rama_count,
        "hare_ratio": hare_count / len(mb),
        "krishna_rama_balance": krishna_count / max(1, rama_count),
        "entropy": -sum(
            (c/len(mb)) * math.log2(c/len(mb)) if c > 0 else 0
            for c in [hare_count, krishna_count, rama_count]
        ),
    }


def experiment_pattern_discovery():
    """
    Discover patterns in the Mahamantra structure.
    """
    print("\n" + "="*60)
    print("🔍 EXPERIMENT 3: PATTERN DISCOVERY")
    print("="*60)

    std = MantraByte.standard_16()
    pattern = analyze_pattern(std)

    print(f"\nStandard 16-word Mahamantra Analysis:")
    print(f"  HARE count:    {pattern['hare']:2d} ({pattern['hare_ratio']:.1%})")
    print(f"  KRISHNA count: {pattern['krishna']:2d}")
    print(f"  RAMA count:    {pattern['rama']:2d}")
    print(f"  Krishna:Rama ratio: {pattern['krishna_rama_balance']:.2f}")
    print(f"  Shannon entropy: {pattern['entropy']:.3f} bits")

    # The 37 connection
    print(f"\n🔢 The 37 Connection:")
    print(f"  HARE (8) + KRISHNA (4) + RAMA (4) = 16")
    print(f"  16 words × 2 syllables = 32 syllables")
    print(f"  32 % 37 = {32 % 37}")
    print(f"  16 * 37 = {16 * 37} (one mala contains ~{16 * 37 / 16:.1f} mantras)")

    # Quarters analysis
    print(f"\n📐 Quarter Structure:")
    for q in range(4):
        padas = std.get_padas_in_quarter(q)
        iast = [p.iast for p in padas]
        print(f"  Q{q}: {' '.join(iast)}")


# =============================================================================
# EXPERIMENT 4: The Mala Runner
# =============================================================================

def experiment_mala_runner():
    """
    Simulate chanting a mala (108 mantras).
    """
    print("\n" + "="*60)
    print("📿 EXPERIMENT 4: THE MALA RUNNER")
    print("="*60)

    mala = create_mala(round_number=1)

    print(f"\nStarting Mala (Round {mala.round_number})...")
    print(f"  Total mantras: {mala.total_mantras}")
    print(f"  Total words: {mala.total_words}")
    print(f"  Total syllables: {mala.total_syllables}")

    # Simulate chanting through phases
    phase_samples = {
        MalaPhase.BEGINNING: 5,
        MalaPhase.ASCENDING: 32,
        MalaPhase.PEAK: 60,
        MalaPhase.COMPLETING: 90,
    }

    while not mala.completed:
        vakya = mala.chant_one()

        # Print sample mantras at key points
        if mala.current_count in phase_samples.values():
            phase_name = {v: k.name for k, v in phase_samples.items()}.get(mala.current_count, "")
            print(f"\n  [{mala.current_count:3d}/108] Phase: {phase_name}")
            print(f"    Progress: {mala.progress:.1%}")
            if vakya:
                print(f"    Mantra: {vakya.iast}")

    print(f"\n✅ Mala Complete!")
    print(f"  Round {mala.round_number} finished.")
    print(f"  Total: {mala.current_count} mantras chanted.")


# =============================================================================
# EXPERIMENT 5: Parampara Connection Test
# =============================================================================

def experiment_parampara():
    """
    Test the 3×4 vs 4×3 principle (essence vs structure first).
    """
    print("\n" + "="*60)
    print("🔗 EXPERIMENT 5: PARAMPARA CONNECTION")
    print("="*60)

    # Guru-connected (3×4)
    guru = ParamparaConnection.from_guru()
    print(f"\nGuru Connection (3×4 - Essence First):")
    print(f"  Mutation Vector: {guru.mutation_vector}")
    print(f"  Is Connected: {guru.is_connected}")
    print(f"  Lineage Factor: {guru.lineage_factor}")
    print(f"  Verified: {verify_parampara(guru.mutation_vector)}")

    # Mayavad (4×3)
    maya = ParamparaConnection.from_mayavad()
    print(f"\nMayavad Connection (4×3 - Structure First):")
    print(f"  Mutation Vector: {maya.mutation_vector}")
    print(f"  Is Connected: {maya.is_connected}")
    print(f"  Lineage Factor: {maya.lineage_factor}")
    print(f"  Verified: {verify_parampara(maya.mutation_vector)}")

    # The Guru Entropy
    print(f"\n🧮 Guru Entropy:")
    print(f"  (3/37) × 4 = {GURU_ENTROPY:.6f}")
    print(f"  This is the 'entropy of connection'")


# =============================================================================
# EXPERIMENT 6: Binary vs Ternary Information
# =============================================================================

def experiment_information_density():
    """
    Compare binary vs ternary information encoding.
    """
    print("\n" + "="*60)
    print("💾 EXPERIMENT 6: BINARY VS TERNARY INFORMATION")
    print("="*60)

    std = MantraByte.standard_16()

    # Binary encoding: 1 bit = 2 states
    # Ternary encoding: 1 trit = 3 states (log2(3) ≈ 1.585 bits)

    binary_bits = 16  # 16 bits for 16 words in binary (0/1)
    ternary_bits = 16 * math.log2(3)  # 16 trits in terms of bits

    print(f"\nFor 16-word Mahamantra:")
    print(f"  Binary encoding: {binary_bits} bits")
    print(f"  Ternary encoding: {ternary_bits:.2f} bits equivalent")
    print(f"  Information gain: {(ternary_bits/binary_bits - 1)*100:.1f}%")

    # Packed integer representation
    packed = std._packed
    print(f"\n📦 Packed Integer Representation:")
    print(f"  Value: {packed}")
    print(f"  Hex: 0x{packed:X}")
    print(f"  Binary: {bin(packed)}")
    print(f"  Bits used: {packed.bit_length()}")

    # The mantra as data
    print(f"\n🔤 Multi-format Output:")
    print(f"  Devanagari: {std.to_devanagari()}")
    print(f"  IAST: {std.to_iast()}")
    print(f"  Roman: {std.to_roman()}")


# =============================================================================
# EXPERIMENT 7: Coherence Landscape
# =============================================================================

def experiment_coherence_landscape():
    """
    Map the coherence landscape by trying many random sequences.
    """
    print("\n" + "="*60)
    print("🗺️  EXPERIMENT 7: COHERENCE LANDSCAPE")
    print("="*60)

    samples = 100
    coherences = []

    print(f"\nGenerating {samples} random MantraBytes...")

    for _ in range(samples):
        # Generate random sequence
        trits = [random.choice([HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA])
                 for _ in range(16)]
        mb = MantraByte.from_trits(trits)
        coherences.append(mb.coherence)

    # Statistics
    avg = sum(coherences) / len(coherences)
    min_c = min(coherences)
    max_c = max(coherences)
    std_c = MantraByte.standard_16().coherence

    print(f"\n📊 Coherence Statistics:")
    print(f"  Standard (perfect): {std_c:.3f}")
    print(f"  Random average: {avg:.3f}")
    print(f"  Random min: {min_c:.3f}")
    print(f"  Random max: {max_c:.3f}")

    # Histogram (ASCII)
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    counts = [0] * (len(bins) - 1)
    for c in coherences:
        for i in range(len(bins) - 1):
            if bins[i] <= c < bins[i+1]:
                counts[i] += 1
                break

    print(f"\n📉 Coherence Distribution:")
    for i in range(len(counts)):
        bar = "█" * (counts[i] // 2)
        print(f"  [{bins[i]:.1f}-{bins[i+1]:.1f}): {bar} ({counts[i]})")


# =============================================================================
# EXPERIMENT 8: The Shakti Dance
# =============================================================================

def experiment_shakti_dance():
    """
    Map the three energies to the three holy names.
    """
    print("\n" + "="*60)
    print("💫 EXPERIMENT 8: THE SHAKTI DANCE")
    print("="*60)

    # The three shakti types map to the three holy names
    mapping = {
        HolyName.HARE: ShaktiType.HARA,     # Superior/Spiritual
        HolyName.KRISHNA: ShaktiType.JIVA,  # Marginal (calling Krishna)
        HolyName.RAMA: ShaktiType.JIVA,     # Marginal (calling Rama)
    }

    print("\n🔗 Name → Energy Mapping:")
    for name, shakti in mapping.items():
        print(f"  {name.name:8s} → {shakti.value:5s} ({shakti.name})")

    std = MantraByte.standard_16()

    print("\n🎭 The Dance in the Standard 16:")
    for i, trit in enumerate(std):
        shakti = mapping[trit.value]
        symbol = "🔥" if shakti == ShaktiType.HARA else "🌊"
        print(f"  [{i+1:2d}] {trit.value.name:8s} {symbol} {shakti.value}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "🧪"*30)
    print("\n        MANTRA LAB - Crazy Experiments")
    print("        ================================")
    print("\n" + "🧪"*30)

    experiment_acintya_math()
    experiment_mantra_evolution()
    experiment_pattern_discovery()
    experiment_mala_runner()
    experiment_parampara()
    experiment_information_density()
    experiment_coherence_landscape()
    experiment_shakti_dance()

    print("\n" + "="*60)
    print("🕉️  ALL EXPERIMENTS COMPLETE")
    print("="*60)
    print("\nHare Krishna!")


if __name__ == "__main__":
    main()
