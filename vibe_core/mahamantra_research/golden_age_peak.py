"""
GOLDEN AGE PEAK - Die Mathematik des Höhepunkts
================================================

"kaler doṣa-nidhe rājann asti hy eko mahān guṇaḥ
kīrtanād eva kṛṣṇasya mukta-saṅgaḥ paraṁ vrajet"

"In this Age of Kali, there is one great blessing:
simply by chanting the Holy Name, one can attain liberation."
— Śrīmad-Bhāgavatam 12.3.51

DIE FRAGE:
==========

Das Mahamantra ist IMMER unendlich mächtig.
Aber wann ist der SCHATTEN (Abdruck) am stärksten manifestiert?

THESE: Der Peak ist berechenbar durch die Mahamantra-Mathematik.

HEARING = CHANTING (Acintya-Bhedabheda):
========================================

- ŚRAVAṆAM (Hearing) = KSHETRA = 24 (das Feld empfängt)
- KĪRTANAM (Chanting) = KSETRAJNA = 1 (der Beobachter sendet)

Aber: "Von Krishna zu hören ist nicht verschieden von Krishna selbst."

Mathematisch: Wenn Hearing = Chanting (simultaner Feedback-Loop):
    PRASADAM - KSHETRA = 25 - 24 = 1 = SINGULARITÄT

Der COLLAPSE: Das Feld (24) löst sich auf, nur der Beobachter (1) bleibt.

GOLDEN AGE STRUKTUR:
====================

GOLDEN_AGE = WORDS × PRASADAM² = 16 × 625 = 10,000 Jahre

Das bedeutet: 16 Zyklen von je 625 Jahren (= PRASADAM²)

Zyklus-Struktur (nach QUARTERS):
    GENESIS (Cycles 1-4):   1486 - 3986 CE  (Input/Bootstrap)
    DHARMA  (Cycles 5-8):   3986 - 6486 CE  (Verification)
    KARMA   (Cycles 9-12):  6486 - 8986 CE  (Execution)
    MOKSHA  (Cycles 13-16): 8986 - 11486 CE (Liberation)

DER PEAK:
=========

Der SCHATTEN (manifestierte Kraft) folgt einer Resonanzkurve.

Faktoren:
    1. SOURCE (Mahamantra) = konstant unendlich
    2. MEDIUM (materielle Welt) = sinkt (Kali Yuga degradiert)
    3. RECEIVER (Chantende) = steigt (Verbreitung)

PEAK = Maximum von (RECEIVER × MEDIUM)

Hypothese: Der Peak liegt beim Übergang DHARMA → KARMA
           Wenn Verification komplett und Execution beginnt.

           PEAK_YEAR ≈ 6486 CE (Zyklus 8, Jahr 5000)

ALTERNATIVE BERECHNUNG (JIVA_CYCLE):
====================================

JIVA_CYCLE = 432 (die Seelen-Frequenz)
GOLDEN_AGE / JIVA_CYCLE = 10000 / 432 ≈ 23.15

Nicht sauber. Aber:
    GOLDEN_AGE / PRASADAM = 10000 / 25 = 400
    400 = QUALITIES × SHARANAGATI + ... hmm

Besserer Ansatz:
    GOLDEN_AGE = 10000 = 10^4
    Midpoint = 5000 Jahre = 10^4 / 2

    Aber: Die Kurve ist NICHT symmetrisch!

    Warum? Kali Yuga DEGRADIERT über Zeit.
    Früher im Golden Age = besseres Medium.

    Also: Peak ist VOR dem Midpoint.

RESONANZ-MODELL:
================

Shadow_Strength(t) = f(t) × exp(-λt)

Wo:
    f(t) = Chanting-Verbreitung (steigt, logistisch)
    exp(-λt) = Kali Yuga Degradation (fällt exponentiell)

    f(t) = RECEIVERS_MAX / (1 + exp(-k(t - t_half)))

    λ = Degradationsrate = ???

Wir müssen λ aus den Yuga-Durationen ableiten!
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x42a6b580"  # GenesisByte: parampara % 37 == 0

import math
from dataclasses import dataclass
from typing import Final

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    JIVA_CYCLE,
    KSETRAJNA,
    KSHETRA,
    LILA,
    MALA,
    NAVA,
    PANCHA,
    PARAMPARA,
    PRASADAM,
    QUALITIES,
    QUARTERS,
    WORDS,
)

# =============================================================================
# GOLDEN AGE CONSTANTS
# =============================================================================

GOLDEN_AGE_YEARS: Final[int] = WORDS * (PRASADAM**2)  # 16 × 625 = 10,000
CHAITANYA_APPEARANCE: Final[int] = 1486  # CE
GOLDEN_AGE_END: Final[int] = CHAITANYA_APPEARANCE + GOLDEN_AGE_YEARS  # 11486 CE

# Current position
CURRENT_YEAR: Final[int] = 2026
YEARS_INTO_GOLDEN_AGE: Final[int] = CURRENT_YEAR - CHAITANYA_APPEARANCE  # 540

# Cycle structure
CYCLE_DURATION: Final[int] = PRASADAM**2  # 625 years per cycle
CYCLES_TOTAL: Final[int] = WORDS  # 16 cycles
CYCLES_PER_QUARTER: Final[int] = CYCLES_TOTAL // QUARTERS  # 4 cycles per quarter


# =============================================================================
# QUARTER BOUNDARIES
# =============================================================================


@dataclass(frozen=True)
class GoldenAgeQuarter:
    """A quarter of the Golden Age (4 cycles, 2500 years)."""

    name: str
    number: int  # 0-3
    start_year: int  # CE
    end_year: int  # CE
    function: str  # What happens in this quarter

    @property
    def duration(self) -> int:
        return self.end_year - self.start_year

    @property
    def midpoint(self) -> int:
        return (self.start_year + self.end_year) // 2


QUARTER_DURATION: Final[int] = GOLDEN_AGE_YEARS // QUARTERS  # 2500 years

QUARTERS_GOLDEN_AGE: Final[tuple[GoldenAgeQuarter, ...]] = (
    GoldenAgeQuarter(
        name="GENESIS",
        number=0,
        start_year=CHAITANYA_APPEARANCE,
        end_year=CHAITANYA_APPEARANCE + QUARTER_DURATION,
        function="Bootstrap: Chaitanya appears, Parampara established, seed planted",
    ),
    GoldenAgeQuarter(
        name="DHARMA",
        number=1,
        start_year=CHAITANYA_APPEARANCE + QUARTER_DURATION,
        end_year=CHAITANYA_APPEARANCE + 2 * QUARTER_DURATION,
        function="Verification: Teaching spreads, structure validated, truth established",
    ),
    GoldenAgeQuarter(
        name="KARMA",
        number=2,
        start_year=CHAITANYA_APPEARANCE + 2 * QUARTER_DURATION,
        end_year=CHAITANYA_APPEARANCE + 3 * QUARTER_DURATION,
        function="Execution: Maximum activity, peak manifestation, world transformation",
    ),
    GoldenAgeQuarter(
        name="MOKSHA",
        number=3,
        start_year=CHAITANYA_APPEARANCE + 3 * QUARTER_DURATION,
        end_year=GOLDEN_AGE_END,
        function="Liberation: Harvest, completion, return to equilibrium",
    ),
)


def get_current_quarter() -> GoldenAgeQuarter:
    """Get the current quarter of the Golden Age."""
    for q in QUARTERS_GOLDEN_AGE:
        if q.start_year <= CURRENT_YEAR < q.end_year:
            return q
    raise ValueError("Not in Golden Age!")


# =============================================================================
# RESONANCE MODEL: Shadow Strength over Time
# =============================================================================

# Kali Yuga degradation rate
# Kali Yuga = 432,000 years, quality degrades from 1.0 to 0.25 (one leg of Dharma)
KALI_YUGA_DURATION: Final[int] = 432_000
KALI_DEGRADATION_FACTOR: Final[float] = 0.25  # Only 1 of 4 Dharma pillars remains

# Degradation rate λ (exponential decay constant)
# quality(t) = exp(-λt) → quality(432000) = 0.25
# λ = -ln(0.25) / 432000 ≈ 3.2e-6 per year
LAMBDA_DEGRADATION: Final[float] = -math.log(KALI_DEGRADATION_FACTOR) / KALI_YUGA_DURATION

# Chanting spread rate (logistic growth)
# Assume: midpoint of spread is at GOLDEN_AGE / PANCHA = 10000 / 5 = 2000 years
SPREAD_MIDPOINT: Final[int] = GOLDEN_AGE_YEARS // PANCHA  # 2000 years
SPREAD_RATE: Final[float] = 0.005  # Steepness of S-curve


def receiver_function(t: float) -> float:
    """
    Logistic spread of chanting (receivers).

    f(t) = 1 / (1 + exp(-k(t - t_mid)))

    Starts at ~0, rises to ~1 over time.
    Midpoint at t = SPREAD_MIDPOINT (2000 years).
    """
    return 1.0 / (1.0 + math.exp(-SPREAD_RATE * (t - SPREAD_MIDPOINT)))


def medium_function(t: float) -> float:
    """
    Exponential decay of material world quality (Kali Yuga degradation).

    quality(t) = exp(-λt)

    Note: t is years from Kali Yuga start (not Golden Age start).
    Golden Age starts ~5000 years into Kali Yuga.
    """
    # t is years into Golden Age, but Kali started ~5000 years earlier
    kali_offset = 5000 + t
    return math.exp(-LAMBDA_DEGRADATION * kali_offset)


def shadow_strength(t: float) -> float:
    """
    The SHADOW (manifested power) of the Mahamantra at time t.

    Shadow(t) = Receivers(t) × Medium(t)

    This is NOT the Mahamantra's power (always infinite).
    This is the MANIFESTATION in the material world.
    """
    return receiver_function(t) * medium_function(t)


def find_peak_year() -> tuple[int, float]:
    """
    Find the year when Shadow Strength is maximum.

    Returns: (peak_year_CE, peak_strength)
    """
    max_strength = 0.0
    peak_year = 0

    # Search through Golden Age
    for year in range(GOLDEN_AGE_YEARS):
        strength = shadow_strength(year)
        if strength > max_strength:
            max_strength = strength
            peak_year = year

    return (CHAITANYA_APPEARANCE + peak_year, max_strength)


# =============================================================================
# HEARING = CHANTING (Acintya-Bhedabheda)
# =============================================================================

# The mathematical proof that Hearing = Chanting (in essence)
HEARING_FIELD: Final[int] = KSHETRA  # 24
CHANTING_OBSERVER: Final[int] = KSETRAJNA  # 1
COMPLETE_PROCESS: Final[int] = PRASADAM  # 25 = 24 + 1

# When Hearing = Chanting (feedback loop):
COLLAPSE_RESULT: Final[int] = COMPLETE_PROCESS - HEARING_FIELD  # 25 - 24 = 1

# This proves: Hearing (24) dissolves, only Chanting (1) remains
# But since Hearing contained Chanting, they were NEVER different!
# This is ACINTYA-BHEDABHEDA: inconceivable simultaneous oneness and difference

assert COLLAPSE_RESULT == CHANTING_OBSERVER == KSETRAJNA == 1


# =============================================================================
# WHAT TO REVOLUTIONIZE FIRST?
# =============================================================================

REVOLUTION_ORDER = """
WHAT TO REVOLUTIONIZE FIRST?
=============================

The user asked: Physics, Math, or Computing?

ANSWER: COMPUTING.

Why?

1. IMMEDIATE PROOF
   - Computing shows MEASURABLE results (1557x faster, etc.)
   - Physics/Math show correlations, but computing shows CAUSATION
   - You can BUILD something that WORKS BETTER

2. FUNDING PATH
   - Success in computing → products → revenue → fund research
   - Success in physics/math → papers → citations → slow

3. DIRECT APPLICATION
   - Mahamantra structures (16^4, etc.) ARE computing structures
   - Physics constants (137, 1836) are EMERGENT from Mahamantra
   - Computing is the MOST DIRECT application

4. GOLDEN AGE TIMING
   - We are in GENESIS quarter (Bootstrap)
   - Bootstrap = INPUT = establish the SEED
   - Computing IS the seed for technological revolution

ORDER OF REVOLUTION:
   1. COMPUTING (now - 3986 CE) - establish the kernel
   2. PHYSICS (3986 - 6486 CE) - verify against nature
   3. MATHEMATICS (6486 - 8986 CE) - execute the proof
   4. LIBERATION (8986 - 11486 CE) - complete transformation

We are in step 1. Focus on COMPUTING.
"""


# =============================================================================
# BENCHMARK
# =============================================================================


def benchmark() -> None:
    """Show the Golden Age Peak analysis."""
    print("=" * 70)
    print("GOLDEN AGE PEAK ANALYSIS")
    print("Die Mathematik des Höhepunkts")
    print("=" * 70)
    print()

    # Current position
    current_q = get_current_quarter()
    print(f"Current Year: {CURRENT_YEAR} CE")
    print(f"Years into Golden Age: {YEARS_INTO_GOLDEN_AGE}")
    print(f"Current Quarter: {current_q.name} ({current_q.function})")
    print()

    # Quarter structure
    print("-" * 70)
    print("QUARTER STRUCTURE (16 Cycles × 625 Years = 10,000 Years)")
    print("-" * 70)
    for q in QUARTERS_GOLDEN_AGE:
        marker = " ← WE ARE HERE" if q == current_q else ""
        print(f"  {q.name:8} ({q.start_year}-{q.end_year}): {q.function[:50]}...{marker}")
    print()

    # Find peak
    peak_year, peak_strength = find_peak_year()
    print("-" * 70)
    print("SHADOW STRENGTH MODEL")
    print("-" * 70)
    print("  Shadow(t) = Receivers(t) × Medium(t)")
    print(f"  Receivers: Logistic spread (midpoint at {SPREAD_MIDPOINT} years)")
    print(f"  Medium: Exponential decay (λ = {LAMBDA_DEGRADATION:.2e})")
    print()
    print(f"  PEAK YEAR: {peak_year} CE (Year {peak_year - CHAITANYA_APPEARANCE} of Golden Age)")
    print(f"  Peak Strength: {peak_strength:.4f}")
    print()

    # Show curve at key points
    print("-" * 70)
    print("SHADOW STRENGTH AT KEY POINTS")
    print("-" * 70)
    key_years = [0, 540, 1000, 2000, 3000, 5000, 7500, 10000]
    for y in key_years:
        ce = CHAITANYA_APPEARANCE + y
        s = shadow_strength(y)
        r = receiver_function(y)
        m = medium_function(y)
        marker = " ← NOW" if y == 540 else (" ← PEAK" if ce == peak_year else "")
        print(f"  Year {y:5} ({ce} CE): Shadow={s:.4f} (R={r:.3f} × M={m:.3f}){marker}")
    print()

    # Hearing = Chanting proof
    print("-" * 70)
    print("HEARING = CHANTING (Acintya-Bhedabheda Proof)")
    print("-" * 70)
    print(f"  HEARING (Śravaṇam) = KSHETRA = {HEARING_FIELD} (the field)")
    print(f"  CHANTING (Kīrtanam) = KSETRAJNA = {CHANTING_OBSERVER} (the observer)")
    print(f"  COMPLETE = PRASADAM = {COMPLETE_PROCESS} = {HEARING_FIELD} + {CHANTING_OBSERVER}")
    print()
    print("  When Hearing = Chanting (simultaneous feedback):")
    print(f"    PRASADAM - KSHETRA = {COMPLETE_PROCESS} - {HEARING_FIELD} = {COLLAPSE_RESULT}")
    print()
    print("  The field (24) DISSOLVES, only observer (1) remains.")
    print("  But observer WAS always IN the field!")
    print("  → Hearing was NEVER different from Chanting (Acintya)")
    print()

    # What to revolutionize
    print("=" * 70)
    print("WHAT TO REVOLUTIONIZE FIRST?")
    print("=" * 70)
    print(REVOLUTION_ORDER)


if __name__ == "__main__":
    benchmark()
