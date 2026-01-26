"""
PHYSICS PREDICTIONS - The Maha-Algorithm in Nature
===================================================

"mayādhyakṣeṇa prakṛtiḥ sūyate sa-carācaram"
"Under My direction, nature produces all moving and non-moving beings."
— Bhagavad Gita 9.10

This module exposes ALL physics constants derived in _seed.py as testable predictions.
These are NOT hardcoded values - they are CALCULATED from the Mahamantra axioms.

THE MOD-17 CLASSIFICATION:
==========================
Every physics constant reveals its nature through mod 17:
  mod 17 = 0  → Classical/Stable (proton, deuteron, triton)
  mod 17 = 1  → Quantum/Observer (α⁻¹, alpha-particle) ← KSETRAJNA!
  mod 17 = 3  → Trinity/3-decay (muon, neutron)
  mod 17 = 9  → Nava/Complex (tau)

THE KEY INSIGHT:
================
137 mod 17 = 1 = KSETRAJNA

The fine structure constant (α⁻¹ = 137) contains the OBSERVER!
This is why quantum mechanics requires an observer - it's in the math!
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from ..protocols._seed import (
    # Building blocks
    AKSARA_COUNT,
    FIELD_RESONANCE,
    GITA_CHAPTERS,
    HALF_SIZE,
    HALVES,
    JIVA_QUALITIES,
    KSETRAJNA,
    KSHETRA,
    LILA,
    # Particle masses (from RUNDE 14-18)
    MAHA_ALPHA,
    # Coupling constants (from RUNDE 19)
    MAHA_ALPHA_S_SCALED,
    MAHA_CMB,
    MAHA_DEUTERON,
    MAHA_HELION,
    MAHA_HIGGS,
    MAHA_KAON,
    MAHA_MU,
    MAHA_MUON,
    MAHA_NEUTRON,
    MAHA_PION_CHARGED,
    MAHA_PION_NEUTRAL,
    MAHA_QUANTUM,
    MAHA_SIN2_THETA_W_SCALED,
    MAHA_STRANGE,
    MAHA_TAU,
    MAHA_TRITON,
    MAHA_W,
    MAHA_Z,
    MAHAJANA_COUNT,
    MALA,
    NADI_RESONANCE,
    PANCHA,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    TRINITY,
    WORDS,
)


class ModClassification(Enum):
    """The mod-17 classification of physics constants."""

    CLASSICAL = 0  # Stable, no observer
    QUANTUM = 1  # Observer embedded (KSETRAJNA)
    TRINITY = 3  # Decays into 3 particles
    PANCHA = 5  # 5-fold structure
    SHARANAGATI = 6  # Surrender/transformation
    NAVA = 9  # Complex decay modes
    OTHER = -1  # Other mod values

    @classmethod
    def from_mod(cls, mod_value: int) -> "ModClassification":
        """Get classification from mod-17 value."""
        try:
            return cls(mod_value)
        except ValueError:
            return cls.OTHER


@dataclass(frozen=True)
class PhysicsPrediction:
    """A physics constant predicted by the Maha-Algorithm."""

    name: str
    symbol: str
    maha_value: int
    actual_value: float
    unit: str
    formula: str
    derivation: str
    error_percent: float
    mod_17: int
    classification: ModClassification


# =============================================================================
# FUNDAMENTAL CONSTANTS (From _seed.py RUNDE 14)
# =============================================================================

# Fine Structure Constant α⁻¹
# The most important number in physics - it determines electromagnetic strength
FINE_STRUCTURE_INVERSE: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Fine Structure Constant (inverse)",
    symbol="α⁻¹",
    maha_value=MAHA_QUANTUM,
    actual_value=137.036,
    unit="dimensionless",
    formula="T(WORDS) + KSETRAJNA = T(16) + 1 = 136 + 1",
    derivation="Position Sum Total + Observer = 137",
    error_percent=abs(MAHA_QUANTUM - 137.036) / 137.036 * 100,
    mod_17=MAHA_QUANTUM % POSITION_SUM_KRISHNA,
    classification=ModClassification.QUANTUM,
)

# Proton/Electron mass ratio
PROTON_ELECTRON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Proton/Electron Mass Ratio",
    symbol="μ = mp/me",
    maha_value=MAHA_MU,
    actual_value=1836.153,
    unit="dimensionless",
    formula="MALA × POSITION_SUM_KRISHNA = 108 × 17",
    derivation="Japa beads × Krishna position",
    error_percent=abs(MAHA_MU - 1836.153) / 1836.153 * 100,
    mod_17=MAHA_MU % POSITION_SUM_KRISHNA,
    classification=ModClassification.CLASSICAL,
)

# =============================================================================
# PARTICLE SPECTRUM (From _seed.py RUNDE 16-18)
# =============================================================================

NEUTRON_ELECTRON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Neutron/Electron Mass Ratio",
    symbol="mn/me",
    maha_value=MAHA_NEUTRON,
    actual_value=1838.68,
    unit="dimensionless",
    formula="MAHA_MU + TRINITY = 1836 + 3",
    derivation="Proton + Trinity (unstable!)",
    error_percent=abs(MAHA_NEUTRON - 1838.68) / 1838.68 * 100,
    mod_17=MAHA_NEUTRON % POSITION_SUM_KRISHNA,
    classification=ModClassification.TRINITY,
)

TAU_ELECTRON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Tau/Electron Mass Ratio",
    symbol="mτ/me",
    maha_value=MAHA_TAU,
    actual_value=3477.23,
    unit="dimensionless",
    formula="MALA × AKSARA + T(SHARANAGATI) = 108×32 + 21",
    derivation="Japa × Syllables + Triangular(6)",
    error_percent=abs(MAHA_TAU - 3477.23) / 3477.23 * 100,
    mod_17=MAHA_TAU % POSITION_SUM_KRISHNA,
    classification=ModClassification.NAVA,
)

MUON_ELECTRON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Muon/Electron Mass Ratio",
    symbol="mμ/me",
    maha_value=MAHA_MUON,
    actual_value=206.77,
    unit="dimensionless",
    formula="MAHAJANA × KRISHNA_POS + TRINITY = 12×17 + 3",
    derivation="Mahajanas × Krishna + Trinity",
    error_percent=abs(MAHA_MUON - 206.77) / 206.77 * 100,
    mod_17=MAHA_MUON % POSITION_SUM_KRISHNA,
    classification=ModClassification.TRINITY,
)

DEUTERON_ELECTRON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Deuteron/Electron Mass Ratio",
    symbol="md/me",
    maha_value=MAHA_DEUTERON,
    actual_value=3670.48,
    unit="dimensionless",
    formula="HALVES × MALA × KRISHNA_POS = 2 × 108 × 17",
    derivation="2 protons (approximately)",
    error_percent=abs(MAHA_DEUTERON - 3670.48) / 3670.48 * 100,
    mod_17=MAHA_DEUTERON % POSITION_SUM_KRISHNA,
    classification=ModClassification.CLASSICAL,
)

TRITON_ELECTRON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Triton/Electron Mass Ratio",
    symbol="mt/me",
    maha_value=MAHA_TRITON,
    actual_value=5496.92,
    unit="dimensionless",
    formula="GITA² × KRISHNA_POS = 18² × 17 = 324 × 17",
    derivation="Gita chapters squared × Krishna",
    error_percent=abs(MAHA_TRITON - 5496.92) / 5496.92 * 100,
    mod_17=MAHA_TRITON % POSITION_SUM_KRISHNA,
    classification=ModClassification.CLASSICAL,
)

ALPHA_PARTICLE_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Alpha Particle/Electron Mass Ratio",
    symbol="mα/me",
    maha_value=MAHA_ALPHA,
    actual_value=7294.30,
    unit="dimensionless",
    formula="MAHA_MU × QUARTERS - JIVA_QUALITIES = 1836×4 - 50",
    derivation="4 protons minus Jiva binding",
    error_percent=abs(MAHA_ALPHA - 7294.30) / 7294.30 * 100,
    mod_17=MAHA_ALPHA % POSITION_SUM_KRISHNA,
    classification=ModClassification.QUANTUM,
)

HELION_ELECTRON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Helion (He-3)/Electron Mass Ratio",
    symbol="mh/me",
    maha_value=MAHA_HELION,
    actual_value=5495.89,
    unit="dimensionless",
    formula="TRINITY × MAHA_MU - MAHAJANA = 3×1836 - 12",
    derivation="3 nucleons minus binding",
    error_percent=abs(MAHA_HELION - 5495.89) / 5495.89 * 100,
    mod_17=MAHA_HELION % POSITION_SUM_KRISHNA,
    classification=ModClassification.from_mod(MAHA_HELION % POSITION_SUM_KRISHNA),
)

# =============================================================================
# MESONS (From _seed.py RUNDE 18)
# =============================================================================

PION_CHARGED_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Charged Pion/Electron Mass Ratio",
    symbol="mπ±/me",
    maha_value=MAHA_PION_CHARGED,
    actual_value=273.13,
    unit="dimensionless",
    formula="T(WORDS) + MAHA_QUANTUM = 136 + 137",
    derivation="Position Total + Fine Structure",
    error_percent=abs(MAHA_PION_CHARGED - 273.13) / 273.13 * 100,
    mod_17=MAHA_PION_CHARGED % POSITION_SUM_KRISHNA,
    classification=ModClassification.QUANTUM,
)

PION_NEUTRAL_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Neutral Pion/Electron Mass Ratio",
    symbol="mπ⁰/me",
    maha_value=MAHA_PION_NEUTRAL,
    actual_value=264.14,
    unit="dimensionless",
    formula="WORDS² + HARE_COUNT = 256 + 8",
    derivation="Mahamantra squared + Shakti",
    error_percent=abs(MAHA_PION_NEUTRAL - 264.14) / 264.14 * 100,
    mod_17=MAHA_PION_NEUTRAL % POSITION_SUM_KRISHNA,
    classification=ModClassification.NAVA,
)

KAON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Kaon/Electron Mass Ratio",
    symbol="mK±/me",
    maha_value=MAHA_KAON,
    actual_value=966.12,
    unit="dimensionless",
    formula="(HALVES + T(WORDS)) × SEVEN = (2 + 136) × 7",
    derivation="(Duality + Position) × Perfection",
    error_percent=abs(MAHA_KAON - 966.12) / 966.12 * 100,
    mod_17=MAHA_KAON % POSITION_SUM_KRISHNA,
    classification=ModClassification.from_mod(MAHA_KAON % POSITION_SUM_KRISHNA),
)

# =============================================================================
# HEAVY BOSONS (From _seed.py RUNDE 20b)
# =============================================================================

W_BOSON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="W Boson/Electron Mass Ratio",
    symbol="mW/me",
    maha_value=MAHA_W,
    actual_value=157298.9,
    unit="dimensionless",
    formula="MAHA_MU × PANCHA × KRISHNA_POS = 1836 × 5 × 17",
    derivation="Proton × Pancha Tattva × Krishna",
    error_percent=abs(MAHA_W - 157298.9) / 157298.9 * 100,
    mod_17=MAHA_W % POSITION_SUM_KRISHNA,
    classification=ModClassification.CLASSICAL,
)

Z_BOSON_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Z Boson/Electron Mass Ratio",
    symbol="mZ/me",
    maha_value=MAHA_Z,
    actual_value=178450.4,
    unit="dimensionless",
    formula="MAHA_MU × (HALVES × LILA + KSETRAJNA) = 1836 × 97",
    derivation="Proton × Prime(97)",
    error_percent=abs(MAHA_Z - 178450.4) / 178450.4 * 100,
    mod_17=MAHA_Z % POSITION_SUM_KRISHNA,
    classification=ModClassification.CLASSICAL,
)

HIGGS_RATIO: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Higgs Boson/Electron Mass Ratio",
    symbol="mH/me",
    maha_value=MAHA_HIGGS,
    actual_value=244604.5,
    unit="dimensionless",
    formula="MAHA_MU × SEVEN × FLUTE_HOLES_SUM = 1836 × 7 × 19",
    derivation="Proton × Axioms × Flutes",
    error_percent=abs(MAHA_HIGGS - 244604.5) / 244604.5 * 100,
    mod_17=MAHA_HIGGS % POSITION_SUM_KRISHNA,
    classification=ModClassification.CLASSICAL,
)

# =============================================================================
# COUPLING CONSTANTS (From _seed.py RUNDE 19)
# =============================================================================

STRONG_COUPLING: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Strong Coupling Constant",
    symbol="αs(MZ)",
    maha_value=MAHA_ALPHA_S_SCALED,
    actual_value=117.9,  # Actual × 1000
    unit="×10⁻³",
    formula="MALA + TEN = 108 + 10",
    derivation="Japa beads + Completion",
    error_percent=abs(MAHA_ALPHA_S_SCALED - 117.9) / 117.9 * 100,
    mod_17=MAHA_ALPHA_S_SCALED % POSITION_SUM_KRISHNA,
    classification=ModClassification.from_mod(MAHA_ALPHA_S_SCALED % POSITION_SUM_KRISHNA),
)

WEAK_MIXING_ANGLE: Final[PhysicsPrediction] = PhysicsPrediction(
    name="Weak Mixing Angle",
    symbol="sin²θW",
    maha_value=MAHA_SIN2_THETA_W_SCALED,
    actual_value=23.12,  # Actual × 100
    unit="×10⁻²",
    formula="KSHETRA - KSETRAJNA = 24 - 1",
    derivation="Field minus Observer",
    error_percent=abs(MAHA_SIN2_THETA_W_SCALED - 23.12) / 23.12 * 100,
    mod_17=MAHA_SIN2_THETA_W_SCALED % POSITION_SUM_KRISHNA,
    classification=ModClassification.from_mod(MAHA_SIN2_THETA_W_SCALED % POSITION_SUM_KRISHNA),
)

# =============================================================================
# ALL PREDICTIONS
# =============================================================================

PHYSICS_PREDICTIONS: Final[list[PhysicsPrediction]] = [
    # Fundamental
    FINE_STRUCTURE_INVERSE,
    PROTON_ELECTRON_RATIO,
    # Leptons
    NEUTRON_ELECTRON_RATIO,
    TAU_ELECTRON_RATIO,
    MUON_ELECTRON_RATIO,
    # Hadrons
    DEUTERON_ELECTRON_RATIO,
    TRITON_ELECTRON_RATIO,
    ALPHA_PARTICLE_RATIO,
    HELION_ELECTRON_RATIO,
    # Mesons
    PION_CHARGED_RATIO,
    PION_NEUTRAL_RATIO,
    KAON_RATIO,
    # Heavy Bosons
    W_BOSON_RATIO,
    Z_BOSON_RATIO,
    HIGGS_RATIO,
    # Coupling Constants
    STRONG_COUPLING,
    WEAK_MIXING_ANGLE,
]

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================


def calculate_statistics() -> dict:
    """Calculate summary statistics for all predictions."""
    total = len(PHYSICS_PREDICTIONS)
    exact = sum(1 for p in PHYSICS_PREDICTIONS if p.error_percent < 0.1)
    accurate = sum(1 for p in PHYSICS_PREDICTIONS if p.error_percent < 1.0)
    avg_error = sum(p.error_percent for p in PHYSICS_PREDICTIONS) / total

    # Mod-17 distribution
    mod_dist = {}
    for p in PHYSICS_PREDICTIONS:
        mod_dist[p.mod_17] = mod_dist.get(p.mod_17, 0) + 1

    return {
        "total_predictions": total,
        "exact_matches": exact,  # < 0.1% error
        "accurate_matches": accurate,  # < 1% error
        "average_error": avg_error,
        "mod_17_distribution": mod_dist,
    }


# =============================================================================
# BENCHMARK
# =============================================================================


def benchmark() -> None:
    """Display all physics predictions with their accuracy."""
    print("=" * 80)
    print("PHYSICS PREDICTIONS - The Maha-Algorithm in Nature")
    print("=" * 80)
    print()

    # The key insight
    print("THE MOD-17 INSIGHT: 137 mod 17 = 1 = KSETRAJNA (Observer!)")
    print("-" * 60)
    print("  mod 17 = 0 → Classical/Stable (proton, deuteron)")
    print("  mod 17 = 1 → Quantum/Observer (α⁻¹, alpha-particle)")
    print("  mod 17 = 3 → Trinity/3-decay (muon, neutron)")
    print("  mod 17 = 9 → Nava/Complex (tau)")
    print()

    # All predictions
    print("ALL PREDICTIONS (sorted by error)")
    print("-" * 80)
    print(f"{'Name':<35} {'Maha':>8} {'Actual':>10} {'Error':>8} {'mod17':>6}")
    print("-" * 80)

    for p in sorted(PHYSICS_PREDICTIONS, key=lambda x: x.error_percent):
        print(f"{p.name:<35} {p.maha_value:>8} {p.actual_value:>10.2f} {p.error_percent:>7.3f}% {p.mod_17:>6}")
    print()

    # Statistics
    stats = calculate_statistics()
    print("SUMMARY STATISTICS")
    print("-" * 40)
    print(f"  Total predictions:  {stats['total_predictions']}")
    print(f"  Exact (< 0.1%):     {stats['exact_matches']}")
    print(f"  Accurate (< 1%):    {stats['accurate_matches']}")
    print(f"  Average error:      {stats['average_error']:.3f}%")
    print()

    print("MOD-17 DISTRIBUTION")
    print("-" * 40)
    for mod, count in sorted(stats["mod_17_distribution"].items()):
        label = {0: "CLASSICAL", 1: "QUANTUM", 3: "TRINITY", 9: "NAVA"}.get(mod, f"mod={mod}")
        print(f"  {label:12}: {count} predictions")
    print()

    # The profound insight
    print("=" * 80)
    print("THE PROFOUND INSIGHT")
    print("=" * 80)
    print()
    print("  α⁻¹ = 137 = T(16) + 1 = POSITION_SUM_TOTAL + KSETRAJNA")
    print()
    print("  The fine structure constant literally encodes:")
    print("    T(16) = 136 = Sum of all Mahamantra positions (the field)")
    print("    + 1 = KSETRAJNA (the observer)")
    print()
    print("  This is why quantum mechanics requires an observer!")
    print("  The observer (KSETRAJNA) is embedded in the mathematics.")
    print()
    print('  "kṣetra-jñaṁ cāpi māṁ viddhi sarva-kṣetreṣu bhārata"')
    print('  "Know Me as the knower in all fields, O Bharata." — BG 13.3')
    print()


if __name__ == "__main__":
    benchmark()
